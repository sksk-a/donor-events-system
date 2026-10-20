from django.http import HttpResponse
from django.utils.html import escape

from app.utils.web_data import find_by_id, load_catalog
from homepage.views import page


def list_view(request):
    catalog = load_catalog()
    items = getattr(catalog, "participants")
    links = "".join(
        f'<li class="list-group-item"><a href="/participants/{item.id}/">{escape(str(item.full_name))}</a></li>'
        for item in items
    )
    content = '<h1>Участники</h1><ul class="list-group">' + (
        links or '<li class="list-group-item">Пока нет данных.</li>'
    ) + '</ul>'
    return HttpResponse(page("Участники", content))


def detail(request, entity_id):
    catalog = load_catalog()
    item = find_by_id(catalog.participants, entity_id)
    if item is None:
        return HttpResponse(page("Объект не найден", '<h1>Объект не найден</h1><a href="/participants/">К списку</a>'), status=404)
    content = f'<h1>Участник: {escape(str(item.full_name))}</h1><p><strong>Дата рождения:</strong> {escape(str(item.birth_date if item.birth_date is not None else "Не указано"))}</p><p><strong>Группа крови:</strong> {escape(str(item.blood_type.value if item.blood_type.value is not None else "Не указано"))}</p><p><strong>Телефон:</strong> {escape(str(item.phone if item.phone is not None else "Не указано"))}</p><p><strong>Email:</strong> {escape(str(item.email if item.email is not None else "Не указано"))}</p><p><strong>Активен:</strong> {escape(str(item.active if item.active is not None else "Не указано"))}</p>'

    content += '<a class="btn btn-outline-secondary" href="/participants/">К списку</a>'
    return HttpResponse(page("Участник", content))
