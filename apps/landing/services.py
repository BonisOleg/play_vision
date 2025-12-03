import requests
import logging
from django.conf import settings
from django.core.cache import cache
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class SendPulseService:
    """Сервіс для роботи з SendPulse CRM API"""
    
    BASE_URL = 'https://api.sendpulse.com'
    TOKEN_CACHE_KEY = 'sendpulse_access_token'
    TOKEN_CACHE_TIMEOUT = 3600  # 1 година
    
    def __init__(self):
        self.client_id = getattr(settings, 'SENDPULSE_ID', '')
        self.client_secret = getattr(settings, 'SENDPULSE_SECRET', '')
        
    def _get_access_token(self) -> Optional[str]:
        """Отримати access token через OAuth 2.0"""
        # Спробувати отримати з кешу
        cached_token = cache.get(self.TOKEN_CACHE_KEY)
        if cached_token:
            return cached_token
        
        if not self.client_id or not self.client_secret:
            logger.error('SendPulse credentials not configured')
            return None
        
        try:
            url = f'{self.BASE_URL}/oauth/access_token'
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data.get('access_token')
            
            if access_token:
                # Зберегти в кеш
                cache.set(self.TOKEN_CACHE_KEY, access_token, self.TOKEN_CACHE_TIMEOUT)
                logger.info('SendPulse access token obtained successfully')
                return access_token
            
            logger.error('No access token in SendPulse response')
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f'Failed to get SendPulse access token: {str(e)}')
            return None
    
    def add_contact(
        self,
        email: str,
        phone: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Додати контакт в SendPulse CRM
        
        Args:
            email: Email контакту
            phone: Телефон контакту
            variables: Додаткові змінні (first_name, promo_code, source)
        
        Returns:
            ID створеного контакту або None у разі помилки
        """
        token = self._get_access_token()
        if not token:
            logger.error('Cannot add contact: no access token')
            return None
        
        try:
            url = f'{self.BASE_URL}/crm/v1/contacts'
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            }
            
            # Підготовка даних контакту
            contact_data = {
                'email': email,
                'phones': [phone],
            }
            
            # Додати firstName та lastName завжди
            if variables and 'first_name' in variables:
                first_name = variables.get('first_name', '').strip()
            else:
                first_name = ''
            
            # Якщо first_name порожнє, використати email як fallback
            if not first_name:
                # Взяти частину email до @
                email_part = email.split('@')[0] if '@' in email else 'User'
                first_name = email_part if email_part else 'User'
            
            # Розділити ім'я на firstName та lastName
            name_parts = first_name.split(maxsplit=1)
            contact_data['firstName'] = name_parts[0] if name_parts else first_name
            contact_data['lastName'] = name_parts[1] if len(name_parts) > 1 else name_parts[0]
            
            # Додати додаткові змінні якщо є
            if variables:
                contact_data['variables'] = variables
            
            response = requests.post(
                url,
                json=contact_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                contact_id = result.get('id')
                logger.info(f'Contact added to SendPulse CRM: {email} (ID: {contact_id})')
                return str(contact_id) if contact_id else None
            
            # Обробка різних типів помилок
            error_response = response.text
            try:
                error_data = response.json()
                error_message = error_data.get('message', '')
                
                # Перевірка на дублікат контакту
                if 'already exists' in error_message.lower() or 'duplicate' in error_message.lower():
                    logger.info(
                        f'Contact {email} already exists in SendPulse CRM. '
                        f'Treating as successful sync.'
                    )
                    # Спробувати отримати існуючий контакт
                    existing_contact = self.get_contact(email)
                    if existing_contact and existing_contact.get('id'):
                        return str(existing_contact['id'])
                    return 'existing'  # Повертаємо маркер, що контакт існує
            except (ValueError, KeyError):
                pass
            
            # Детальне логування помилки для діагностики
            logger.error(
                f'Failed to add contact to SendPulse CRM: '
                f'Status {response.status_code}, Response: {error_response}, '
                f'Payload: {contact_data}, '
                f'URL: {url}, '
                f'Headers: {headers}'
            )
            
            # Спробувати отримати детальну інформацію про помилку
            try:
                error_json = response.json()
                logger.error(f'Error details: {error_json}')
            except (ValueError, KeyError):
                logger.error(f'Could not parse error response as JSON')
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f'Error adding contact to SendPulse: {str(e)}')
            return None
    
    def get_contact(self, email: str) -> Optional[Dict[str, Any]]:
        """Отримати контакт з SendPulse CRM за email"""
        token = self._get_access_token()
        if not token:
            return None
        
        try:
            url = f'{self.BASE_URL}/crm/v1/contacts'
            headers = {
                'Authorization': f'Bearer {token}',
            }
            params = {
                'email': email,
            }
            
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            contacts = data.get('data', [])
            
            if contacts:
                return contacts[0]
            
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f'Error getting contact from SendPulse: {str(e)}')
            return None
    
    def add_contact_to_addressbook(
        self,
        addressbook_id: int,
        email: str,
        phone: str,
        name: str,
        source: str = 'hub'
    ) -> bool:
        """
        Додати контакт до адресної книги SendPulse через Email Service API
        
        Args:
            addressbook_id: ID адресної книги (int)
            email: Email контакту
            phone: Телефон контакту
            name: Ім'я контакту
            source: Джерело заявки
        
        Returns:
            True якщо успішно, False у разі помилки
        """
        token = self._get_access_token()
        if not token:
            logger.error('Cannot add contact to addressbook: no access token')
            return False
        
        try:
            url = f'{self.BASE_URL}/addressbooks/{int(addressbook_id)}/emails'
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            }
            
            # Валідація name - має бути не порожнім
            if not name or not name.strip():
                # Використати email як fallback
                email_part = email.split('@')[0] if '@' in email else 'User'
                name = email_part if email_part else 'User'
            else:
                name = name.strip()
            
            # Розділити ім'я на firstName та lastName
            name_parts = name.split(maxsplit=1)
            first_name = name_parts[0] if name_parts else 'User'
            last_name = name_parts[1] if len(name_parts) > 1 else first_name
            
            payload = {
                'emails': [
                    {
                        'email': email,
                        'firstName': first_name,
                        'lastName': last_name,
                        'variables': {
                            'phone': phone,
                            'name': name if name else first_name,
                            'source': source,
                        }
                    }
                ]
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result') is True:
                    logger.info(f'Contact added to SendPulse addressbook {addressbook_id}: {email}')
                    return True
            
            # Обробка різних типів помилок
            error_response = response.text
            try:
                error_data = response.json()
                error_message = error_data.get('message', '')
                
                # Перевірка на дублікат контакту
                if 'already exists' in error_message.lower() or 'duplicate' in error_message.lower():
                    logger.info(
                        f'Contact {email} already exists in addressbook {addressbook_id}. '
                        f'Treating as successful sync.'
                    )
                    return True
            except (ValueError, KeyError):
                pass
            
            # Детальне логування помилки для діагностики
            logger.error(
                f'Failed to add contact to SendPulse addressbook {addressbook_id}: '
                f'Status {response.status_code}, Response: {error_response}, '
                f'Payload: {payload}, '
                f'URL: {url}, '
                f'Headers: {headers}'
            )
            
            # Спробувати отримати детальну інформацію про помилку
            try:
                error_json = response.json()
                logger.error(f'Error details: {error_json}')
            except (ValueError, KeyError):
                logger.error(f'Could not parse error response as JSON')
            
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f'Error adding contact to SendPulse addressbook: {str(e)}')
            return False

