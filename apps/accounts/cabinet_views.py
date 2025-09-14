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
        tab = kwargs.get('tab', self.request.GET.get('tab', 'subscription'))
        
        # Загальна інформація користувача
        context['active_tab'] = tab
        context['user_profile'] = getattr(user, 'profile', None)
        
        # Активна підписка
        active_subscription = user.subscriptions.filter(
            status='active',
            end_date__gte=timezone.now()
        ).first()
        context['active_subscription'] = active_subscription
        
        # Аккаунт лояльності
        try:
            loyalty_account = user.loyalty_account
            created = False
        except LoyaltyAccount.DoesNotExist:
            loyalty_account = LoyaltyAccount.objects.create(
                user=user,
                points=0,
                lifetime_points=0,
                lifetime_spent=0
            )
            created = True
            
        if created:
            # Встановити початковий рівень
            bronze_tier = LoyaltyTier.objects.filter(is_active=True).order_by('points_required').first()
            if bronze_tier:
                loyalty_account.current_tier = bronze_tier
                loyalty_account.save()
        
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
                
                materials_data.append({
                    'id': material.id,
                    'title': material.title,
                    'course_title': course.title,
                    'content_type': content_type_display,
                    'progress': material_progress,
                    'is_completed': is_completed,
                    'is_favorite': user.favorites.filter(course=course).exists(),
                    'can_download': material.content_type in ['pdf', 'video'] and material_progress > 0,
                })
        
        context['materials'] = materials_data
        context['accessible_courses'] = accessible_courses
        
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
        
        current_tier = loyalty_account.current_tier
        context['current_tier'] = current_tier
        
        # Прогрес до наступного рівня
        next_tier = loyalty_account.get_next_tier()
        if next_tier:
            points_needed = loyalty_account.points_to_next_tier()
            progress_percentage = loyalty_account.progress_to_next_tier()
            
            context['next_tier'] = next_tier
            context['points_needed'] = points_needed
            context['progress_percentage'] = min(progress_percentage, 100)
        
        # Поточні знижки
        current_discount = loyalty_account.get_discount_percentage()
        potential_discount = next_tier.discount_percentage if next_tier else current_discount
        
        context['discounts'] = {
            'current': current_discount,
            'potential': potential_discount,
        }
        
        # Останні транзакції балів
        context['recent_transactions'] = loyalty_account.point_transactions.order_by('-created_at')[:5]
        
        # Всі рівні для відображення
        context['all_tiers'] = LoyaltyTier.objects.filter(is_active=True).order_by('points_required')
        
        return context
    
    def _get_payments_context(self, user):
        """Контекст для вкладки платежів"""
        context = {}
        
        if Payment:
            # Історія платежів
            payments = user.payments.order_by('-created_at')[:10]
            context['recent_payments'] = payments
            
            # Статистика платежів
            successful_payments = user.payments.filter(status='succeeded')
            context['payment_stats'] = {
                'total_payments': user.payments.count(),
                'successful_payments': successful_payments.count(),
                'total_amount': successful_payments.aggregate(
                    total=models.Sum('amount')
                )['total'] or 0,
                'last_payment': user.payments.filter(status='succeeded').order_by('-created_at').first()
            }
        else:
            # Fallback якщо модель Payment не існує
            context['recent_payments'] = []
            context['payment_stats'] = {
                'total_payments': 0,
                'successful_payments': 0,
                'total_amount': 0,
                'last_payment': None
            }
        
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
            
            # Обробити аватар якщо завантажений
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            
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
