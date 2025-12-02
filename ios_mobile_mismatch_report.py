#!/usr/bin/env python3
"""
Детальний звіт про невідповідності між iOS та стандартними мобільними медіа-запитами
"""
import re
from pathlib import Path

css_dir = Path('static/css')

issues = []

for css_file in sorted(css_dir.rglob('*.css')):
    rel_path = str(css_file.relative_to('static/css'))
    
    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Знаходимо всі iOS блоки
        ios_blocks = []
        for match in re.finditer(r'@supports\s*\([^)]*-webkit-touch-callout[^)]*\)\s*\{', content):
            start_pos = match.start()
            # Знаходимо закриваючу дужку
            brace_count = 1
            i = match.end()
            while i < len(content) and brace_count > 0:
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                i += 1
            end_pos = i - 1
            ios_blocks.append((start_pos, end_pos))
        
        # Знаходимо всі медіа-запити
        all_media_queries = []
        for match in re.finditer(r'@media\s*\([^)]+\)', content):
            line_num = content[:match.start()].count('\n') + 1
            query = match.group(0)
            
            # Визначаємо чи всередині iOS блоку
            is_ios = any(start <= match.start() <= end for start, end in ios_blocks)
            
            # Витягуємо breakpoint
            bp_match = re.search(r'max-width:\s*(\d+)px', query)
            if bp_match:
                bp = int(bp_match.group(1))
                if bp <= 1024:  # Тільки мобільні та планшетні
                    all_media_queries.append({
                        'line': line_num,
                        'query': query,
                        'breakpoint': bp,
                        'is_ios': is_ios,
                        'position': match.start()
                    })
        
        # Групуємо за breakpoints
        ios_by_bp = {}
        standard_by_bp = {}
        
        for mq in all_media_queries:
            if mq['is_ios']:
                if mq['breakpoint'] not in ios_by_bp:
                    ios_by_bp[mq['breakpoint']] = []
                ios_by_bp[mq['breakpoint']].append(mq)
            else:
                if mq['breakpoint'] not in standard_by_bp:
                    standard_by_bp[mq['breakpoint']] = []
                standard_by_bp[mq['breakpoint']].append(mq)
        
        # Перевіряємо невідповідності
        if ios_by_bp or standard_by_bp:
            ios_bps = set(ios_by_bp.keys())
            standard_bps = set(standard_by_bp.keys())
            
            # Невідповідності breakpoints
            only_ios = ios_bps - standard_bps
            only_standard = standard_bps - ios_bps
            
            if only_ios or only_standard:
                issues.append({
                    'file': rel_path,
                    'type': 'breakpoint_mismatch',
                    'ios_only': sorted(only_ios),
                    'standard_only': sorted(only_standard),
                    'ios_queries': {bp: ios_by_bp[bp] for bp in only_ios},
                    'standard_queries': {bp: standard_by_bp[bp] for bp in only_standard}
                })
            
            # Перевіряємо різні breakpoints для однакових селекторів
            common_bps = ios_bps & standard_bps
            if common_bps:
                # Витягуємо селектори з медіа-запитів
                for bp in common_bps:
                    ios_mqs = ios_by_bp[bp]
                    standard_mqs = standard_by_bp[bp]
                    
                    # Витягуємо CSS блоки
                    for ios_mq in ios_mqs:
                        ios_start = ios_mq['position'] + len(ios_mq['query'])
                        # Знаходимо CSS блок
                        brace_count = 0
                        i = ios_start
                        while i < len(content) and (content[i] != '{' or brace_count > 0):
                            if content[i] == '{':
                                brace_count += 1
                            elif content[i] == '}':
                                brace_count -= 1
                            i += 1
                        if content[i] == '{':
                            css_start = i + 1
                            brace_count = 1
                            j = css_start
                            while j < len(content) and brace_count > 0:
                                if content[j] == '{':
                                    brace_count += 1
                                elif content[j] == '}':
                                    brace_count -= 1
                                j += 1
                            ios_css = content[css_start:j-1]
                            
                            # Порівнюємо зі стандартними
                            for standard_mq in standard_mqs:
                                if standard_mq['breakpoint'] == bp:
                                    std_start = standard_mq['position'] + len(standard_mq['query'])
                                    brace_count = 0
                                    k = std_start
                                    while k < len(content) and (content[k] != '{' or brace_count > 0):
                                        if content[k] == '{':
                                            brace_count += 1
                                        elif content[k] == '}':
                                            brace_count -= 1
                                        k += 1
                                    if content[k] == '{':
                                        std_css_start = k + 1
                                        brace_count = 1
                                        l = std_css_start
                                        while l < len(content) and brace_count > 0:
                                            if content[l] == '{':
                                                brace_count += 1
                                            elif content[l] == '}':
                                                brace_count -= 1
                                            l += 1
                                        std_css = content[std_css_start:l-1]
                                        
                                        # Видаляємо iOS-специфічні властивості для порівняння
                                        ios_normalized = re.sub(r'-webkit-[^:]+:\s*[^;]+;', '', ios_css)
                                        ios_normalized = re.sub(r'tap-highlight-color[^;]+;', '', ios_normalized)
                                        ios_normalized = re.sub(r'touch-callout[^;]+;', '', ios_normalized)
                                        ios_normalized = re.sub(r'user-select[^;]+;', '', ios_normalized)
                                        ios_normalized = re.sub(r'user-drag[^;]+;', '', ios_normalized)
                                        ios_normalized = re.sub(r'backface-visibility[^;]+;', '', ios_normalized)
                                        ios_normalized = re.sub(r'overflow-scrolling[^;]+;', '', ios_normalized)
                                        ios_normalized = re.sub(r'font-smoothing[^;]+;', '', ios_normalized)
                                        
                                        std_normalized = std_css
                                        
                                        # Порівнюємо (ігноруючи пробіли)
                                        ios_clean = ' '.join(ios_normalized.split())
                                        std_clean = ' '.join(std_normalized.split())
                                        
                                        if ios_clean != std_clean and len(ios_clean) > 10 and len(std_clean) > 10:
                                            issues.append({
                                                'file': rel_path,
                                                'type': 'css_content_mismatch',
                                                'breakpoint': bp,
                                                'ios_line': ios_mq['line'],
                                                'standard_line': standard_mq['line'],
                                                'ios_css_preview': ios_css[:150],
                                                'standard_css_preview': std_css[:150]
                                            })
                                            
    except Exception as e:
        print(f"Помилка при читанні {css_file}: {e}")

