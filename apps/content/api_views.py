from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Course, Material, UserCourseProgress
from .utils import check_user_course_access
import json


class MaterialProgressAPIView(APIView):
    """
    API view to track material progress
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        material_id = request.data.get('material_id')
        time_spent = request.data.get('time_spent', 0)
        is_final = request.data.get('is_final', False)
        
        if not material_id:
            return Response(
                {'error': 'material_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            material = Material.objects.get(id=material_id)
            
            # Check if user has access to this material
            if not check_user_course_access(request.user, material.course):
                return Response(
                    {'error': 'Access denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get or create progress
            progress, created = UserCourseProgress.objects.get_or_create(
                user=request.user,
                course=material.course
            )
            
            # Update last accessed time
            progress.last_accessed = timezone.now()
            
            # Track time spent if significant
            if time_spent >= 30:  # At least 30 seconds
                progress.save()
            
            return Response({
                'success': True,
                'progress_percentage': float(progress.progress_percentage),
                'materials_completed': progress.materials_completed.count(),
                'total_materials': material.course.materials.count()
            })
            
        except Material.DoesNotExist:
            return Response(
                {'error': 'Material not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseProgressAPIView(APIView):
    """
    API view to update course progress
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, course_id):
        material_id = request.data.get('material_id')
        
        if not material_id:
            return Response(
                {'error': 'material_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            course = Course.objects.get(id=course_id)
            material = Material.objects.get(id=material_id, course=course)
        
            # Check access
            if not check_user_course_access(request.user, course):
                return Response(
                    {'error': 'Access denied'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
            # Get or create progress
            progress, created = UserCourseProgress.objects.get_or_create(
                user=request.user,
                course=course
            )
            
            # Mark material as completed
            progress.materials_completed.add(material)
            progress.last_accessed = timezone.now()
            progress.update_progress()
        
            return Response({
                'success': True,
                'progress_percentage': float(progress.progress_percentage),
                'completed_count': progress.materials_completed.count(),
                'total_count': course.materials.count(),
                'is_completed': progress.progress_percentage >= 100
            })
            
        except (Course.DoesNotExist, Material.DoesNotExist):
            return Response(
                {'error': 'Course or material not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchSuggestionsAPIView(APIView):
    """
    API view for search suggestions/autocomplete
    """
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return Response({'suggestions': []})
        
        # Search in course titles and tags
        courses = Course.objects.filter(
            title__icontains=query,
            is_published=True
        ).values_list('title', flat=True)[:5]
        
        # Search in tags
        from .models import Tag
        tags = Tag.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:3]
        
        # Combine suggestions
        suggestions = list(courses) + list(tags)
        
        return Response({
            'suggestions': suggestions[:8],  # Limit to 8 suggestions
            'query': query
        })


class UserFavoritesAPIView(APIView):
    """
    API view to manage user favorites
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's favorite courses"""
        from .models import Favorite
        
        favorites = Favorite.objects.filter(
            user=request.user
        ).select_related('course').order_by('-created_at')
        
        course_data = []
        for favorite in favorites:
            course = favorite.course
            course_data.append({
                'id': course.id,
                'title': course.title,
                'slug': course.slug,
                'thumbnail': course.thumbnail.url if course.thumbnail else None,
                'price': float(course.price),
                'is_free': course.is_free,
                'category': course.category.name,
                'difficulty': course.get_difficulty_display(),
                'duration_display': course.duration_display,
                'url': course.get_absolute_url()
            })
        
        return Response({
            'favorites': course_data,
            'count': len(course_data)
        })
    
    def post(self, request):
        """Add course to favorites"""
        course_id = request.data.get('course_id')
        
        if not course_id:
            return Response(
                {'error': 'course_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            course = Course.objects.get(id=course_id, is_published=True)
            
            from .models import Favorite
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                course=course
            )
            
            return Response({
                'success': True,
                'is_favorite': True,
                'message': 'Додано в улюблені'
            })
        
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request):
        """Remove course from favorites"""
        course_id = request.data.get('course_id')
        
        if not course_id:
            return Response(
                {'error': 'course_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from .models import Favorite
            favorite = Favorite.objects.get(
                user=request.user,
                course_id=course_id
            )
            favorite.delete()
            
            return Response({
                'success': True,
                'is_favorite': False,
                'message': 'Видалено з улюблених'
            })
            
        except Favorite.DoesNotExist:
            return Response(
                {'error': 'Favorite not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class CourseAnalyticsAPIView(APIView):
    """
    API view for course analytics (admin only)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id):
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            course = Course.objects.get(id=course_id)
            
            # Get progress statistics
            progress_records = UserCourseProgress.objects.filter(course=course)
            
            total_enrolled = progress_records.count()
            completed = progress_records.filter(progress_percentage__gte=100).count()
            in_progress = progress_records.filter(
                progress_percentage__gt=0,
                progress_percentage__lt=100
            ).count()
            
            # Average progress
            avg_progress = 0
            if total_enrolled > 0:
                total_progress = sum(p.progress_percentage for p in progress_records)
                avg_progress = total_progress / total_enrolled
            
            # Material completion rates
            materials = course.materials.all()
            material_stats = []
            
            for material in materials:
                completed_count = sum(
                    1 for p in progress_records 
                    if material in p.materials_completed.all()
                )
                completion_rate = (completed_count / total_enrolled * 100) if total_enrolled > 0 else 0
                
                material_stats.append({
                    'material_id': material.id,
                    'title': material.title,
                    'content_type': material.content_type,
                    'completion_rate': round(completion_rate, 2),
                    'completed_count': completed_count
                })
            
            return Response({
                'course': {
                    'id': course.id,
                    'title': course.title,
                    'total_materials': materials.count()
                },
                'enrollment': {
                    'total': total_enrolled,
                    'completed': completed,
                    'in_progress': in_progress,
                    'not_started': max(0, total_enrolled - completed - in_progress)
                },
                'progress': {
                    'average': round(avg_progress, 2),
                    'completion_rate': round((completed / total_enrolled * 100), 2) if total_enrolled > 0 else 0
                },
                'materials': material_stats
            })
            
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )