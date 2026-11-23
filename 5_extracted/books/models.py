from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'в наличии'),
        ('issued', 'выдана'),
        ('written_off', 'списана'),
    ]

    title = models.CharField(max_length=200)
    publication_year = models.PositiveIntegerField()
    pages = models.PositiveIntegerField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    in_stock = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return self.title