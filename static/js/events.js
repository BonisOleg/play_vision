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

    // Set hero background image from data attribute
    initHeroBackground();

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

// Initialize hero background from data attribute
function initHeroBackground() {
    const heroSection = document.querySelector('.event-hero[data-bg-image]');
    if (heroSection) {
        const bgImage = heroSection.getAttribute('data-bg-image');
        if (bgImage) {
            heroSection.style.backgroundImage = `url('${bgImage}')`;
        }
    }
}

// Enhanced Event Calendar Component
function eventCalendar() {
    return {
        selectedType: 'all',
        selectedFormat: 'all',
        loading: false,
        currentWeekStart: new Date(),
        visibleDays: [],
        allEvents: [],

        init() {
            console.log('🗓️ Initializing enhanced event calendar...');
            this.setCurrentWeek();
            this.loadEvents();

            // Initialize sidebar on page load
            setTimeout(() => {
                this.updateSidebarEvents();
            }, 100);
        },

        get currentPeriodText() {
            const start = new Date(this.currentWeekStart);
            const end = new Date(start);
            end.setDate(start.getDate() + 6); // Fix: 6 days, not 7

            const options = { day: 'numeric', month: 'short' };
            const startStr = start.toLocaleDateString('uk-UA', options);
            const endStr = end.toLocaleDateString('uk-UA', options);

            const periodText = `${startStr} - ${endStr}`;
            console.log(`📅 Current period: ${periodText}`);
            return periodText;
        },

        setCurrentWeek() {
            const today = new Date();
            // Set to beginning of week (Monday)
            const dayOfWeek = today.getDay();
            const monday = new Date(today);
            monday.setDate(today.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1));
            monday.setHours(0, 0, 0, 0); // Reset time
            this.currentWeekStart = monday;
        },

        async loadEvents() {
            this.loading = true;
            try {
                const start = this.currentWeekStart.toISOString().split('T')[0];
                const end = new Date(this.currentWeekStart);
                end.setDate(end.getDate() + 7);
                const endStr = end.toISOString().split('T')[0];

                console.log(`📅 Loading events for: ${start} to ${endStr}`);

                const response = await fetch(`/api/events/calendar/?start=${start}&end=${endStr}&type=${this.selectedType}&format=${this.selectedFormat}`);

                if (response.ok) {
                    this.allEvents = await response.json();
                } else {
                    // Fallback to test data if API not available
                    this.allEvents = this.getTestEvents();
                }

                this.generateVisibleDays();
                this.updateSidebarEvents();
            } catch (error) {
                console.warn('📅 Using test data for calendar:', error);
                this.allEvents = this.getTestEvents();
                this.generateVisibleDays();
                this.updateSidebarEvents();
            } finally {
                this.loading = false;
            }
        },

        getTestEvents() {
            // Dynamic test data that changes based on current week
            const testEvents = [];
            const eventTemplates = [
                {
                    title: 'Форум футбольних фахівців 5',
                    type: 'forum',
                    type_display: 'ФОРУМ',
                    time: '18:00',
                    location: 'Онлайн',
                    location_short: 'Онлайн',
                    price: 1290,
                    is_free: false,
                    event_type: 'forum'
                },
                {
                    title: 'Майстер-клас xG',
                    type: 'masterclass',
                    type_display: 'МАЙСТЕР-КЛАС',
                    time: '19:00',
                    location: 'Онлайн',
                    location_short: 'Онлайн',
                    price: 890,
                    is_free: false,
                    event_type: 'masterclass'
                },
                {
                    title: 'Круглий стіл: Академії',
                    type: 'seminar',
                    type_display: 'СЕМІНАР',
                    time: '12:00',
                    location: 'Онлайн',
                    location_short: 'Онлайн',
                    price: 0,
                    is_free: true,
                    event_type: 'seminar'
                },
                {
                    title: 'Аналіз тактики',
                    type: 'seminar',
                    type_display: 'СЕМІНАР',
                    time: '14:00',
                    location: 'Онлайн',
                    location_short: 'Онлайн',
                    price: 450,
                    is_free: false,
                    event_type: 'seminar'
                },
                {
                    title: 'Лекція психології',
                    type: 'workshop',
                    type_display: 'ВОРКШОП',
                    time: '16:00',
                    location: 'Київ',
                    location_short: 'Київ',
                    price: 500,
                    is_free: false,
                    event_type: 'workshop'
                },
                {
                    title: 'Тренінг для тренерів',
                    type: 'masterclass',
                    type_display: 'МАЙСТЕР-КЛАС',
                    time: '10:00',
                    location: 'Львів',
                    location_short: 'Львів',
                    price: 750,
                    is_free: false,
                    event_type: 'masterclass'
                }
            ];

            console.log(`🎯 Generating events for week starting: ${this.currentWeekStart.toDateString()}`);

            // Create a week identifier to ensure consistent event generation
            const weekStart = new Date(this.currentWeekStart);
            const weekId = Math.floor(weekStart.getTime() / (7 * 24 * 60 * 60 * 1000));

            // Distribute events across the week dynamically but consistently
            for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
                const eventDate = new Date(this.currentWeekStart);
                eventDate.setDate(this.currentWeekStart.getDate() + dayIndex);
                eventDate.setHours(0, 0, 0, 0); // Reset time to start of day

                const dayOfWeek = eventDate.getDay();
                let eventsToAdd = [];

                // Use week + day as seed for consistent randomization
                const seed = (weekId + dayIndex) % 100;

                // Monday, Wednesday, Friday - more events (2-3)
                if (dayOfWeek === 1 || dayOfWeek === 3 || dayOfWeek === 5) {
                    const eventCount = (seed % 2) + 2; // 2 or 3 events
                    for (let i = 0; i < eventCount; i++) {
                        const templateIndex = (dayIndex + i + weekId) % eventTemplates.length;
                        eventsToAdd.push(templateIndex);
                    }
                }
                // Tuesday, Thursday - moderate events (1-2)  
                else if (dayOfWeek === 2 || dayOfWeek === 4) {
                    const eventCount = (seed % 2) + 1; // 1 or 2 events
                    for (let i = 0; i < eventCount; i++) {
                        const templateIndex = (dayIndex + i + weekId) % eventTemplates.length;
                        eventsToAdd.push(templateIndex);
                    }
                }
                // Saturday - 1 event sometimes
                else if (dayOfWeek === 6) {
                    if (seed % 3 === 0) { // Every 3rd week roughly
                        const templateIndex = (dayIndex + weekId) % eventTemplates.length;
                        eventsToAdd.push(templateIndex);
                    }
                }
                // Sunday - no events usually

                // Generate actual events
                eventsToAdd.forEach((templateIndex, eventIndex) => {
                    const template = eventTemplates[templateIndex];
                    const eventDateTime = new Date(eventDate);

                    // Set event time from template
                    const [hours, minutes] = template.time.split(':');
                    eventDateTime.setHours(parseInt(hours), parseInt(minutes), 0, 0);

                    testEvents.push({
                        ...template,
                        id: `test_${weekId}_${dayIndex}_${eventIndex}`,
                        start_datetime: eventDateTime.toISOString(),
                        available_tickets: template.is_free ? null : Math.floor(15 + (seed % 40)), // 15-55 tickets
                        url: '#', // Safe placeholder URL for test events
                        is_test_event: true
                    });

                    console.log(`📅 Added event: ${template.title} on ${eventDate.toDateString()} at ${template.time}`);
                });
            }

            console.log(`🎯 Generated ${testEvents.length} total events for this week`);
            return testEvents;
        },

        generateVisibleDays() {
            this.visibleDays = [];
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            console.log(`🗓️ Generating visible days for week: ${this.currentWeekStart.toDateString()}`);
            console.log(`📋 Total events available: ${this.allEvents.length}`);

            for (let i = 0; i < 7; i++) { // Show only 7 days (1 week)
                const date = new Date(this.currentWeekStart);
                date.setDate(this.currentWeekStart.getDate() + i);
                date.setHours(0, 0, 0, 0);

                // Find events for this specific date (ОБМЕЖЕННЯ: ТІЛЬКИ 1 ПОДІЯ)
                const dayEvents = this.allEvents.filter(event => {
                    const eventDate = new Date(event.start_datetime);
                    eventDate.setHours(0, 0, 0, 0);
                    const match = eventDate.getTime() === date.getTime();

                    if (match) {
                        console.log(`🎯 Found event "${event.title}" for ${date.toDateString()}`);
                    }

                    return match;
                }).slice(0, 1);

                // Apply filters
                const filteredEvents = dayEvents.filter(event => {
                    // Type filter
                    if (this.selectedType !== 'all' && event.event_type !== this.selectedType) {
                        console.log(`❌ Event "${event.title}" filtered out by type: ${event.event_type} !== ${this.selectedType}`);
                        return false;
                    }

                    // Format filter
                    if (this.selectedFormat !== 'all') {
                        const isOnline = event.location === 'Онлайн' ||
                            event.location.toLowerCase().includes('онлайн') ||
                            event.location_short === 'Онлайн';

                        if (this.selectedFormat === 'online' && !isOnline) {
                            console.log(`❌ Event "${event.title}" filtered out - not online`);
                            return false;
                        }
                        if (this.selectedFormat === 'offline' && isOnline) {
                            console.log(`❌ Event "${event.title}" filtered out - not offline`);
                            return false;
                        }
                    }

                    return true;
                });

                // Sort events by time
                filteredEvents.sort((a, b) => {
                    const timeA = a.start_datetime ? new Date(a.start_datetime) : new Date();
                    const timeB = b.start_datetime ? new Date(b.start_datetime) : new Date();
                    return timeA - timeB;
                });

                const dayNames = ['Нд', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];

                const dayData = {
                    date: date.toISOString().split('T')[0],
                    dayNumber: date.getDate(),
                    dayName: dayNames[date.getDay()],
                    events: filteredEvents,
                    isToday: date.getTime() === today.getTime(),
                    isPast: date.getTime() < today.getTime(),
                    isWeekend: date.getDay() === 0 || date.getDay() === 6
                };

                console.log(`📅 Day ${dayData.dayNumber} ${dayData.dayName}: ${filteredEvents.length} events`);
                filteredEvents.forEach((event, index) => {
                    console.log(`  ${index + 1}. ${event.title} at ${event.time}`);
                });

                this.visibleDays.push(dayData);
            }

            console.log(`✅ Generated ${this.visibleDays.length} visible days`);
        },

        async filterEvents() {
            console.log(`🔍 Filtering events: type=${this.selectedType}, format=${this.selectedFormat}`);
            await this.loadEvents();
        },

        resetFilters() {
            console.log('🔄 Resetting filters');
            this.selectedType = 'all';
            this.selectedFormat = 'all';
            this.filterEvents();
        },

        previousWeek() {
            console.log('📅 Previous week clicked');
            const newWeekStart = new Date(this.currentWeekStart);
            newWeekStart.setDate(newWeekStart.getDate() - 7);
            this.currentWeekStart = newWeekStart;
            this.loadEvents();
            this.updateSidebarEvents();
        },

        nextWeek() {
            console.log('📅 Next week clicked');
            const newWeekStart = new Date(this.currentWeekStart);
            newWeekStart.setDate(newWeekStart.getDate() + 7);
            this.currentWeekStart = newWeekStart;
            this.loadEvents();
            this.updateSidebarEvents();
        },

        goToToday() {
            console.log('📅 Go to today clicked');
            this.setCurrentWeek();
            this.loadEvents();
            this.updateSidebarEvents();
        },

        updateSidebarEvents() {
            // Get upcoming events from current week and sort by date
            const now = new Date();
            const upcomingEvents = this.allEvents
                .filter(event => {
                    const eventDate = new Date(event.start_datetime);
                    return eventDate >= now;
                })
                .sort((a, b) => new Date(a.start_datetime) - new Date(b.start_datetime))
                .slice(0, 6); // Show max 6 events

            console.log(`📋 Updating sidebar with ${upcomingEvents.length} upcoming events`);

            // Format events for display
            const formattedEvents = upcomingEvents.map(event => {
                const eventDate = new Date(event.start_datetime);
                const formatted_date = eventDate.toLocaleDateString('uk-UA', {
                    day: 'numeric',
                    month: 'short'
                });

                return {
                    ...event,
                    formatted_date: formatted_date
                };
            });

            // Update sidebar container with new HTML
            const sidebarContainer = document.querySelector('.upcoming-events');
            if (sidebarContainer) {
                if (formattedEvents.length > 0) {
                    sidebarContainer.innerHTML = formattedEvents.map(event => `
                        <li class="upcoming-event">
                            <a href="${event.is_test_event ? '#' : (event.url || '#')}" 
                               onclick="${event.is_test_event ? 'return false;' : ''}"
                               class="upcoming-link ${event.is_test_event ? 'upcoming-link--demo' : ''}">
                                <div class="upcoming-event-info">
                                    <h4 class="upcoming-event-title">
                                        ${event.is_test_event ? '🎯 ' : ''}${event.title}
                                    </h4>
                                    <p class="upcoming-event-meta">
                                        ${event.formatted_date} • ${event.time}
                                        ${event.is_test_event ? ' • ДЕМО' : ''}
                                    </p>
                                </div>
                                <div class="upcoming-event-badge">
                                    <span class="event-badge ${event.location_short === 'Онлайн' ? 'event-badge--online' : 'event-badge--offline'
                        } ${event.is_free ? 'event-badge--free' : ''}">
                                        ${event.is_free ? 'безкоштовно' : (event.location_short === 'Онлайн' ? 'онлайн' : 'офлайн')}
                                    </span>
                                    ${!event.is_free ? `<span class="event-price">${event.price}₴</span>` : ''}
                                </div>
                            </a>
                        </li>
                    `).join('');
                } else {
                    sidebarContainer.innerHTML = `
                        <li class="no-upcoming-events">
                            <p>Найближчих подій немає</p>
                        </li>
                    `;
                }
            }
        },

        showEventPreview(event) {
            console.log('Show event preview:', event);
            // Could show tooltip or preview popup
        },

        hideEventPreview() {
            // Hide preview popup
        },

        showAllDayEvents(day) {
            console.log('Show all events for day:', day);
            // Could open modal with all day events
        },

        showTestEventInfo(event) {
            // Show info about test event
            const eventDate = new Date(event.start_datetime);
            const formattedDate = eventDate.toLocaleDateString('uk-UA', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });

            const message = `
🎯 ДЕМО ПОДІЯ

📅 ${event.title}
🗓️ ${formattedDate} о ${event.time}
📍 ${event.location}
💰 ${event.is_free ? 'Безкоштовно' : event.price + '₴'}

Це демонстраційна подія для прикладу роботи календаря.
Реальні події будуть доступні після створення в адмін-панелі.
            `;

            alert(message);
            console.log('📍 Demo event clicked:', event);
        },

        selectDay(day, index) {
            console.log('📅 Selected day:', day.displayTitle, 'Events:', day.events.length);

            // Remove active class from all days
            this.visibleDays.forEach(d => d.isActive = false);

            // Set selected day as active
            day.isActive = true;

            // If day has only one event, navigate directly
            if (day.events.length === 1) {
                window.location.href = day.events[0].url;
            }
        }
    };
}

