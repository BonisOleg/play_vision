"""
Django management команда для витягування зображень з PDF файлів.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
import json


class Command(BaseCommand):
    help = 'Витягує зображення з PDF файлів та генерує CSS класи для фонів'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dpi',
            type=int,
            default=150,
            help='DPI для витягування зображень (default: 150)'
        )
        parser.add_argument(
            '--max-width',
            type=int,
            default=1920,
            help='Максимальна ширина зображень (default: 1920)'
        )
        parser.add_argument(
            '--pdf-dir',
            type=str,
            default='static/guideline',
            help='Директорія з PDF файлами (default: static/guideline)'
        )

    def handle(self, *args, **options):
        dpi = options['dpi']
        max_width = options['max_width']
        pdf_dir = Path(settings.BASE_DIR) / options['pdf_dir']
        output_dir = Path(settings.BASE_DIR) / 'static' / 'images' / 'pdf-backgrounds'
        css_file = Path(settings.BASE_DIR) / 'static' / 'css' / 'pdf-backgrounds.css'
        manifest_file = output_dir / 'manifest.json'
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('PDF Background Extractor'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # Перевіряємо директорію
        if not pdf_dir.exists():
            self.stdout.write(self.style.ERROR(f'❌ Директорія не знайдена: {pdf_dir}'))
            return
        
        # Знаходимо всі PDF
        pdf_files = list(pdf_dir.glob('**/*.pdf'))
        if not pdf_files:
            self.stdout.write(self.style.WARNING(f'⚠️  PDF файли не знайдено в {pdf_dir}'))
            return
        
        self.stdout.write(f'🔍 Знайдено {len(pdf_files)} PDF файлів')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        manifest = {}
        zoom = dpi / 72
        total_images = 0
        
        # Обробляємо кожен PDF
        for pdf_path in sorted(pdf_files):
            self.stdout.write(f'\n📄 Обробка: {pdf_path.name}')
            
            try:
                doc = fitz.open(pdf_path)
                pdf_name = pdf_path.stem
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    matrix = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=matrix, alpha=False)
                    
                    # Зберігаємо
                    output_name = f"{pdf_name}_page{page_num + 1}.png"
                    output_path = output_dir / output_name
                    pix.save(str(output_path))
                    
                    # Оптимізуємо
                    self._optimize_image(output_path, max_width)
                    
                    # Додаємо до маніфесту
                    manifest[output_name] = {
                        "original_pdf": str(pdf_path.relative_to(settings.BASE_DIR)),
                        "page": page_num + 1,
                        "width": pix.width,
                        "height": pix.height,
                        "css_class": self._generate_css_class(pdf_name, page_num + 1)
                    }
                    
                    total_images += 1
                    self.stdout.write(f"  ✓ Сторінка {page_num + 1} → {output_name}")
                
                doc.close()
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Помилка: {e}"))
        
        # Генеруємо CSS
        self._generate_css(manifest, css_file)
        
        # Зберігаємо маніфест
        manifest_file.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        # Фінальний звіт
        self.stdout.write('\n' + self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'✅ Готово! Витягнуто {total_images} зображень'))
        self.stdout.write(self.style.SUCCESS(f'📝 CSS: {css_file}'))
        self.stdout.write(self.style.SUCCESS(f'📋 Manifest: {manifest_file}'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        self.stdout.write('\n📚 Як використовувати:')
        self.stdout.write('1. Додай в base.html:')
        self.stdout.write('   {% load static %}')
        self.stdout.write('   <link rel="stylesheet" href="{% static \'css/pdf-backgrounds.css\' %}">')
        self.stdout.write('\n2. Використовуй класи:')
        self.stdout.write('   <div class="bg-pattern-1">Контент</div>')
        self.stdout.write('\n3. Переглянь демо:')
        self.stdout.write('   http://localhost:8000/pdf-backgrounds-demo/')
    
    def _optimize_image(self, image_path: Path, max_width: int):
        """Оптимізує зображення для веб."""
        try:
            img = Image.open(image_path)
            
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            img.save(image_path, optimize=True, quality=85)
        except Exception:
            pass
    
    def _generate_css_class(self, base_name: str, page: int) -> str:
        """Генерує CSS клас."""
        clean_name = base_name.replace('_', '-').replace(' ', '-').lower()
        return f"bg-{clean_name}-{page}"
    
    def _generate_css(self, manifest: dict, css_path: Path):
        """Генерує CSS файл."""
        css_lines = [
            "/* Автогенеровані класи для PDF фонів */",
            "/* Використання: <div class='bg-название'></div> */\n"
        ]
        
        for img_name, info in manifest.items():
            css_class = info['css_class']
            img_url = f"/static/images/pdf-backgrounds/{img_name}"
            
            css_lines.append(f".{css_class} {{")
            css_lines.append(f"  background-image: url('{img_url}');")
            css_lines.append("  background-size: cover;")
            css_lines.append("  background-position: center;")
            css_lines.append("  background-repeat: no-repeat;")
            css_lines.append(f"  /* {info['width']}×{info['height']}px */")
            css_lines.append("}\n")
        
        css_path.write_text("\n".join(css_lines), encoding="utf-8")

