from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import ArticleForm, FeedbackForm
from .models import Article, Category, Feedback

BASE_DIR = Path(__file__).resolve().parent.parent


class ArticleFixtureMixin:
    """Общие данные: 6 статей в 2 категориях (для пагинации нужно > 5)."""

    @classmethod
    def setUpTestData(cls):
        # Тестовая БД создаётся из миграций, включая seed с демо-статьями:
        # очищаем таблицы, чтобы проверки были детерминированными.
        Article.objects.all().delete()
        Category.objects.all().delete()
        cls.django = Category.objects.create(name='Django', slug='django')
        cls.python = Category.objects.create(name='Python', slug='python')
        cls.articles = []
        for i in range(1, 7):
            category = cls.django if i % 2 else cls.python
            title = f'Статья №{i} про Django' if i % 2 else f'Статья №{i} про Python'
            cls.articles.append(
                Article.objects.create(
                    title=title,
                    text=f'Текст статьи номер {i}.',
                    category=category,
                )
            )
        cls.first = cls.articles[0]


class ArticleListTests(ArticleFixtureMixin, TestCase):
    def test_list_returns_200(self):
        response = self.client.get(reverse('article_list'))
        self.assertEqual(response.status_code, 200)

    def test_list_shows_articles(self):
        response = self.client.get('/articles/')
        # Сортировка «новые сверху», на первой странице — статьи 6…2.
        self.assertContains(response, 'Статья №6 про Python')
        self.assertContains(response, 'Статья №2 про Python')
        self.assertNotContains(response, 'Статья №1 про Django')

    def test_pagination_by_5(self):
        response = self.client.get('/articles/')
        self.assertEqual(len(response.context['articles']), 5)
        page2 = self.client.get('/articles/?page=2')
        self.assertEqual(page2.status_code, 200)
        self.assertEqual(len(page2.context['articles']), 1)

    def test_search_by_title(self):
        response = self.client.get('/articles/', {'q': 'python'})
        self.assertEqual(response.status_code, 200)
        titles = [a.title for a in response.context['articles']]
        self.assertTrue(all('Python' in t for t in titles))
        self.assertEqual(len(titles), 3)

    def test_search_reflected_in_context(self):
        response = self.client.get('/articles/', {'q': 'django'})
        self.assertEqual(response.context['q'], 'django')

    def test_search_no_results(self):
        response = self.client.get('/articles/', {'q': 'нетакогослова'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['articles']), 0)


