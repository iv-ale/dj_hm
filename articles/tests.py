from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Article, Category

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
