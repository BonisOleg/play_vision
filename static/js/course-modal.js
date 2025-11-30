/**
 * Course Modal - Модальне вікно для курсів
 * Дані передаються через data-атрибути кнопки
 * БЕЗ AJAX - миттєве відкриття
 */

(function() {
    'use strict';

    class CourseModal {
        constructor() {
            this.modal = document.getElementById('course-modal');
            this.modalBody = document.getElementById('course-modal-body');
            this.savedScrollY = 0;

            if (!this.modal || !this.modalBody) {
                console.warn('CourseModal: Required elements not found');
                return;
            }

            this.init();
        }

        init() {
            this.attachTriggerListeners();
            this.attachCloseListeners();
            this.attachKeyboardListeners();
        }

        attachTriggerListeners() {
            document.addEventListener('click', (e) => {
                const trigger = e.target.closest('.course-modal-trigger');
                if (trigger) {
                    e.preventDefault();
                    this.open(trigger);
                }
            });
        }

        open(trigger) {
            // Отримати дані з data-атрибутів
            const data = this.getDataFromTrigger(trigger);

            // Заповнити контент
            this.renderContent(data);

            // Заблокувати scroll body
            this.lockBodyScroll();

            // Показати модальне вікно
            if (this.modal) {
                this.modal.classList.remove('is-hidden');
                this.modal.classList.add('is-visible');
            }

            // Focus на кнопку закриття (accessibility)
            const closeBtn = this.modal.querySelector('.course-modal-close');
            if (closeBtn) {
                closeBtn.focus();
            }
        }

        close() {
            if (this.modal) {
                this.modal.classList.remove('is-visible');
                this.modal.classList.add('is-hidden');
            }
            this.unlockBodyScroll();
        }

        lockBodyScroll() {
            this.savedScrollY = window.scrollY;
            document.body.style.position = 'fixed';
            document.body.style.top = `-${this.savedScrollY}px`;
            document.body.style.width = '100%';
            document.body.classList.add('modal-open');
        }

        unlockBodyScroll() {
            document.body.style.position = '';
            document.body.style.top = '';
            document.body.style.width = '';
            document.body.classList.remove('modal-open');
            window.scrollTo(0, this.savedScrollY);
        }

        renderContent(data) {
            // Визначити, чи є медіа для правої колонки
            const hasRightColumn = data.logo || data.video;

            let rightColumnHtml = '';
            if (hasRightColumn) {
                if (data.video) {
                    rightColumnHtml = `
                        <div class="course-modal-right">
                            <iframe src="${this.escapeHtml(data.video)}?autoplay=false" 
                                    frameborder="0" 
                                    allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" 
                                    allowfullscreen></iframe>
                        </div>
                    `;
                } else if (data.logo) {
                    rightColumnHtml = `
                        <div class="course-modal-right">
                            <img src="${this.escapeHtml(data.logo)}" alt="${this.escapeHtml(data.title)}" class="course-modal-logo">
                        </div>
                    `;
                }
            }

            const audienceHtml = data.audience ? `
                <div class="meta-item">
                    <span class="meta-label">Кому підходить:</span>
                    <span class="meta-value">${this.escapeHtml(data.audience)}</span>
                </div>
            ` : '';

            const html = `
                <div class="course-modal-grid ${hasRightColumn ? 'two-columns' : 'single-column'}">
                    <div class="course-modal-left">
                        <nav class="course-modal-breadcrumb">
                            <span>Хаб знань</span>
                            <span>/</span>
                            <span>${this.escapeHtml(data.title)}</span>
                        </nav>

                        ${data.featured ? '<span class="badge badge-featured">топ-продажів</span>' : ''}

                        <h2 class="course-modal-title" id="course-modal-title">${this.escapeHtml(data.title)}</h2>

                        <p class="course-modal-description" id="course-description">${this.escapeHtml(data.description)}</p>
                        <button type="button" class="read-more-btn" id="read-more-btn">
                            <span class="read-more-text">Читати далі</span>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M6 9l6 6 6-6"/>
                            </svg>
                        </button>

                        <div class="course-modal-meta">
                            <div class="meta-item">
                                <span class="meta-label">Ціна:</span>
                                <span class="meta-value price">${this.escapeHtml(data.price)}₴</span>
                            </div>
                            ${audienceHtml}
                        </div>

                        <div class="course-modal-actions">
                            <a href="${this.escapeHtml(data.joinUrl)}" 
                               class="btn btn-primary btn-large" 
                               target="_blank" 
                               rel="noopener noreferrer">
                                Приєднатись до клубу
                            </a>
                        </div>
                    </div>

                    ${rightColumnHtml}
                </div>
            `;

            if (this.modalBody) {
                this.modalBody.innerHTML = html;
                this.attachReadMoreListener();
            }
        }

        attachReadMoreListener() {
            const readMoreBtn = document.getElementById('read-more-btn');
            const description = document.getElementById('course-description');

            if (readMoreBtn && description) {
                readMoreBtn.addEventListener('click', () => {
                    description.classList.toggle('expanded');
                    readMoreBtn.classList.toggle('expanded');
                    
                    const textSpan = readMoreBtn.querySelector('.read-more-text');
                    if (description.classList.contains('expanded')) {
                        textSpan.textContent = 'Згорнути';
                    } else {
                        textSpan.textContent = 'Читати далі';
                    }
                });
            }
        }

        getDataFromTrigger(trigger) {
            return {
                id: trigger.dataset.courseId || '',
                title: trigger.dataset.courseTitle || '',
                description: trigger.dataset.courseDescription || '',
                price: trigger.dataset.coursePrice || '0',
                featured: trigger.dataset.courseFeatured === 'True',
                audience: trigger.dataset.courseAudience || '',
                logo: trigger.dataset.courseLogo || '',
                video: trigger.dataset.courseVideo || '',
                joinUrl: trigger.dataset.courseJoinUrl || '#',
                author: trigger.dataset.courseAuthor || ''
            };
        }

        attachCloseListeners() {
            if (!this.modal) return;

            // Кнопки закриття з data-close-modal
            this.modal.addEventListener('click', (e) => {
                const closeBtn = e.target.closest('[data-close-modal]');
                if (closeBtn) {
                    e.stopPropagation();
                    this.close();
                }
            });
        }

        attachKeyboardListeners() {
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.modal && this.modal.classList.contains('is-visible')) {
                    this.close();
                }
            });
        }

        /**
         * Escape HTML для запобігання XSS
         */
        escapeHtml(text) {
            if (!text) return '';
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return String(text).replace(/[&<>"']/g, (m) => map[m]);
        }
    }

    // Ініціалізація
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new CourseModal();
        });
    } else {
        new CourseModal();
    }
})();

