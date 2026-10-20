from django.http import HttpResponse
from django.utils.html import escape

from app.utils.web_data import find_by_id, load_catalog
from homepage.views import page


def list_view(request):
    catalog = load_catalog()
    items = getattr(catalog, "organizations")
    links = "".join(
        f'<li class="list-group-item"><a href="/organizations/{item.id}/">{escape(str(item.name))}</a></li>'
        for item in items
    )
    content = '<h1>Организации</h1><ul class="list-group">' + (
        links or '<li class="list-group-item">Пока нет данных.</li>'
    ) + '</ul>'
    return HttpResponse(page("Организации", content))


def detail(request, entity_id):
    catalog = load_catalog()
    item = find_by_id(catalog.organizations, entity_id)
    if item is None:
        return HttpResponse(page("Объект не найден", '<h1>Объект не найден</h1><a href="/organizations/">К списку</a>'), status=404)
    content = f'<h1>Организация: {escape(str(item.name))}</h1><p><strong>Город:</strong> {escape(str(item.city if item.city is not None else "Не указано"))}</p><p><strong>Адрес:</strong> {escape(str(item.address if item.address is not None else "Не указано"))}</p><p><strong>Телефон:</strong> {escape(str(item.phone if item.phone is not None else "Не указано"))}</p><p><strong>Email:</strong> {escape(str(item.email if item.email is not None else "Не указано"))}</p>'

    content += '<a class="btn btn-outline-secondary" href="/organizations/">К списку</a>'
    return HttpResponse(page("Организация", content))
