// Events JavaScript

document.addEventListener('DOMContentLoaded', function () {
    console.log('🎯 Events page loaded - initializing...');

    // Restore scroll position after filter reload
    const savedScrollPosition = sessionStorage.getItem('eventsScrollPosition');
    if (savedScrollPosition) {
        window.scrollTo(0, parseInt(savedScrollPosition));
        sessionStorage.removeItem('eventsScrollPosition');
        console.log('📍 Restored scroll position:', savedScrollPosition);
    }

    // Calendar functionality
    initCalendar();

    // Filter functionality
    initFilters();

    // Share functionality
    initShareButtons();

    // Event registration
    initEventRegistration();

    // Debug info
    console.log('✅ Events page initialization complete');
});

// Calendar functionality
function initCalendar() {
    const calendarDays = document.querySelectorAll('.calendar-day');

    console.log('Found calendar days:', calendarDays.length);

    calendarDays.forEach((day, index) => {
        // Primary click handler
        day.addEventListener('click', function (e) {
            handleCalendarDayClick(this, index, e);
        });

        // Touch support for mobile
        day.addEventListener('touchend', function (e) {
            e.preventDefault();
            handleCalendarDayClick(this, index, e);
        });

        // Add pointer cursor to indicate clickability
        day.style.cursor = 'pointer';

        // Add visual hover effect
        day.addEventListener('mouseenter', function () {
            if (!this.classList.contains('calendar-day--active')) {
                this.style.opacity = '0.8';
            }
        });

        day.addEventListener('mouseleave', function () {
            this.style.opacity = '1';
        });
    });

    function handleCalendarDayClick(dayElement, index, event) {
        console.log('📅 Calendar day clicked:', index);

        // Remove active class from all days
        calendarDays.forEach(d => d.classList.remove('calendar-day--active'));

        // Add active class to clicked day
        dayElement.classList.add('calendar-day--active');

        // Get event details from the clicked day
        const eventCard = dayElement.querySelector('.event-card');
        if (eventCard) {
            const eventTitle = eventCard.querySelector('.event-title');
            if (eventTitle) {
                console.log('🎯 Selected event:', eventTitle.textContent);

                // Navigate to event detail if it has a link
                if (eventCard.href && eventCard.href !== '#' && eventCard.href !== window.location.href) {
                    console.log('🔗 Navigating to:', eventCard.href);

                    // Add loading visual feedback
                    dayElement.style.opacity = '0.6';

                    setTimeout(() => {
                        window.location.href = eventCard.href;
                    }, 150);
                } else {
                    console.log('⚠️ No valid link found for event');
                }
            }
        } else {
            console.log('⚠️ No event card found in day');
        }
    }

    // Auto-scroll to active day on load
    const activeDay = document.querySelector('.calendar-day--active');
    if (activeDay) {
        activeDay.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
    }
}

// Filter functionality
function initFilters() {
    const eventTypeCheckboxes = document.querySelectorAll('input[name="event_type"]');
    const formatRadios = document.querySelectorAll('input[name="format"]');

    console.log('Found event type checkboxes:', eventTypeCheckboxes.length);
    console.log('Found format radios:', formatRadios.length);

    // Restore filter states from URL
    restoreFilterStates();

    // Event type filters
    eventTypeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function (e) {
            console.log('Checkbox changed:', this.value, this.checked);
            debounceApplyFilters();
        });

        // Add visual feedback
        checkbox.addEventListener('change', function () {
            const label = this.closest('label') || this.nextElementSibling;
            if (label) {
                if (this.checked) {
                    label.classList.add('filter-selected');
                } else {
                    label.classList.remove('filter-selected');
                }
            }
        });
    });

    // Format filters
    formatRadios.forEach(radio => {
        radio.addEventListener('change', function (e) {
            console.log('Radio changed:', this.value, this.checked);
            debounceApplyFilters();
        });

        // Add visual feedback
        radio.addEventListener('change', function () {
            // Remove selected class from all format labels
            document.querySelectorAll('input[name="format"]').forEach(r => {
                const label = r.closest('label') || r.nextElementSibling;
                if (label) label.classList.remove('filter-selected');
            });

            // Add selected class to current label
            const label = this.closest('label') || this.nextElementSibling;
            if (label && this.checked) {
                label.classList.add('filter-selected');
            }
        });
    });
}

function restoreFilterStates() {
    const urlParams = new URLSearchParams(window.location.search);

    // Restore event type checkboxes
    const selectedTypes = urlParams.get('type');
    if (selectedTypes) {
        const types = selectedTypes.split(',');
        types.forEach(type => {
            const checkbox = document.querySelector(`input[name="event_type"][value="${type}"]`);
            if (checkbox) {
                checkbox.checked = true;
                const label = checkbox.closest('label') || checkbox.nextElementSibling;
                if (label) label.classList.add('filter-selected');
            }
        });
    }

    // Restore format radio
    const selectedFormat = urlParams.get('format');
    if (selectedFormat) {
        const radio = document.querySelector(`input[name="format"][value="${selectedFormat}"]`);
        if (radio) {
            radio.checked = true;
            const label = radio.closest('label') || radio.nextElementSibling;
            if (label) label.classList.add('filter-selected');
        }
    }
}

