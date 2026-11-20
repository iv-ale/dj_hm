"""Демо-данные: категории и статьи для урока 49.

Запускается автоматически при python manage.py migrate, поэтому после
клонирования репозитория список статей не пустой.
"""
from django.db import migrations

CATEGORIES = [
    ('Django', 'django'),
    ('Python', 'python'),
    ('Вёрстка', 'layout'),
]

# (заголовок, категория-слаг, текст)
ARTICLES = [
    (
        'Маршрутизация в Django: как работают URL',
        'django',
        'Django сопоставляет адреса с представлениями через urlpatterns. '
        'Каждый path() задаёт шаблон адреса, имя маршрута и функцию или '
        'класс, которая вернёт ответ. Имя маршрута позволяет ссылаться на '
        'адрес из шаблонов через тег {% url %}, не зашивая строку вручную.',
    ),
    (
        'Представления Views: функции и классы',
        'django',
        'View принимает HttpRequest и возвращает HttpResponse. Функциональные '
        'представления просты и читаемы, классовые (ListView, DetailView) '
        'удобны, когда нужна типовая логика: список, детальная страница, '
        'пагинация и фильтрация через переопределение get_queryset.',
    ),
    (
        'Конвертеры путей int, str и slug',
        'django',
        'Специальные конструкции в адресе <int:pk>, <str:name>, <slug:slug> '
        'проверяют и преобразуют часть URL. Если значение не подходит под '
        'конвертер, маршрут не совпадает, и Django возвращает 404 — '
        'дополнительная проверка не нужна.',
    ),
    (
        'get_object_or_404: короткий путь к 404',
        'django',
        'Хелпер get_object_or_404(Model, pk=pk) делает get() и поднимает '
        'Http404, если объекта нет. Это заменяет проверку if obj is None '
        'и делает код представления короче и безопаснее.',
    ),
    (
        'Функции и области видимости в Python',
        'python',
        'Функция определяется через def, аргументы передаются позиционно или '
        'по имени. Локальные переменные не видны снаружи, глобальные '
        'читаются, но для изменения требуют объявления global. Правильная '
        'область видимости — половина успеха при рефакторинге.',
    ),
    (
        'Словари, списки и кортежи на практике',
        'python',
        'Список — упорядоченная изменяемая коллекция, кортеж — '
        'неизменяемая, словарь — пары ключ: значение. Выбор структуры '
        'зависит от задачи: индексы и порядок — список, быстрый доступ по '
        'ключу — словарь, фиксированный набор полей — кортеж.',
    ),
    (
        'Теги шаблонов Django: url, for и if',
        'django',
        'Шаблоны Django содержат теги {% url %}, {% for %}, {% if %} и '
        'фильтры вида {{ value|upper }}. Тег url с именем маршрута '
        'подставляет адрес по имени: переименуйте маршрут в одном '
        'месте — и все ссылки обновятся сами.',
    ),
    (
        'Пагинация в ListView: paginate_by',
        'django',
        'Аргумент paginate_by = 5 режет queryset на страницы по 5 объектов. '
        'В шаблоне доступны page_obj, is_paginated и paginator — остальное '
        'Django берёт на себя: номера страниц, проверку выхода за границы '
        'и ссылки «Назад»/«Вперёд».',
    ),
    (
        'Flexbox: основные свойства для вёрстки',
        'layout',
        'Контейнеру задаётся display: flex, направление — flex-direction, '
        'выравнивание по поперечной оси — align-items. Свойство gap '
        'заменяет отступы между элементами, а flex: 1 позволяет блоку '
        'занимать всё оставшееся место.',
    ),
    (
        'Адаптивность: медиазапросы без боли',
        'layout',
        'Медиазапрос @media (max-width: 768px) применяет стили на узких '
        'экранах. Начинайте с мобильной вёрстки и добавляйте правила для '
        'десктопа — так проще, чем ломать готовый десктоп под телефон.',
    ),
]


def seed(apps, schema_editor):
    Category = apps.get_model('articles', 'Category')
    Article = apps.get_model('articles', 'Article')

    categories = {}
    for name, slug in CATEGORIES:
        category, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name})
        categories[slug] = category

    for title, slug, text in ARTICLES:
        Article.objects.get_or_create(
            title=title,
            defaults={'text': text, 'category': categories[slug]},
        )


def unseed(apps, schema_editor):
    Category = apps.get_model('articles', 'Category')
    Article = apps.get_model('articles', 'Article')
    Article.objects.filter(title__in=[title for title, _, _ in ARTICLES]).delete()
    Category.objects.filter(slug__in=[slug for _, slug in CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
