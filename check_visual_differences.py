#!/usr/bin/env python3
"""
Перевірка розбіжностей в ВІЗУАЛЬНИХ властивостях між iOS та стандартними медіа-запитами
"""
import re
from pathlib import Path
from collections import defaultdict

css_dir = Path('static/css')

# Візуальні властивості що мають бути ідентичними
VISUAL_PROPS = [
    'font-size', 'font-weight', 'font-family',
    'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
    'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
    'width', 'max-width', 'min-width',
    'height', 'max-height', 'min-height',
    'border-radius', 'border-width',
    'gap', 'flex', 'grid-template-columns'
]

# iOS-специфічні властивості (можуть бути різними)
IOS_SPECIFIC = [
    'env(safe-area-inset', '100dvh', '100vh', 
    '-webkit-', 'backface-visibility', 'transform',
    'overflow-scrolling', 'font-smoothing'
]

def extract_props(css_text, selector_filter=None):
    """Витягує властивості з CSS тексту"""
    props = defaultdict(dict)
    
    # Знаходимо всі правила
    for match in re.finditer(r'([^{}]+)\{([^{}]+)\}', css_text, re.DOTALL):
        selector = match.group(1).strip()
        
        # Фільтр селекторів
        if selector_filter and selector_filter not in selector:
            continue
            
        declarations = match.group(2)
        
        for decl in declarations.split(';'):
            decl = decl.strip()
            if ':' in decl:
                prop, value = decl.split(':', 1)
                prop = prop.strip()
                value = value.strip()
                
                # Тільки візуальні властивості
                if any(vp in prop for vp in VISUAL_PROPS):
                    # Пропускаємо iOS-специфічні значення
                    if not any(ios_spec in value for ios_spec in IOS_SPECIFIC):
                        props[selector][prop] = value
    
    return props

issues = []

for css_file in sorted(css_dir.rglob('*.css')):
    rel_path = str(css_file.relative_to('static/css'))
    
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Шукаємо iOS блок
    ios_match = re.search(r'@supports[^{]*-webkit-touch-callout[^{]*\{(.*)', content, re.DOTALL)
    if not ios_match:
        continue
    
    ios_content = ios_match.group(1)
    
    # Для кожного breakpoint
    for breakpoint in [480, 768, 1024]:
        # Знаходимо стандартний медіа-запит
        standard_media = []
        for match in re.finditer(rf'@media \(max-width: {breakpoint}px\)[^{{]*\{{', content):
            # Перевіряємо що це НЕ всередині iOS блоку
            if match.start() < ios_match.start() or match.start() > len(content):
                start = match.end()
                level = 1
                i = start
                while i < len(content) and level > 0:
                    if content[i] == '{': level += 1
                    elif content[i] == '}': level -= 1
                    i += 1
                standard_media.append(content[start:i-1])
        
        # Знаходимо iOS медіа-запит
        ios_media = []
        for match in re.finditer(rf'@media \(max-width: {breakpoint}px\)[^{{]*\{{', ios_content):
            start = match.end()
            level = 1
            i = start
            while i < len(ios_content) and level > 0:
                if ios_content[i] == '{': level += 1
                elif ios_content[i] == '}': level -= 1
                i += 1
            ios_media.append(ios_content[start:i-1])
        
        if not standard_media or not ios_media:
            continue
        
        # Витягуємо властивості
        std_props = {}
        for sm in standard_media:
            std_props.update(extract_props(sm))
        
        ios_props = {}
        for im in ios_media:
            ios_props.update(extract_props(im))
        
        # Порівнюємо для спільних селекторів
        common_selectors = set(std_props.keys()) & set(ios_props.keys())
        
        for selector in common_selectors:
            std_sel_props = std_props[selector]
            ios_sel_props = ios_props[selector]
            
            # Знаходимо розбіжності
            for prop in std_sel_props:
                if prop in ios_sel_props:
                    std_val = std_sel_props[prop].strip()
                    ios_val = ios_sel_props[prop].strip()
                    
                    if std_val != ios_val:
                        issues.append({
                            'file': rel_path,
                            'breakpoint': breakpoint,
                            'selector': selector,
                            'property': prop,
                            'standard': std_val,
                            'ios': ios_val
                        })

# Виводимо звіт
print("=" * 100)
print("РОЗБІЖНОСТІ У ВІЗУАЛЬНИХ ВЛАСТИВОСТЯХ (font-size, padding, margin, width, height)")
print("=" * 100)

if not issues:
    print("\n✅ Розбіжностей не знайдено! Всі візуальні властивості ідентичні.")
else:
    print(f"\n⚠️  Знайдено {len(issues)} розбіжностей:\n")
    
    by_file = defaultdict(list)
    for issue in issues:
        by_file[issue['file']].append(issue)
    
    for file, file_issues in sorted(by_file.items()):
        print(f"\n📄 {file}:")
        for issue in file_issues:
            print(f"   Breakpoint {issue['breakpoint']}px | {issue['selector']}")
            print(f"      {issue['property']}:")
            print(f"         Стандартний: {issue['standard']}")
            print(f"         iOS:         {issue['ios']}")
            print()

print("\n" + "=" * 100)
print(f"ПІДСУМОК: {len(issues)} розбіжностей у {len(by_file)} файлах")
print("=" * 100)







