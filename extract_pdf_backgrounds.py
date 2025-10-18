#!/usr/bin/env python
"""
Скрипт для витягування зображень з PDF файлів та підготовки для використання як фони.

ВИКОРИСТАННЯ:
    python extract_pdf_backgrounds.py

ВИХІДНІ ФАЙЛИ:
    - static/images/pdf-backgrounds/*.png - витягнуті зображення
    - static/css/pdf-backgrounds.css - готові CSS класи
    - static/images/pdf-backgrounds/manifest.json - інформація про зображення

ЗАЛЕЖНОСТІ:
    pip install PyMuPDF Pillow

ПРИКЛАД ВИКОРИСТАННЯ В КОДІ:
    HTML:
        <div class="bg-02-backpack-black-1">Контент</div>
    
    CSS:
        background-image: url('/static/images/pdf-backgrounds/pattern_page1.png');
"""
import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image
import json
import sys


class PDFBackgroundExtractor:
    def __init__(self, pdf_dir: str, output_dir: str, dpi: int = 150):
        self.pdf_dir = Path(pdf_dir)
        self.output_dir = Path(output_dir)
        self.dpi = dpi
        self.zoom = dpi / 72  # PDF default DPI is 72
        self.manifest = {}
        
    def extract_from_pdf(self, pdf_path: Path, optimize: bool = True):
        """Витягує зображення з PDF файлу."""
        doc = fitz.open(pdf_path)
        pdf_name = pdf_path.stem
        images = []
        
        print(f"\n📄 Обробка: {pdf_path.name}")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Рендеримо сторінку як зображення
            matrix = fitz.Matrix(self.zoom, self.zoom)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            
            # Зберігаємо як PNG
            output_name = f"{pdf_name}_page{page_num + 1}.png"
            output_path = self.output_dir / output_name
            pix.save(str(output_path))
            
            # Оптимізуємо якщо потрібно
            if optimize:
                self._optimize_image(output_path)
            
            img_info = {
                "original_pdf": str(pdf_path.relative_to(self.pdf_dir.parent)),
                "page": page_num + 1,
                "width": pix.width,
                "height": pix.height,
                "css_class": self._generate_css_class(pdf_name, page_num + 1)
            }
            images.append(output_name)
            self.manifest[output_name] = img_info
            
            print(f"  ✓ Сторінка {page_num + 1} → {output_name} ({pix.width}×{pix.height})")
        
        doc.close()
        return images
    
    def _optimize_image(self, image_path: Path, max_width: int = 1920):
        """Оптимізує зображення для веб."""
        try:
            img = Image.open(image_path)
            
            # Зменшуємо якщо занадто велике
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Зберігаємо з оптимізацією
            img.save(image_path, optimize=True, quality=85)
            
        except Exception as e:
            print(f"    ⚠️  Помилка оптимізації: {e}")
    
    def _generate_css_class(self, base_name: str, page: int) -> str:
        """Генерує CSS клас для background."""
        clean_name = base_name.replace('_', '-').replace(' ', '-').lower()
        return f"bg-{clean_name}-{page}"
    
    def process_directory(self, recursive: bool = True):
        """Обробляє всі PDF в директорії."""
        pattern = "**/*.pdf" if recursive else "*.pdf"
        pdf_files = list(self.pdf_dir.glob(pattern))
        
        if not pdf_files:
            print(f"❌ PDF файли не знайдено в {self.pdf_dir}")
            return
        
        print(f"🔍 Знайдено {len(pdf_files)} PDF файлів")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        total_images = 0
        for pdf_path in sorted(pdf_files):
            try:
                images = self.extract_from_pdf(pdf_path)
                total_images += len(images)
            except Exception as e:
                print(f"  ❌ Помилка: {e}")
        
        print(f"\n✅ Готово! Витягнуто {total_images} зображень")
        return total_images
    
    def generate_css(self, css_path: Path):
        """Генерує CSS файл з класами для фонів."""
        css_lines = [
            "/* Автогенеровані класи для PDF фонів */",
            "/* Використання: <div class='bg-название'></div> */\n"
        ]
        
        for img_name, info in self.manifest.items():
            css_class = info['css_class']
            img_url = f"/static/images/pdf-backgrounds/{img_name}"
            
            css_lines.append(f".{css_class} {{")
            css_lines.append(f"  background-image: url('{img_url}');")
            css_lines.append("  background-size: cover;")
            css_lines.append("  background-position: center;")
            css_lines.append("  background-repeat: no-repeat;")
            css_lines.append(f"  /* {info['width']}×{info['height']}px */")
            css_lines.append("}\n")
        
        css_path.parent.mkdir(parents=True, exist_ok=True)
        css_path.write_text("\n".join(css_lines), encoding="utf-8")
        print(f"📝 CSS збережено: {css_path}")
    
    def save_manifest(self, manifest_path: Path):
        """Зберігає маніфест з інформацією про зображення."""
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(self.manifest, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"📋 Маніфест збережено: {manifest_path}")


def main():
    # Конфігурація
    BASE_DIR = Path(__file__).parent
    PDF_DIR = BASE_DIR / "static" / "guideline"
    OUTPUT_DIR = BASE_DIR / "static" / "images" / "pdf-backgrounds"
    CSS_FILE = BASE_DIR / "static" / "css" / "pdf-backgrounds.css"
    MANIFEST_FILE = OUTPUT_DIR / "manifest.json"
    
    # Параметри
    DPI = 150  # Якість (72-низька, 150-середня, 300-висока)
    
    print("=" * 60)
    print("PDF Background Extractor для Play Vision")
    print("=" * 60)
    
    extractor = PDFBackgroundExtractor(
        pdf_dir=str(PDF_DIR),
        output_dir=str(OUTPUT_DIR),
        dpi=DPI
    )
    
    # Обробляємо всі PDF
    total = extractor.process_directory(recursive=True)
    
    if total:
        # Генеруємо CSS
        extractor.generate_css(CSS_FILE)
        
        # Зберігаємо маніфест
        extractor.save_manifest(MANIFEST_FILE)
        
        print("\n" + "=" * 60)
        print("📚 Як використовувати:")
        print("=" * 60)
        print("1. Додай в base.html:")
        print('   <link rel="stylesheet" href="{% static \'css/pdf-backgrounds.css\' %}">')
        print("\n2. Використовуй класи:")
        print('   <div class="bg-backpack-black-1"></div>')
        print("\n3. Або напряму:")
        print('   background-image: url("/static/images/pdf-backgrounds/...")');
        print("\n4. Подивись manifest.json для всіх доступних зображень")
        print("=" * 60)


if __name__ == "__main__":
    main()

