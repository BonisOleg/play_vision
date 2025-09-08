import time
import hmac
import hashlib
import secrets
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from apps.content.utils import check_user_course_access


class SecureVideoService:
    """Сервіс для захищеної доставки відео"""
    
    @staticmethod
    def is_enabled():
        """Перевірка чи увімкнена система захисту"""
        return getattr(settings, 'VIDEO_SECURITY_ENABLED', False)
    
    @staticmethod
    def get_secure_url(material, user):
        """Отримати захищений URL для відео"""
        if not SecureVideoService.is_enabled():
            # Fallback до звичайного файлу
            return material.video_file.url if material.video_file else None
        
        # Перевірка доступу (використовуємо ІСНУЮЧУ функцію!)
        if not check_user_course_access(user, material.course):
            return None
        
        # Генерація токену
        token_data = SecureVideoService._generate_token(material.id, user.id)
        
        # Зберігаємо токен в материалі
        material.video_access_token = token_data['token']
        material.token_expires_at = timezone.now() + timezone.timedelta(
            seconds=getattr(settings, 'VIDEO_TOKEN_LIFETIME', 3600)
        )
        material.save(update_fields=['video_access_token', 'token_expires_at'])
        
        return f"/video-security/secure-video/{material.id}/?token={token_data['token']}"
    
    @staticmethod
    def _generate_token(material_id, user_id):
        """Генерація захищеного токену"""
        timestamp = int(time.time())
        nonce = secrets.token_hex(8)
        
        # Використовуємо існуючий SECRET_KEY
        data = f"{material_id}:{user_id}:{timestamp}:{nonce}"
        signature = hmac.new(
            settings.SECRET_KEY.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        
        token = f"{timestamp}.{nonce}.{signature}"
        
        return {
            'token': token,
            'expires': timestamp + getattr(settings, 'VIDEO_TOKEN_LIFETIME', 3600)
        }
    
    @staticmethod
    def validate_token(token, material_id, user_id):
        """Валідація токену"""
        try:
            timestamp_str, nonce, signature = token.split('.')
            timestamp = int(timestamp_str)
            
            # Перевірка терміну дії
            lifetime = getattr(settings, 'VIDEO_TOKEN_LIFETIME', 3600)
            if time.time() > timestamp + lifetime:
                return False
            
            # Перевірка підпису
            data = f"{material_id}:{user_id}:{timestamp}:{nonce}"
            expected_signature = hmac.new(
                settings.SECRET_KEY.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()[:16]
            
            return hmac.compare_digest(signature, expected_signature)
        except (ValueError, AttributeError) as e:
            # Логуємо спроби з неправильними токенами
            SecurityLogger.log_security_incident("invalid_token_format", {
                'error': str(e),
                'material_id': material_id,
                'user_id': user_id,
                'token_preview': token[:10] if token and len(token) > 10 else token
            })
            return False
        except Exception as e:
            # Інші непередбачені помилки валідації
            SecurityLogger.log_security_incident("token_validation_error", {
                'error': str(e),
                'material_id': material_id,
                'user_id': user_id,
                'error_type': type(e).__name__
            })
            return False


class VideoUploadService:
    """Сервіс для завантаження відео в S3"""
    
    @staticmethod
    def upload_to_s3(video_file, material_id):
        """Завантаження відео в S3 bucket"""
        if not SecureVideoService.is_enabled():
            return None
        
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', ''),
                aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', ''),
                region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'eu-central-1')
            )
            
            # Унікальний ключ файлу
            file_key = f"protected/videos/material_{material_id}/{video_file.name}"
            
            # Завантаження з приватними правами
            s3_client.upload_fileobj(
                video_file,
                getattr(settings, 'AWS_STORAGE_BUCKET_NAME', ''),
                file_key,
                ExtraArgs={
                    'ContentType': 'video/mp4',
                    'ServerSideEncryption': 'AES256',
                    'ACL': 'private'  # Приватний доступ!
                }
            )
            
            return file_key
            
        except ImportError as e:
            # boto3 не встановлений
            SecurityLogger.log_security_incident("boto3_missing", {
                'error': str(e),
                'material_id': material_id
            })
            return None
        except ClientError as e:
            # Помилка S3 (права доступу, bucket не існує, тощо)
            SecurityLogger.log_security_incident("s3_upload_error", {
                'error': str(e),
                'material_id': material_id,
                'error_code': e.response.get('Error', {}).get('Code', 'Unknown')
            })
            return None
        except Exception as e:
            # Інші непередбачені помилки
            SecurityLogger.log_security_incident("upload_unexpected_error", {
                'error': str(e),
                'material_id': material_id,
                'error_type': type(e).__name__
            })
            return None
    
    @staticmethod
    def generate_s3_signed_url(s3_key, expires_in=3600):
        """Генерація підписаного S3 URL"""
        try:
            import boto3
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', ''),
                aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', ''),
                region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'eu-central-1')
            )
            
            # Підписаний URL з обмеженим часом життя
            signed_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', ''),
                    'Key': s3_key
                },
                ExpiresIn=expires_in,
                HttpMethod='GET'
            )
            
            return signed_url
            
        except ImportError as e:
            # boto3 не встановлений
            SecurityLogger.log_security_incident("boto3_missing_signed_url", {
                'error': str(e),
                's3_key': s3_key
            })
            return None
        except ClientError as e:
            # Помилка S3
            SecurityLogger.log_security_incident("s3_signed_url_error", {
                'error': str(e),
                's3_key': s3_key,
                'error_code': e.response.get('Error', {}).get('Code', 'Unknown')
            })
            return None
        except Exception as e:
            # Інші помилки
            SecurityLogger.log_security_incident("signed_url_unexpected_error", {
                'error': str(e),
                's3_key': s3_key,
                'error_type': type(e).__name__
            })
            return None


