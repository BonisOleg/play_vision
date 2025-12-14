#!/usr/bin/env python3
"""
Generator для PWA іконок Play Vision
Конвертує logomain.svg в PNG іконки всіх необхідних розмірів
"""
import os
import sys
from pathlib import Path
from PIL import Image
import subprocess

# Шлях до джерельного SVG
SOURCE_SVG = Path(__file__).parent.parent / 'logomain.svg'

def convert_svg_to_png_cairosvg(svg_path, output_path, size, background_color='white'):
    """Конвертувати SVG в PNG за допомогою cairosvg"""
    try:
        import cairosvg
        # Конвертувати SVG в PNG
        png_data = cairosvg.svg2png(
            url=str(svg_path),
            output_width=size,
            output_height=size
        )
        
        # Відкрити як PIL Image для додавання фону
        from io import BytesIO
        img = Image.open(BytesIO(png_data))
        
        # Додати фон якщо потрібно
        if background_color != 'transparent':
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            background = Image.new('RGBA', (size, size), background_color)
            background.paste(img, (0, 0), img)
            background.save(output_path, 'PNG', optimize=True)
        else:
            img.save(output_path, 'PNG', optimize=True)
        
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"Error with cairosvg: {e}")
        return False

def convert_svg_to_png_imagemagick(svg_path, output_path, size, background_color='white'):
    """Конвертувати SVG в PNG за допомогою ImageMagick"""
    try:
        # Створити тимчасовий файл з білим фоном
        temp_png = output_path.parent / f'temp_{size}.png'
        
        # Конвертувати SVG в PNG
        subprocess.run([
            'convert',
            '-background', background_color,
            '-resize', f'{size}x{size}',
            str(svg_path),
            str(temp_png)
        ], check=True, capture_output=True)
        
        # Якщо потрібен білий фон, додати його
        if background_color != 'transparent':
            img = Image.open(temp_png)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Створити білий фон
            background = Image.new('RGBA', (size, size), background_color)
            background.paste(img, (0, 0), img if img.mode == 'RGBA' else None)
            background.save(output_path, 'PNG', optimize=True)
            temp_png.unlink()
        else:
            temp_png.rename(output_path)
        
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    except Exception as e:
        print(f"Error with ImageMagick: {e}")
        return False

def convert_svg_to_png_pillow(svg_path, output_path, size, background_color='white'):
    """Конвертувати SVG в PNG за допомогою Pillow (обмежена підтримка)"""
    try:
        from PIL import Image
        # Pillow має обмежену підтримку SVG, спробуємо через svglib
        try:
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPM
            
            drawing = svg2rlg(str(svg_path))
            if drawing:
                renderPM.drawToFile(drawing, str(output_path), fmt='PNG', dpi=72 * (size / 100))
                
                # Масштабувати до потрібного розміру
                img = Image.open(output_path)
                img = img.resize((size, size), Image.Resampling.LANCZOS)
                
                # Додати фон якщо потрібно
                if background_color != 'transparent':
                    background = Image.new('RGBA', (size, size), background_color)
                    if img.mode == 'RGBA':
                        background.paste(img, (0, 0), img)
                    else:
                        background.paste(img, (0, 0))
                    background.save(output_path, 'PNG', optimize=True)
                else:
                    img.save(output_path, 'PNG', optimize=True)
                
                return True
        except ImportError:
            pass
    except Exception as e:
        print(f"Error with Pillow/svglib: {e}")
    return False

def convert_svg_to_png(svg_path, output_path, size, background_color='white'):
    """Конвертувати SVG в PNG, спробувати різні методи"""
    if not svg_path.exists():
        raise FileNotFoundError(f"SVG file not found: {svg_path}")
    
    # Спробувати cairosvg (найкращий варіант)
    if convert_svg_to_png_cairosvg(svg_path, output_path, size, background_color):
        return True
    
    # Спробувати ImageMagick
    if convert_svg_to_png_imagemagick(svg_path, output_path, size, background_color):
        return True
    
    # Спробувати svglib + Pillow
    if convert_svg_to_png_pillow(svg_path, output_path, size, background_color):
        return True
    
    raise RuntimeError("No SVG converter available. Install cairosvg: pip install cairosvg")

