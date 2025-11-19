from rest_framework import serializers
from django.utils import timezone
from .models import (
    Course, Material, UserCourseProgress, Favorite
)
from .utils import check_user_course_access, calculate_content_preview_limits


class MaterialSerializer(serializers.ModelSerializer):
    """Material/Lesson serializer"""
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    preview_data = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    is_accessible = serializers.SerializerMethodField()
    
    class Meta:
        model = Material
        fields = [
            'id', 'title', 'slug', 'content_type', 'content_type_display',
            'order', 'is_preview', 'preview_seconds', 'preview_percentage',
            'video_duration_seconds', 'preview_data', 'duration_display',
            'is_accessible', 'created_at'
        ]
    
    def get_preview_data(self, obj):
        """Get preview data based on content type"""
        return calculate_content_preview_limits(obj.content_type, obj)
    
    def get_duration_display(self, obj):
        """Get human-readable duration"""
        if obj.content_type == 'video' and obj.video_duration_seconds:
            minutes = obj.video_duration_seconds // 60
            seconds = obj.video_duration_seconds % 60
            return f"{minutes}:{seconds:02d}"
        return None
    
    def get_is_accessible(self, obj):
        """Check if material is accessible to current user"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return obj.is_preview
        
        return check_user_course_access(request.user, obj.course)


class MaterialDetailSerializer(MaterialSerializer):
    """Detailed material serializer with content"""
    content_data = serializers.SerializerMethodField()
    
    class Meta(MaterialSerializer.Meta):
        fields = MaterialSerializer.Meta.fields + ['content_data']
    
    def get_content_data(self, obj):
        """Get content based on user access"""
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        
        has_access = check_user_course_access(user, obj.course) if user else False
        
        if has_access or obj.is_preview:
            # Full access
            if obj.content_type == 'video' and obj.video_file:
                return {
                    'video_url': obj.video_file.url,
                    'duration': obj.video_duration_seconds
                }
            elif obj.content_type == 'pdf' and obj.pdf_file:
                return {
                    'pdf_url': obj.pdf_file.url
                }
            elif obj.content_type == 'article':
                return {
                    'article_content': obj.article_content
                }
        elif obj.is_preview and not has_access:
            # Preview access only
            preview_data = calculate_content_preview_limits(obj.content_type, obj)
            if obj.content_type == 'video' and obj.video_file:
                return {
                    'video_url': obj.video_file.url,
                    'preview_seconds': preview_data.get('preview_seconds', 20),
                    'is_preview': True
                }
            elif obj.content_type == 'article':
                return {
                    'article_content': preview_data.get('preview_text', ''),
                    'is_preview': True
                }
        
        return None


class CourseSerializer(serializers.ModelSerializer):
    """Basic course serializer"""
    absolute_url = serializers.ReadOnlyField(source='get_absolute_url')
    
    # User-specific fields
    is_favorite = serializers.SerializerMethodField()
    has_access = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description',
            'price', 'is_featured', 'is_free', 'requires_subscription',
            'thumbnail', 'rating', 'view_count', 'enrollment_count',
            'absolute_url', 'is_favorite', 'has_access', 'user_progress',
            'created_at', 'published_at'
        ]
    
    def get_is_favorite(self, obj):
        """Check if course is in user's favorites"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        return Favorite.objects.filter(user=request.user, course=obj).exists()
    
    def get_has_access(self, obj):
        """Check if user has access to this course"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return obj.is_free
        
        return check_user_course_access(request.user, obj)
    
    def get_user_progress(self, obj):
        """Get user's progress for this course"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            progress = UserCourseProgress.objects.get(user=request.user, course=obj)
            return {
                'percentage': float(progress.progress_percentage),
                'started_at': progress.started_at,
                'last_accessed': progress.last_accessed,
                'completed_at': progress.completed_at,
                'completed_materials': progress.materials_completed.count(),
                'total_materials': obj.materials.count()
            }
        except UserCourseProgress.DoesNotExist:
            return None


class CourseDetailSerializer(CourseSerializer):
    """Detailed course serializer"""
    materials = MaterialSerializer(many=True, read_only=True)
    content_state = serializers.SerializerMethodField()
    preview_data = serializers.SerializerMethodField()
    related_courses = serializers.SerializerMethodField()
    
    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + [
            'description', 'materials', 'content_state', 'preview_data',
            'related_courses', 'meta_title', 'meta_description'
        ]
    
    def get_content_state(self, obj):
        """Get content state for paywall logic"""
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        
        has_access = self.get_has_access(obj)
        
        if obj.is_free or has_access:
            return 'unlocked'
        elif obj.preview_video:
            return 'preview'
        else:
            return 'locked'
    
    def get_preview_data(self, obj):
        """Get preview data for the course"""
        if obj.preview_video:
            return {
                'preview_video_url': obj.preview_video.url,
                'preview_duration': 20  # 20 seconds
            }
        return None
    
    def get_related_courses(self, obj):
        """Get related courses (simply latest published courses)"""
        related = Course.objects.filter(
            is_published=True
        ).exclude(id=obj.id)[:4]
        
        return CourseSerializer(
            related, 
            many=True, 
            context=self.context
        ).data


class UserCourseProgressSerializer(serializers.ModelSerializer):
    """User course progress serializer"""
    course = CourseSerializer(read_only=True)
    completed_materials_count = serializers.SerializerMethodField()
    total_materials_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserCourseProgress
        fields = [
            'course', 'progress_percentage', 'started_at', 'last_accessed',
            'completed_at', 'completed_materials_count', 'total_materials_count'
        ]
    
    def get_completed_materials_count(self, obj):
        return obj.materials_completed.count()
    
    def get_total_materials_count(self, obj):
        return obj.course.materials.count()


class FavoriteSerializer(serializers.ModelSerializer):
    """Favorite course serializer"""
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'course', 'created_at']


class CourseStatsSerializer(serializers.Serializer):
    """Course statistics serializer"""
    total_courses = serializers.IntegerField()
    free_courses = serializers.IntegerField()
    premium_courses = serializers.IntegerField()
    total_materials = serializers.IntegerField()
    total_duration_hours = serializers.FloatField()
    categories_count = serializers.IntegerField()
    featured_courses = serializers.IntegerField()


class SearchResultSerializer(serializers.Serializer):
    """Search results serializer"""
    query = serializers.CharField()
    total_results = serializers.IntegerField()
    courses = CourseSerializer(many=True)
    suggestions = serializers.ListField(child=serializers.CharField(), required=False)
    filters = serializers.DictField(required=False)


class ContentProgressUpdateSerializer(serializers.Serializer):
    """Progress update serializer"""
    material_id = serializers.IntegerField()
    completed = serializers.BooleanField(default=True)
    
    def validate_material_id(self, value):
        """Validate that material exists and belongs to accessible course"""
        try:
            material = Material.objects.get(id=value)
            request = self.context.get('request')
            
            if request and request.user.is_authenticated:
                if not check_user_course_access(request.user, material.course):
                    raise serializers.ValidationError("Немає доступу до цього матеріалу")
            else:
                raise serializers.ValidationError("Необхідна авторизація")
                
            return value
        except Material.DoesNotExist:
            raise serializers.ValidationError("Матеріал не знайдено")


class FavoriteToggleSerializer(serializers.Serializer):
    """Favorite toggle serializer"""
    course_id = serializers.IntegerField()
    
    def validate_course_id(self, value):
        """Validate that course exists"""
        try:
            Course.objects.get(id=value, is_published=True)
            return value
        except Course.DoesNotExist:
            raise serializers.ValidationError("Курс не знайдено")
