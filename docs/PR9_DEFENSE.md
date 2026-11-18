# ПР9 Модели Django и ORM

## Архитектура и перенос

Применён вариант 2 из методички: исходная `data/donor_events.sqlite` ПР7 сохранена,
миграции создали новые таблицы `organizations_organization`, `participants_participant`,
`events_event`, `registrations_registration` в `db.sqlite3`. Последняя теперь содержит
и предметные, и служебные таблицы Django. Модель `ContactInfo` абстрактная, таблицы нет.

До переноса локальные копии обеих баз сохранены отдельно. Команда
`python manage.py import_pr7` читает исходную базу в режиме `mode=ro`, проверяет FK,
затем внутри `transaction.atomic()` выполняет `update_or_create(pk=..., defaults=...)`.
ID и внешние ключи сохраняются, даты превращаются в `date`, active — в bool.
Повторный запуск обновляет совпадающие ID, но не удаляет посторонние записи ORM.
Поэтому на чистой базе ожидаются 2 организации, 2 участника, 1 мероприятие, 0 регистраций.

## Модели и связи

- `organizations.models.Organization`: название, город, адрес, унаследованные телефон/email.
- `participants.models.Participant`: ФИО, дата рождения, группа крови, активность и контакты.
- `events.models.Event`: организация ForeignKey, название, дата, адрес, вместимость,
  статус TextChoices и описание. M:N с участниками через Registration.
- `registrations.models.Registration`: участник и мероприятие ForeignKey, дата,
  статус, примечания. Метод cancel() обновляет статус и вызывает save().

Все ForeignKey имеют `related_name` и `on_delete=PROTECT`: нельзя случайно удалить
организатора с мероприятиями или участника/мероприятие с регистрациями.
`UniqueConstraint(participant, event)` предотвращает дубликат записи;
`CheckConstraint` проверяет статусы, положительную вместимость и группу крови.
Модель `ContactInfo` наследует Model с abstract=True и переиспользует поля без таблицы.

## Реальные ORM выражения

Каждый пункт ниже — отдельная выборка или выражение; составные цепочки не
учитываются несколько раз в общем количестве. В представлениях более 20 выражений.

| № | Выражение / место | Назначение |
| --- | --- | --- |
| 1 | homepage: Event.objects.all() | Все мероприятия |
| 2 | homepage: Organization.objects.all() | Все организации |
| 3 | homepage: Participant.objects.all() | Все участники |
| 4 | homepage: Registration.objects.all() | Все регистрации |
| 5 | events.list_view: order_by(event_date, id) | Стабильная сортировка |
| 6 | filter(max_participants__gte=capacity) | Фильтр по вместимости |
| 7 | filter(title__icontains=q) | Поиск по названию |
| 8 | with_free_places(): Count + F | Занятые и свободные места |
| 9 | available: filter(event_date, status__in, free_places__gte) | Несколько условий |
| 10 | available: filter(city=city) | Отбор города |
| 11 | get_object_or_404(with_free_places(), pk=id) | Отдельное мероприятие |
| 12 | organization.events.order_by(event_date, id) | Обратная связь FK |
| 13 | event_directory: select_related(organization).order_by(organization__name, ...) | Связь и сортировка по связанному полю |
| 14 | registrations: select_related(participant, event__organization) | FK без N+1 запросов |
| 15 | active: exclude(status__in=...).filter(event__status__in=...) | Исключение и фильтр по связанному полю |
| 16 | filter(registration_date=date) | Фильтрация даты |
| 17 | filter(event=event) | Выбор мероприятия |
| 18 | filter(participant=participant) | Выбор участника |
| 19 | filter(event__city=city) | Фильтр связанной модели |
| 20 | filter(Q(participant__full_name__icontains=q) OR Q(event__title__icontains=q)) | Поиск по двум полям |
| 21 | order_by(*SORT_FIELDS[...]) | Разрешённая сортировка, включая связанные поля |
| 22 | statistics: Registration.aggregate(Count, filtered Count) | Общие показатели регистраций |
| 23 | statistics: Event.aggregate(Count, Sum, Avg, Min, Max) | Общие показатели мероприятий |
| 24 | Event.annotate(total=Count(registrations), occupied=...) | Группировка по мероприятиям |
| 25 | Organization.annotate(total=Count(events)) | Группировка по организациям |
| 26 | Event.annotate(total=...).filter(total__gt=threshold) | Аналог HAVING |

## Фильтрация сортировка пагинация

Оба списка `/registrations/` и `/registrations/active/` имеют единую форму:
дата регистрации, мероприятие, участник, город, поиск по ФИО/названию и сортировка.
Страница всех регистраций сохраняет прежний сценарий ПР7; активные вынесены отдельно.
Все условия применяются как И, два поисковых поля объединяются Q через ИЛИ.
Неизвестная сортировка заменяется на date; произвольный ввод не попадает в order_by.
Некорректные дата/ID показывают ошибки формы и пустую выборку.

После фильтрации и сортировки вызывается Paginator(queryset, 5).get_page(page).
page=abc даёт первую страницу, слишком большой или отрицательный номер — последнюю.
В ссылках используется `{% querystring page=... %}`, поэтому остальные GET-параметры
сохраняются. Форма не передаёт page: смена условий начинает показ с первой страницы.

## Команды для защиты

```powershell
.\.venv\Scripts\python.exe -B manage.py check
.\.venv\Scripts\python.exe -B manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -B manage.py showmigrations
.\.venv\Scripts\python.exe -B manage.py sqlmigrate events 0001
.\.venv\Scripts\python.exe -B manage.py demo_orm
.\.venv\Scripts\python.exe -B -m pytest -v
.\.venv\Scripts\python.exe -B -m flake8 . --extend-exclude=venv
```

`demo_orm` выполняет create → get → save → delete внутри откатываемой транзакции,
поэтому демонстрация не засоряет рабочую базу. Защита удаления проверяется тестами.

Fixture: `python manage.py dumpdata organizations participants events registrations --indent 2 --output data/pr9_fixture.json`.
Загрузка в совместимую базу после migrate: `python manage.py loaddata data/pr9_fixture.json`.
Перед загрузкой в существующую базу следует учитывать совпадение ID. Автоматический
тест выгрузки/загрузки выполняется в изолированной базе.

Для демонстрации получения объекта в shell:

```python
from events.models import Event
Event.objects.get(pk=1)
Event.objects.filter(pk=99999)  # пустой QuerySet
# get(pk=99999) выбросит Event.DoesNotExist;
# get() по неуникальному критерию может выбросить MultipleObjectsReturned.
```

## Проверка сохранности прежних сценариев

Поиск свободных мест использует filter статусов PLANNED/OPEN, выбранную дату,
Count регистраций без CANCELLED и F(max_participants)-F(occupied).
LEFT JOIN в annotate сохраняет мероприятия и организации с нулевыми связями.
HTML-шаблоны получают модели и обращаются к event.organization.name и
registration.participant.full_name; даты остаются date, статусы — строки choices.
Нет вызовов слоя `db.database`/`db.catalog` в представлениях. Ручной SQL остался
только в исторической реализации ПР7 и в чтении источника при переносе.

Тесты проверяют CRUD, PROTECT, UNIQUE/CHECK, сохранность исходной базы, rollback,
перенос связей, 404, SQL-инъекции, поиск, группировки и пагинацию на 12 записях.
Непустые учебные записи существуют только в тестовой базе. Сервер не запускался.
Темы Яндекс Практикума проходятся отдельно в учебном аккаунте.