def create_icon(size, output_path, background_color='white'):
    """Створити PNG іконку заданого розміру з logomain.svg"""
    convert_svg_to_png(SOURCE_SVG, output_path, size, background_color)
    print(f"✅ Created {output_path.name} ({size}x{size})")

def main():
    """Створити всі необхідні іконки з logomain.svg"""
    if not SOURCE_SVG.exists():
        print(f"❌ Error: Source SVG not found at {SOURCE_SVG}")
        print("Please ensure logomain.svg exists in static/ directory")
        sys.exit(1)
    
    current_dir = Path(__file__).parent
    
    # PWA іконки (всі розміри)
    pwa_sizes = [16, 32, 72, 96, 128, 144, 152, 192, 384, 512]
    
    # Apple Touch Icons (iOS)
    apple_sizes = [57, 60, 72, 76, 114, 120, 144, 152, 180]
    
    # Shortcut іконки
    shortcut_size = 96
    
    # Badge для notifications
    badge_size = 72
    
    # Action іконки для notifications
    action_size = 24
    
    print("🎨 Generating PWA icons from logomain.svg...")
    print(f"📁 Source: {SOURCE_SVG}")
    print(f"📁 Output: {current_dir}\n")
    
    total_created = 0
    
    # Генерація PWA іконок
    print("📱 Creating PWA icons...")
    for size in pwa_sizes:
        icon_path = current_dir / f'icon-{size}x{size}.png'
        try:
            create_icon(size, icon_path, background_color='white')
            total_created += 1
        except Exception as e:
            print(f"❌ Failed to create icon-{size}x{size}.png: {e}")
    
    # Генерація Apple Touch Icons
    print("\n🍎 Creating Apple Touch Icons...")
    for size in apple_sizes:
        apple_path = current_dir / f'apple-touch-icon-{size}x{size}.png'
        try:
            # Apple Touch Icons зазвичай мають білий фон
            create_icon(size, apple_path, background_color='white')
            total_created += 1
        except Exception as e:
            print(f"❌ Failed to create apple-touch-icon-{size}x{size}.png: {e}")
    
    # Генерація Shortcut іконок
    print("\n🔗 Creating Shortcut icons...")
    shortcut_names = ['shortcut-hub', 'shortcut-account', 'shortcut-ai']
    for name in shortcut_names:
        shortcut_path = current_dir / f'{name}.png'
        try:
            create_icon(shortcut_size, shortcut_path, background_color='white')
            total_created += 1
        except Exception as e:
            print(f"❌ Failed to create {name}.png: {e}")
    
    # Генерація Badge для notifications
    print("\n🏷️ Creating Badge icon...")
    badge_path = current_dir / 'badge-72x72.png'
    try:
        create_icon(badge_size, badge_path, background_color='white')
        total_created += 1
    except Exception as e:
        print(f"❌ Failed to create badge-72x72.png: {e}")
    
    # Генерація Action іконок
    print("\n⚡ Creating Action icons...")
    action_names = ['action-open', 'action-close']
    for name in action_names:
        action_path = current_dir / f'{name}.png'
        try:
            create_icon(action_size, action_path, background_color='transparent')
            total_created += 1
        except Exception as e:
            print(f"❌ Failed to create {name}.png: {e}")
    
    print(f"\n✅ Successfully created {total_created} icons from logomain.svg")
    print("📱 All icons are ready for PWA installation")
    print("\n💡 Note: If conversion failed, install cairosvg:")
    print("   pip install cairosvg")

if __name__ == "__main__":
    main()