# Виводимо звіт
print("=" * 100)
print("ДЕТАЛЬНИЙ ЗВІТ ПРО НЕВІДПОВІДНОСТІ iOS ТА СТАНДАРТНИХ МОБІЛЬНИХ МЕДІА-ЗАПИТІВ")
print("=" * 100)

breakpoint_issues = [i for i in issues if i['type'] == 'breakpoint_mismatch']
content_issues = [i for i in issues if i['type'] == 'css_content_mismatch']

if breakpoint_issues:
    print("\n" + "=" * 100)
    print("1. НЕВІДПОВІДНОСТІ BREAKPOINTS")
    print("=" * 100)
    
    for issue in breakpoint_issues:
        print(f"\n📄 {issue['file']}:")
        
        if issue['ios_only']:
            print(f"   ⚠️  iOS має breakpoints, яких немає в стандартних:")
            for bp in issue['ios_only']:
                print(f"      • {bp}px:")
                for mq in issue['ios_queries'][bp]:
                    print(f"        Рядок {mq['line']}: {mq['query']}")
        
        if issue['standard_only']:
            print(f"   ⚠️  Стандартні мають breakpoints, яких немає в iOS:")
            for bp in issue['standard_only']:
                print(f"      • {bp}px:")
                for mq in issue['standard_queries'][bp]:
                    print(f"        Рядок {mq['line']}: {mq['query']}")

if content_issues:
    print("\n" + "=" * 100)
    print("2. НЕВІДПОВІДНОСТІ В CSS ВМІСТІ (для однакових breakpoints)")
    print("=" * 100)
    
    for issue in content_issues:
        print(f"\n📄 {issue['file']} (breakpoint {issue['breakpoint']}px):")
        print(f"   iOS медіа-запит (рядок {issue['ios_line']}):")
        print(f"   {issue['ios_css_preview']}...")
        print(f"   Стандартний медіа-запит (рядок {issue['standard_line']}):")
        print(f"   {issue['standard_css_preview']}...")

if not issues:
    print("\n✅ Невідповідностей не знайдено!")

print("\n" + "=" * 100)
print("ПІДСУМОК")
print("=" * 100)
print(f"Файлів з невідповідностями breakpoints: {len(set(i['file'] for i in breakpoint_issues))}")
print(f"Файлів з невідповідностями CSS вмісту: {len(set(i['file'] for i in content_issues))}")
print(f"Всього проблем: {len(issues)}")





