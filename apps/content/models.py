from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings


class Category(models.Model):
    """
    Course categories
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='CSS class or SVG icon')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """
    Content tags
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    """
    Educational courses
    """
    DIFFICULTY_CHOICES = [
        ('beginner', 'Початковий'),
        ('intermediate', 'Середній'),
        ('advanced', 'Експертний'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    tags = models.ManyToManyField(Tag, blank=True, related_name='courses')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    duration_minutes = models.PositiveIntegerField(help_text='Duration in minutes')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Access control
    is_featured = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    requires_subscription = models.BooleanField(default=True)
    subscription_tiers = models.JSONField(default=list, help_text='List of allowed subscription tiers')
    
    # Media
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    preview_video = models.FileField(upload_to='course_previews/', blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    
    # Statistics
    view_count = models.PositiveIntegerField(default=0)
    enrollment_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)
    
    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_published', 'published_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def duration_display(self):
        """Get human-readable duration"""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours:
            return f"{hours}г {minutes}хв"
        return f"{minutes}хв"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('content:course_detail', kwargs={'slug': self.slug})


class Material(models.Model):
    """
    Course materials/lessons
    """
    CONTENT_TYPES = [
        ('video', 'Відео'),
        ('pdf', 'PDF'),
        ('article', 'Стаття'),
        ('quiz', 'Тест'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    order = models.PositiveIntegerField(default=0)
    
    # Content
    video_file = models.FileField(upload_to='materials/videos/', blank=True)
    video_duration_seconds = models.PositiveIntegerField(default=0)
    pdf_file = models.FileField(upload_to='materials/pdfs/', blank=True)
    article_content = models.TextField(blank=True)
    
    # Access
    is_preview = models.BooleanField(default=False, help_text='Available without subscription')
    preview_seconds = models.PositiveIntegerField(default=20, help_text='Preview duration for video')
    preview_percentage = models.PositiveIntegerField(default=10, help_text='Preview percentage for PDF/article')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'materials'
        verbose_name = 'Material'
        verbose_name_plural = 'Materials'
        unique_together = ['course', 'slug']
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class UserCourseProgress(models.Model):
    """
    Track user progress in courses
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_progress')
    materials_completed = models.ManyToManyField(Material, blank=True, related_name='completed_by')
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_course_progress'
        verbose_name = 'User Course Progress'
        verbose_name_plural = 'User Course Progress'
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title} ({self.progress_percentage}%)"
    
    def update_progress(self):
        """Update progress percentage based on completed materials"""
        total_materials = self.course.materials.count()
        if total_materials == 0:
            self.progress_percentage = 0
        else:
            completed_count = self.materials_completed.count()
            self.progress_percentage = (completed_count / total_materials) * 100
        
        if self.progress_percentage >= 100 and not self.completed_at:
            self.completed_at = timezone.now()
        
        self.save()


class Favorite(models.Model):
    """
    User favorite courses
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'favorites'
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title}"