from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count, Sum, Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import (
    Category, Tag, Course, Material, UserCourseProgress, Favorite
)
from .serializers import (
    CategorySerializer, TagSerializer, CourseSerializer, CourseDetailSerializer,
    MaterialSerializer, MaterialDetailSerializer, UserCourseProgressSerializer,
    FavoriteSerializer, SearchResultSerializer, ContentProgressUpdateSerializer,
    FavoriteToggleSerializer, CourseStatsSerializer
)
from .utils import check_user_course_access, get_user_accessible_courses


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Categories API viewset"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def courses(self, request, slug=None):
        """Get courses for specific category"""
        category = self.get_object()
        courses = Course.objects.filter(
            category=category,
            is_published=True
        ).order_by('-created_at')
        
        # Apply filters
        difficulty = request.query_params.get('difficulty')
        if difficulty:
            courses = courses.filter(difficulty=difficulty)
        
        price_filter = request.query_params.get('price')
        if price_filter == 'free':
            courses = courses.filter(is_free=True)
        elif price_filter == 'paid':
            courses = courses.filter(is_free=False)
        
        # Pagination
        page = self.paginate_queryset(courses)
        if page is not None:
            serializer = CourseSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = CourseSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Tags API viewset"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Courses API viewset"""
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_published=True).select_related(
            'category'
        ).prefetch_related('tags', 'materials')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        # Filter by tags
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = tags.split(',')
            queryset = queryset.filter(tags__slug__in=tag_list).distinct()
        
        # Filter by price
        price_filter = self.request.query_params.get('price')
        if price_filter == 'free':
            queryset = queryset.filter(is_free=True)
        elif price_filter == 'paid':
            queryset = queryset.filter(is_free=False)
        
        # Filter by access (for authenticated users)
        access_filter = self.request.query_params.get('access')
        if access_filter and self.request.user.is_authenticated:
            if access_filter == 'accessible':
                # Only courses user has access to
                accessible_courses = get_user_accessible_courses(self.request.user)
                queryset = queryset.filter(id__in=accessible_courses.values_list('id', flat=True))
            elif access_filter == 'subscribed':
                # Only subscription courses user has access to
                active_subscriptions = self.request.user.subscriptions.filter(
                    status='active',
                    start_date__lte=timezone.now(),
                    end_date__gte=timezone.now()
                )
                if active_subscriptions.exists():
                    subscription_tiers = list(active_subscriptions.values_list('plan__slug', flat=True))
                    queryset = queryset.filter(
                        requires_subscription=True,
                        subscription_tiers__overlap=subscription_tiers
                    )
                else:
                    queryset = queryset.none()
        
        # Featured only
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Sorting
        sort = self.request.query_params.get('sort', '-created_at')
        if sort in ['price', '-price', 'title', '-title', '-created_at', '-view_count', '-rating']:
            queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Get course details and increment view count"""
        instance = self.get_object()
        
        # Increment view count
        Course.objects.filter(id=instance.id).update(view_count=instance.view_count + 1)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def materials(self, request, slug=None):
        """Get course materials"""
        course = self.get_object()
        materials = course.materials.all().order_by('order')
        
        serializer = MaterialSerializer(
            materials, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, slug=None):
        """Get user's progress for this course"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        course = self.get_object()
        
        try:
            progress = UserCourseProgress.objects.get(user=request.user, course=course)
            serializer = UserCourseProgressSerializer(progress)
            return Response(serializer.data)
        except UserCourseProgress.DoesNotExist:
            return Response({
                'course': CourseSerializer(course, context={'request': request}).data,
                'progress_percentage': 0,
                'started_at': None,
                'last_accessed': None,
                'completed_at': None,
                'completed_materials_count': 0,
                'total_materials_count': course.materials.count()
            })


