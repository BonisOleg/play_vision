#!/usr/bin/env python3
"""
Скрипт для аналізу медіа-запитів та виявлення невідповідностей
"""
import re
import os
from collections import defaultdict
from pathlib import Path

css_dir = Path('static/css')

# Категорії breakpoints
MOBILE_MAX = 768  # Мобільні до 768px
TABLET_MIN = 768  # Планшети від 768px
TABLET_MAX = 1024  # Планшети до 1024px
DESKTOP_MIN = 1024  # Десктоп від 1024px

def extract_media_query_block(content, start_pos):
    """Витягує повний блок медіа-запиту з фігурними дужками"""
    brace_count = 0
    start_brace = content.find('{', start_pos)
    if start_brace == -1:
        return None, None
    
    i = start_brace + 1
    while i < len(content):
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            if brace_count == 0:
                return content[start_pos:start_brace].strip(), content[start_brace+1:i].strip()
            brace_count -= 1
        i += 1
    return None, None

def parse_media_query(query_str):
    """Парсить медіа-запит і визначає його категорію"""
    query_str = query_str.strip()
    
    # Мобільні breakpoints
    mobile_patterns = [
        r'max-width:\s*(\d+)px',
    ]
    
    # Планшетні breakpoints
    tablet_patterns = [
        r'min-width:\s*76[89]px',
        r'max-width:\s*1024px',
        r'min-width:\s*48[0-9]px.*max-width:\s*76[89]px',
    ]
    
    # Десктопні breakpoints
    desktop_patterns = [
        r'min-width:\s*102[5-9]px',
        r'min-width:\s*1200px',
        r'max-width:\s*1199px',
        r'max-width:\s*1200px',
    ]
    
    # Визначаємо категорію
    category = None
    breakpoint = None
    
    # Перевіряємо мобільні
    for pattern in mobile_patterns:
        match = re.search(pattern, query_str)
        if match:
            bp = int(match.group(1)) if match.groups() else None
            if bp and bp < MOBILE_MAX:
                category = 'mobile'
                breakpoint = bp
                break
    
    # Перевіряємо планшетні
    if not category:
        for pattern in tablet_patterns:
            if re.search(pattern, query_str):
                category = 'tablet'
                # Витягуємо breakpoint
                min_match = re.search(r'min-width:\s*(\d+)px', query_str)
                max_match = re.search(r'max-width:\s*(\d+)px', query_str)
                if min_match and max_match:
                    breakpoint = f"{min_match.group(1)}-{max_match.group(1)}"
                elif max_match:
                    breakpoint = max_match.group(1)
                elif min_match:
                    breakpoint = min_match.group(1)
                break
    
    # Перевіряємо десктопні
    if not category:
        for pattern in desktop_patterns:
            if re.search(pattern, query_str):
                category = 'desktop'
                match = re.search(r'(?:min-width|max-width):\s*(\d+)px', query_str)
                if match:
                    breakpoint = match.group(1)
                break
    
    return category, breakpoint, query_str

def extract_css_properties(css_block):
    """Витягує всі CSS властивості з блоку"""
    properties = {}
    
    # Знаходимо всі правила
    rules = re.findall(r'([^{}]+)\{([^{}]+)\}', css_block, re.DOTALL)
    
    for selector, declarations in rules:
        selector = selector.strip()
        # Парсимо декларації
        for decl in declarations.split(';'):
            decl = decl.strip()
            if ':' in decl:
                prop, value = decl.split(':', 1)
                prop = prop.strip()
                value = value.strip()
                
                # Групуємо за типами властивостей
                if prop in ['font-size', 'font-weight', 'line-height']:
                    if 'typography' not in properties:
                        properties['typography'] = {}
                    properties['typography'][prop] = value
                elif prop in ['padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left']:
                    if 'padding' not in properties:
                        properties['padding'] = {}
                    properties['padding'][prop] = value
                elif prop in ['margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left']:
                    if 'margin' not in properties:
                        properties['margin'] = {}
                    properties['margin'][prop] = value
                elif prop in ['width', 'height', 'max-width', 'min-width', 'max-height', 'min-height']:
                    if 'sizing' not in properties:
                        properties['sizing'] = {}
                    properties['sizing'][prop] = value
    
    return properties

# Збираємо всі медіа-запити
media_data = defaultdict(lambda: defaultdict(list))

for css_file in css_dir.rglob('*.css'):
    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Знаходимо всі медіа-запити
            for match in re.finditer(r'@media\s*\([^)]+\)', content):
                query_str = match.group(0)
                category, breakpoint, full_query = parse_media_query(query_str)
                
                if category:
                    # Витягуємо блок стилів
                    query_block, css_block = extract_media_query_block(content, match.end())
                    if css_block:
                        properties = extract_css_properties(css_block)
                        media_data[category][breakpoint].append({
                            'file': str(css_file.relative_to('static/css')),
                            'query': full_query,
                            'properties': properties,
                            'block': css_block[:200]  # Перші 200 символів для прикладу
                        })
    except Exception as e:
        print(f'Помилка при читанні {css_file}: {e}')

# Виводимо результати
print("=" * 80)
print("АНАЛІЗ НЕВІДПОВІДНОСТЕЙ У МЕДІА-ЗАПИТАХ")
print("=" * 80)

for category in ['mobile', 'tablet', 'desktop']:
    print(f"\n{'='*80}")
    print(f"КАТЕГОРІЯ: {category.upper()}")
    print(f"{'='*80}")
    
    if category not in media_data:
        print("Немає медіа-запитів для цієї категорії")
        continue
    
    # Групуємо за breakpoints
    def sort_key(x):
        if isinstance(x, str) and '-' in x:
            return int(x.split('-')[0])
        elif isinstance(x, (int, str)):
            try:
                return int(x)
            except:
                return 0
        return 0
    
    breakpoints = sorted(media_data[category].keys(), key=sort_key)
    
    print(f"\nЗнайдено {len(breakpoints)} різних breakpoints: {breakpoints}")
    print(f"\n⚠️  ПРОБЛЕМА: Різні breakpoints для однієї категорії!")
    print(f"   Потрібно стандартизувати на один breakpoint для {category}")
    
    # Для кожного breakpoint показуємо файли
    for bp in breakpoints:
        entries = media_data[category][bp]
        print(f"\n  Breakpoint: {bp}px ({len(entries)} використань)")
        for entry in entries[:5]:  # Показуємо перші 5
            print(f"    - {entry['file']}: {entry['query']}")
        if len(entries) > 5:
            print(f"    ... та ще {len(entries) - 5} використань")

print("\n" + "=" * 80)
print("РЕКОМЕНДАЦІЇ:")
print("=" * 80)
print("""
1. МОБІЛЬНІ (mobile): Стандартизувати на max-width: 768px
   Знайдені breakpoints: 375px, 390px, 400px, 479px, 480px, 576px, 767px
   
2. ПЛАНШЕТНІ (tablet): Стандартизувати на min-width: 769px and max-width: 1024px
   Знайдені breakpoints: різні комбінації 768px-1024px
   
3. ДЕСКТОПНІ (desktop): Стандартизувати на min-width: 1025px
   Знайдені breakpoints: 1025px, 1199px, 1200px

Потрібно замінити всі нестандартні breakpoints на стандартні!
""")

