# 📧 Налаштування Gmail для реєстрації через телефон

## Крок 1: Увімкнути 2-факторну автентифікацію

1. Перейдіть у [Google Account](https://myaccount.google.com/)
2. Оберіть **Безпека** → **2-Step Verification**
3. Увімкніть двоетапну перевірку

## Крок 2: Створити пароль додатку

1. У розділі **Безпека** оберіть **App passwords**
2. Оберіть **Mail** як тип додатку
3. Скопіюйте згенерований 16-символьний пароль

## Крок 3: Налаштувати .env файл

Створіть файл `.env` у корені проекту:

```bash
# Email settings
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App password з кроку 2
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# Other settings
SECRET_KEY=your-secret-key
DEBUG=True
```

## Крок 4: Перевірити роботу

Після налаштування система буде:
- ✅ Дозволяти реєстрацію через номер телефону
- ✅ Надавати 3-денний доступ
- ✅ Відправляти нагадування про додавання email
- ✅ Відправляти коди підтвердження на email

## Примітки

- Використовуйте **App Password**, а не звичайний пароль Gmail
- Переконайтесь, що 2FA увімкнена у вашому Google акаунті
- Коди підтвердження діють 15 хвилин
