# DEPS

## BASE
base.html
├─ CSS: design-tokens→theme→main→utilities→animations→accessibility→mobile-bottom-nav→notifications→scroll-popup(inline)
├─ JS: theme-manager→theme-toggle→interval-manager→dom-utils→api-utils→notifications→main→cart-header(auth)→scroll-popup
├─ HTMX: 1.9.10 CDN
├─ PARTS: mobile-bottom-nav.html
└─ CTX: cart_items_count,cart_total_amount,upcoming_events_menu

## PAGES

### home.html
├─ BASE+home.css+home-additions.css
├─ JS: home.js(HeroCarousel,CoursesCarousel)
└─ PARTS: scroll-popup.html

### about.html
├─ BASE+about.css
└─ JS: about.js

### course_list.html
├─ BASE+hub.css+hub-additions.css+search.css
├─ JS: hub.js(SubscriptionBanner,MaterialsCarousel,FiltersManager,SupportWidget)+search-autocomplete.js
├─ LOAD: loyalty_filters
└─ PARTS: _monthly_quote.html

### course_detail.html
├─ BASE+hub.css+course-detail.css
└─ JS: course-detail.js

### material_detail.html
├─ BASE+hub.css+course-detail.css+material-detail.css
└─ JS: material-detail.js+material-detail-handlers.js

### cabinet.html
├─ BASE+cabinet.css+cabinet-additions.css
└─ JS: cabinet.js

### chat.html
├─ BASE+ai-chat.css
└─ JS: ai-chat.js(chat UI,send API)

### cart.html
├─ BASE+cart.css
└─ JS: cart.js

### event_detail.html
├─ BASE+events.css
└─ JS: events.js

### login.html
├─ BASE+auth.css
└─ JS: auth.js(tabs,phone input)

### register.html
├─ BASE+auth.css
└─ JS: auth.js

### pricing.html
├─ BASE+pricing.css
└─ JS: inline(form submit handlers)

## CSS DEPS
design-tokens.css: vars(colors,spacing,fonts,shadows,breakpoints)
theme.css: [data-theme=dark|light]
main.css: layout,typography,buttons,forms,cards
utilities.css: helpers,flex,grid,spacing,display
animations.css: keyframes,transitions
accessibility.css: focus,sr-only,skip-links
mobile-bottom-nav.css: bottom-nav≤768px
notifications.css: toast/alerts
scroll-popup.css: modal popup
about.css: about page
ai-chat.css: chat UI
auth.css: login/register
cabinet.css+cabinet-additions.css: user dashboard
cart.css: shopping cart
course-detail.css: course page
events.css: events
home.css+home-additions.css: homepage
hub.css+hub-additions.css: courses list
loyalty-rules.css: loyalty page
material-detail.css: material view
pricing.css: subscriptions
search.css: autocomplete
development.css: dev helpers

## JS DEPS
theme-manager.js: init theme from localStorage,read pref
theme-toggle.js: toggle btn handler,save to localStorage
interval-manager.js: cleanup intervals/timeouts,prevent leaks
dom-utils.js: DOMUtils class(sanitizeHTML,safeQuerySelector,createElement,safeClassList,isVisible,getElementSize)
api-utils.js: APIUtils class(safeFetch,retry,timeout,CSRF,get/post/put/delete,handleAPIError)
notifications.js: showNotification(msg,type,duration)→window.PlayVision
main.js: DOMContentLoaded init→initializeHTMX(CSRF,errors,afterSwap),initializePWA(SW register),initializeCart(HTMX trigger),initializeMessages(auto-close 5s),initializeProgressBars([data-progress]),initializeDropdownMenu(events dropdown),window.PlayVision={showMessage,getCookie}
cart-header.js: update cart count via HTMX trigger
scroll-popup.js: popup logic+closeScrollPopup() global
about.js: about page animations
auth.js: tabs switch(email/phone),phone input mask
cabinet.js: profile form submit,avatar upload,tabs
cabinet-handlers.js: tabs switching logic
cart.js: add/remove items HTMX,coupon apply,recommendations
course-detail.js: preview modal(20s timer),favorites HTMX,start free course
course-detail-handlers.js: HTMX handlers for course actions
events.js: event UI,share buttons,registration
home.js: HeroCarousel class(7 slides,autoplay 5s,dots),CoursesCarousel class(responsive 1-3 slides,nav buttons)
hub.js: SubscriptionBanner class(localStorage),MaterialsCarousel class(prev/next),FiltersManager class(mobile toggle,clear,auto-submit),SupportWidget class(toggle)
material-detail.js: video player controls,mark complete,preview timer
material-detail-handlers.js: progress tracking API calls
ai-chat.js: chat interface,send message API,suggested questions
pwa.js: service worker registration
search-autocomplete.js: search dropdown suggestions API

