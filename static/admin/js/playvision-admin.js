/**
 * PlayVision Admin Panel JavaScript
 * Theme toggle, image previews, keyboard shortcuts
 */

(function() {
    'use strict';
    
    // Theme Management
    const ThemeManager = {
        init() {
            this.toggleBtn = document.querySelector('[data-theme-toggle]');
            if (!this.toggleBtn) return;
            
            // Load saved theme
            this.currentTheme = localStorage.getItem('pv-admin-theme') || 'light';
            this.applyTheme(this.currentTheme);
            
            // Bind toggle
            this.toggleBtn.addEventListener('click', () => this.toggle());
        },
        
        applyTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            this.currentTheme = theme;
            localStorage.setItem('pv-admin-theme', theme);
        },
        
        toggle() {
            const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
            this.applyTheme(newTheme);
        }
    };
    
    // Image Preview on Upload
    const ImagePreview = {
        init() {
            const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
            imageInputs.forEach(input => {
                input.addEventListener('change', (e) => this.handleFileSelect(e, input));
            });
        },
        
        handleFileSelect(e, input) {
            const file = e.target.files[0];
            if (!file || !file.type.startsWith('image/')) return;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                let preview = input.parentElement.querySelector('.pv-image-preview');
                
                if (!preview) {
                    preview = document.createElement('div');
                    preview.className = 'pv-image-preview';
                    input.parentElement.appendChild(preview);
                }
                
                preview.innerHTML = `
                    <img src="${e.target.result}" alt="Preview">
                    <p style="margin-top: 1rem; color: var(--pv-text-light); font-size: 0.875rem;">
                        ${file.name} (${(file.size / 1024).toFixed(1)} KB)
                    </p>
                `;
            };
            reader.readAsDataURL(file);
        }
    };
    
    // Keyboard Shortcuts
    const KeyboardShortcuts = {
        init() {
            document.addEventListener('keydown', (e) => this.handleKeyPress(e));
        },
        
        handleKeyPress(e) {
            const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
            const cmdOrCtrl = isMac ? e.metaKey : e.ctrlKey;
            
            // Cmd/Ctrl + S = Save
            if (cmdOrCtrl && e.key === 's') {
                e.preventDefault();
                const saveBtn = document.querySelector('input[type="submit"][name="_save"]');
                if (saveBtn) saveBtn.click();
            }
            
            // Cmd/Ctrl + Enter = Save and Continue
            if (cmdOrCtrl && e.key === 'Enter') {
                e.preventDefault();
                const continueBtn = document.querySelector('input[type="submit"][name="_continue"]');
                if (continueBtn) continueBtn.click();
            }
        }
    };
    
    // Color Picker Enhancement
    const ColorPicker = {
        init() {
            const colorInputs = document.querySelectorAll('input[type="text"][name*="color"]');
            colorInputs.forEach(input => {
                if (!input.classList.contains('pv-color-enhanced')) {
                    input.classList.add('pv-color-enhanced');
                    
                    // Create color picker
                    const picker = document.createElement('input');
                    picker.type = 'color';
                    picker.value = input.value || '#E50914';
                    picker.style.marginLeft = '1rem';
                    picker.style.cursor = 'pointer';
                    picker.style.width = '50px';
                    picker.style.height = '40px';
                    picker.style.border = '2px solid var(--pv-border)';
                    picker.style.borderRadius = '6px';
                    
                    // Sync values
                    picker.addEventListener('change', () => {
                        input.value = picker.value;
                    });
                    
                    input.addEventListener('change', () => {
                        if (/^#[0-9A-F]{6}$/i.test(input.value)) {
                            picker.value = input.value;
                        }
                    });
                    
                    input.parentElement.appendChild(picker);
                }
            });
        }
    };
    
    // Sortable Enhancement (for drag-drop ordering)
    const SortableEnhancement = {
        init() {
            // Will be implemented with django-admin-sortable2
            console.log('✅ Sortable ready');
        }
    };
    
    // Auto-save Draft
    const AutoSave = {
        timer: null,
        
        init() {
            const form = document.querySelector('.form-horizontal, #content-main form');
            if (!form) return;
            
            form.addEventListener('input', () => {
                clearTimeout(this.timer);
                this.timer = setTimeout(() => this.saveDraft(form), 30000); // 30 seconds
            });
        },
        
        saveDraft(form) {
            const formData = new FormData(form);
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            
            localStorage.setItem('pv-admin-draft', JSON.stringify(data));
            console.log('Draft saved');
        },
        
        loadDraft() {
            const draft = localStorage.getItem('pv-admin-draft');
            if (draft) {
                console.log('Draft available');
                // Can implement restore functionality
            }
        }
    };
    
    // Initialize all features
    document.addEventListener('DOMContentLoaded', function() {
        ThemeManager.init();
        ImagePreview.init();
        KeyboardShortcuts.init();
        ColorPicker.init();
        SortableEnhancement.init();
        AutoSave.init();
        
        console.log('✅ PlayVision Admin initialized');
    });
    
})();

