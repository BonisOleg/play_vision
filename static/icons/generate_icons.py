#!/usr/bin/env python3
"""
Generator для PWA іконок Play Vision
Створює всі необхідні розміри з SVG placeholder
"""
import os
from PIL import Image, ImageDraw, ImageFont
import io

def create_icon(size, output_path):
    """Створити PNG іконку заданого розміру"""
    # Створити зображення з помаранчевим фоном
    img = Image.new('RGBA', (size, size), color='#ff6b35')
    draw = ImageDraw.Draw(img)
    
    # Заокруглені кути
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    corner_radius = size // 6  # 16.67% радіус заокруглення
    mask_draw.rounded_rectangle([0, 0, size, size], radius=corner_radius, fill=255)
    
    # Застосувати маску
    output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    output.paste(img, mask=mask)
    
    # Додати простий логотип
    center = size // 2
    
    # Біле коло
    circle_radius = size // 3
    draw = ImageDraw.Draw(output)
    
    # Трикутник play
    triangle_size = size // 6
    triangle_points = [
        (center - triangle_size//2, center - triangle_size//2),
        (center - triangle_size//2, center + triangle_size//2),
        (center + triangle_size//2, center)
    ]
    
    # Намалювати на новому зображенні
    draw = ImageDraw.Draw(output)
    draw.ellipse([center-circle_radius, center-circle_radius, 
                  center+circle_radius, center+circle_radius], 
                 outline='white', width=max(2, size//50))
    
    draw.polygon(triangle_points, fill='white')
    
    # Текст PV
    try:
        font_size = max(12, size // 12)
        # Використати системний шрифт
        font = ImageFont.load_default()
        
        text = "PV"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = center - text_width // 2
        text_y = center + circle_radius // 2
        
        draw.text((text_x, text_y), text, fill='white', font=font)
    except:
        pass  # Якщо проблеми з шрифтом, пропустити текст
    
    # Зберегти
    output.save(output_path, 'PNG', optimize=True)
    print(f"Created {output_path} ({size}x{size})")

def main():
    """Створити всі необхідні іконки"""
    icon_sizes = [
        16, 32, 57, 60, 72, 76, 96, 114, 120, 128, 
        144, 152, 180, 192, 384, 512
    ]
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("Creating PWA icons for Play Vision...")
    
    for size in icon_sizes:
        # Regular icons
        icon_path = os.path.join(current_dir, f'icon-{size}x{size}.png')
        create_icon(size, icon_path)
        
        # Apple touch icons
        if size in [57, 60, 72, 76, 114, 120, 144, 152, 180]:
            apple_path = os.path.join(current_dir, f'apple-touch-icon-{size}x{size}.png')
            create_icon(size, apple_path)
    
    print(f"\n✅ Created {len(icon_sizes)} PWA icons")
    print("📝 TODO: Replace placeholder icons with real Play Vision logo")
    print("📱 Icons ready for PWA installation")

if __name__ == "__main__":
    main()
