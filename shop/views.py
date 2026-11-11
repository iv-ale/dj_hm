from django.http import HttpResponse
from django.utils.html import escape


def _page(title: str, content: str) -> HttpResponse:
    """Собирает простую HTML-страницу с общим меню.

    Пока это HttpResponse, как требует уровень 1: шаблоны появятся позже.
    """
    return HttpResponse(
        f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(title)} | Магазин</title>
    <style>
        body {{ font-family: system-ui, sans-serif; max-width: 720px;
                margin: 40px auto; padding: 0 16px; line-height: 1.6;
                color: #1f2933; background: #f7f9fb; }}
        nav a {{ margin-right: 16px; color: #0b5fff; text-decoration: none; }}
        nav a:hover {{ text-decoration: underline; }}
        h1 {{ margin-bottom: 8px; }}
        table {{ border-collapse: collapse; margin-top: 16px; }}
        th, td {{ border: 1px solid #cbd2d9; padding: 8px 16px; text-align: left; }}
        th {{ background: #e4e7eb; }}
        footer {{ margin-top: 32px; color: #7b8794; font-size: 14px; }}
    </style>
</head>
<body>
    <nav>
        <a href="/">Главная</a>
        <a href="/about/">О проекте</a>
        <a href="/contacts/">Контакты</a>
    </nav>
    <h1>{escape(title)}</h1>
    {content}
    <footer>Учебный проект по Django · урок 45</footer>
</body>
</html>""",
        content_type="text/html; charset=utf-8",
    )


def home(request):
    """Главная страница: /"""
    return _page(
        "Главная",
        "<p>Это учебный сайт-магазин, созданный на Django.</p>"
        "<p>Здесь мы учимся запускать сервер, настраивать маршруты "
        "и возвращать ответы из представлений.</p>",
    )


def about(request):
    """Страница о проекте: /about/"""
    return _page(
        "О проекте",
        "<p>Проект сделан в рамках домашнего задания урока 45 "
        "«Запуск и базовая настройка первого сервера».</p>"
        "<p>Цель — разобраться, как Django сопоставляет адреса с функциями-"
        "представлениями и как работают динамические маршруты.</p>",
    )


def contacts(request):
    """Страница контактов: /contacts/"""
    return _page(
        "Контакты",
        "<p>Связаться с автором проекта можно так:</p>"
        "<ul>"
        "<li>Email: student@example.com</li>"
        "<li>Телефон: +998 90 123-45-67</li>"
        "<li>Город: Ташкент</li>"
        "</ul>",
    )


def hello(request, name):
    """Динамический маршрут: /hello/<name>/"""
    return _page(
        "Приветствие",
        f"<p>Привет, {escape(name)}!</p>",
    )


def calc(request, a, b):
    """Динамический маршрут: /calc/<int:a>/<int:b>/"""
    rows = (
        ("Сумма", a + b, f"{a} + {b}"),
        ("Разность", a - b, f"{a} − {b}"),
        ("Произведение", a * b, f"{a} × {b}"),
    )
    table = "".join(
        f"<tr><th>{label}</th><td>{expression} = {result}</td></tr>"
        for label, result, expression in rows
    )
    return _page(
        f"Калькулятор: {a} и {b}",
        f"<table>{table}</table>",
    )
