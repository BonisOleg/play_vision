import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models
from django.contrib import messages
from django.core.files.storage import default_storage
from django.conf import settings
from datetime import timedelta

from .models import User, Profile
from .forms import ProfileForm, PasswordChangeForm
from apps.subscriptions.models import Subscription, Plan
from apps.loyalty.models import LoyaltyAccount, LoyaltyTier
from apps.content.models import Course, Material, UserCourseProgress, Favorite
try:
    from apps.payments.models import Payment
except ImportError:
    Payment = None


class CabinetView(LoginRequiredMixin, TemplateView):
    """Основний view кабінету користувача з вкладками"""
    template_name = 'account/cabinet.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        tab = kwargs.get('tab', self.request.GET.get('tab', 'profile'))
        
        # Загальна інформація користувача
        context['active_tab'] = tab
        context['user_profile'] = getattr(user, 'profile', None)
        
        # Індикатор "днів з нами"
        days = (timezone.now().date() - user.date_joined.date()).days
        context['days_count'] = days
        context['days_word'] = self._get_days_word(days)
        
        # Додати інтереси для форми
        from apps.content.models import Tag
        context['interests'] = Tag.objects.filter(
            tag_type='interest'
        ).order_by('display_order')
        
        # Активна підписка
        active_subscription = user.subscriptions.filter(
            status='active',
            end_date__gte=timezone.now()
        ).first()
        context['active_subscription'] = active_subscription
        
        # Аккаунт лояльності
        loyalty_account = None
        try:
            loyalty_account = user.loyalty_account
            created = False
        except (LoyaltyAccount.DoesNotExist, AttributeError):
            # Спробувати створити, але обробити помилки БД
            try:
                loyalty_account = LoyaltyAccount.objects.create(
                    user=user,
                    points=0,
                    lifetime_points=0,
                    lifetime_spent_points=0
                )
                created = True
                
                # Встановити початковий рівень
                bronze_tier = LoyaltyTier.objects.filter(is_active=True).order_by('points_required').first()
                if bronze_tier:
                    loyalty_account.current_tier = bronze_tier
                    loyalty_account.save()
            except Exception as e:
                # Якщо таблиці немає або є проблеми з БД, просто логуємо
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not create loyalty account for user {user.id}: {e}")
                created = False
        
        context['loyalty_account'] = loyalty_account
        
        # Специфічний контекст для кожної вкладки
        if tab == 'subscription':
            context.update(self._get_subscription_context(user, active_subscription))
        elif tab == 'files':
            context.update(self._get_files_context(user, active_subscription))
        elif tab == 'loyalty':
            context.update(self._get_loyalty_context(user, loyalty_account))
        elif tab == 'payments':
            context.update(self._get_payments_context(user))
        
        return context
    
    def _get_days_word(self, n):
        """Повертає правильне слово для кількості днів"""
        if n % 10 == 1 and n % 100 != 11:
            return "день"
        elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
            return "дні"
        else:
            return "днів"
    
    def _get_subscription_context(self, user, active_subscription):
        """Контекст для вкладки підписки"""
        context = {}
        
        # Доступні плани
        context['available_plans'] = Plan.objects.filter(is_active=True).order_by('duration_months')
        
        # Переваги поточного плану
        if active_subscription:
            context['plan_benefits'] = [
                'Безлімітний перегляд',
                '5-15% знижки на матеріали',
                'Ексклюзивні матеріали (для Pro)',
            ]
            context['next_payment_date'] = active_subscription.end_date
        
        # Статистика
        context['subscription_stats'] = {
            'total_subscriptions': user.subscriptions.count(),
            'days_remaining': active_subscription.days_remaining if active_subscription else 0,
        }
        
        # Додати loyalty дані
        if hasattr(user, 'loyalty_account'):
            loyalty_account = user.loyalty_account
            
            # Отримати наступний tier
            next_tier = None
            points_to_next = 0
            if loyalty_account.current_tier:
                next_tier = LoyaltyTier.objects.filter(
                    is_active=True,
                    points_required__gt=loyalty_account.current_tier.points_required
                ).order_by('points_required').first()
                if next_tier:
                    points_to_next = max(0, next_tier.points_required - loyalty_account.lifetime_points)
            
            # Розрахувати прогрес
            progress_pct = 0
            if next_tier and points_to_next > 0:
                total_for_tier = next_tier.points_required - (loyalty_account.current_tier.points_required if loyalty_account.current_tier else 0)
                current_progress = loyalty_account.lifetime_points - (loyalty_account.current_tier.points_required if loyalty_account.current_tier else 0)
                progress_pct = int((current_progress / total_for_tier) * 100) if total_for_tier > 0 else 0
            
            # Потенційна знижка
            potential_discount = next_tier.discount_percentage if next_tier else loyalty_account.get_discount_percentage()
            
            context['loyalty_account'] = {
                'current_tier': loyalty_account.current_tier or LoyaltyTier.objects.filter(is_active=True).order_by('points_required').first(),
                'next_tier': next_tier,
                'total_points': loyalty_account.lifetime_points,
                'points_to_next_tier': points_to_next,
                'progress_percentage': progress_pct,
                'current_discount': loyalty_account.get_discount_percentage(),
                'potential_discount': potential_discount,
            }
        
        return context
    
    def _get_files_context(self, user, active_subscription):
        """Контекст для вкладки файлів"""
        context = {}
        
        # Доступні курси через підписку
        accessible_courses = []
        if active_subscription:
            accessible_courses = Course.objects.filter(
                is_published=True,
                requires_subscription=True
            ).select_related('category').prefetch_related('materials')
        
        # Прогрес по курсах
        progress_map = {
            p.course_id: p for p in user.course_progress.filter(
                course__in=accessible_courses
            ).select_related('course').prefetch_related('materials_completed')
        }
        
        # Підготувати дані для відображення матеріалів
        materials_data = []
        for course in accessible_courses:
            progress = progress_map.get(course.id)
            for material in course.materials.all()[:6]:  # Показати перші 6 матеріалів як на дизайні
                material_progress = 0
                is_completed = False
                
                if progress:
                    is_completed = material in progress.materials_completed.all()
                    if is_completed:
                        material_progress = 100
                    elif progress.progress_percentage > 0:
                        # Припустимий прогрес для поточного матеріалу
                        completed_count = progress.materials_completed.count()
                        total_materials = course.materials.count()
                        if total_materials > 0:
                            material_progress = min(85, (completed_count / total_materials) * 100)
                
                # Визначити тип контенту
                content_type_display = "PDF / Відео"
                if material.content_type == 'video':
                    content_type_display = "Відео"
                elif material.content_type == 'pdf':
                    content_type_display = "PDF"
                elif material.content_type == 'article':
                    content_type_display = "Стаття"
                
                # Перевірка доступу
                has_access = bool(active_subscription)  # Є підписка = є доступ
                purchased_separately = False
                
                # Перевірити чи куплений окремо (не через підписку)
                if Payment and not active_subscription:
                    purchased_separately = Payment.objects.filter(
                        user=user,
                        course=course,
                        status='succeeded',
                        subscription__isnull=True
                    ).exists()
                    if purchased_separately:
                        has_access = True
                
                materials_data.append({
                    'id': material.id,
                    'title': material.title,
                    'course_title': course.title,
                    'content_type': content_type_display,
                    'progress': material_progress,
                    'is_completed': is_completed,
                    'is_favorite': user.favorites.filter(course=course).exists(),
                    'can_download': material.content_type in ['pdf', 'video'] and material_progress > 0,
                    'course_id': course.id,
                    'has_access': has_access,
                    'purchased_separately': purchased_separately,
                })
        
        context['materials'] = materials_data
        context['accessible_courses'] = accessible_courses
        
        # Підготувати дані курсів з прогресом
        courses_data = []
        for course in accessible_courses:
            progress = progress_map.get(course.id)
            progress_percentage = progress.progress_percentage if progress else 0
            
            courses_data.append({
                'id': course.id,
                'title': course.title,
                'progress_percentage': progress_percentage,
                'is_completed': progress.completed if progress else False,
                'total_materials': course.materials.count(),
                'completed_materials': progress.materials_completed.count() if progress else 0
            })
        
        context['user_courses'] = courses_data
        
        # Статистика файлів
        context['files_stats'] = {
            'total_materials': len(materials_data),
            'completed_materials': sum(1 for m in materials_data if m['is_completed']),
            'in_progress_materials': sum(1 for m in materials_data if 0 < m['progress'] < 100),
            'favorite_courses': user.favorites.count(),
        }
        
        return context
    
    def _get_loyalty_context(self, user, loyalty_account):
        """Контекст для вкладки лояльності"""
        context = {}
        
        if not loyalty_account:
            context['loyalty_account'] = None
            context['next_reward'] = None
            context['reward_progress'] = 0
            context['active_subscription'] = None
            context['current_discount'] = 0
            context['potential_discount'] = 0
            context['recent_transactions'] = []
            return context
        
        context['loyalty_account'] = loyalty_account
        
        # Активна підписка (для відображення рівня та множників балів)
        active_subscription = user.subscriptions.filter(
            status='active',
            end_date__gte=timezone.now()
        ).first()
        context['active_subscription'] = active_subscription
        
        # Наступна винагорода (RedemptionOption)
        from apps.loyalty.models import RedemptionOption
        next_reward = RedemptionOption.objects.filter(
            is_active=True,
            points_required__gt=loyalty_account.points
        ).order_by('points_required').first()
        
        context['next_reward'] = next_reward
        
        # Прогрес до наступної винагороди
        if next_reward and next_reward.points_required > 0:
            reward_progress = (loyalty_account.points / next_reward.points_required) * 100
            context['reward_progress'] = min(int(reward_progress), 100)
        else:
            context['reward_progress'] = 0
        
        # Поточні та потенційні знижки
        current_discount = loyalty_account.get_discount_percentage()
        
        # Потенційна знижка - наступна доступна за балами
        potential_discount_option = RedemptionOption.objects.filter(
            is_active=True,
            option_type='discount',
            points_required__gt=loyalty_account.points
        ).order_by('points_required').first()
        
        potential_discount = potential_discount_option.discount_percentage if potential_discount_option else current_discount
        
        context['current_discount'] = current_discount
        context['potential_discount'] = potential_discount
        
        # Останні транзакції балів
        context['recent_transactions'] = loyalty_account.transactions.order_by('-created_at')[:5]
        
        # Legacy tier система (залишаємо для сумісності)
        current_tier = loyalty_account.current_tier
        context['current_tier'] = current_tier
        
        next_tier = loyalty_account.get_next_tier()
        if next_tier:
            context['next_tier'] = next_tier
            context['points_needed'] = loyalty_account.points_to_next_tier()
            context['progress_percentage'] = min(loyalty_account.progress_to_next_tier(), 100)
        
        context['all_tiers'] = LoyaltyTier.objects.filter(is_active=True).order_by('points_required')
        
        return context
    
    def _get_payments_context(self, user):
        """Контекст для вкладки платежів"""
        context = {}
        
        if Payment:
            # ВСІ успішні платежі (підписки, курси, івенти)
            all_payments = user.payments.filter(
                status='succeeded'
            ).select_related(
                'subscription',
                'subscription__plan',
                'course',
                'event_ticket',
                'event_ticket__event'
            ).order_by('-created_at')
            
            context['all_payments'] = all_payments
        else:
            # Fallback якщо модель Payment не існує
            context['all_payments'] = []
        
        return context