## TEMPLATES TREE
base/
  base.html: ROOT(header,footer,messages,nav,scripts,css)
pages/
  home.html→BASE
  about.html→BASE
  home_simple.html→BASE
  coming_soon.html→BASE
hub/
  course_list.html→BASE
  course_detail.html→BASE
  material_detail.html→BASE
  search_results.html→BASE
  _monthly_quote.html
account/
  cabinet.html→BASE
  tabs/(profile|subscription|files|loyalty|payments).html
  add_email.html→BASE
  verify_email_form.html→BASE
auth/
  login.html→BASE
  register.html→BASE
ai/
  chat.html→BASE
  widgets/(base|cabinet|faq|hub)_widget.html
cart/
  cart.html→BASE
events/
  event_list.html→BASE
  event_detail.html→BASE
  event_registration_form.html→BASE
partials/
  mobile-bottom-nav.html: nav links(auth check)
  scroll-popup.html: modal(sessionStorage check)
  course_card.html: reusable card
htmx/
  cart_count.html: count badge
  error.html: error display
loyalty/
  rules.html→BASE
subscriptions/
  pricing.html→BASE
pwa/
  install.html→BASE
  offline.html→BASE
admin/ai/
  load_knowledge.html
  test_ai.html

## CONTEXT PROCESSORS
cart.context_processors.cart_context→{cart_items_count,cart_total_amount}
events.context_processors.upcoming_events→{upcoming_events_menu}(7 events,published,future)

