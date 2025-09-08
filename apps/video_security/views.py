from django.http import HttpResponse, Http404, FileResponse, HttpResponseRedirect, JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from apps.content.models import Material
from apps.content.utils import check_user_course_access
from .services import SecureVideoService, VideoUploadService, SecurityLogger, BehaviorAnalyzer


class SecureVideoView(LoginRequiredMixin, View):
    """View для захищеної доставки відео"""
    
    def get(self, request, material_id):
        material = get_object_or_404(Material, id=material_id)
        token = request.GET.get('token')
        
        # Логування спроби доступу
        SecurityLogger.log_access_attempt(material_id, request.user.id)
        
        # Перевірка доступу (існуюча логіка!)
        if not check_user_course_access(request.user, material.course):
            SecurityLogger.log_access_attempt(
                material_id, request.user.id, 
                success=False, reason="no_course_access"
            )
            raise Http404
        
        # Аналіз поведінки користувача
        if not BehaviorAnalyzer.is_legitimate_access(request.user.id, material_id, request):
            SecurityLogger.log_access_attempt(
                material_id, request.user.id,
                success=False, reason="suspicious_behavior"
            )
            raise Http404
        
        # Якщо захист відключений - fallback до звичайного файлу
        if not SecureVideoService.is_enabled():
            if material.video_file and material.video_file.name:
                try:
                    return FileResponse(material.video_file, content_type='video/mp4')
                except (FileNotFoundError, ValueError) as e:
                    SecurityLogger.log_security_incident("file_access_error", {
                        'material_id': material_id,
                        'user_id': request.user.id,
                        'error': str(e)
                    })
                    raise Http404
            raise Http404
        
        # Валідація токену
        if not token or not SecureVideoService.validate_token(token, material_id, request.user.id):
            SecurityLogger.log_access_attempt(
                material_id, request.user.id,
                success=False, reason="invalid_token"
            )
            raise Http404
        
        # Доставка захищеного відео
        return self._serve_secure_video(material)
    
    def _serve_secure_video(self, material):
        """Доставка відео залежно від налаштувань"""
        if material.s3_video_key:
            # Генерація підписаного S3 URL
            return self._serve_s3_video(material)
        elif material.video_file and material.video_file.name:
            # Fallback до локального файлу
            try:
                response = FileResponse(material.video_file, content_type='video/mp4')
                # Додаємо заголовки безпеки
                response['X-Content-Type-Options'] = 'nosniff'
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
                return response
            except (FileNotFoundError, ValueError) as e:
                SecurityLogger.log_security_incident("local_file_error", {
                    'material_id': material.id,
                    'error': str(e)
                })
                raise Http404
        else:
            raise Http404
    
    def _serve_s3_video(self, material):
        """Генерація підписаного S3 URL"""
        try:
            signed_url = VideoUploadService.generate_s3_signed_url(
                material.s3_video_key, 
                expires_in=3600  # 1 година
            )
            
            if signed_url:
                # Redirect на підписаний URL
                return HttpResponseRedirect(signed_url)
            else:
                # Fallback до локального файлу
                if material.video_file and material.video_file.name:
                    try:
                        return FileResponse(material.video_file, content_type='video/mp4')
                    except (FileNotFoundError, ValueError) as e:
                        SecurityLogger.log_security_incident("s3_fallback_error", {
                            'material_id': material.id,
                            'error': str(e)
                        })
                        raise Http404
                raise Http404
                
        except Exception as e:
            # Fallback якщо є проблеми з S3
            SecurityLogger.log_security_incident("s3_exception", {
                'material_id': material.id,
                'error': str(e)
            })
            if material.video_file and material.video_file.name:
                try:
                    return FileResponse(material.video_file, content_type='video/mp4')
                except (FileNotFoundError, ValueError) as fallback_error:
                    SecurityLogger.log_security_incident("final_fallback_error", {
                        'material_id': material.id,
                        'original_error': str(e),
                        'fallback_error': str(fallback_error)
                    })
                    raise Http404
            raise Http404


class SecureVideoURLView(LoginRequiredMixin, View):
    """API endpoint для отримання захищеного URL відео"""
    
    def get(self, request, material_id):
        material = get_object_or_404(Material, id=material_id)
        
        # Перевірка доступу
        if not check_user_course_access(request.user, material.course):
            return JsonResponse({'error': 'No access'}, status=403)
        
        # Аналіз поведінки
        if not BehaviorAnalyzer.is_legitimate_access(request.user.id, material_id, request):
            return JsonResponse({'error': 'Suspicious activity'}, status=429)
        
        # Отримання захищеного URL
        secure_url = material.get_video_url(request.user)
        
        if secure_url:
            return JsonResponse({
                'video_url': secure_url,
                'expires_in': getattr(settings, 'VIDEO_TOKEN_LIFETIME', 3600)
            })
        else:
            return JsonResponse({'error': 'Video not available'}, status=404)


class VideoUploadView(LoginRequiredMixin, View):
    """View для завантаження відео в S3 (тільки для адміністраторів)"""
    
    def post(self, request, material_id):
        # Перевірка прав адміністратора
        if not request.user.is_staff:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        material = get_object_or_404(Material, id=material_id)
        video_file = request.FILES.get('video')
        
        if not video_file:
            return JsonResponse({'error': 'No video file provided'}, status=400)
        
        # Завантаження в S3
        s3_key = VideoUploadService.upload_to_s3(video_file, material_id)
        
        if s3_key:
            # Оновлення материалу
            material.s3_video_key = s3_key
            material.secure_video_enabled = True
            material.save(update_fields=['s3_video_key', 'secure_video_enabled'])
            
            return JsonResponse({
                'success': True,
                's3_key': s3_key,
                'message': 'Video uploaded successfully'
            })
        else:
            return JsonResponse({
                'error': 'Failed to upload video'
            }, status=500)


class SecurityStatsView(LoginRequiredMixin, View):
    """View для перегляду статистики безпеки (тільки для адміністраторів)"""
    
    def get(self, request):
        if not request.user.is_staff:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Тут можна додати статистику по захищеним відео
        # Поки що повертаємо базову інформацію
        
        from django.core.cache import cache
        from apps.content.models import Material
        
        stats = {
            'total_secure_videos': Material.objects.filter(secure_video_enabled=True).count(),
            'total_materials': Material.objects.count(),
            'security_enabled': SecureVideoService.is_enabled(),
            'cache_info': {
                'backend': settings.CACHES['default']['BACKEND'],
                'location': settings.CACHES['default'].get('LOCATION', 'N/A')
            }
        }
        
        return JsonResponse(stats)


class SecureVideoDemoView(View):
    """Демо сторінка для тестування захищеного відео"""
    
    def get(self, request):
        context = {
            'security_enabled': SecureVideoService.is_enabled(),
            'token_lifetime': getattr(settings, 'VIDEO_TOKEN_LIFETIME', 3600),
            'aws_enabled': bool(getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')),
        }
        
        return render(request, 'video_security/demo.html', context)