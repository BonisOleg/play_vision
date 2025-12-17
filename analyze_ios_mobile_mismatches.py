#!/usr/bin/env python3
"""
Аналіз невідповідностей між iOS-специфічними та стандартними мобільними медіа-запитами
"""
import re
from pathlib import Path
from collections import defaultdict

css_dir = Path('static/css')

# Збираємо дані
ios_media_queries = defaultdict(list)  # iOS медіа-запити
standard_mobile_queries = defaultdict(list)  # Стандартні мобільні
mismatches = []

def extract_css_properties(css_block):
    """Витягує CSS властивості з блоку"""
    props = {}
    # Знаходимо всі правила
    for rule_match in re.finditer(r'([^{}]+)\{([^{}]+)\}', css_block, re.DOTALL):
        selector = rule_match.group(1).strip()
        declarations = rule_match.group(2)
        
        for decl in declarations.split(';'):
            decl = decl.strip()
            if ':' in decl:
                prop, value = decl.split(':', 1)
                prop = prop.strip()
                value = value.strip()
                if selector not in props:
                    props[selector] = {}
                props[selector][prop] = value
    return props

for css_file in sorted(css_dir.rglob('*.css')):
    rel_path = str(css_file.relative_to('static/css'))
    
    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Знаходимо всі @supports (-webkit-touch-callout: none) блоки
        ios_blocks = []
        for match in re.finditer(r'@supports\s*\([^)]*-webkit-touch-callout[^)]*\)\s*\{', content):
            start = match.end()
            # Знаходимо закриваючу дужку
            brace_count = 1
            i = start
            while i < len(content) and brace_count > 0:
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                i += 1
            
            ios_block = content[start:i-1]
            ios_blocks.append((match.start(), i-1, ios_block))
            
            # Шукаємо медіа-запити всередині iOS блоку
            for media_match in re.finditer(r'@media\s*\([^)]+\)\s*\{', ios_block):
                media_start = media_match.start()
                media_query = media_match.group(0)
                
                # Витягуємо breakpoint
                bp_match = re.search(r'max-width:\s*(\d+)px', media_query)
                if bp_match:
                    bp = int(bp_match.group(1))
                    
                    # Витягуємо CSS блок
                    media_block_start = media_match.end()
                    media_brace_count = 1
                    j = media_block_start
                    while j < len(ios_block) and media_brace_count > 0:
                        if ios_block[j] == '{':
                            media_brace_count += 1
                        elif ios_block[j] == '}':
                            media_brace_count -= 1
                        j += 1
                    
                    media_css = ios_block[media_block_start:j-1]
                    props = extract_css_properties(media_css)
                    
                    ios_media_queries[rel_path].append({
                        'line': content[:match.start()].count('\n') + 1,
                        'breakpoint': bp,
                        'query': media_query,
                        'properties': props,
                        'css': media_css[:200]
                    })
        
        # Знаходимо стандартні мобільні медіа-запити (поза iOS блоками)
        for match in re.finditer(r'@media\s*\([^)]+max-width:\s*(\d+)px[^)]*\)\s*\{', content):
            bp = int(match.group(1))
            if bp <= 768:  # Тільки мобільні
                # Перевіряємо чи не всередині iOS блоку
                is_inside_ios = False
                for ios_start, ios_end, _ in ios_blocks:
                    if ios_start <= match.start() <= ios_end:
                        is_inside_ios = True
                        break
                
                if not is_inside_ios:
                    # Витягуємо CSS блок
                    css_start = match.end()
                    brace_count = 1
                    k = css_start
                    while k < len(content) and brace_count > 0:
                        if content[k] == '{':
                            brace_count += 1
                        elif content[k] == '}':
                            brace_count -= 1
                        k += 1
                    
                    css_block = content[css_start:k-1]
                    props = extract_css_properties(css_block)
                    
                    standard_mobile_queries[rel_path].append({
                        'line': content[:match.start()].count('\n') + 1,
                        'breakpoint': bp,
                        'query': match.group(0),
                        'properties': props,
                        'css': css_block[:200]
                    })
                    
    except Exception as e:
        print(f"Помилка при читанні {css_file}: {e}")

# Порівнюємо iOS та стандартні медіа-запити
print("=" * 100)
print("АНАЛІЗ НЕВІДПОВІДНОСТЕЙ МІЖ iOS ТА СТАНДАРТНИМИ МОБІЛЬНИМИ МЕДІА-ЗАПИТАМИ")
print("=" * 100)

