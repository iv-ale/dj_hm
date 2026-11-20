from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from .models import Article, Category


class ArticleListView(ListView):
    """Список статей: /articles/ — поиск ?q= и пагинация по 5 (уровень 3)."""

    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.q = self.request.GET.get('q', '').strip()
        if self.q:
            queryset = queryset.filter(title__icontains=self.q)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = getattr(self, 'q', '')
        context['categories'] = Category.objects.all()
        return context


class ArticleDetailView(DetailView):
    """Детальная страница статьи: /articles/<id>/."""

    model = Article
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'
    # Маршрут объявлен как <int:id>, поэтому читаем id, а не pk.
    pk_url_kwarg = 'id'

    def get_object(self, queryset=None):
        # Уровень 1: на несуществующую статью отвечаем 404
        # через get_object_or_404 (DetailView сам поднимает Http404,
        # но здесь это показано явно, как в задании).
        return get_object_or_404(Article, pk=self.kwargs[self.pk_url_kwarg])


def category_detail(request, slug):
    """Страница категории: /category/<slug:slug>/ (уровень 2)."""
    category = get_object_or_404(Category, slug=slug)
    articles = category.articles.all()
    return render(
        request,
        'articles/category.html',
        {'category': category, 'articles': articles},
    )
