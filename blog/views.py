from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def home(request):
    """Главная страница blog: приветствие (уровень 3)."""
    return HttpResponse("Привет, Django!")
