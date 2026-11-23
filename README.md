# Django-проект `config` — урок 45 «Запуск и базовая настройка первого сервера»

Учебный проект по Django. Внутри — проект `config` и приложения:
`articles` (уроки 49–50), `shop` (урок 45), `books` (админка библиотеки),
`blog` и `users` (из урока 44).

## Урок 50 — Работа с шаблонами и формами

* `templates/base.html` — общий каркас (шапка с меню, подвал, сообщения
  `messages`), все страницы блога наследуют его;
* дата статьи `|date:"d.m.Y"` и превью `|truncatewords:20`;
* создание `/articles/new/` и редактирование `/articles/<id>/edit/` через
  `ArticleForm(ModelForm)` с валидацией `clean_title` (заголовок ≥ 5 символов,
  ошибки выводятся под полем);
* челлендж: форма обратной связи `/feedback/` (`forms.Form`), модель
  `Feedback`, `django.contrib.messages` и Bootstrap 5 через CDN.

Подробности и критерии — в `Отчёт_ДЗ_Шаблоны_и_Формы.md`.

| Список и статья | Форма и валидация |
|---|---|
| ![Список](screenshots/50-01-list.png) | ![Создание](screenshots/50-03-create.png) |
| ![Статья](screenshots/50-02-detail.png) | ![Валидация](screenshots/50-04-validation.png) |

| Редактирование | Обратная связь и успех |
|---|---|
| ![Редактирование](screenshots/50-05-edit.png) | ![Feedback](screenshots/50-06-feedback.png) |
| | ![Успех](screenshots/50-07-feedback-success.png) |

## Урок 49 — Маршрутизация (URLs) и логика представлений (Views)

Приложение `articles`: модели `Article` и `Category` (ForeignKey),
маршруты `/articles/`, `/articles/<int:id>/`, `/category/<slug:slug>/`.

* список и детальная страница — `ListView` и `DetailView`, пагинация по 5;
* поиск по заголовку `/articles/?q=django`;
* 404 для несуществующей статьи — через `get_object_or_404`;
* все ссылки в шаблонах — только через `{% url %}`.

Подробности и критерии — в `Отчёт_ДЗ_Маршрутизация_Views.md`.

| Список и поиск | Статья и 404 |
|---|---|
| ![Список](screenshots/49-01-list.png) | ![Статья](screenshots/49-03-detail.png) |
| ![Поиск](screenshots/49-02-search.png) | ![404](screenshots/49-04-404.png) |


Что сделано по заданию:

* запущен сервер разработки, выполнены миграции, создан суперпользователь;
* три статические страницы на `HttpResponse`: `/`, `/about/`, `/contacts/`;
* два динамических маршрута: `/hello/<name>/` и `/calc/<int:a>/<int:b>/`;
* `SECRET_KEY`, `DEBUG` и `ALLOWED_HOSTS` вынесены в `.env`, добавлен `.env.example`;
* своя страница 404 через `templates/404.html` при `DEBUG=False`;
* сервер проверен с телефона в той же Wi-Fi сети (`runserver 0.0.0.0:8000`).

## Быстрый старт

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 2. Зависимости
pip install -r requirements.txt

# 3. Локальные настройки: скопировать шаблон и подставить свои значения
copy .env.example .env         # Windows
# cp .env.example .env         # macOS / Linux

# 4. База данных и администратор
python manage.py migrate
python manage.py createsuperuser

# 5. Сервер
python manage.py runserver
```

После запуска:

| Адрес | Что показывает |
|-------|----------------|
| http://127.0.0.1:8000/ | главная страница |
| http://127.0.0.1:8000/about/ | о проекте |
| http://127.0.0.1:8000/contacts/ | контакты |
| http://127.0.0.1:8000/hello/Азиз/ | «Привет, Азиз!» |
| http://127.0.0.1:8000/calc/7/3/ | сумма, разность, произведение |
| http://127.0.0.1:8000/admin/ | админка Django |

## Скриншоты

| Главная | О проекте |
|---|---|
| ![Главная](screenshots/01-home.jpg) | ![О проекте](screenshots/02-about.jpg) |

| Контакты | `/hello/<name>/` |
|---|---|
| ![Контакты](screenshots/03-contacts.jpg) | ![Приветствие](screenshots/04-hello.jpg) |

| `/calc/<int:a>/<int:b>/` | Админка |
|---|---|
| ![Калькулятор](screenshots/05-calc.jpg) | ![Админка](screenshots/06-admin.png) |

| Своя страница 404 | Сайт с телефона (эмуляция узкого экрана) |
|---|---|
| ![404](screenshots/07-404.png) | ![Мобильный вид](screenshots/08-mobile-emulation.png) |

## Как устроены маршруты

`config/urls.py` подключает маршруты приложения `shop` от корня сайта:

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("shop.urls")),
]
```