// Debounce filter application to avoid rapid URL changes
let filterTimeout;
function debounceApplyFilters() {
    clearTimeout(filterTimeout);
    filterTimeout = setTimeout(applyFilters, 300);
}

function applyFilters() {
    console.log('🔍 Applying filters...');

    const selectedTypes = Array.from(document.querySelectorAll('input[name="event_type"]:checked'))
        .map(cb => cb.value);
    const selectedFormat = document.querySelector('input[name="format"]:checked')?.value || 'all';

    console.log('📋 Selected types:', selectedTypes);
    console.log('🎛️ Selected format:', selectedFormat);

    // Build URL parameters
    const params = new URLSearchParams(window.location.search);

    // Update event types
    if (selectedTypes.length > 0) {
        params.set('type', selectedTypes.join(','));
    } else {
        params.delete('type');
    }

    // Update format
    if (selectedFormat !== 'all') {
        params.set('format', selectedFormat);
    } else {
        params.delete('format');
    }

    // Get current scroll position
    const scrollY = window.scrollY;

    // Store scroll position
    sessionStorage.setItem('eventsScrollPosition', scrollY);

    console.log('🔗 New URL params:', params.toString());
    console.log('📍 Saving scroll position:', scrollY);

    // Show loading state
    const filterElements = document.querySelectorAll('.filter-option');
    filterElements.forEach(el => {
        el.style.opacity = '0.6';
        el.style.pointerEvents = 'none';
    });

    // Reload page with new filters
    window.location.search = params.toString();
}

// Share functionality
function initShareButtons() {
    const shareButtons = document.querySelectorAll('.share-button');
    const currentUrl = window.location.href;
    const pageTitle = document.querySelector('.event-title')?.textContent || 'Play Vision Event';

    shareButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();

            if (button.classList.contains('share-button--facebook')) {
                shareOnFacebook(currentUrl);
            } else if (button.classList.contains('share-button--twitter')) {
                shareOnTwitter(currentUrl, pageTitle);
            } else if (button.classList.contains('share-button--telegram')) {
                shareOnTelegram(currentUrl, pageTitle);
            } else if (button.classList.contains('share-button--copy')) {
                copyToClipboard(currentUrl);
            }
        });
    });
}

function shareOnFacebook(url) {
    const shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
    window.open(shareUrl, '_blank', 'width=600,height=400');
}

function shareOnTwitter(url, text) {
    const shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`;
    window.open(shareUrl, '_blank', 'width=600,height=400');
}

function shareOnTelegram(url, text) {
    const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`;
    window.open(shareUrl, '_blank');
}

function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Посилання скопійовано!', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.select();

    try {
        document.execCommand('copy');
        showNotification('Посилання скопійовано!', 'success');
    } catch (err) {
        showNotification('Не вдалося скопіювати посилання', 'error');
    }

    document.body.removeChild(textArea);
}

// Event registration
function initEventRegistration() {
    const registrationForm = document.querySelector('.registration-form');
    const waitlistForm = document.querySelector('.waitlist-form');

    if (registrationForm) {
        registrationForm.addEventListener('submit', function (e) {
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.classList.add('btn--loading');
            submitButton.disabled = true;
        });
    }

    if (waitlistForm) {
        waitlistForm.addEventListener('submit', function (e) {
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.classList.add('btn--loading');
            submitButton.disabled = true;
        });
    }
}

// Notification helper
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification--${type}`;
    notification.textContent = message;

    // Add styles if not present
    if (!document.querySelector('#notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                padding: 16px 24px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 1000;
                animation: slideUp 0.3s ease;
            }
            
            .notification--success {
                background: #4CAF50;
            }
            
            .notification--error {
                background: #F44336;
            }
            
            .notification--info {
                background: #2196F3;
            }
            
            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translate(-50%, 20px);
                }
                to {
                    opacity: 1;
                    transform: translate(-50%, 0);
                }
            }
        `;
        document.head.appendChild(styles);
    }

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideDown 0.3s ease forwards';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Touch swipe support for calendar on mobile
let touchStartX = 0;
let touchEndX = 0;

function handleTouchStart(e) {
    touchStartX = e.changedTouches[0].screenX;
}

function handleTouchEnd(e) {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}

function handleSwipe() {
    const calendarGrid = document.querySelector('.calendar-grid');
    if (!calendarGrid) return;

    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            // Swipe left - scroll right
            calendarGrid.scrollBy({ left: 200, behavior: 'smooth' });
        } else {
            // Swipe right - scroll left
            calendarGrid.scrollBy({ left: -200, behavior: 'smooth' });
        }
    }
}

// Add touch listeners to calendar
const calendarGrid = document.querySelector('.calendar-grid');
if (calendarGrid) {
    calendarGrid.addEventListener('touchstart', handleTouchStart);
    calendarGrid.addEventListener('touchend', handleTouchEnd);
}

// Lazy loading for event images
const lazyImages = document.querySelectorAll('.event-image[data-src]');
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });

    lazyImages.forEach(img => imageObserver.observe(img));
} else {
    // Fallback for browsers without IntersectionObserver
    lazyImages.forEach(img => {
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
    });
}