class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    """Materials API viewset"""
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        if course_slug:
            return Material.objects.filter(
                course__slug=course_slug,
                course__is_published=True
            ).select_related('course').order_by('order')
        return Material.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MaterialDetailSerializer
        return MaterialSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Get material details with access control"""
        instance = self.get_object()
        
        # Check access
        if not check_user_course_access(request.user, instance.course):
            return Response(
                {'error': 'Access denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update progress
        progress, created = UserCourseProgress.objects.get_or_create(
            user=request.user,
            course=instance.course
        )
        progress.materials_completed.add(instance)
        progress.last_accessed = timezone.now()
        progress.update_progress()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class SearchAPIView(APIView):
    """Search courses API"""
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response({
                'query': '',
                'total_results': 0,
                'courses': [],
                'suggestions': []
            })
        
        # Search courses
        courses = Course.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(category__name__icontains=query),
            is_published=True
        ).distinct()
        
        # Apply additional filters
        category = request.query_params.get('category')
        if category:
            courses = courses.filter(category__slug=category)
        
        difficulty = request.query_params.get('difficulty')
        if difficulty:
            courses = courses.filter(difficulty=difficulty)
        
        # Sort by relevance (title match first, then description, then tags)
        courses = courses.extra(
            select={
                'title_match': f"CASE WHEN LOWER(title) LIKE LOWER('%%{query}%%') THEN 1 ELSE 0 END",
                'desc_match': f"CASE WHEN LOWER(description) LIKE LOWER('%%{query}%%') THEN 1 ELSE 0 END"
            },
            order_by=['-title_match', '-desc_match', '-view_count']
        )
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_results = courses.count()
        courses_page = courses[start:end]
        
        # Generate suggestions based on similar titles
        suggestions = []
        if total_results == 0:
            similar_courses = Course.objects.filter(
                title__icontains=query[:3],  # First 3 characters
                is_published=True
            ).values_list('title', flat=True)[:5]
            suggestions = list(similar_courses)
        
        serializer = CourseSerializer(
            courses_page, 
            many=True, 
            context={'request': request}
        )
        
        return Response({
            'query': query,
            'total_results': total_results,
            'courses': serializer.data,
            'suggestions': suggestions,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_results + page_size - 1) // page_size
        })


class FavoritesAPIView(APIView):
    """User favorites API"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's favorite courses"""
        favorites = Favorite.objects.filter(
            user=request.user
        ).select_related('course').order_by('-created_at')
        
        serializer = FavoriteSerializer(favorites, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        """Toggle course favorite status"""
        serializer = FavoriteToggleSerializer(data=request.data)
        
        if serializer.is_valid():
            course_id = serializer.validated_data['course_id']
            course = get_object_or_404(Course, id=course_id, is_published=True)
            
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                course=course
            )
            
            if not created:
                favorite.delete()
                return Response({
                    'is_favorite': False,
                    'message': 'Видалено з улюблених'
                })
            else:
                return Response({
                    'is_favorite': True,
                    'message': 'Додано в улюблені'
                })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProgressAPIView(APIView):
    """Course progress API"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's course progress"""
        progress = UserCourseProgress.objects.filter(
            user=request.user
        ).select_related('course').order_by('-last_accessed')
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter == 'completed':
            progress = progress.filter(completed_at__isnull=False)
        elif status_filter == 'in_progress':
            progress = progress.filter(
                completed_at__isnull=True,
                progress_percentage__gt=0
            )
        elif status_filter == 'not_started':
            progress = progress.filter(progress_percentage=0)
        
        serializer = UserCourseProgressSerializer(
            progress, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    def post(self, request):
        """Update course progress"""
        serializer = ContentProgressUpdateSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            material_id = serializer.validated_data['material_id']
            completed = serializer.validated_data['completed']
            
            material = get_object_or_404(Material, id=material_id)
            
            progress, created = UserCourseProgress.objects.get_or_create(
                user=request.user,
                course=material.course
            )
            
            if completed:
                progress.materials_completed.add(material)
            else:
                progress.materials_completed.remove(material)
            
            progress.last_accessed = timezone.now()
            progress.update_progress()
            
            return Response({
                'progress_percentage': float(progress.progress_percentage),
                'completed_materials': progress.materials_completed.count(),
                'total_materials': material.course.materials.count(),
                'is_completed': bool(progress.completed_at)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StatsAPIView(APIView):
    """Content statistics API"""
    
    def get(self, request):
        """Get content statistics"""
        stats = {
            'total_courses': Course.objects.filter(is_published=True).count(),
            'free_courses': Course.objects.filter(is_published=True, is_free=True).count(),
            'premium_courses': Course.objects.filter(is_published=True, is_free=False).count(),
            'total_materials': Material.objects.filter(course__is_published=True).count(),
            'categories_count': Category.objects.filter(is_active=True).count(),
            'featured_courses': Course.objects.filter(is_published=True, is_featured=True).count(),
        }
        
        # Calculate total duration
        total_duration = Course.objects.filter(
            is_published=True
        ).aggregate(
            total=Sum('duration_minutes')
        )['total'] or 0
        
        stats['total_duration_hours'] = round(total_duration / 60, 1)
        
        serializer = CourseStatsSerializer(stats)
        return Response(serializer.data)


class RecommendationsAPIView(APIView):
    """Course recommendations API"""
    
    def get(self, request):
        """Get course recommendations for user"""
        user = request.user
        
        if not user.is_authenticated:
            # For anonymous users, show featured courses
            recommendations = Course.objects.filter(
                is_published=True,
                is_featured=True
            ).order_by('-view_count')[:6]
        else:
            # For authenticated users, personalized recommendations
            recommendations = self.get_personalized_recommendations(user)
        
        serializer = CourseSerializer(
            recommendations, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    def get_personalized_recommendations(self, user):
        """Get personalized recommendations for user"""
        recommendations = []
        
        # Get user's interests from profile
        user_interests = []
        if hasattr(user, 'profile') and user.profile.interests.exists():
            user_interests = list(user.profile.interests.all())
        
        # Get user's progress
        user_progress = UserCourseProgress.objects.filter(user=user)
        completed_courses = user_progress.filter(completed_at__isnull=False)
        in_progress_courses = user_progress.filter(
            completed_at__isnull=True,
            progress_percentage__gt=0
        )
        
        # Categories from completed courses
        completed_categories = []
        if completed_courses.exists():
            completed_categories = list(
                completed_courses.values_list('course__category', flat=True).distinct()
            )
        
        # Get courses user already has access to (to exclude them)
        accessible_courses = get_user_accessible_courses(user)
        accessible_ids = list(accessible_courses.values_list('id', flat=True))
        
        # Build recommendations
        base_queryset = Course.objects.filter(
            is_published=True
        ).exclude(id__in=accessible_ids)
        
        # 1. Courses from same categories as completed
        if completed_categories:
            category_recommendations = base_queryset.filter(
                category__in=completed_categories
            ).order_by('-rating', '-view_count')[:3]
            recommendations.extend(category_recommendations)
        
        # 2. Courses with user's interests tags
        if user_interests:
            interest_recommendations = base_queryset.filter(
                tags__in=user_interests
            ).exclude(
                id__in=[c.id for c in recommendations]
            ).order_by('-rating', '-view_count')[:2]
            recommendations.extend(interest_recommendations)
        
        # 3. Fill with featured courses if needed
        if len(recommendations) < 6:
            featured = base_queryset.filter(
                is_featured=True
            ).exclude(
                id__in=[c.id for c in recommendations]
            ).order_by('-view_count')[:6-len(recommendations)]
            recommendations.extend(featured)
        
        return recommendations[:6]