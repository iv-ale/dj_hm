import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection, reset_queries
from django.db.models import Avg, Max, Count
from books.models import Author, Book

q1 = Book.objects.filter(pages__gt=300)
print('1. pages__gt=300:')
for b in q1:
    print(f'{b.title} - {b.pages} стр.')

q2 = Book.objects.filter(title__icontains='души')
print('\n2. title__icontains=души:')
for b in q2:
    print(f'{b.title}')

q3 = Book.objects.filter(status__in=['issued', 'written_off'])
print('\n3. status__in=[issued, written_off]:')
for b in q3:
    print(f'{b.title} ({b.get_status_display()})')

q4 = Book.objects.filter(publication_year__range=(1830, 1870))
print('\n4. publication_year__range=(1830, 1870):')
for b in q4:
    print(f'{b.title} ({b.publication_year} г.)')

q5 = Author.objects.filter(birth_date__year=1828)
print('\n5. birth_date__year=1828:')
for a in q5:
    print(f'{a.name} ({a.birth_date})')

q6 = Book.objects.order_by('-pages')[:5]
print('\n6. Топ-5 книг по страницам:')
for b in q6:
    print(f'{b.title} - {b.pages} стр.')

q7 = Book.objects.exclude(status='written_off')
print(f'\n7. exclude(status=written_off) count: {q7.count()}')

q8 = Book.objects.aggregate(avg_pages=Avg('pages'), max_pages=Max('pages'), total_books=Count('id'))
avg_val = q8['avg_pages']
max_val = q8['max_pages']
tot_val = q8['total_books']
print(f'\n8. Агрегация: среднее страниц = {avg_val:.1f}, макс = {max_val}, всего = {tot_val}')

q9 = Author.objects.annotate(book_count=Count('books'), avg_pages=Avg('books__pages'))
print('\n9. Отчёт по авторам (annotate):')
for a in q9:
    avg_p = a.avg_pages if a.avg_pages else 0
    print(f'{a.name}: книг = {a.book_count}, средний объём = {avg_p:.1f} стр.')

print('\n10. 20 книг с именами авторов и проверка N+1:')
reset_queries()
books_no_select = list(Book.objects.all()[:20])
for b in books_no_select:
    print(f'{b.title} — {b.author.name}')
queries_without = len(connection.queries)

reset_queries()
books_with_select = list(Book.objects.select_related('author')[:20])
for b in books_with_select:
    _ = b.author.name
queries_with = len(connection.queries)

print(f'\nЧисло запросов без select_related: {queries_without}')
print(f'Число запросов с select_related: {queries_with}')