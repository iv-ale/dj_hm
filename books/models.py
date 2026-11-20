from django.db import models


class Author(models.Model):
    name = models.CharField('Имя', max_length=150)
    bio = models.TextField('Биография', blank=True)
    email = models.EmailField('Email', unique=True, blank=True, null=True)
    birth_date = models.DateField('Дата рождения', blank=True, null=True)

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'в наличии'),
        ('issued', 'выдана'),
        ('written_off', 'списана'),
    ]

    title = models.CharField('Заголовок', max_length=200)
    publication_year = models.PositiveIntegerField('Год издания')
    pages = models.PositiveIntegerField('Страниц')
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name='Автор',
    )
    in_stock = models.BooleanField('В наличии', default=True)
    status = models.CharField(
        'Статус', max_length=20, choices=STATUS_CHOICES, default='available'
    )

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ('title',)

    def __str__(self):
        return self.title
