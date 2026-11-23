from django.urls import path

from . import views

urlpatterns = [
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path(
        'articles/new/',
        views.article_create,
        name='article_create',
    ),
    path(
        'articles/<int:id>/',
        views.ArticleDetailView.as_view(),
        name='article_detail',
    ),
    path(
        'articles/<int:id>/edit/',
        views.article_edit,
        name='article_edit',
    ),
    path('feedback/', views.feedback, name='feedback'),
    path(
        'category/<slug:slug>/',
        views.category_detail,
        name='category_detail',
    ),
]
