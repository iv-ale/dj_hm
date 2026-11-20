from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from .models import Author, Book


class BooksAdminTests(TestCase):
    """Проверки ДЗ: админка, inline, действия и группа «Библиотекари»."""

    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(name='Пушкин', email='pushkin@example.com')
        cls.book = Book.objects.create(
            title='Евгений Онегин',
            publication_year=1833,
            pages=448,
            author=cls.author,
            status='available',
        )
        cls.admin_user = User.objects.create_superuser('root', 'root@example.com', 'pass')
        cls.librarian = User.objects.create_user(
            'librarian', 'librarian@example.com', 'librarian123', is_staff=True
        )
        cls.librarian.groups.set([])
        for codename in ('add_book', 'change_book', 'delete_book', 'view_book'):
            perm = Permission.objects.get(codename=codename, content_type__app_label='books')
            cls.librarian.user_permissions.add(perm)

    def test_book_list_columns_filters_search(self):
        """В списке книг есть колонки, фильтры и поиск."""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin:books_book_changelist'))
        self.assertEqual(response.status_code, 200)
        for column in ('Заголовок', 'Автор', 'Год издания', 'Страниц', 'Статус'):
            self.assertContains(response, column)
        self.assertContains(response, 'status__exact')
        self.assertContains(response, 'name="q"')

    def test_author_page_has_book_inline(self):
        """На странице автора — таблица его книг (TabularInline)."""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin:books_author_change', args=(self.author.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'books-group')
        self.assertContains(response, 'Евгений Онегин')

    def test_admin_actions_issue_and_write_off(self):
        """Действия «Выдать» и «Списать» меняют статус книги."""
        self.client.force_login(self.admin_user)
        url = reverse('admin:books_book_changelist')

        self.client.post(url, {'action': 'issue_books', '_selected_action': [self.book.pk]})
        self.book.refresh_from_db()
        self.assertEqual(self.book.status, 'issued')
        self.assertFalse(self.book.in_stock)

        self.client.post(url, {'action': 'write_off_books', '_selected_action': [self.book.pk]})
        self.book.refresh_from_db()
        self.assertEqual(self.book.status, 'written_off')

    def test_librarian_sees_only_books(self):
        """Сотрудник видит только книги, остальное — нет."""
        self.client.force_login(self.librarian)
        response = self.client.get(reverse('admin:index'))
        self.assertContains(response, 'Книги')
        self.assertNotContains(response, 'Пользователи')
        self.assertNotContains(response, 'Группы')

        # Страница автора и модели вне групп — 403 (нет прав).
        response = self.client.get(reverse('admin:books_author_changelist'))
        self.assertEqual(response.status_code, 403)

    def test_librarian_cannot_open_other_models(self):
        """Сотрудник не может открыть чужие разделы админки."""
        self.client.force_login(self.librarian)
        response = self.client.get(reverse('admin:auth_user_changelist'))
        self.assertEqual(response.status_code, 403)