// Enhanced Event Filters Component
function eventFilters() {
    return {
        searchTerm: '',

        init() {
            console.log('🔍 Initializing event filters...');
        },

        hasActiveFilters() {
            // Check if any filters are active
            const form = this.$el;
            const searchInput = form.querySelector('input[name="search"]');
            const checkboxes = form.querySelectorAll('input[type="checkbox"]:checked');
            const radios = form.querySelectorAll('input[type="radio"]:checked');

            // Check search
            if (searchInput && searchInput.value.trim()) {
                return true;
            }

            // Check event type checkboxes
            if (checkboxes.length > 0) {
                return true;
            }

            // Check non-default radio selections
            const activeRadios = Array.from(radios).filter(radio =>
                radio.value !== 'all' && radio.checked
            );

            return activeRadios.length > 0;
        },

        clearSearch() {
            const searchInput = this.$el.querySelector('input[name="search"]');
            if (searchInput) {
                searchInput.value = '';
                this.submitForm();
            }
        },

        clearFilter(filterName, filterValue) {
            const input = this.$el.querySelector(`input[name="${filterName}"][value="${filterValue}"]`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = false;
                } else if (input.type === 'radio') {
                    // Set back to default 'all' option
                    const defaultOption = this.$el.querySelector(`input[name="${filterName}"][value="all"]`);
                    if (defaultOption) {
                        defaultOption.checked = true;
                    }
                }
                this.submitForm();
            }
        },

        submitForm() {
            this.$el.submit();
        }
    };
}

