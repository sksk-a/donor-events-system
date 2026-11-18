# ПР10 Администрирование и ORM

## Что реализовано

Админка `/admin/` управляет Organization, Participant, Event и Registration.
Столбцы, поиск и фильтры заданы в admin.py каждого приложения. Inline регистраций
включён для мероприятий и участников. Приложения и поля имеют русские названия.
Аккаунты, пароли и локальная ORM-база не включаются в Git.

Команды первого запуска и настройки администратора приведены в начале README.
Права is_staff определяют доступ в панель; модельные view/change/add/delete — действия.
Тест с пользователем только view_registration подтверждает запрет изменения и отмены.
Не утверждать, что Admin сам предотвращает превышение вместимости: такого правила нет.

## Запросы и статусы

`Registration.objects` — менеджер собственного QuerySet. active() выбирает
REGISTERED/CONFIRMED на мероприятиях PLANNED/OPEN; cancelled() выбирает CANCELLED;
completed() выбирает ATTENDED. for_date() фильтрует **дату регистрации**, occupied()
исключает отменённые записи. Статистика и доступность учитывают эти определения.

for_listing() получает поля связанных сущностей через annotate(F()) и values().
В результате возвращаются словари, а не экземпляры Registration. Нет последующего
обращения к объектам FK, поэтому select_related для такой проекции не нужен.
В карточке возвращается модель, поэтому select_related(event, participant) полезен.

## Вопрос 25 Связанные данные без лишних запросов

Показать registrations/models.py → RegistrationQuerySet.for_listing():

```python
Registration.objects.annotate(
    participant_name=F("participant__full_name"),
    event_title=F("event__title"),
    organization_name=F("event__organization__name"),
).values("id", "participant_name", "event_title", "organization_name")
```

F ссылается на столбцы, двойное подчёркивание проходит по FK. ORM формирует JOIN
participants, events и organizations. values возвращает выбранные поля словарями.
Обращение row['participant_name'] не выполняет новый SQL, поскольку значение уже в строке.
select_related нужен при загрузке моделей и последующем доступе item.participant.

Запустить `manage.py profile_orm`: для 3 объектов без оптимизации 10 запросов,
select_related 1, annotate/values 1; для карточки 3 → 1.
В реальной странице дополнительных запросов формы, COUNT пагинатора и общего
контекста может быть больше одного; это не признак N+1. DDT показывает их отдельно.

## Вопрос 26 Вычисляемое и связанное значение

Event.is_large — GeneratedField с CASE WHEN max_participants >= 100.
В Shell можно сравнить 99 и 100 на отдельной учебной записи. После изменения
max_participants и save() повторно выполнить get() или refresh_from_db():

```python
from events.models import Event
event = Event.objects.get(pk=1)
original = event.max_participants
event.max_participants = 100
event.save(update_fields=["max_participants"])
event.refresh_from_db()
print(event.max_participants, event.is_large)  # 100 True
event.max_participants = 99
event.save(update_fields=["max_participants"])
event.refresh_from_db()
print(event.max_participants, event.is_large)  # 99 False
# Восстановить учебное изменение после демонстрации:
event.max_participants = original
event.save(update_fields=["max_participants"])
```

Вместимость хранится непосредственно. is_large тоже физически хранится (db_persist=True),
но формируется базой по выражению и не редактируется вручную. Python-объект может
содержать старое вычисляемое значение до перечитывания. Имя организации — поле
связанной Organization; event хранит organization_id, а не копию её имени.
Поэтому после изменения Organization.name новая выборка event.organization.name
покажет обновлённое имя. get_absolute_url вычисляет URL из сохранённого slug.

## Slug контекст и миграции

Event.get_absolute_url() использует именованный маршрут events:detail-slug.
Старый detail по ID сохранён. Миграция events.0003 заполнила slug действующих записей,
используя замороженное правило транслитерации и суффикс ID. Новым объектам slug
назначается при save(), а при переименовании сохраняется для устойчивости ссылок.

Контекстный процессор site_context передаёт название сайта и счётчик мероприятий;
он зарегистрирован в settings и реально используется навигацией. COUNT выполняется
при формировании шаблона и учитывается при анализе числа SQL-запросов.

## Реальные проверки интерфейса

18.11.2026 создана отдельная копия базы для проверки, в неё добавлены только учебные
записи и временный администратор. Сервер работал локально на 127.0.0.1:8765 и остановлен.
Рабочая ORM-база и источник ПР7 этими демонстрационными регистрациями не заполнялись.

- Admin: четыре модели доступны; поиск «Учебный» и статус CONFIRMED дают 8 из 12 записей.
- Inline: видны связанные участники, даты и статусы в карточке мероприятия.
- Пагинация: фильтры даты/города/мероприятия и сортировка по участнику сохранены;
  вторая страница содержит регистрации 6–10 и маркер 2 из 3.
- Статистика: всего 12, занятых мест 11, активных 10, отменённых 1, посещённых 1.
- Мероприятие с вместимостью 20 имеет 9 свободных мест; поиск на 9 находит его,
  на 10 возвращает пустой результат. Адрес по slug открывается.
- В SQLPanel DDT карточки регистрации видны один JOIN с участником и мероприятием
  и один COUNT мероприятий из общего контекстного процессора.
- В SQLPanel списка без фильтров реально 5 запросов: COUNT регистраций, COUNT
  мероприятий, два списка вариантов формы и SELECT текущей страницы с JOIN всех
  четырёх таблиц и LIMIT 5. Снимок `09-list-sql.jpg` подходит для вопроса 25.

Снимки сохранены в docs/screenshots/pr10. 122 автоматизированных теста проверяют
CRUD Admin, права, ограничения, статусы, GeneratedField, slug, контекст, JOIN, DDT и
регрессии ПР9. `check`, `makemigrations --check --dry-run`, flake8 и diff-check успешны.
