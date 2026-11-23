"""Скриншоты страниц ДЗ урока 50 (запуск: python make_screenshots.py).

GET-страницы снимаются headless Chrome с запущенного сервера,
POST-ответы (ошибка валидации, сообщение об успехе) рендерятся
через django.test.Client и сохраняются во временные HTML-файлы.
"""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
# django.test.Client обращается к серверу с именем хоста "testserver".
os.environ['ALLOWED_HOSTS'] = '127.0.0.1,localhost,testserver'

import django

django.setup()

from django.test import Client  # noqa: E402

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BASE = 'http://127.0.0.1:8000'
SHOTS = Path('screenshots')
SHOTS.mkdir(exist_ok=True)

# (имя файла, URL или (метод, путь, данные))
PAGES = [
    ('50-01-list.png', ('GET', '/articles/', None)),
    ('50-02-detail.png', ('GET', '/articles/1/', None)),
    ('50-03-create.png', ('GET', '/articles/new/', None)),
    ('50-04-validation.png', ('POST', '/articles/new/', {
        'title': 'abc',
        'text': 'Текст статьи для проверки валидации.',
        'category': '1',
    })),
    ('50-05-edit.png', ('GET', '/articles/1/edit/', None)),
    ('50-06-feedback.png', ('GET', '/feedback/', None)),
    ('50-07-feedback-success.png', ('POST', '/feedback/', {
        'name': 'Иван',
        'email': 'ivan@example.com',
        'message': 'Отличный блог, спасибо за уроки!',
    })),
]


def chrome_screenshot(url: str, out: Path) -> None:
    # Уникальный профиль на каждый запуск: иначе Chrome переиспользует
    # уже работающий экземпляр и скриншот уходит не на ту страницу.
    profile = Path(tempfile.mkdtemp(prefix='chrome-shot-'))
    subprocess.run([
        CHROME,
        '--headless=new',
        '--disable-gpu',
        '--hide-scrollbars',
        '--no-first-run',
        '--no-default-browser-check',
        f'--user-data-dir={profile}',
        '--force-device-scale-factor=1',
        f'--window-size=1280,1800',
        f'--screenshot={out.resolve()}',
        url,
    ], check=True, capture_output=True, timeout=60)
    shutil.rmtree(profile, ignore_errors=True)


def main() -> None:
    client = Client()
    tmp = Path(tempfile.gettempdir())
    for name, (method, path, data) in PAGES:
        out = SHOTS / name
        if method == 'GET':
            chrome_screenshot(BASE + path, out)
        else:
            # POST-ответы: редирект после успешной отправки (PRG) отслеживаем.
            response = getattr(client, method.lower())(path, data, follow=True)
            assert response.status_code == 200, (path, response.status_code)
            html_file = tmp / f'shot_{name}.html'
            html_file.write_bytes(response.content)
            chrome_screenshot(html_file.as_uri(), out)
        print('OK', out, out.stat().st_size, 'bytes')


if __name__ == '__main__':
    main()