// Calendar functionality
function initCalendar() {
    const calendarDays = document.querySelectorAll('.calendar-day');

    console.log('Found calendar days:', calendarDays.length);

    calendarDays.forEach((day, index) => {
        // Use click with debouncing to prevent double execution
        let isHandled = false;

        day.addEventListener('click', function (e) {
            if (isHandled) return;
            isHandled = true;

            // Reset flag after short delay
            setTimeout(() => { isHandled = false; }, 300);

            handleCalendarDayClick(this, index, e);
        });

        // Prevent touchend conflicts on mobile
        day.addEventListener('touchend', function (e) {
            e.preventDefault(); // Prevent click event firing after touchend
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

                    // Direct navigation without delay to prevent conflicts
                    window.location.href = eventCard.href;
                } else {
                    console.log('⚠️ No valid link found for event');
                }
            }
        } else {
            console.log('⚠️ No event card found in day');
        }
    }

    // Auto-scroll to active day on load (only if not visible)
    const activeDay = document.querySelector('.calendar-day--active');
    if (activeDay) {
        const rect = activeDay.getBoundingClientRect();
        const isVisible = rect.top >= 0 && rect.left >= 0 &&
            rect.bottom <= window.innerHeight &&
            rect.right <= window.innerWidth;

        if (!isVisible) {
            // Use requestAnimationFrame to prevent layout conflicts
            requestAnimationFrame(() => {
                activeDay.scrollIntoView({
                    behavior: 'smooth',
                    inline: 'center',
                    block: 'nearest'
                });
            });
        }
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
    // Використовуємо нову централізовану систему якщо доступна
    if (window.notify && typeof window.notify.show === 'function') {
        return window.notify.show(message, type, 3000);
    }

    // Fallback на стару систему (для сумісності)
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