## EXTERNAL
HTMX: unpkg.com/htmx.org@1.9.10(CDN)
Icons: static/icons/*.svg|*.png(29 files)
Images: static/images/*.jpg|*.svg(17 files)
Fonts: theme.css(system fonts,no external)
SW: static/sw.js(service worker)

## TEMPLATE TAGS
content_filters: apps/content/templatetags/content_filters.py
loyalty_filters: apps/content/templatetags/loyalty_filters.py(get_item filter)

## INSTALLED APPS
Django: admin,auth,contenttypes,sessions,messages,staticfiles,sites,humanize
3rd-party: rest_framework,corsheaders,django_htmx,widget_tweaks,whitenoise
Local(13): core,accounts,subscriptions,payments,content,cart,events,loyalty,mentoring,ai,analytics,notifications,cms,video_security

## AUTH
User model: apps.accounts.User(custom)
Backends: EmailBackend,ModelBackend
Login URL: /auth/login/
Redirect: /account/
Password: min 8 chars,similarity,common,numeric validators

## CACHING
Backend: LocMemCache
Session: cached_db(30 days)
Rate limit: 5 req/min(cache-based)

## SECURITY
CSRF: HttpOnly,SameSite=Lax
Session: HttpOnly,SameSite=Lax
Headers: X-Frame-Options=DENY,X-Content-Type-Options=nosniff
Upload: 5MB limit
CORS: localhost:3000,localhost:8000

## LOAD ORDER
1. design-tokens
2. theme
3. main
4. utilities
5. animations
6. accessibility
7. component CSS
8. page CSS
9. theme-manager(FIRST!)
10. theme-toggle
11. core JS(interval,dom,api)
12. shared JS(notifications)
13. main.js
14. cart-header(auth)
15. scroll-popup
16. page JS

## KEY PATTERNS
- BASE extends: all pages inherit base.html
- CSS cascade: tokens→theme→main→component→page
- JS modules: utils first(dom,api)→shared(notifications)→main→page-specific
- JS classes: ES6 classes in hub.js,home.js,api-utils.js,dom-utils.js
- JS global: window.PlayVision,window.APIUtils,window.DOMUtils
- HTMX: cart updates,form submits,hx-post/hx-swap/hx-trigger/hx-vals
- Auth checks: {% if user.is_authenticated %} for cart,cabinet,favorites
- Lazy load: data-src for images(home.js)
- Theme: localStorage+[data-theme] attr,init before render
- Mobile: ≤768px bottom nav shows,filters collapse
- Desktop: >768px full header nav,inline filters
- Modals: preview(course-detail),progress(material-detail),scroll-popup(home)
- Forms: CSRF token via getCookie('csrftoken'),X-CSRFToken header
- Errors: try/catch→APIUtils.handleAPIError→showMessage
- Storage: localStorage(theme,banner_closed),sessionStorage(popup_dismissed)

## MIDDLEWARE
1. SecurityMiddleware(Django)
2. WhiteNoiseMiddleware(static files)
3. SessionMiddleware(Django)
4. CorsMiddleware(corsheaders)
5. CommonMiddleware(Django)
6. CsrfViewMiddleware(Django)→CSRF protection
7. AuthenticationMiddleware(Django)
8. PhoneRegistrationMiddleware(custom)→3-day phone limit check
9. MessageMiddleware(Django)
10. XFrameOptionsMiddleware(Django)
11. HtmxMiddleware(django_htmx)

## CUSTOM MIDDLEWARE(playvision/middleware.py)
SecurityHeadersMiddleware: X-Content-Type-Options,X-Frame-Options,Referrer-Policy,Permissions-Policy
NoCacheMiddleware: no-cache in DEBUG mode
BasicRateLimitMiddleware: 5 req/min for /auth/login,/auth/register,/auth/password-reset
PaywallMiddleware: check course/material access
MaintenanceMiddleware: MAINTENANCE_MODE flag
AnalyticsMiddleware: log PageView for /hub,/events,/account,/pricing
PhoneRegistrationMiddleware: 3-day expiry,email verification reminders

## CRITICAL DEPS
theme-manager MUST load before any render
design-tokens MUST load before theme
HTMX loaded in <head>
cart-header only if authenticated
notifications.css+js for all pages
PhoneRegistrationMiddleware checks auth before every request

## URL STRUCTURE
/→core:home
/about/→core:about
/hub/→content:course_list
/hub/<slug>/→content:course_detail
/hub/<course>/<material>/→content:material_detail
/events/→events:event_list
/events/<slug>/→events:event_detail
/auth/login/→accounts:login
/auth/register/→accounts:register
/account/→cabinet:dashboard
/cart/→cart:cart
/ai/→ai:chat
/pricing/→core:pricing(subscriptions)
/api/v1/accounts/→API
/api/v1/content/→API
/api/v1/cart/→API
/api/v1/notifications/→API
/htmx/→core HTMX endpoints
/htmx/cart/→cart HTMX endpoints
/video-security/→video_security

## CMS ADMIN
Django Admin→CMS:
├─ HeroSlide: image/video,title,subtitle,badge,cta(text+url),order,active
├─ PageSection: page,type,title,subtitle,bg(image+color),order,active
│  └─ SectionBlock(inline): type,title,text,image,cta,order
├─ ExpertCard: photo,name,position,specialization,bio,order,active,show_homepage
├─ HexagonItem: title,icon_svg,description,color,order,active
├─ Banner: existing(title,type,position,image,cta...)
├─ FAQ: existing(question,answer,category...)
└─ Settings: existing(key,value,type,group...)

Admin features:
- Image preview on upload(JS)
- Auto-optimization(Pillow: 1920×1080 hero, 400×400 expert, quality=85)
- Ctrl+S save, Ctrl+Enter continue
- Color picker for hexagons
- Inline editing for blocks
- List editable: order,active

CMS pages:
- home: hero_slides(1),experts(4),hexagons(6)
- about: sections(4),blocks(9),experts(shared)

## FILE COUNTS
CSS: 27(components:22,admin:1)
JS: 26(components:3,core:1,shared:1,admin:1)
Templates: 50+(base:1,pages:4,hub:5,account:7,events:3,auth:2,cart:1,ai:4,partials:3)
Icons: 29(svg:3,png:26)
Images: 17
Apps: 13(accounts,ai,analytics,cart,cms,content,core,events,loyalty,mentoring,notifications,payments,subscriptions,video_security)
CMS tables: 12(hero_slides,expert_cards,hexagon_items,page_sections,section_blocks,+7 existing)