class SecurityLogger:
    """Логування безпекових подій"""
    
    @staticmethod
    def log_access_attempt(material_id, user_id, success=True, reason=""):
        """Логування спроб доступу до відео"""
        log_key = f"video_access_log_{material_id}_{user_id}"
        current_time = time.time()
        
        # Отримуємо історію доступу
        access_history = cache.get(log_key, [])
        access_history.append({
            'timestamp': current_time,
            'success': success,
            'reason': reason
        })
        
        # Зберігаємо тільки останні 10 записів
        access_history = access_history[-10:]
        cache.set(log_key, access_history, 86400)  # 24 години
        
        return access_history
    
    @staticmethod
    def log_security_incident(incident_type, details):
        """Логування інцидентів безпеки"""
        incident_key = f"security_incident_{int(time.time())}"
        cache.set(incident_key, {
            'type': incident_type,
            'details': details,
            'timestamp': time.time()
        }, 86400 * 7)  # Тиждень


class BehaviorAnalyzer:
    """Аналіз поведінки користувачів"""
    
    @staticmethod
    def is_legitimate_access(user_id, material_id, request):
        """Перевірка чи є доступ легітимним"""
        current_time = time.time()
        
        # Перевірка частоти запитів
        access_key = f"video_access_{user_id}_{material_id}"
        recent_accesses = cache.get(access_key, [])
        recent_accesses = [t for t in recent_accesses if current_time - t < 300]  # 5 хвилин
        
        if len(recent_accesses) > 5:  # Більше 5 запитів за 5 хвилин = підозріло
            SecurityLogger.log_security_incident("too_many_requests", {
                'user_id': user_id,
                'material_id': material_id,
                'requests_count': len(recent_accesses)
            })
            return False
        
        # Перевірка IP адреси
        current_ip = BehaviorAnalyzer._get_client_ip(request)
        user_ips = cache.get(f"user_ips_{user_id}", [])
        
        # Backward compatibility: конвертуємо set в list якщо потрібно
        if isinstance(user_ips, set):
            user_ips = list(user_ips)
        
        if current_ip not in user_ips and len(user_ips) > 3:  # Більше 3 IP = підозріло
            SecurityLogger.log_security_incident("multiple_ips", {
                'user_id': user_id,
                'current_ip': current_ip,
                'known_ips': user_ips
            })
            return False
        
        # Оновлення статистики
        recent_accesses.append(current_time)
        cache.set(access_key, recent_accesses, 300)
        
        # Безпечно додаємо IP та видаляємо дублікати
        if current_ip not in user_ips:
            user_ips.append(current_ip)
        
        # Зберігаємо тільки останні 5 IP для економії пам'яті
        user_ips = user_ips[-5:]
        cache.set(f"user_ips_{user_id}", user_ips, 86400)
        
        return True
    
    @staticmethod
    def _get_client_ip(request):
        """Отримання IP адреси клієнта"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
