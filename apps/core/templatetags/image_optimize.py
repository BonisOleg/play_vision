"""
Template tags для оптимізації зображень Cloudinary
"""
import re
from django import template

register = template.Library()


@register.filter
def cloudinary_optimize(url, size='auto'):
    """
    Оптимізує Cloudinary URL додаючи трансформації.
    
    Args:
        url: URL зображення (може бути Cloudinary або звичайний)
        size: Розмір зображення ('auto', число або 'width,height')
    
    Returns:
        Оптимізований URL з параметрами f_auto,q_auto,w_*,h_*
        або оригінальний URL якщо не Cloudinary
    """
    if not url:
        return url
    
    # Перевірка чи це Cloudinary URL
    if 'cloudinary.com' not in str(url):
        return url
    
    url_str = str(url)
    
    # Перевірка чи вже є трансформації в URL
    # Якщо є /upload/ з параметрами після нього, не додаємо подвійні
    if '/upload/' in url_str:
        # Перевіряємо чи вже є трансформації (паттерн: /upload/параметри/шлях)
        upload_match = re.search(r'/upload/([^/]+)/', url_str)
        if upload_match and upload_match.group(1) != 'v1':
            # Вже є трансформації, повертаємо оригінал
            return url_str
    
    # Визначення розміру
    width = None
    height = None
    
    if size == 'auto':
        # Без зміни розміру, тільки формат та якість
        transform = 'f_auto,q_auto'
    elif isinstance(size, (int, str)) and str(size).isdigit():
        # Тільки ширина
        width = int(size)
        transform = f'w_{width},f_auto,q_auto'
    elif ',' in str(size):
        # Ширина та висота
        parts = str(size).split(',')
        width = int(parts[0]) if parts[0].isdigit() else None
        height = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
        if width and height:
            transform = f'w_{width},h_{height},f_auto,q_auto'
        elif width:
            transform = f'w_{width},f_auto,q_auto'
        else:
            transform = 'f_auto,q_auto'
    else:
        # Fallback
        transform = 'f_auto,q_auto'
    
    # Додавання трансформацій до URL
    # Замінюємо /upload/ на /upload/transform/
    if '/upload/v1/' in url_str:
        # Версія з v1
        url_str = url_str.replace('/upload/v1/', f'/upload/{transform}/v1/')
    elif '/upload/' in url_str:
        # Без версії
        url_str = url_str.replace('/upload/', f'/upload/{transform}/')
    else:
        # Неочікуваний формат, повертаємо оригінал
        return url
    
    return url_str


@register.simple_tag
def cloudinary_srcset(url, sizes_list):
    """
    Генерує srcset для responsive images.
    
    Args:
        url: Базовий URL зображення
        sizes_list: Список розмірів через кому (напр. "300,600,1200")
    
    Returns:
        Строка srcset (напр. "url?w=300 300w, url?w=600 600w")
    """
    if not url:
        return ''
    
    sizes = [s.strip() for s in str(sizes_list).split(',') if s.strip().isdigit()]
    if not sizes:
        return ''
    
    srcset_parts = []
    for size in sizes:
        optimized_url = cloudinary_optimize(url, size)
        srcset_parts.append(f'{optimized_url} {size}w')
    
    return ', '.join(srcset_parts)