for file in sorted(set(list(ios_media_queries.keys()) + list(standard_mobile_queries.keys()))):
    ios_queries = ios_media_queries.get(file, [])
    standard_queries = standard_mobile_queries.get(file, [])
    
    if not ios_queries and not standard_queries:
        continue
    
    print(f"\n{'='*100}")
    print(f"📄 {file}")
    print(f"{'='*100}")
    
    # Групуємо за breakpoints
    ios_by_bp = defaultdict(list)
    standard_by_bp = defaultdict(list)
    
    for q in ios_queries:
        ios_by_bp[q['breakpoint']].append(q)
    
    for q in standard_queries:
        standard_by_bp[q['breakpoint']].append(q)
    
    # Перевіряємо невідповідності breakpoints
    ios_bps = set(ios_by_bp.keys())
    standard_bps = set(standard_by_bp.keys())
    
    if ios_bps != standard_bps:
        print(f"\n⚠️  НЕВІДПОВІДНІСТЬ BREAKPOINTS:")
        print(f"   iOS breakpoints: {sorted(ios_bps)}")
        print(f"   Стандартні breakpoints: {sorted(standard_bps)}")
        
        only_ios = ios_bps - standard_bps
        only_standard = standard_bps - ios_bps
        
        if only_ios:
            print(f"   ❌ Тільки в iOS: {sorted(only_ios)}")
            for bp in only_ios:
                for q in ios_by_bp[bp]:
                    print(f"      Рядок {q['line']}: {q['query']}")
        
        if only_standard:
            print(f"   ❌ Тільки в стандартних: {sorted(only_standard)}")
            for bp in only_standard:
                for q in standard_by_bp[bp]:
                    print(f"      Рядок {q['line']}: {q['query']}")
    
    # Порівнюємо властивості для однакових breakpoints
    common_bps = ios_bps & standard_bps
    for bp in common_bps:
        ios_qs = ios_by_bp[bp]
        standard_qs = standard_by_bp[bp]
        
        # Порівнюємо селектори та властивості
        ios_selectors = set()
        standard_selectors = set()
        
        for q in ios_qs:
            ios_selectors.update(q['properties'].keys())
        
        for q in standard_qs:
            standard_selectors.update(q['properties'].keys())
        
        if ios_selectors != standard_selectors:
            print(f"\n⚠️  НЕВІДПОВІДНІСТЬ СЕЛЕКТОРІВ для breakpoint {bp}px:")
            only_ios_sel = ios_selectors - standard_selectors
            only_standard_sel = standard_selectors - ios_selectors
            
            if only_ios_sel:
                print(f"   ❌ Тільки в iOS: {only_ios_sel}")
            if only_standard_sel:
                print(f"   ❌ Тільки в стандартних: {only_standard_sel}")
        
        # Порівнюємо властивості для спільних селекторів
        common_selectors = ios_selectors & standard_selectors
        for selector in common_selectors:
            ios_props = {}
            standard_props = {}
            
            for q in ios_qs:
                if selector in q['properties']:
                    ios_props.update(q['properties'][selector])
            
            for q in standard_qs:
                if selector in q['properties']:
                    standard_props.update(q['properties'][selector])
            
            # Порівнюємо властивості (ігноруючи webkit-префікси)
            ios_normalized = {k.replace('-webkit-', ''): v for k, v in ios_props.items()}
            standard_normalized = {k.replace('-webkit-', ''): v for k, v in standard_props.items()}
            
            # Виключаємо iOS-специфічні властивості
            ios_specific = {'tap-highlight-color', 'touch-callout', 'appearance', 'user-select', 'user-drag', 
                          'backface-visibility', 'transform', 'overflow-scrolling', 'font-smoothing'}
            
            ios_filtered = {k: v for k, v in ios_normalized.items() 
                          if not any(ios_spec in k.lower() for ios_spec in ios_specific)}
            standard_filtered = standard_normalized.copy()
            
            if ios_filtered != standard_filtered:
                diff_props = set(ios_filtered.keys()) ^ set(standard_filtered.keys())
                if diff_props:
                    print(f"\n⚠️  НЕВІДПОВІДНІСТЬ ВЛАСТИВОСТЕЙ для {selector} (breakpoint {bp}px):")
                    print(f"   Різні властивості: {diff_props}")
                
                # Перевіряємо різні значення
                for prop in ios_filtered:
                    if prop in standard_filtered:
                        if ios_filtered[prop] != standard_filtered[prop]:
                            print(f"\n⚠️  РІЗНІ ЗНАЧЕННЯ для {selector}.{prop} (breakpoint {bp}px):")
                            print(f"   iOS: {ios_filtered[prop]}")
                            print(f"   Стандарт: {standard_filtered[prop]}")

print("\n" + "=" * 100)
print("ПІДСУМОК")
print("=" * 100)
print(f"Файлів з iOS медіа-запитами: {len(ios_media_queries)}")
print(f"Файлів зі стандартними мобільними: {len(standard_mobile_queries)}")
print(f"Файлів з обома: {len(set(ios_media_queries.keys()) & set(standard_mobile_queries.keys()))}")
