class UpdateProfileView(LoginRequiredMixin, View):
    """AJAX оновлення профілю"""
    
    def post(self, request):
        try:
            profile = getattr(request.user, 'profile', None)
            if not profile:
                profile = Profile.objects.create(user=request.user)
            
            # Отримати дані з POST
            data = {
                'first_name': request.POST.get('first_name', '').strip(),
                'last_name': request.POST.get('last_name', '').strip(),
                'birth_date': request.POST.get('birth_date', '').strip(),
                'profession': request.POST.get('profession', '').strip(),
            }
            
            # Видалити пусті значення
            data = {k: v for k, v in data.items() if v}
            
            # Оновити профіль
            for field, value in data.items():
                setattr(profile, field, value)
            
            # Покращена обробка аватара
            if 'avatar' in request.FILES:
                avatar = request.FILES['avatar']
                
                # Валідація розміру (5MB)
                MAX_SIZE = 5 * 1024 * 1024
                if avatar.size > MAX_SIZE:
                    return JsonResponse({
                        'success': False,
                        'message': 'Файл занадто великий. Максимум 5MB'
                    }, status=400)
                
                # Валідація типу
                ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
                content_type = avatar.content_type.lower()
                if content_type not in ALLOWED_TYPES:
                    return JsonResponse({
                        'success': False,
                        'message': 'Дозволені формати: JPEG, PNG, WEBP'
                    }, status=400)
                
                # Видалити старий аватар
                if profile.avatar:
                    try:
                        profile.avatar.delete(save=False)
                    except Exception:
                        pass
                
                profile.avatar = avatar
            
            # Обробити інтереси
            if 'interests' in request.POST:
                interest_ids = request.POST.getlist('interests')
                profile.interests.set(interest_ids)
            
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Профіль успішно оновлено'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Помилка оновлення профілю: {str(e)}'
            })


