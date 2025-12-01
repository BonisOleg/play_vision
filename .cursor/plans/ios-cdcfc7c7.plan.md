<!-- cdcfc7c7-021b-4caf-99a3-4541c3fcedb2 231dc026-5da3-41c9-b8e3-42b1126334b5 -->
# Виправлення Hero блоку та Footer для OPPO (обережний підхід)

## Важливе уточнення

Оскільки на інших мобільних пристроях Hero працює добре, використовуємо **мінімальні зміни**, які:

- Виправлять проблему на OPPO
- **НЕ змінять** iPhone та інші Android (де все працює)
- **НЕ зламають** десктоп

## Точне рішення

### Зміна 1: Мінімальний padding-bottom тільки для OPPO (safe-area = 0)

**Файл:** [`static/css/components/home.css`](static/css/components/home.css)

**Рядок 112** - замінити padding-bottom:

```css
/* БУЛО */
calc(var(--spacing-md) + env(safe-area-inset-bottom, 0px))

/* СТАНЕ - додаємо мінімум 8px ТІЛЬКИ якщо safe-area = 0 (OPPO) */
calc(var(--spacing-md) + max(env(safe-area-inset-bottom, 0px), 8px))
```

**Чому це безпечно:**

- На iPhone: `env(safe-area-inset-bottom) ≈ 20-34px`, тому `max(20px, 8px) = 20px` - **НЕ ЗМІНЮЄТЬСЯ**
- На інших Android з safe-area > 8px - також не змінюється
- На OPPO (safe-area = 0): `max(0px, 8px) = 8px` - додає 8px, **виправляє проблему**

### Зміна 2: Дозволити перенос email тільки коли не вміщається

**Файл:** [`static/css/components/footer.css`](static/css/components/footer.css)

**В `@media (max-width: 767px)`** (рядок 444-450) - замінити:

```css
/* БУЛО */
footer.site-footer .contact-item {
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    gap: 4px;
    width: auto;
}

/* СТАНЕ - дозволяємо перенос тільки якщо не вміщається */
footer.site-footer .contact-item {
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    gap: 4px;
    width: auto;
    flex-wrap: wrap; /* Переносить тільки якщо не вміщається */
    min-width: 0; /* Дозволяє стискатися */
}

footer.site-footer .contact-link {
    word-break: break-word; /* М'який перенос */
    overflow-wrap: break-word;
    min-width: 0;
}
```

**Чому це безпечно:**

- `flex-wrap: wrap` - переносить **тільки якщо не вміщається**
- На пристроях де email вміщається (iPhone, інші Android) - залишається в один рядок
- На OPPO де не вміщається - переноситься, **виправляє проблему**

## Гарантії безпечності

### Hero блок:

1. ✅ **iPhone**: `max(20px, 8px) = 20px` - значення не змінюється
2. ✅ **Інші Android з safe-area > 8px**: також не змінюється
3. ✅ **OPPO (safe-area = 0)**: додається 8px - виправляє проблему
4. ✅ **Десктоп**: медіа-запит не спрацює

### Footer:

1. ✅ **Пристрої де email вміщається**: `flex-wrap: wrap` не активується, залишається в один рядок
2. ✅ **OPPO де не вміщається**: переноситься - виправляє проблему
3. ✅ **Десктоп**: медіа-запит не спрацює

## Файли для редагування

- [`static/css/components/home.css`](static/css/components/home.css) - рядок 112
- [`static/css/components/footer.css`](static/css/components/footer.css) - рядки 444-450

## Очікуваний результат

- **OPPO Hero**: +8px padding-bottom (виправляє проблему)
- **OPPO Footer**: email переноситься (виправляє проблему)
- **Інші пристрої**: **НЕ ЗМІНЮЮТЬСЯ** (iPhone, інші Android, десктоп)