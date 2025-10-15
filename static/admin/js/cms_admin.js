(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {

        // Auto preview on file selection
        const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
        imageInputs.forEach(input => {
            input.addEventListener('change', function (e) {
                const file = e.target.files[0];
                if (file && file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        let preview = input.parentElement.querySelector('.image-preview');
                        if (!preview) {
                            preview = document.createElement('div');
                            preview.className = 'image-preview';
                            input.parentElement.appendChild(preview);
                        }

                        preview.innerHTML = `
                            <img src="${e.target.result}" 
                                 alt="Превью">
                            <p style="margin:10px 0 0;font-size:13px;color:#718096;">
                                ${file.name} (${(file.size / 1024).toFixed(1)} KB)
                            </p>
                        `;
                    };
                    reader.readAsDataURL(file);
                }
            });
        });

        // Ctrl/Cmd + S to save
        document.addEventListener('keydown', function (e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                const submitBtn = document.querySelector('input[type="submit"][name="_save"]');
                if (submitBtn) {
                    submitBtn.click();
                }
            }
        });

        // Ctrl/Cmd + Enter to save and continue
        document.addEventListener('keydown', function (e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                const submitBtn = document.querySelector('input[type="submit"][name="_continue"]');
                if (submitBtn) {
                    submitBtn.click();
                }
            }
        });

        // Color input improvements
        const colorInputs = document.querySelectorAll('input[type="text"][name*="color"]');
        colorInputs.forEach(input => {
            if (!input.classList.contains('color-enhanced')) {
                input.classList.add('color-enhanced');
                input.setAttribute('type', 'color');
                input.style.height = '40px';
                input.style.cursor = 'pointer';
            }
        });

        console.log('✅ CMS Admin JS initialized');
    });
})();