class ChangePasswordView(LoginRequiredMixin, View):
    """AJAX зміна пароля"""
    
    def post(self, request):
        try:
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Пароль успішно змінено'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Помилки в формі',
                    'errors': form.errors
                })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Помилка зміни пароля: {str(e)}'
            })


class ToggleFavoriteView(LoginRequiredMixin, View):
    """AJAX додавання/видалення з улюблених"""
    
    def post(self, request):
        try:
            course_id = request.POST.get('course_id')
            if not course_id:
                return JsonResponse({'success': False, 'message': 'Не вказано ID курсу'})
            
            course = get_object_or_404(Course, id=course_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                course=course
            )
            
            if not created:
                favorite.delete()
                is_favorite = False
                action = 'removed'
            else:
                is_favorite = True
                action = 'added'
            
            return JsonResponse({
                'success': True,
                'is_favorite': is_favorite,
                'action': action,
                'message': f'Курс {"додано до" if is_favorite else "видалено з"} улюблених'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Помилка: {str(e)}'
            })


class UpdateMaterialProgressView(LoginRequiredMixin, View):
    """AJAX оновлення прогресу матеріалу"""
    
    def post(self, request):
        try:
            material_id = request.POST.get('material_id')
            completed = request.POST.get('completed') == 'true'
            
            if not material_id:
                return JsonResponse({'success': False, 'message': 'Не вказано ID матеріалу'})
            
            material = get_object_or_404(Material, id=material_id)
            course = material.course
            
            # Отримати або створити прогрес курсу
            progress, created = UserCourseProgress.objects.get_or_create(
                user=request.user,
                course=course
            )
            
            # Оновити прогрес матеріалу
            if completed:
                progress.materials_completed.add(material)
            else:
                progress.materials_completed.remove(material)
            
            # Оновити загальний прогрес
            progress.update_progress()
            
            return JsonResponse({
                'success': True,
                'completed': completed,
                'course_progress': float(progress.progress_percentage),
                'message': f'Прогрес {"оновлено" if completed else "скинуто"}'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Помилка: {str(e)}'
            })


