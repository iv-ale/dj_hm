from django.contrib import admin
from django.db.models import Count

from .models import Author, Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Админка книг: колонки, фильтры, поиск, сортировка и свои действия."""

    list_display = (
        'title',
        'author',
        'publication_year',
        'pages',
        'status',
        'in_stock',
    )
    list_display_links = ('title',)
    list_filter = ('status', 'in_stock', 'publication_year', 'author')
    search_fields = ('title', 'author__name')
    ordering = ('title',)
    list_select_related = ('author',)
    empty_value_display = '—'

    actions = ('issue_books', 'write_off_books')

    @admin.action(
        description='Выдать: отметить книги как выданные',
        permissions=('change',),
    )
    def issue_books(self, request, queryset):
        updated = queryset.filter(status='available').update(
            status='issued', in_stock=False
        )
        self.message_user(
            request, f'Выдано книг: {updated}.', level='success'
        )

    @admin.action(
        description='Списать: отметить книги как списанные',
        permissions=('change',),
    )
    def write_off_books(self, request, queryset):
        updated = queryset.exclude(status='written_off').update(
            status='written_off', in_stock=False
        )
        self.message_user(
            request, f'Списано книг: {updated}.', level='success'
        )


class BookInline(admin.TabularInline):
    """Таблица книг автора на странице самого автора."""

    model = Book
    extra = 1
    fields = ('title', 'publication_year', 'pages', 'status', 'in_stock')
    readonly_fields = ()
    ordering = ('title',)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Админка авторов: колонки, фильтры, поиск, сортировка и книги inline."""

    list_display = ('name', 'email', 'birth_date', 'book_count')
    list_display_links = ('name',)
    list_filter = ('birth_date',)
    search_fields = ('name', 'email')
    ordering = ('name',)
    empty_value_display = '—'
    inlines = (BookInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_book_count=Count('books'))

    @admin.display(description='Книг', ordering='_book_count')
    def book_count(self, obj):
        return obj._book_count
