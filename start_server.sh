#!/bin/bash

# Змінні оточення для розробки
export SECRET_KEY='django-insecure-temp-key-for-development'
export DEBUG=True
export DJANGO_ENV=development

# Активація віртуального середовища
source venv/bin/activate

# Запуск сервера
python3 manage.py runserver
