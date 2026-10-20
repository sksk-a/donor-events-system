from django.http import HttpResponse
from django.utils.html import escape

from app.utils.web_data import load_catalog


def page(title, content):
    """Общий HTML-каркас ПР5; в ПР6 заменяется base.html."""
    bootstrap = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
    return f'''<!DOCTYPE html>
<html lang="ru"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title><link rel="stylesheet" href="{bootstrap}">
<style>body {{background:#f7f8fa}} main {{padding:2rem 0}} .card {{margin:1rem 0}}</style>
</head><body><nav class="nav container" aria-label="Основная навигация">
<a class="nav-link" href="/">Главная</a>
<a class="nav-link" href="/events/">Мероприятия</a>
<a class="nav-link" href="/organizations/">Организации</a>
<a class="nav-link" href="/participants/">Участники</a>
<a class="nav-link" href="/registrations/">Регистрации</a>
</nav><main class="container">{content}</main></body></html>'''


def index(request):
    catalog = load_catalog()
    content = (
        '<h1>Сервис донорских мероприятий</h1>'
        '<p class="lead">Организации, доноры и донорские акции.</p>'
        f'<p>Мероприятий: {len(catalog.events)}. '
        f'Участников: {len(catalog.participants)}.</p>'
        '<a class="btn btn-danger" href="/events/">Посмотреть мероприятия</a>'
    )
    return HttpResponse(page("Главная — Донорские мероприятия", content))


def page_not_found(request, exception):
    return HttpResponse(page("404", '<h1>404 — страница не найдена</h1>'), status=404)
