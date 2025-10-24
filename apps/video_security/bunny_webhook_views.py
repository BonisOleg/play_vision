"""
Bunny.net Webhook Views
Обробка webhook повідомлень від Bunny.net про статус відео
"""
import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.content.models import Material

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class BunnyWebhookView(View):
    """
    Webhook endpoint для отримання повідомлень від Bunny.net
    
    Bunny.net відправляє POST запити коли:
    - Відео завантажено
    - Відео оброблено (encoding завершено)
    - Відео готове до перегляду
    - Помилка обробки
    """
    
    def post(self, request):
        """Обробка webhook від Bunny.net"""
        try:
            # Отримати дані з запиту
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
            
            logger.info(f"Bunny webhook received: {data}")
            
            # Отримати дані про відео
            video_id = data.get('VideoGuid') or data.get('videoGuid')
            status = data.get('Status') or data.get('status')
            
            if not video_id:
                logger.warning("No video ID in webhook data")
                return JsonResponse({'status': 'error', 'message': 'No video ID'}, status=400)
            
            # Знайти матеріал з цим video_id
            try:
                material = Material.objects.get(bunny_video_id=video_id)
            except Material.DoesNotExist:
                logger.warning(f"Material not found for video_id: {video_id}")
                return JsonResponse({'status': 'ok', 'message': 'Material not found'}, status=200)
            
            # Оновити статус відео
            if status is not None:
                material.bunny_video_status = str(status)
                
                # Оновити thumbnail якщо доступний
                thumbnail_url = data.get('ThumbnailUrl') or data.get('thumbnailUrl')
                if thumbnail_url:
                    material.bunny_thumbnail_url = thumbnail_url
                
                # Оновити тривалість якщо доступна
                duration = data.get('Length') or data.get('length')
                if duration:
                    material.video_duration_seconds = int(duration)
                
                material.save()
                
                logger.info(f"Material {material.id} updated: status={status}")
            
            return JsonResponse({'status': 'ok', 'message': 'Webhook processed'})
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in webhook: {e}")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    def get(self, request):
        """GET запит для перевірки доступності endpoint"""
        return HttpResponse("Bunny.net Webhook Endpoint is active", content_type="text/plain")

