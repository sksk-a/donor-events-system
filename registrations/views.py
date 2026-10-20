from django.http import HttpResponse
from django.utils.html import escape

from app.utils.web_data import find_by_id, load_catalog
from homepage.views import page


def list_view(request):
    catalog = load_catalog()
    items = getattr(catalog, "registrations")
    links = "".join(
        f'<li class="list-group-item"><a href="/registrations/{item.id}/">{escape(str(item.id))}</a></li>'
        for item in items
    )
    content = '<h1>Регистрации</h1><ul class="list-group">' + (
        links or '<li class="list-group-item">Пока нет данных.</li>'
    ) + '</ul>'
    return HttpResponse(page("Регистрации", content))


def detail(request, entity_id):
    catalog = load_catalog()
    item = find_by_id(catalog.registrations, entity_id)
    if item is None:
        return HttpResponse(page("Объект не найден", '<h1>Объект не найден</h1><a href="/registrations/">К списку</a>'), status=404)
    content = f'<h1>Регистрация: {escape(str(item.id))}</h1><p><strong>Дата регистрации:</strong> {escape(str(item.registration_date if item.registration_date is not None else "Не указано"))}</p><p><strong>Статус:</strong> {escape(str(item.status.value if item.status.value is not None else "Не указано"))}</p><p><strong>Примечания:</strong> {escape(str(item.notes if item.notes is not None else "Не указано"))}</p>'

    event = find_by_id(catalog.events, item.event_id)
    participant = find_by_id(catalog.participants, item.participant_id)
    if event:
        content += f'<p>Мероприятие: <a href="/events/{event.id}/">{escape(event.title)}</a></p>'
    if participant:
        content += f'<p>Участник: <a href="/participants/{participant.id}/">{escape(participant.full_name)}</a></p>'

    content += '<a class="btn btn-outline-secondary" href="/registrations/">К списку</a>'
    return HttpResponse(page("Регистрация", content))
