from django.urls import path

from . import views

urlpatterns = [
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path(
        'articles/<int:id>/',
        views.ArticleDetailView.as_view(),
        name='article_detail',
    ),
    path(
        'category/<slug:slug>/',
        views.category_detail,
        name='category_detail',
    ),
]
