from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from .forms import ArticleForm, FeedbackForm
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


def article_create(request):
    """Создание статьи: /articles/new/ через ModelForm (урок 50, уровень 2)."""
    form = ArticleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        article = form.save()
        messages.success(request, f'Статья «{article.title}» создана.')
        return redirect('article_detail', article.pk)
    return render(
        request,
        'articles/form.html',
        {'form': form, 'page_title': 'Новая статья'},
    )


def article_edit(request, id):
    """Редактирование статьи: /articles/<id>/edit/ (та же форма с instance=)."""
    article = get_object_or_404(Article, pk=id)
    form = ArticleForm(request.POST or None, instance=article)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Изменения сохранены.')
        return redirect('article_detail', article.pk)
    return render(
        request,
        'articles/form.html',
        {
            'form': form,
            'page_title': f'Редактирование: {article.title}',
            'article': article,
        },
    )


def feedback(request):
    """Форма обратной связи: /feedback/ (урок 50, челлендж)."""
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Спасибо! Ваше сообщение отправлено.',
            )
            return redirect('feedback')
    else:
        form = FeedbackForm()
    return render(
        request,
        'articles/feedback.html',
        {'form': form},
    )
