#!/usr/bin/env python3
"""
Генерація детального звіту про невідповідності в медіа-запитах
"""
import re
from pathlib import Path
from collections import defaultdict

css_dir = Path('static/css')

# Стандартні breakpoints з design-tokens.css
STANDARD_BREAKPOINTS = {
    'mobile': 768,  # max-width: 768px
    'tablet_min': 769,  # min-width: 769px
    'tablet_max': 1024,  # max-width: 1024px
    'desktop': 1025,  # min-width: 1025px
}

issues = {
    'mobile': [],
    'tablet': [],
    'desktop': [],
}

def find_media_queries_in_file(file_path):
    """Знаходить всі медіа-запити у файлі"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        media_queries = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if '@media' in line:
                # Знаходимо повний медіа-запит
                media_match = re.search(r'@media\s*\([^)]+\)', line)
                if media_match:
                    query = media_match.group(0)
                    # Визначаємо категорію
                    category = None
                    breakpoint = None
                    
                    # Мобільні
                    mobile_match = re.search(r'max-width:\s*(\d+)px', query)
                    if mobile_match:
                        bp = int(mobile_match.group(1))
                        if bp < 768:
                            category = 'mobile'
                            breakpoint = bp
                    
                    # Планшетні
                    if not category:
                        tablet_min = re.search(r'min-width:\s*(\d+)px', query)
                        tablet_max = re.search(r'max-width:\s*(\d+)px', query)
                        if tablet_min and tablet_max:
                            min_bp = int(tablet_min.group(1))
                            max_bp = int(tablet_max.group(1))
                            if 768 <= min_bp <= 1024 or 768 <= max_bp <= 1024:
                                category = 'tablet'
                                breakpoint = f"{min_bp}-{max_bp}"
                        elif tablet_max:
                            max_bp = int(tablet_max.group(1))
                            if 768 <= max_bp <= 1024:
                                category = 'tablet'
                                breakpoint = max_bp
                        elif tablet_min:
                            min_bp = int(tablet_min.group(1))
                            if 768 <= min_bp <= 1024:
                                category = 'tablet'
                                breakpoint = min_bp
                    
                    # Десктопні
                    if not category:
                        desktop_match = re.search(r'(?:min-width|max-width):\s*(\d+)px', query)
                        if desktop_match:
                            bp = int(desktop_match.group(1))
                            if bp >= 1025 or (bp >= 1024 and 'min-width' in query):
                                category = 'desktop'
                                breakpoint = bp
                    
                    if category:
                        media_queries.append({
                            'line': i + 1,
                            'query': query,
                            'category': category,
                            'breakpoint': breakpoint,
                        })
            i += 1
        
        return media_queries
    except Exception as e:
        print(f"Помилка при читанні {file_path}: {e}")
        return []

# Скануємо всі CSS файли
for css_file in sorted(css_dir.rglob('*.css')):
    rel_path = str(css_file.relative_to('static/css'))
    queries = find_media_queries_in_file(css_file)
    
    for q in queries:
        category = q['category']
        bp = q['breakpoint']
        standard_bp = None
        
        if category == 'mobile':
            standard_bp = STANDARD_BREAKPOINTS['mobile']
            if bp != standard_bp:
                issues['mobile'].append({
                    'file': rel_path,
                    'line': q['line'],
                    'current': bp,
                    'standard': standard_bp,
                    'query': q['query'],
                })
        elif category == 'tablet':
            # Перевіряємо чи відповідає стандарту
            if isinstance(bp, str) and '-' in bp:
                min_bp, max_bp = map(int, bp.split('-'))
                if min_bp != STANDARD_BREAKPOINTS['tablet_min'] or max_bp != STANDARD_BREAKPOINTS['tablet_max']:
                    issues['tablet'].append({
                        'file': rel_path,
                        'line': q['line'],
                        'current': bp,
                        'standard': f"{STANDARD_BREAKPOINTS['tablet_min']}-{STANDARD_BREAKPOINTS['tablet_max']}",
                        'query': q['query'],
                    })
            elif isinstance(bp, int):
                if bp == 768:
                    # Це може бути окремий breakpoint, перевіряємо контекст
                    if 'min-width: 768px' in q['query']:
                        issues['tablet'].append({
                            'file': rel_path,
                            'line': q['line'],
                            'current': f"min-width: {bp}px",
                            'standard': f"min-width: {STANDARD_BREAKPOINTS['tablet_min']}px",
                            'query': q['query'],
                        })
                elif bp == 1024:
                    # max-width: 1024px - це нормально для планшетів
                    pass
        elif category == 'desktop':
            standard_bp = STANDARD_BREAKPOINTS['desktop']
            if isinstance(bp, int) and bp != standard_bp:
                issues['desktop'].append({
                    'file': rel_path,
                    'line': q['line'],
                    'current': bp,
                    'standard': standard_bp,
                    'query': q['query'],
                })

# Виводимо звіт
print("=" * 100)
print("ПОВНИЙ ЗВІТ ПРО НЕВІДПОВІДНОСТІ В МЕДІА-ЗАПИТАХ")
print("=" * 100)

for category in ['mobile', 'tablet', 'desktop']:
    print(f"\n{'='*100}")
    print(f"КАТЕГОРІЯ: {category.upper()}")
    print(f"{'='*100}\n")
    
    if not issues[category]:
        print("✅ Невідповідностей не знайдено!")
        continue
    
    print(f"⚠️  Знайдено {len(issues[category])} невідповідностей:\n")
    
    # Групуємо за файлами
    by_file = defaultdict(list)
    for issue in issues[category]:
        by_file[issue['file']].append(issue)
    
    for file, file_issues in sorted(by_file.items()):
        print(f"📄 {file}:")
        for issue in file_issues:
            print(f"   Рядок {issue['line']}:")
            print(f"      Поточний: {issue['query']}")
            print(f"      Потрібно:  @media (max-width: {issue['standard']}px)" if category == 'mobile' else 
                  f"      Потрібно:  @media (min-width: {issue['standard'].split('-')[0]}px) and (max-width: {issue['standard'].split('-')[1]}px)" if category == 'tablet' and '-' in str(issue['standard']) else
                  f"      Потрібно:  @media (min-width: {issue['standard']}px)")
            print()
        print()

print("\n" + "=" * 100)
print("ПІДСУМОК")
print("=" * 100)
print(f"Мобільні невідповідності: {len(issues['mobile'])}")
print(f"Планшетні невідповідності: {len(issues['tablet'])}")
print(f"Десктопні невідповідності: {len(issues['desktop'])}")
print(f"\nВСЬОГО: {sum(len(issues[c]) for c in issues)} невідповідностей")

















