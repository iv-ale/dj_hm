from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Категория статей: страница /category/<slug:slug>/."""

    name = models.CharField('Название', max_length=100)
    slug = models.SlugField(
        'Слаг',
        max_length=100,
        unique=True,
        help_text='Адрес страницы, например: django',
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', args=[self.slug])


class Article(models.Model):
    """Статья: список /articles/, детальная страница /articles/<id>/."""

    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        # Новые сверху; "id" стабилизирует порядок при одинаковом времени.
        ordering = ('-created_at', 'id')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', args=[self.pk])
