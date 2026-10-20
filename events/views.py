from django.http import HttpResponse
from django.utils.html import escape

from app.utils.web_data import find_by_id, load_catalog
from homepage.views import page


def list_view(request):
    catalog = load_catalog()
    items = getattr(catalog, "events")
    links = "".join(
        f'<li class="list-group-item"><a href="/events/{item.id}/">{escape(str(item.title))}</a></li>'
        for item in items
    )
    content = '<h1>Мероприятия</h1><ul class="list-group">' + (
        links or '<li class="list-group-item">Пока нет данных.</li>'
    ) + '</ul>'
    return HttpResponse(page("Мероприятия", content))


def detail(request, entity_id):
    catalog = load_catalog()
    item = find_by_id(catalog.events, entity_id)
    if item is None:
        return HttpResponse(page("Объект не найден", '<h1>Объект не найден</h1><a href="/events/">К списку</a>'), status=404)
    content = f'<h1>Мероприятие: {escape(str(item.title))}</h1><p><strong>Дата:</strong> {escape(str(item.event_date if item.event_date is not None else "Не указано"))}</p><p><strong>Город:</strong> {escape(str(item.city if item.city is not None else "Не указано"))}</p><p><strong>Адрес:</strong> {escape(str(item.address if item.address is not None else "Не указано"))}</p><p><strong>Лимит мест:</strong> {escape(str(item.max_participants if item.max_participants is not None else "Не указано"))}</p><p><strong>Статус:</strong> {escape(str(item.status.value if item.status.value is not None else "Не указано"))}</p><p><strong>Описание:</strong> {escape(str(item.description if item.description is not None else "Не указано"))}</p>'

    organization = find_by_id(catalog.organizations, item.organization_id)
    if organization:
        content += f'<p>Организатор: <a href="/organizations/{organization.id}/">{escape(organization.name)}</a></p>'
    content += f'<p>Свободных мест: {catalog.free_places(item)}</p>'

    content += '<a class="btn btn-outline-secondary" href="/events/">К списку</a>'
    return HttpResponse(page("Мероприятие", content))
