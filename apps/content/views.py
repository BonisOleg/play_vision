from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q, Count
from django.utils import timezone
from .models import Course, Material, Favorite, UserCourseProgress
from .utils import check_user_course_access


class CourseListView(ListView):
    """Course catalog view"""
    model = Course
    template_name = 'hub/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Course.objects.filter(
            is_published=True
        ).select_related('category').prefetch_related('tags')
        
        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Difficulty filter
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Tag filter
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        
        # Price filter
        price_filter = self.request.GET.get('price')
        if price_filter == 'free':
            queryset = queryset.filter(is_free=True)
        elif price_filter == 'paid':
            queryset = queryset.filter(is_free=False)
        
        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        if sort in ['price', '-price', 'title', '-title', '-created_at', 'view_count']:
            queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add categories for filter
        from .models import Category
        context['categories'] = Category.objects.filter(is_active=True)
        
        # Add featured courses for main materials section
        context['featured_courses'] = Course.objects.filter(
            is_published=True,
            is_featured=True
        ).select_related('category').prefetch_related('tags')[:6]
        
        # Add current filters
        context['current_category'] = self.request.GET.get('category')
        context['current_difficulty'] = self.request.GET.get('difficulty')
        context['current_price'] = self.request.GET.get('price')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        
        # Check user favorites
        if self.request.user.is_authenticated:
            favorites = Favorite.objects.filter(
                user=self.request.user,
                course__in=context['courses']
            ).values_list('course_id', flat=True)
            context['user_favorites'] = list(favorites)
        else:
            context['user_favorites'] = []
        
        return context


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
        user = self.request.user
        
        # Check access
        if user.is_authenticated:
            context['has_access'] = check_user_course_access(user, course)
            context['is_favorite'] = Favorite.objects.filter(
                user=user, course=course
            ).exists()
            
            # Get user progress
            try:
                progress = UserCourseProgress.objects.get(user=user, course=course)
                context['user_progress'] = progress
            except UserCourseProgress.DoesNotExist:
                context['user_progress'] = None
        else:
            context['has_access'] = False
            context['is_favorite'] = False
        
        # Content state for paywall
        if course.is_free or context['has_access']:
            context['content_state'] = 'unlocked'
        elif course.preview_video:
            context['content_state'] = 'preview'
        else:
            context['content_state'] = 'locked'
        
        # Get course materials
        context['materials'] = course.materials.all().order_by('order')
        
        # Get related courses
        context['related_courses'] = Course.objects.filter(
            category=course.category,
            is_published=True
        ).exclude(id=course.id)[:4]
        
        return context


class CourseSearchView(ListView):
    """Course search view"""
    model = Course
    template_name = 'hub/search_results.html'
    context_object_name = 'courses'
    paginate_by = 20
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if not query:
            return Course.objects.none()
        
        return Course.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query),
            is_published=True
        ).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
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