`include()` передаёт управление в `shop/urls.py`, поэтому адреса приложения
не нужно повторять в главном файле маршрутов:

```python
urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contacts/", views.contacts, name="contacts"),
    path("hello/<str:name>/", views.hello, name="hello"),
    path("calc/<int:a>/<int:b>/", views.calc, name="calc"),
]
```

* `<str:name>` — конвертер `str`: принимает любую строку без `/` и передаёт её
  в представление аргументом `name`;
* `<int:a>`, `<int:b>` — конвертер `int`: принимает только целые числа.
  Для `/calc/seven/3/` маршрут не совпадёт, и Django вернёт 404.

Представления лежат в `shop/views.py`. Страницы пока собираются в `HttpResponse`
(как требует уровень 1), а имя из адреса экранируется через
`django.utils.html.escape`, чтобы вставленный в URL HTML не попал на страницу
как разметка.

## Секреты в `.env`

`SECRET_KEY` — ключ подписи cookie и токенов, `DEBUG` — режим отладки. Их нельзя
хранить в репозитории, поэтому значения лежат в файле `.env`:

```
SECRET_KEY=...
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,192.168.1.10
```

* `.env` указан в `.gitignore` и в git не попадает;
* `.env.example` — шаблон без секретов, его коммитим, чтобы другой разработчик
  знал, какие переменные нужны;
* в `.gitignore` после правила `.env.*` стоит исключение `!.env.example`,
  иначе шаблон тоже был бы проигнорирован.

В `config/settings.py` файл читается библиотекой `python-dotenv`:

```python
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-change-me-in-dot-env-file")
DEBUG = os.getenv("DEBUG", "False").strip().lower() in {"1", "true", "yes", "on"}
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "127.0.0.1,localhost")
```

`DEBUG` сравнивается со строкой, потому что переменные окружения — всегда строки:
`"True"` превращается в `True`, `"False"` — в `False`. `ALLOWED_HOSTS` читается
как список через запятую.

## Своя страница 404

1. В `.env` ставим `DEBUG=False` (в боевом режиме Django не показывает отладочную
   страницу, а ищет шаблон `404.html`);
2. в `settings.py` добавлен каталог шаблонов `BASE_DIR / "templates"`;
3. файл `templates/404.html` — своя страница с кодом 404 и ссылкой на главную.

При `DEBUG=False` статические файлы админки сервер разработки не отдаёт. Чтобы
посмотреть админку со стилями в таком режиме, запускайте
`python manage.py runserver --insecure`.

## Доступ с телефона по Wi-Fi

```bash
python manage.py runserver 0.0.0.0:8000
```

* `0.0.0.0` — слушать все сетевые интерфейсы, а не только `127.0.0.1`;
* в `ALLOWED_HOSTS` нужно добавить IP компьютера в локальной сети
  (узнать: `ipconfig`), иначе Django ответит `400 Bad Request`;
* на телефоне открываем `http://<IP-компьютера>:8000/`;
* если страница не открывается — разрешить Python в брандмауэре Windows для
  частных сетей.

Скриншот `08-mobile-emulation.png` сделан в браузере с эмуляцией экрана телефона
по адресу `http://10.85.250.187:8000/` — это проверка того, что сервер доступен
не только с `localhost`. Настоящее фото экрана телефона нужно приложить отдельно.

## Тесты

```bash
python manage.py test shop
```

Проверяются все страницы, динамические маршруты (включая 404 для нечисловых
аргументов) и своя страница 404 при `DEBUG=False`.

## Структура проекта

```
config/                 # проект целиком
├── manage.py
├── config/
│   ├── settings.py     # настройки: приложения, БД, .env, шаблоны, язык
│   └── urls.py         # корневые маршруты, подключает shop.urls
├── shop/               # приложение урока 45
│   ├── views.py        # home, about, contacts, hello, calc
│   ├── urls.py         # маршруты приложения
│   └── tests.py        # тесты страниц и 404
├── blog/               # приложение из урока 44
├── users/              # приложение из урока 44
├── templates/
│   └── 404.html        # своя страница ошибки 404
├── screenshots/        # скриншоты для сдачи
├── .env.example        # шаблон переменных окружения (без секретов)
└── requirements.txt
```

## Чек-лист по критериям

* миграции, админ и три страницы — 3 балла;
* динамические маршруты `/hello/<name>/` и `/calc/<int:a>/<int:b>/` — 3 балла;
* `.env`, `.env.example`, `.gitignore` и чтение настроек из окружения — 2 балла;
* челлендж: своя 404 и запуск с телефона по Wi-Fi — 2 балла.