class DownloadMaterialView(LoginRequiredMixin, View):
    """Завантаження матеріалу для офлайн перегляду"""
    
    def get(self, request, material_id):
        try:
            material = get_object_or_404(Material, id=material_id)
            
            # Перевірити доступ користувача до матеріалу
            if not self._user_has_access(request.user, material):
                raise Http404("Доступ заборонено")
            
            # Визначити файл для завантаження
            file_field = None
            filename = None
            
            if material.content_type == 'pdf' and material.pdf_file:
                file_field = material.pdf_file
                filename = f"{material.title}.pdf"
            elif material.content_type == 'video' and material.video_file:
                file_field = material.video_file
                filename = f"{material.title}.mp4"
            else:
                raise Http404("Файл недоступний для завантаження")
            
            # Відправити файл
            response = HttpResponse(
                file_field.read(),
                content_type='application/octet-stream'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        
        except Exception as e:
            raise Http404(f"Помилка завантаження: {str(e)}")
    
    def _user_has_access(self, user, material):
        """Перевірити чи має користувач доступ до матеріалу"""
        course = material.course
        
        # Перевірити активну підписку
        active_subscription = user.subscriptions.filter(
            status='active',
            end_date__gte=timezone.now()
        ).exists()
        
        if active_subscription and course.requires_subscription:
            return True
        
        # Перевірити чи це безкоштовний матеріал
        if course.is_free or material.is_preview:
            return True
        
        # TODO: Додати перевірку індивідуальних покупок
        
        return False


class CancelSubscriptionView(LoginRequiredMixin, View):
    """View для скасування підписки"""
    
    def post(self, request):
        try:
            # Знаходимо активну підписку
            active_subscription = request.user.subscriptions.filter(
                status='active',
                end_date__gte=timezone.now()
            ).first()
            
            if not active_subscription:
                return JsonResponse({'error': 'Активна підписка не знайдена'}, status=404)
            
            # Скасовуємо підписку
            active_subscription.status = 'cancelled'
            active_subscription.cancelled_at = timezone.now()
            active_subscription.auto_renew = False
            active_subscription.save()
            
            messages.success(request, 'Підписку успішно скасовано')
            return JsonResponse({
                'success': True,
                'message': 'Підписку скасовано. Доступ залишиться до кінця оплаченого періоду.'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class RenewSubscriptionView(LoginRequiredMixin, View):
    """View для поновлення підписки"""
    
    def post(self, request):
        try:
            # Знаходимо скасовану підписку
            subscription = request.user.subscriptions.filter(
                status='cancelled',
                end_date__gte=timezone.now()
            ).first()
            
            if not subscription:
                return JsonResponse({'error': 'Підписка для поновлення не знайдена'}, status=404)
            
            # Поновлюємо підписку
            subscription.status = 'active'
            subscription.cancelled_at = None
            subscription.auto_renew = True
            subscription.save()
            
            messages.success(request, 'Підписку успішно поновлено')
            return JsonResponse({
                'success': True,
                'message': 'Підписку поновлено. Автоматичне поновлення увімкнено.'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class ChangeSubscriptionView(LoginRequiredMixin, View):
    """View для зміни плану підписки"""
    
    def post(self, request):
        try:
            plan_id = request.POST.get('plan_id')
            if not plan_id:
                return JsonResponse({'error': 'Не вказано план підписки'}, status=400)
            
            new_plan = get_object_or_404(Plan, id=plan_id, is_active=True)
            
            # Знаходимо активну підписку
            active_subscription = request.user.subscriptions.filter(
                status='active',
                end_date__gte=timezone.now()
            ).first()
            
            if active_subscription:
                # Оновлюємо існуючу підписку
                active_subscription.plan = new_plan
                active_subscription.save()
                message = f'План підписки змінено на "{new_plan.name}"'
            else:
                # Створюємо нову підписку
                Subscription.objects.create(
                    user=request.user,
                    plan=new_plan,
                    status='active',
                    start_date=timezone.now(),
                    end_date=timezone.now() + timedelta(days=30),
                    auto_renew=True
                )
                message = f'Оформлено підписку "{new_plan.name}"'
            
            messages.success(request, message)
            return JsonResponse({
                'success': True,
                'message': message,
                'redirect_url': '/account/'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class AddLoyaltyPointsView(LoginRequiredMixin, View):
    """View для додавання балів лояльності (тестовий)"""
    
    def post(self, request):
        try:
            points = int(request.POST.get('points', 50))
            reason = request.POST.get('reason', 'Тестове нарахування балів')
            
            # Отримуємо або створюємо аккаунт лояльності
            loyalty_account, created = LoyaltyAccount.objects.get_or_create(
                user=request.user,
                defaults={
                    'points': 0,
                    'lifetime_points': 0,
                    'current_tier': LoyaltyTier.objects.filter(is_active=True).order_by('points_required').first()
                }
            )
            
            # Додаємо бали
            old_points = loyalty_account.points
            loyalty_account.add_points(points, 'earned', reason)
            
            # Перевіряємо зміну рівня
            tier_changed = loyalty_account.current_tier != loyalty_account.get_tier_for_points(old_points)
            
            message = f'Додано {points} балів!'
            if tier_changed:
                message += f' Вітаємо з досягненням рівня "{loyalty_account.current_tier.name}"!'
            
            messages.success(request, message)
            return JsonResponse({
                'success': True,
                'message': message,
                'new_points': loyalty_account.points,
                'tier_changed': tier_changed
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class MarkCourseCompleteView(LoginRequiredMixin, View):
    """View для позначення курсу як завершеного"""
    
    def post(self, request):
        try:
            course_id = request.POST.get('course_id')
            if not course_id:
                return JsonResponse({'error': 'Не вказано ID курсу'}, status=400)
            
            course = get_object_or_404(Course, id=course_id)
            
            # Оновлюємо прогрес користувача
            progress, created = UserCourseProgress.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={
                    'progress_percentage': 100,
                    'completed': True,
                    'completed_at': timezone.now()
                }
            )
            
            if not progress.completed:
                progress.progress_percentage = 100
                progress.completed = True
                progress.completed_at = timezone.now()
                progress.save()
                
                # Додаємо бали лояльності за завершення курсу
                try:
                    loyalty_account = request.user.loyalty_account
                    loyalty_account.add_points(100, 'course_completion', f'Завершення курсу "{course.title}"')
                except LoyaltyAccount.DoesNotExist:
                    pass
                
                message = f'Курс "{course.title}" позначено як завершений! +100 балів лояльності'
            else:
                message = f'Курс "{course.title}" вже був завершений'
            
            messages.success(request, message)
            return JsonResponse({
                'success': True,
                'message': message,
                'completed': True
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
