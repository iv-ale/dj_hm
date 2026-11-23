from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand

from books.models import Book

GROUP_NAME = 'Библиотекари'
BOOK_PERMISSIONS = ('add_book', 'change_book', 'delete_book', 'view_book')


class Command(BaseCommand):
    help = (
        'Создаёт группу «Библиотекари» с правами только на книги '
        'и сотрудника-библиотекаря в этой группе.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--username', default='librarian')
        parser.add_argument('--password', default='librarian123')
        parser.add_argument('--email', default='librarian@example.com')

    def handle(self, *args, **options):
        book_perms = Permission.objects.filter(
            content_type__app_label='books',
            codename__in=BOOK_PERMISSIONS,
        )
        if book_perms.count() != len(BOOK_PERMISSIONS):
            self.stderr.write('Не найдены все права на книги. Сначала выполните migrate.')
            return

        group, created = Group.objects.get_or_create(name=GROUP_NAME)
        group.permissions.set(book_perms)
        self.stdout.write(
            f'Группа «{GROUP_NAME}» {"создана" if created else "обновлена"}: '
            f'{group.permissions.count()} прав (только на книги).'
        )

        user, user_created = User.objects.get_or_create(
            username=options['username'],
            defaults={
                'email': options['email'],
                'is_staff': True,
            },
        )
        if not user.is_staff:
            user.is_staff = True
        user.set_password(options['password'])
        user.save()
        user.groups.add(group)

        # Сотрудник не суперпользователь: видит только то, что есть в группе.
        if user.is_superuser:
            user.is_superuser = False
            user.save()

        self.stdout.write(
            f'Сотрудник "{user.username}" '
            f'{"создан" if user_created else "обновлён"} '
            f'(is_staff={user.is_staff}, суперпользователь={user.is_superuser}).'
        )
        self.stdout.write(
            f'Права сотрудника: '
            f'{", ".join(sorted(user.get_all_permissions())) or "нет"}.'
        )
        self.stdout.write(self.style.SUCCESS(
            f'Готово. Вход в админку: /admin/ — {user.username} / {options["password"]}'
        ))
