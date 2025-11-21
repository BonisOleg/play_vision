"""
Bunny.net CDN Video Streaming Service
Сервіс для інтеграції з Bunny.net Stream API
"""
import requests
import json
from django.conf import settings
from django.core.cache import cache
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BunnyService:
    """Сервіс для роботи з Bunny.net Stream API"""
    
    @staticmethod
    def is_enabled() -> bool:
        """Перевірка чи увімкнена Bunny.net інтеграція"""
        return getattr(settings, 'BUNNY_ENABLED', False)
    
    @staticmethod
    def _get_headers() -> Dict[str, str]:
        """Отримати заголовки для API запитів"""
        return {
            'AccessKey': settings.BUNNY_API_KEY,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
    
    @staticmethod
    def _get_library_url() -> str:
        """Отримати base URL для library API"""
        library_id = settings.BUNNY_LIBRARY_ID
        return f"{settings.BUNNY_STREAM_API_URL}/{library_id}"
    
    @staticmethod
    def upload_video(title: str, collection_id: Optional[str] = None, 
                     file_path: Optional[str] = None, 
                     file_content: Optional[bytes] = None) -> Optional[Dict[str, Any]]:
        """
        Завантажити відео на Bunny.net
        
        Args:
            title: Назва відео
            collection_id: ID колекції (опціонально)
            file_path: Шлях до відео файлу (для локальних файлів)
            file_content: Вміст файлу в bytes (для Cloudinary/S3)
            
        Returns:
            Dict з інформацією про відео або None якщо помилка
        """
        if not BunnyService.is_enabled():
            logger.warning("Bunny.net disabled, cannot upload video")
            return None
        
        if not file_path and not file_content:
            logger.error("Either file_path or file_content must be provided")
            return None
        
        try:
            # Крок 1: Створити відео запис
            create_url = f"{BunnyService._get_library_url()}/videos"
            data = {
                'title': title,
            }
            if collection_id:
                data['collectionId'] = collection_id
            
            response = requests.post(
                create_url,
                headers=BunnyService._get_headers(),
                json=data,
                timeout=30
            )
            response.raise_for_status()
            video_data = response.json()
            video_id = video_data.get('guid')
            
            if not video_id:
                logger.error("No video ID returned from Bunny.net")
                return None
            
            # Крок 2: Завантажити відео файл
            upload_url = f"{BunnyService._get_library_url()}/videos/{video_id}"
            
            if file_content:
                # Upload з bytes (Cloudinary/S3)
                upload_response = requests.put(
                    upload_url,
                    headers={
                        'AccessKey': settings.BUNNY_API_KEY,
                        'Content-Type': 'application/octet-stream',
                    },
                    data=file_content,
                    timeout=300  # 5 хвилин для великих файлів
                )
            else:
                # Upload з файлу (локальний)
                with open(file_path, 'rb') as video_file:
                    upload_response = requests.put(
                        upload_url,
                        headers={
                            'AccessKey': settings.BUNNY_API_KEY,
                            'Content-Type': 'application/octet-stream',
                        },
                        data=video_file,
                        timeout=300  # 5 хвилин для великих файлів
                    )
            
            upload_response.raise_for_status()
            logger.info(f"Video uploaded successfully: {video_id}")
            return video_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error uploading video to Bunny.net: {e}")
            return None
        except IOError as e:
            logger.error(f"Error reading video file: {e}")
            return None
    
    @staticmethod
    def get_video_info(video_id: str) -> Optional[Dict[str, Any]]:
        """
        Отримати інформацію про відео
        
        Args:
            video_id: GUID відео в Bunny.net
            
        Returns:
            Dict з інформацією про відео
        """
        if not BunnyService.is_enabled():
            return None
        
        # Кешування на 5 хвилин
        cache_key = f'bunny_video_info_{video_id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            url = f"{BunnyService._get_library_url()}/videos/{video_id}"
            response = requests.get(
                url,
                headers=BunnyService._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            video_data = response.json()
            
            # Кешувати на 5 хвилин
            cache.set(cache_key, video_data, 300)
            return video_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting video info from Bunny.net: {e}")
            return None
    
    @staticmethod
    def delete_video(video_id: str) -> bool:
        """
        Видалити відео з Bunny.net
        
        Args:
            video_id: GUID відео
            
        Returns:
            True якщо успішно видалено
        """
        if not BunnyService.is_enabled():
            return False
        
        try:
            url = f"{BunnyService._get_library_url()}/videos/{video_id}"
            response = requests.delete(
                url,
                headers=BunnyService._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            
            # Очистити кеш
            cache.delete(f'bunny_video_info_{video_id}')
            
            logger.info(f"Video deleted successfully: {video_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting video from Bunny.net: {e}")
            return False
    
    @staticmethod
    def get_video_embed_url(video_id: str) -> str:
        """
        Отримати URL для embed плеєра
        
        Args:
            video_id: GUID відео
            
        Returns:
            URL для iframe embed
        """
        library_id = settings.BUNNY_LIBRARY_ID
        return f"{settings.BUNNY_VIDEO_EMBED_URL}/{library_id}/{video_id}"
    
    @staticmethod
    def get_video_stream_url(video_id: str) -> str:
        """
        Отримати URL для прямого стрімінгу (HLS playlist)
        
        Args:
            video_id: GUID відео
            
        Returns:
            URL для HLS playlist
        """
        cdn_hostname = settings.BUNNY_CDN_HOSTNAME
        return f"https://{cdn_hostname}/{video_id}/playlist.m3u8"
    
    @staticmethod
    def generate_signed_url(video_id: str, expires_in: int = 3600) -> Optional[str]:
        """
        Генерувати підписаний URL для захищеного доступу
        
        Args:
            video_id: GUID відео
            expires_in: Час дії токену в секундах
            
        Returns:
            Підписаний URL або None
        """
        if not settings.BUNNY_TOKEN_AUTHENTICATION:
            # Якщо токени відключені - повертаємо звичайний URL
            return BunnyService.get_video_stream_url(video_id)
        
        try:
            import hashlib
            import time
            from urllib.parse import urlencode
            
            # Час закінчення дії
            expires = int(time.time()) + expires_in
            
            # Базовий URL
            base_url = BunnyService.get_video_stream_url(video_id)
            
            # Створити підпис (якщо є security key в Bunny.net)
            # TODO: Додати логіку підпису коли буде налаштовано Token Authentication Key
            
            return base_url
            
        except Exception as e:
            logger.error(f"Error generating signed URL: {e}")
            return None
    
    @staticmethod
    def update_video_meta(video_id: str, title: Optional[str] = None, 
                         collection_id: Optional[str] = None) -> bool:
        """
        Оновити метадані відео
        
        Args:
            video_id: GUID відео
            title: Нова назва (опціонально)
            collection_id: ID колекції (опціонально)
            
        Returns:
            True якщо успішно оновлено
        """
        if not BunnyService.is_enabled():
            return False
        
        try:
            url = f"{BunnyService._get_library_url()}/videos/{video_id}"
            data = {}
            if title:
                data['title'] = title
            if collection_id:
                data['collectionId'] = collection_id
            
            if not data:
                return True  # Нічого оновлювати
            
            response = requests.post(
                url,
                headers=BunnyService._get_headers(),
                json=data,
                timeout=10
            )
            response.raise_for_status()
            
            # Очистити кеш
            cache.delete(f'bunny_video_info_{video_id}')
            
            logger.info(f"Video metadata updated: {video_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating video metadata: {e}")
            return False
    
    @staticmethod
    def list_videos(page: int = 1, items_per_page: int = 100, 
                   collection_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Отримати список відео в бібліотеці
        
        Args:
            page: Номер сторінки
            items_per_page: Кількість на сторінці
            collection_id: Фільтр по колекції
            
        Returns:
            Dict з списком відео та пагінацією
        """
        if not BunnyService.is_enabled():
            return None
        
        try:
            url = f"{BunnyService._get_library_url()}/videos"
            params = {
                'page': page,
                'itemsPerPage': items_per_page,
            }
            if collection_id:
                params['collection'] = collection_id
            
            response = requests.get(
                url,
                headers=BunnyService._get_headers(),
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error listing videos from Bunny.net: {e}")
            return None
    
    @staticmethod
    def create_collection(name: str) -> Optional[Dict[str, Any]]:
        """
        Створити колекцію (папку) для організації відео
        
        Args:
            name: Назва колекції
            
        Returns:
            Dict з інформацією про колекцію
        """
        if not BunnyService.is_enabled():
            return None
        
        try:
            url = f"{BunnyService._get_library_url()}/collections"
            data = {'name': name}
            
            response = requests.post(
                url,
                headers=BunnyService._get_headers(),
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating collection: {e}")
            return None

