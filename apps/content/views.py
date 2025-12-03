from typing import Any
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q, Count, QuerySet
from django.utils import timezone
from .models import Course, Material, Favorite, UserCourseProgress
from .utils import check_user_course_access
from apps.loyalty.services import LoyaltyService


class CourseListView(ListView):
    """Course catalog view"""
    model = Course
    template_name = 'hub/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self) -> QuerySet[Course]:
        from django.db.models import Q
        
        queryset = Course.objects.filter(is_published=True)
        
        # Фільтр за target_audience
        audience_filters = self.request.GET.getlist('audience')
        if audience_filters:
            q_objects = Q()
            for aud in audience_filters:
                q_objects |= Q(target_audience__contains=[aud])
            queryset = queryset.filter(q_objects)
        
        # Пошук
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(author__icontains=search_query)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        # Featured courses for hub carousel
        from apps.cms.models import FeaturedCourse
        
        featured_hub = FeaturedCourse.objects.filter(
            is_active=True,
            page='hub'
        ).select_related('course').order_by('order')
        
        context['featured_courses'] = [
            f.course for f in featured_hub 
            if f.course and f.course.is_published
        ]
        
        # Check user favorites
        if self.request.user.is_authenticated:
            favorites = Favorite.objects.filter(
                user=self.request.user,
                course__in=context['courses']
            ).values_list('course_id', flat=True)
            context['user_favorites'] = list(favorites)
        else:
            context['user_favorites'] = []
        
        # Додати бали для кожного курсу
        course_points = {}
        for course in context['courses']:
            points = LoyaltyService.get_points_for_course_display(
                course.price,
                self.request.user if self.request.user.is_authenticated else None
            )
            course_points[course.id] = points
        context['course_points'] = course_points
        
        return context
    
    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        """Return partial template for HTMX requests"""
        if self.request.headers.get('HX-Request'):
            self.template_name = 'hub/partials/catalog_grid.html'
        return super().render_to_response(context, **response_kwargs)


class CourseDetailView(DetailView):
    """Course detail view with access control"""
    model = Course
    template_name = 'hub/course_detail.html'
    context_object_name = 'course'
    
    def get_object(self):
        obj = super().get_object()
        # Increment view count
        obj.view_count += 1
        obj.save(update_fields=['view_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        
        # Promo video embed URL
        promo_url = course.get_promo_embed_url()
        context['promo_embed_url'] = promo_url
        context['has_promo'] = bool(promo_url)
        
        # External join URL (fallback to default)
        if course.external_join_url:
            context['join_url'] = course.external_join_url
        else:
            from apps.cms.models import SiteSettings
            settings = SiteSettings.get_settings()
            context['join_url'] = settings.external_join_url_default or '#'
        
        # Target audience display
        context['target_audience_display'] = course.get_target_audience_display()
        
        # Related courses
        context['related_courses'] = Course.objects.filter(
            is_published=True
        ).exclude(id=course.id)[:4]
        
        # Materials (закомментовано - для майбутнього)
        # context['materials'] = course.materials.all().order_by('order')
        
        # === ЗАКОММЕНТОВАНО ДЛЯ МАЙБУТНЬОГО ===
        # user = self.request.user
        # if user.is_authenticated:
        #     context['has_access'] = check_user_course_access(user, course)
        #     context['is_favorite'] = Favorite.objects.filter(
        #         user=user, course=course
        #     ).exists()
        #     try:
        #         progress = UserCourseProgress.objects.get(user=user, course=course)
        #         context['user_progress'] = progress
        #     except UserCourseProgress.DoesNotExist:
        #         context['user_progress'] = None
        # else:
        #     context['has_access'] = False
        #     context['is_favorite'] = False
        #
        # # Content state for paywall
        # if course.is_free or context['has_access']:
        #     context['content_state'] = 'unlocked'
        # elif course.preview_video:
        #     context['content_state'] = 'preview'
        # else:
        #     context['content_state'] = 'locked'
        
        return context


class MaterialDetailView(LoginRequiredMixin, DetailView):
    """Course material detail view"""
    model = Material
    template_name = 'hub/material_detail.html'
    context_object_name = 'material'
    
    def get_object(self):
        course_slug = self.kwargs['course_slug']
        material_slug = self.kwargs['material_slug']
        
        material = get_object_or_404(
            Material,
            course__slug=course_slug,
            slug=material_slug
        )
        
        return material
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material = self.object
        user = self.request.user
        
        # Check access
        context['has_access'] = check_user_course_access(user, material.course)
        
        # Get progress if user has access and is authenticated
        if user.is_authenticated and context['has_access']:
            progress, created = UserCourseProgress.objects.get_or_create(
                user=user,
                course=material.course
            )
            context['progress'] = progress
        elif user.is_authenticated:
            # User doesn't have access but might have some progress
            try:
                progress = UserCourseProgress.objects.get(
                    user=user,
                    course=material.course
                )
                context['progress'] = progress
            except UserCourseProgress.DoesNotExist:
                context['progress'] = None
        else:
            context['progress'] = None
        
        # Get next/previous materials
        all_materials = list(material.course.materials.all().order_by('order'))
        try:
            current_index = all_materials.index(material)
            
            if current_index > 0:
                context['previous_material'] = all_materials[current_index - 1]
            if current_index < len(all_materials) - 1:
                context['next_material'] = all_materials[current_index + 1]
        except ValueError:
            # Material not found in list
            pass
        
        return context


class ToggleFavoriteView(LoginRequiredMixin, View):
    """Toggle course favorite status"""
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            course=course
        )
        
        if not created:
            favorite.delete()
            is_favorite = False
        else:
            is_favorite = True
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'is_favorite': is_favorite,
                'message': 'Додано в улюблені' if is_favorite else 'Видалено з улюблених'
            })
        
        return redirect('content:course_detail', slug=course.slug)


class UpdateProgressView(LoginRequiredMixin, View):
    """Update course progress (AJAX)"""
    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        
        if not check_user_course_access(request.user, course):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        material_id = request.POST.get('material_id')
        if material_id:
            material = get_object_or_404(Material, id=material_id, course=course)
            
            progress, created = UserCourseProgress.objects.get_or_create(
                user=request.user,
                course=course
            )
            progress.materials_completed.add(material)
            progress.update_progress()
            
            return JsonResponse({
                'progress_percentage': float(progress.progress_percentage),
                'completed_count': progress.materials_completed.count(),
                'total_count': course.materials.count()
            })
        
        return JsonResponse({'error': 'Material ID required'}, status=400)