class ArticleDetailTests(ArticleFixtureMixin, TestCase):
    def test_detail_returns_200(self):
        response = self.client.get(
            reverse('article_detail', args=[self.first.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.first.title)
        self.assertContains(response, self.first.text)

    def test_missing_article_is_404(self):
        response = self.client.get('/articles/999999/')
        self.assertEqual(response.status_code, 404)

    def test_non_numeric_id_is_404(self):
        # <int:id> не совпадёт с abc — маршрут не сработает.
        response = self.client.get('/articles/abc/')
        self.assertEqual(response.status_code, 404)


class CategoryTests(ArticleFixtureMixin, TestCase):
    def test_category_page_returns_200(self):
        response = self.client.get(reverse('category_detail', args=['django']))
        self.assertEqual(response.status_code, 200)

    def test_category_shows_only_its_articles(self):
        response = self.client.get('/category/django/')
        titles = [a.title for a in response.context['articles']]
        self.assertEqual(len(titles), 3)
        self.assertTrue(all('Django' in t for t in titles))

    def test_unknown_category_is_404(self):
        response = self.client.get('/category/no-such-slug/')
        self.assertEqual(response.status_code, 404)


class NamedRoutesTests(ArticleFixtureMixin, TestCase):
    """Именованные маршруты: reverse() и {% url %} без зашитых адресов."""

    def test_reverse_article_list(self):
        self.assertEqual(reverse('article_list'), '/articles/')

    def test_reverse_article_detail(self):
        self.assertEqual(
            reverse('article_detail', args=[self.first.pk]),
            f'/articles/{self.first.pk}/',
        )

    def test_reverse_category_detail(self):
        self.assertEqual(
            reverse('category_detail', args=['django']),
            '/category/django/',
        )

    def test_templates_contain_no_hardcoded_article_links(self):
        # В исходниках шаблонов не должно быть зашитых адресов статей —
        # только {% url 'article_detail' ... %} и {% url 'category_detail' ... %}.
        templates_dir = BASE_DIR / 'articles' / 'templates'
        for path in templates_dir.rglob('*.html'):
            source = path.read_text(encoding='utf-8')
            self.assertNotIn('href="/articles/', source, path.name)
            self.assertNotIn('href="/category/', source, path.name)


@override_settings(DEBUG=False, ALLOWED_HOSTS=['testserver'])
class Custom404Tests(ArticleFixtureMixin, TestCase):
    def test_missing_article_uses_custom_template(self):
        response = self.client.get('/articles/424242/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'Такой страницы нет', status_code=404)


class TemplateInheritanceTests(ArticleFixtureMixin, TestCase):
    """Уровень 1: все страницы блога наследуют base.html."""

    def test_list_extends_base(self):
        response = self.client.get(reverse('article_list'))
        self.assertContains(response, 'navbar')

    def test_detail_extends_base(self):
        response = self.client.get(
            reverse('article_detail', args=[self.first.pk])
        )
        self.assertContains(response, 'navbar')

    def test_404_extends_base(self):
        with override_settings(DEBUG=False, ALLOWED_HOSTS=['testserver']):
            response = self.client.get('/articles/424242/')
        self.assertContains(response, 'navbar', status_code=404)

    def test_date_format_dd_mm_yyyy(self):
        # дд.мм.гггг — без времени, как требует уровень 1.
        # Дату считаем в текущем часовом поясе (Asia/Tashkent), как в шаблоне.
        from django.utils import timezone

        newest = self.articles[-1]  # №6 — сверху на первой странице
        response = self.client.get(reverse('article_list'))
        expected = timezone.localtime(newest.created_at).strftime(
            '%d.%m.%Y'
        )
        self.assertContains(response, expected)

    def test_preview_is_20_words(self):
        long_text = ' '.join(f'слово{i}' for i in range(40))
        Article.objects.create(
            title='Длинная статья для превью',
            text=long_text,
            category=self.django,
        )
        response = self.client.get(reverse('article_list'))
        html = response.content.decode('utf-8')
        # truncatewords:20 оставляет 20 слов и ставит многоточие.
        self.assertIn('слово19', html)
        self.assertNotIn('слово20', html)
        self.assertIn('…', html)


class ArticleCreateTests(ArticleFixtureMixin, TestCase):
    """Уровень 2: создание статьи через ModelForm."""

    def test_create_page_returns_200(self):
        response = self.client.get(reverse('article_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Новая статья')

    def test_valid_post_creates_article(self):
        response = self.client.post(
            reverse('article_create'),
            {
                'title': 'Новая статья из формы',
                'text': 'Текст новой статьи.',
                'category': self.django.pk,
            },
        )
        article = Article.objects.get(title='Новая статья из формы')
        self.assertRedirects(
            response,
            reverse('article_detail', args=[article.pk]),
        )
        self.assertEqual(article.text, 'Текст новой статьи.')

    def test_short_title_shows_error_under_field(self):
        response = self.client.post(
            reverse('article_create'),
            {
                'title': 'abc',  # короче 5 символов
                'text': 'Текст.',
                'category': self.django.pk,
            },
        )
        # Ошибка валидации: страница рендерится заново, статья не создаётся.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Article.objects.filter(title='abc').count(),
            0,
        )
        self.assertContains(
            response,
            'Заголовок должен быть не короче 5 символов.',
        )
        # Ошибка выводится под полем (invalid-feedback после input).
        html = response.content.decode('utf-8')
        self.assertLess(html.index('name="title"'), html.index('invalid-feedback'))


class ArticleEditTests(ArticleFixtureMixin, TestCase):
    """Уровень 2: редактирование той же формы с instance=."""

    def test_edit_page_returns_200_with_instance(self):
        response = self.client.get(
            reverse('article_edit', args=[self.first.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].instance, self.first)

    def test_valid_post_updates_article(self):
        response = self.client.post(
            reverse('article_edit', args=[self.first.pk]),
            {
                'title': 'Обновлённый заголовок',
                'text': 'Обновлённый текст.',
                'category': self.python.pk,
            },
        )
        self.assertRedirects(
            response,
            reverse('article_detail', args=[self.first.pk]),
        )
        self.first.refresh_from_db()
        self.assertEqual(self.first.title, 'Обновлённый заголовок')
        self.assertEqual(self.first.category, self.python)

    def test_missing_article_is_404(self):
        response = self.client.get('/articles/999999/edit/')
        self.assertEqual(response.status_code, 404)


class FeedbackTests(ArticleFixtureMixin, TestCase):
    """Челлендж: forms.Form + модель Feedback + messages."""

    def test_feedback_page_returns_200(self):
        response = self.client.get(reverse('feedback'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Обратная связь')

    def test_valid_post_saves_feedback_and_shows_message(self):
        response = self.client.post(
            reverse('feedback'),
            {
                'name': 'Иван',
                'email': 'ivan@example.com',
                'message': 'Отличный блог!',
            },
            follow=True,
        )
        self.assertRedirects(response, reverse('feedback'))
        feedback = Feedback.objects.get()
        self.assertEqual(feedback.name, 'Иван')
        self.assertEqual(feedback.email, 'ivan@example.com')
        self.assertContains(response, 'Спасибо! Ваше сообщение отправлено.')

    def test_invalid_email_does_not_save(self):
        response = self.client.post(
            reverse('feedback'),
            {'name': 'Иван', 'email': 'не-почта', 'message': 'Привет'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Feedback.objects.count(), 0)
        self.assertContains(response, 'Введите правильный адрес электронной')

    def test_clean_title_validation(self):
        form = ArticleForm(
            data={'title': 'abc', 'text': 'Текст', 'category': self.django.pk}
        )
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertEqual(
            str(form.errors['title'][0]),
            'Заголовок должен быть не короче 5 символов.',
        )

    def test_feedback_form_requires_fields(self):
        form = FeedbackForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(set(form.errors), {'name', 'email', 'message'})
