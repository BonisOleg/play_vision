<!-- 3183d8d3-a434-43e2-bc12-1053eee9e9e3 7b57eec9-09d6-4da0-9d2a-62d9c8da1c8c -->
# Остаточне виправлення міграції 0017

## Критична проблема

Помилка `KeyError: ('cms', 'aboutsection3')` означає, що моделі AboutSection3 та AboutSection4 **НЕ існують в Django migration state**, навіть після міграції 0007.

## Діагностика на Render (команди для terminal)

Запустіть ці команди на Render terminal ДО застосування міграції:

```bash
# 1. Перевірка що є в migration state
python manage.py shell -c "
from django.db.migrations.loader import MigrationLoader
loader = MigrationLoader(None)
state = loader.project_state(('cms', '0016_fix_experts_visibility'))
print('Models in state after 0016:')
for (app, model), _ in state.models.items():
    if app == 'cms' and 'about' in model.lower():
        print(f'  {app}.{model}')
"

# 2. Перевірка що є в БД
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE 'cms_about%'\")
print('Tables in DB:')
for row in cursor.fetchall():
    print(f'  {row[0]}')
"

# 3. Перевірка полів в таблицях
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name='cms_about_section3'\")
print('Columns in cms_about_section3:')
for row in cursor.fetchall():
    print(f'  {row[0]}')
"
```

## Правильне рішення

Міграція 0017 повинна:

### Варіант A: Якщо моделей НЕМАЄ в state (очікується)

```python
migrations.SeparateDatabaseAndState(
    state_operations=[
        # Додати моделі в state з ІСНУЮЧИМИ полями
        migrations.CreateModel(
            name='AboutSection3',
            fields=[
                # Тільки існуючі поля з БД
                ('id', ...),
                ('title_ua', ...),
                ('svg_ua_light', ...),
                # БЕЗ нових полів
            ],
        ),
        # Потім додати нові поля в state
        migrations.AddField(...),
    ],
    database_operations=[
        # Додати нові поля в БД
        migrations.AddField(...),
    ],
)
```

### Варіант B: Виправити міграцію 0007 (небезпечно)

Додати `state_operations` в 0007, але це вимагатиме `--fake` міграцій, що небезпечно.

## Новий файл міграції 0017

Після діагностики створимо правильну міграцію, яка:

1. Додасть AboutSection3/4 в migration state (якщо їх там немає)
2. Додасть нові SVG поля і в state, і в БД

## Кроки виконання

1. **Запустити діагностику** на Render terminal
2. **Надати результати** для аналізу
3. **Переписати міграцію 0017** на основі результатів
4. **Застосувати** на Render

## Альтернативне рішення (якщо нічого не працює)

Створити міграцію 0017a яка:

- Використовує `RunPython` для додавання полів через raw SQL
- Обходить Django migration state validation
- Гарантовано працює, але менш чисто

### To-dos

- [ ] Переписати 0017_add_grid_svg_fields.py з SeparateDatabaseAndState