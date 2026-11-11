# ПР7 Защита SQLite и SQL

Проект: сервис организации донорских мероприятий. Реализация находится в ветке
`main`. Предметные данные — `data/donor_events.sqlite`, а `db.sqlite3`
содержит только служебные таблицы Django. ORM предметной области не используется.

## Быстрая демонстрация

1. Открыть `sql/schema.sql` и базу в SQLite Viewer: 4 таблицы, первичные и внешние ключи.
2. Открыть `db/import_json.py`: порядок вставки — организации, участники, мероприятия,
   регистрации. Проверить исходные количества: 2, 2, 1, 0. Повторный импорт заменяет данные,
   поэтому демонстрировать его лучше в копию:
   `python -m db.import_json --database data/demo.sqlite`.
3. Открыть `sql/queries.sql` — 20 запросов. Запустить `python -m tools.check_sql`.
4. В запущенном самостоятельно сайте показать `/events/?capacity=30` и
   `/organizations/events/` (название мероприятия и организатора из JOIN).
5. На `/events/available/` ввести дату 15.10.2026, 1 место, Москва. Исходная акция имеет
   50 свободных мест. При требовании 51 места результат пустой.
6. Открыть `/registrations/active/` и `/registrations/statistics/`: регистраций в исходном
   JSON нет, поэтому 0 — правильный результат. Статистика показывает организацию без
   мероприятий и мероприятие без регистраций благодаря LEFT JOIN.
7. Показать тесты `tests/test_sql.py`: на временной БД проверены заполненные,
   отменённые и завершённые акции, отменённые регистрации, JOIN, агрегаты и HAVING.

## Соответствие таблице из методички

| № | Где показать и что объяснить |
| --- | --- |
| 1 | `sql/schema.sql`: organizations, participants, events, registrations; связи 1:N и M:N через registrations |
| 2 | `id INTEGER PRIMARY KEY`, REFERENCES и UNIQUE пары участник/мероприятие |
| 3 | `db/import_json.py`: executescript, CREATE TABLE IF NOT EXISTS; повторное создание схемы не удаляет таблицы |
| 4 | `db/database.py`: sqlite3.connect; путь в DONOR_SQLITE_FILE; `PRAGMA database_list` показывает фактический файл |
| 5 | `executemany`, значения по полям; сначала родители, затем ссылающиеся на них записи |
| 6 | SELECT COUNT(*) по каждой таблице; сравнить с JSON: 2/2/1/0 |
| 7 | `events_list`: поля SELECT определяют данные, доступные представлению и шаблону |
| 8 | `events_capacity`: WHERE max_participants >= ?, параметр capacity из формы |
| 9 | `active_registrations`: только REGISTERED/CONFIRMED на PLANNED/OPEN; отменённые и посещённые исключены |
| 10 | `registrations_related`: JOIN связывает id и FK; получаем ФИО, название акции и организатора |
| 11 | `available_events`: дата + город + статус + свободные места; при изменении даты меняется выборка |
| 12 | `registration_totals`: COUNT(*) возвращает 0 на пустой таблице; SUM обёрнут в COALESCE |
| 13 | `registrations_by_event`, `events_by_organization`: одна строка на группу, LEFT JOIN сохраняет нулевые группы |
| 14 | `popular_events`: HAVING COUNT(r.id) > ?; WHERE отбирает строки до группировки, HAVING — группы после |
| 15 | `fetch_all(name, params)`: значения передаются в execute отдельно, а не вставляются в SQL-строку |
| 16 | row_factory = sqlite3.Row; `row['title']`, `row['total']`; fetchall/fetchone |
| 17 | events.views.list_view → events_capacity/events_list → items → events/list.html |
| 18 | registrations.views.active → active_registrations → items → registrations/list.html |
| 19 | organizations.views.event_directory → events_organizations → organization_name в шаблоне |
| 20 | events.views.available: request.GET → AvailableEventsForm → cleaned_data → кортеж параметров → SQL |
| 21 | registrations.views.statistics: два агрегата и группировки передаются отдельными ключами context |
| 22 | В шаблоне цикл по items: если в context ошибочно назвать список events, карточки не появятся; согласовать имена |
| 23 | `{% empty %}` показывает сообщение; пустая выборка не выбрасывает исключение, ошибка SQL выбрасывает sqlite3.Error |
| 24 | Опечатка в SELECT даёт OperationalError; неверный JOIN может дать неверные строки без исключения; сверять FK и тесты |
| 25 | GET → URL → view → Forms → db.database → SQL/SQLite → Row → context → шаблон |

## Важные различия

- COUNT(*) считает строки, COUNT(r.id) после LEFT JOIN не считает NULL правой таблицы.
- NULL проверяется через IS NULL / IS NOT NULL, а не `= NULL`.
- Даты хранятся как TEXT YYYY-MM-DD, active — INTEGER 0/1.
- Параметры `?` защищают структуру SQL; валидация форм проверяет смысл значений.
- Исходный JSON сохранён, но изменения JSON видны сайту только после явного импорта.
- `PRAGMA foreign_keys = ON` включается для каждого подключения.
- Контекстный менеджер закрывает соединение; импорт явно делает commit или rollback.
- Материалы Яндекс Практикума выполняются в личном учебном аккаунте; их прохождение
  нельзя подтвердить наличием кода в этом репозитории.

## Проверка

В PowerShell из корня проекта:

```powershell
.\.venv\Scripts\python.exe -B manage.py check
.\.venv\Scripts\python.exe -B -m pytest -v
.\.venv\Scripts\python.exe -B -m flake8 . --extend-exclude=venv
.\.venv\Scripts\python.exe -B -m tools.check_sql
```

Сервер для автоматических проверок не нужен. Тестовый Client вызывает Django внутри
процесса; рабочая БД не меняется. Все тестовые регистрации существуют только во
временных БД, удаляемых pytest.
