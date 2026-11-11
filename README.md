# Сервис организации донорских мероприятий

## Текущий этап ПР7 — SQLite и SQL

Веб-сайт получает предметные данные из `data/donor_events.sqlite` через стандартный
модуль `sqlite3`. Django ORM для организаций, мероприятий, участников и регистраций
не используется. Старый JSON-адаптер сохранён в `app/utils/web_data.py`, исходный
`data/sample_data.json` не изменён. Консольная версия продолжает работать с PostgreSQL.

### Запуск сайта в PowerShell

Команды выполняются из папки проекта:

```powershell
cd "C:\Users\Redmi\Desktop\3 курс универ\ТРПНБФ ИП\donor-events-system"
# Только при отсутствии окружения:
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# База уже приложена к проекту. Импорт нужен при её отсутствии или для восстановления:
.\.venv\Scripts\python.exe -m db.import_json
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py runserver
```

Открыть `http://127.0.0.1:8000/`. Остановка сервера — Ctrl+C. При следующих запусках
достаточно команды `manage.py runserver` через Python из `.venv`.
**Импорт заменяет предметные данные содержимым JSON**, поэтому перед повторным
импортом изменённой вручную БД следует сохранить её копию. Ошибка импорта откатывает
удаления и вставки одной транзакции; корректный повторный импорт не создаёт дубликатов.

### Структура хранения и файлы

| Файл | Назначение |
| --- | --- |
| `sql/schema.sql` | Создание таблиц, внешних ключей, CHECK, UNIQUE и индексов; повторное выполнение безопасно |
| `sql/queries.sql` | 20 именованных запросов; именно этот файл исполняется сайтом |
| `db/database.py` | `sqlite3.connect`, `PRAGMA foreign_keys = ON`, `sqlite3.Row`, закрытие соединений |
| `db/import_json.py` | Транзакционный импорт через `executemany()` и явный `commit()` |
| `db/catalog.py` | Преобразование результатов SQL в прежние dataclass, даты и Enum для шаблонов |
| `data/donor_events.sqlite` | Предметные данные сайта ПР7 |
| `db.sqlite3` | Отдельные служебные таблицы Django auth/contenttypes/sessions |

Поля таблиц (полный DDL в `sql/schema.sql`):

| Таблица | Поля |
| --- | --- |
| `organizations` | `id INTEGER PK`, `name TEXT`, `city TEXT`, `address TEXT`, `phone TEXT`, `email TEXT NULL` |
| `participants` | `id INTEGER PK`, `full_name TEXT`, `birth_date TEXT`, `phone TEXT`, `email TEXT NULL`, `blood_type TEXT`, `active INTEGER` |
| `events` | `id INTEGER PK`, `organization_id INTEGER FK`, `title TEXT`, `event_date TEXT`, `city TEXT`, `address TEXT`, `max_participants INTEGER`, `status TEXT`, `description TEXT NULL` |
| `registrations` | `id INTEGER PK`, `participant_id INTEGER FK`, `event_id INTEGER FK`, `registration_date TEXT`, `status TEXT`, `notes TEXT NULL` |

Остальные поля обязательны. Даты хранятся в ISO-формате `YYYY-MM-DD`, логический
`active` — как `0`/`1`. Связи: организация → мероприятия, участник → регистрации,
мероприятие → регистрации. `UNIQUE(participant_id, event_id)` запрещает повторную запись.
Проверки `CHECK` ограничивают статусы, группы крови и положительную вместимость.

Импортированы все исходные записи: 2 организации, 2 участника, 1 мероприятие,
0 регистраций. Пустой список регистраций соответствует JSON, а не ошибке импорта.
Для проверки непустых выборок тесты создают отдельные временные базы с регистрациями.

### Запросы и страницы

| Запросы в `sql/queries.sql` | Где виден результат |
| --- | --- |
| 1–4: списки `events_list`, `organizations_list`, `participants_list`, `registrations_list` | Главная `/` и разделы сущностей |
| 5: `events_capacity`, WHERE с параметром | `/events/?capacity=30` |
| 6: `active_registrations`, WHERE и JOIN | `/registrations/active/` |
| 7: `events_organizations`, JOIN | `/organizations/events/` |
| 8: `registrations_related`, JOIN четырёх таблиц | `/registrations/` |
| 9: `available_events`, дата, город, LEFT JOIN, HAVING | `/events/available/` |
| 10–11: `registration_totals`, `event_totals`, COUNT/SUM/AVG/MIN/MAX | `/registrations/statistics/` |
| 12–13: `registrations_by_event`, `events_by_organization`, GROUP BY | `/registrations/statistics/` |
| 14: `popular_events`, GROUP BY и HAVING с порогом | `/registrations/statistics/?threshold=0` |
| 15–20: карточки, мероприятия организации, занятые места | Страницы сущностей `/<раздел>/<id>/` |

Таким образом, используются не менее двух списковых запросов, двух WHERE, двух JOIN,
двух агрегатных запросов и двух GROUP BY. Все 20 запросов вызываются веб-приложением.
Пользовательские значения проходят валидацию Django Forms и передаются отдельным
кортежем к `execute(sql, params)` через `?`. SQL не показывается в интерфейсе сайта.

Поиск доступных мероприятий: выбираются акции `PLANNED`/`OPEN` **на введённую дату**,
при необходимости в выбранном городе. Число мест — вместимость минус неотменённые
регистрации. Отменённые записи не занимают места, завершённые/отменённые акции и полные
мероприятия не попадают в результат. Активные регистрации — `REGISTERED`/`CONFIRMED`
на мероприятиях `PLANNED`/`OPEN`. Прошедшая дата сама по себе не меняет статус.
Для исходного примера можно искать **15.10.2026**, город **Москва**, 1 свободное место.

`DONOR_SQLITE_FILE` позволяет выбрать другую БД (относительный путь считается от корня
проекта). Например: `$env:DONOR_SQLITE_FILE = "data/demo.sqlite"`.
Веб-настройки читают переменные окружения; файл `.env` предназначен для старой консольной
версии. Сайт не создаёт пустую БД при неверном пути и не выполняет импорт автоматически.

### Проверки и защита

```powershell
.\.venv\Scripts\python.exe -B manage.py check
.\.venv\Scripts\python.exe -B -m pytest -v
.\.venv\Scripts\python.exe -B -m flake8 . --extend-exclude=venv
.\.venv\Scripts\python.exe -B -m tools.check_sql
```

`tools.check_sql` выполняет все запросы через SQLite CLI стандартной библиотеки Python
(`python -m sqlite3`, Python 3.12+). Сам сайт требует Python 3.11+.
Тесты используют временные БД и не меняют рабочую `data/donor_events.sqlite`.
Сценарий защиты и соответствие 25 пунктам: `docs/PR7_DEFENSE.md`.
Материалы Яндекс Практикума проходят отдельно в учебном аккаунте; репозиторий
не подтверждает их прохождение.

## Назначение
Информационная система с консольным и веб-интерфейсом для управления донорскими мероприятиями. Система позволяет организациям регистрировать и проводить донорские акции, участникам записываться на мероприятия, а администраторам отслеживать статистику и экспортировать данные.

## Целевая аудитория
- Организации здравоохранения и волонтерские движения
- Администраторы донорских центров
- Координаторы донорских мероприятий
- Доноры крови

## Предметная область
Организация и координация донорских мероприятий по сдаче крови. Система обеспечивает учет организаций-организаторов, планирование мероприятий, регистрацию участников с указанием группы крови, управление статусами регистраций (зарегистрирован, подтвержден, посетил, отменен) и формирование отчетности.

## Основные сущности
- **Organization** — организации-организаторы донорских мероприятий (название, город, адрес, контакты)
- **Event** — донорские мероприятия (дата, место проведения, количество мест, статус: запланировано, открыто, завершено, отменено)
- **Participant** — участники-доноры (ФИО, дата рождения, группа крови, контактная информация, статус активности)
- **Registration** — регистрации участников на мероприятия (связь участника и мероприятия, статус регистрации, примечания)

## Основные функции
- Управление организациями (создание, просмотр, редактирование, удаление)
- Управление донорскими мероприятиями (планирование, открытие, завершение, отмена)
- Регистрация участников с указанием группы крови и контактных данных
- Запись участников на мероприятия с отслеживанием статусов
- Поиск и фильтрация по различным критериям (статус, город, организация, мероприятие)
- Формирование статистики (количество мероприятий, участников, регистраций по статусам)
- Экспорт данных в Excel для отчетности
- Валидация бизнес-правил (проверка лимитов мест, дат, статусов)

## Стек и архитектура консольной версии

Python 3.11+, PostgreSQL, psycopg 3, openpyxl, python-dotenv, pytest, flake8; веб-слой — Django 5.2. Поток вызова:
`ConsoleApp -> Service -> Repository -> PostgreSQL`. Модели — dataclass и Enum; SQL расположен
только в репозиториях, правила — только в сервисах.

```text
main.py                     точка входа
app/
  models/                   предметные модели и Enum
    oop_classes.py          классы ООП (Person, Donor, Organizer)
  repositories/             параметризованный SQL и CRUD
  services/                 проверки и бизнес-правила
  ui/console.py             циклические меню
  utils/                    Database, InputUtils, ExcelExporter, JsonHandler
  exceptions/               пользовательские исключения
database/                   schema.sql и seed.sql
data/                       sample_data.json (демонстрационные данные)
tests/                      pytest тесты (49 тестов)
docs/                       ER-диаграмма и методичка
.flake8                     конфигурация линтера
pytest.ini                  конфигурация pytest
```

## Модель и правила

Organization 1:N Event; Participant M:N Event через Registration. Система запрещает отсутствующих
и неактивных участников, отсутствующие/закрытые события, дубли, переполнение, прошлую дату нового
мероприятия, неверный переход статуса и удаление связанных организаций/мероприятий. Статусы
регистрации: REGISTERED, CONFIRMED, ATTENDED, CANCELLED; события: PLANNED, OPEN, COMPLETED, CANCELLED.

## Установка PostgreSQL и запуск

Создайте БД и примените скрипты (команды выполняются из корня проекта):

```bash
createdb -U postgres donor_events
psql -U postgres -d donor_events -f database/schema.sql
psql -U postgres -d donor_events -f database/seed.sql
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Отредактируйте `.env`: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. Пароль в коде не
хранится. `schema.sql` пересоздает четыре таблицы, поэтому повторный запуск удалит их данные.

## Возможности меню

Полный CRUD организаций и мероприятий, CRUD с безопасной деактивацией участников, полный CRUD
регистраций, поиск по ID/ФИО/мероприятию/организации, фильтры по статусам/организации/городу,
Python-сортировка по четырем полям, 11 статистических представлений и просмотр таблиц. После каждой
операции меню продолжает работу. Ошибки ввода, правил и БД выводятся понятным сообщением.

Экспорт создает `exports/donor_events.xlsx`: четыре листа, жирные заголовки, автофильтр,
закрепленная строка и настроенная ширина колонок.

## Тестирование и качество кода

Исходный проект включал 49 тестов, после ПР6 было 74; после ПР7 — 89 проверок с использованием pytest:

```powershell
# Запуск всех тестов
.venv\Scripts\activate
pytest tests/ -v

# Проверка кода линтером
flake8 app/models/ tests/ main.py
```

Тесты покрывают:
- Модели данных (dataclass и традиционные классы)
- Enum классы
- Сервисный слой (с mock-объектами)
- ООП классы (Person, Donor, Organizer, ContactManager)
- JSON обработчик

## Демонстрация ООП принципов

Файл `app/models/oop_classes.py` содержит традиционные классы с явной демонстрацией:

**Наследование:**
- `Person` — базовый класс с `__init__`, `__str__`, `__repr__`
- `Donor(Person)` — наследник с дополнительными атрибутами
- `Organizer(Person)` — наследник для организаторов

**Инкапсуляция:**
- Приватные атрибуты через `_attribute`
- Property декораторы для геттеров и сеттеров
- Валидация в сеттерах

**Полиморфизм:**
- Метод `get_contact_info()` переопределен в дочерних классах
- `ContactManager` работает с любым типом `Person`

## Работа с JSON

Модуль `app/utils/json_handler.py` предоставляет класс `JsonHandler` для работы с JSON файлами:

```python
from app.utils.json_handler import JsonHandler

handler = JsonHandler('data/sample_data.json')
data = handler.read_json()
organizations = data['organizations']
```

Демонстрационные данные: `data/sample_data.json`


## План развития

На следующих этапах планируется:
- Расширение веб-интерфейса формами создания и редактирования
- Реализация системы аутентификации и авторизации пользователей
- Разработка REST API для интеграции с внешними системами
- Контейнеризация приложения (Docker)
- Настройка CI/CD для автоматического развертывания
- Добавление уведомлений (email, SMS) для участников
- Интеграция с картографическими сервисами для отображения мест проведения
- Мобильное приложение для доноров

## Типовые ошибки

- `connection refused`: запустите PostgreSQL и проверьте хост/порт в `.env`.
- `password authentication failed`: исправьте `DB_USER`/`DB_PASSWORD`.
- `database does not exist`: выполните `createdb`.
- `relation does not exist`: примените `schema.sql`, затем `seed.sql`.
- `ModuleNotFoundError`: активируйте `.venv` и выполните установку зависимостей.

ER-модель: [docs/er-diagram.md](docs/er-diagram.md).


## История веб-версии ПР5 и ПР6

Ниже сохранено описание предыдущего этапа с JSON-хранилищем. Для текущего запуска,
источника данных и демонстрации используйте раздел ПР7 в начале README.

Django 5.2 добавлен к существующему проекту. PostgreSQL нужен только консольной версии.
Веб-версия читает `data/sample_data.json` существующим `JsonHandler`; адаптер
`app/utils/web_data.py` создаёт прежние dataclass `Event`, `Organization`, `Participant`,
`Registration`, преобразуя даты и Enum. Исходные записи не изменены.
В исходном JSON нет ключа registrations: список регистраций пока пуст, данные не выдумываются.
Страницы предназначены для просмотра; предметные ORM-модели и формы не используются.
Миграции создают только встроенные служебные таблицы Django в SQLite.

### Запуск из корня репозитория (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py runserver
```

Откройте http://127.0.0.1:8000/. Без активации используйте `.venv\Scripts\python` вместо `python`.

| URL | Приложение / функция | Назначение |
| --- | --- | --- |
| `/` | homepage.views.index | Главная и навигация |
| `/events/`, `/events/<int:entity_id>/` | events.views.list_view / detail | Мероприятия |
| `/organizations/`, `/organizations/<int:entity_id>/` | organizations.views.list_view / detail | Организации |
| `/participants/`, `/participants/<int:entity_id>/` | participants.views.list_view / detail | Доноры |
| `/registrations/`, `/registrations/<int:entity_id>/` | registrations.views.list_view / detail | Регистрации |

`donor_site/` содержит settings, корневой urls, wsgi/asgi; `manage.py` запускает команды Django.
Каждое веб-приложение зарегистрировано в INSTALLED_APPS и имеет свой urls.py и views.py.
Донор Participant — предметная сущность, а не учётная запись Django User.
В коммите ПР5 общий HTML собирала `homepage.views.page()`. В ПР6 все обработчики используют render() и шаблоны. Bootstrap 5.3.3 подключён через CDN.
Данные экранируются, отсутствующий объект возвращает 404.
Собственный handler404 в корневом urls применяется при DEBUG=False.

Для проверки собственной 404:

```powershell
$env:DJANGO_DEBUG = "0"
python manage.py runserver
# После остановки сервера Ctrl+C:
Remove-Item Env:DJANGO_DEBUG
```

По умолчанию DEBUG=True для локальной разработки. ALLOWED_HOSTS ограничен localhost и 127.0.0.1.
Ключ по умолчанию предназначен только для локального учебного запуска.

Проверки: `python manage.py check`, `python -m pytest -v`, `python -m flake8 . --extend-exclude=venv`.
Консольные CRUD, Excel, SQL-репозитории и все прежние классы сохранены; их описание приведено выше.


### Шаблоны и статические файлы (ПР6)

Поток: `URL → view → JsonHandler → dataclass → context → render → template → HTML`.
`templates/base.html` содержит каркас и блоки title/content, подключает Bootstrap,
собственный CSS, SVG и JavaScript. `templates/includes/navigation.html` — общая навигация,
`templates/includes/status.html` — статусы. Каждый дочерний шаблон использует extends/block.

```text
homepage/templates/homepage/index.html     главная
<приложение>/templates/<приложение>/
  list.html                               for/empty, length, include
  detail.html                             if item, date/default, ссылки
  includes/card.html                      карточка объекта
homepage/static/homepage/
  css/style.css                           фирменное оформление и адаптивная сетка
  js/main.js                              текущий год в подвале
  img/logo.svg                            логотип: капля с сердцем
```

Карточка мероприятия повторно используется на главной и в списке; include with/only
передаёт item. Контексты передаются словарями, отсутствующий объект — item=None;
шаблон показывает else, а view задаёт status=404. Пустые коллекции обрабатывает empty.
Даты преобразуются в date на этапе загрузки, поэтому date:"d.m.Y" работает на реальных полях.
Фильтры length/default применяются для количества и значений по умолчанию.

Имена: `homepage:index`, `events:list/detail`, `organizations:list/detail`,
`participants:list/detail`, `registrations:list/detail`. Все ссылки между страницами
строятся тегом url, пути CSS/JS/SVG — static после load static.
APP_DIRS=True обнаруживает шаблоны приложений, DIRS добавляет общие templates.

JavaScript с defer обновляет #current-year и добавляет ему data-updated-by="javascript".
У base.html есть серверный запасной год для браузера без JS. Веб-интерфейс не формирует
HTML внутри Python: page() полностью удалена. Код ПР5: `git show 15791ad:homepage/views.py`.

### Проверка и демонстрация

```powershell
python manage.py findstatic homepage/css/style.css homepage/js/main.js homepage/img/logo.svg
python -m pytest -v
python -m flake8 . --extend-exclude=venv
```

Полные фактические результаты: REPORT_PR5.md и REPORT_PR6.md.
Подготовка к защите: DEFENSE_GUIDE.md (52 ответа ПР5, 30 ответов ПР6, сценарий и задания).
Перечень изменённых файлов: CHANGED_FILES.md.

Чтобы показать подтверждённую и отменённую регистрации, создать **отдельную учебную копию**:

```powershell
python tools/prepare_defense_data.py
$env:DONOR_JSON_FILE = "test-results/defense_data.json"
$env:DJANGO_DEBUG = "0"
python manage.py runserver 8001 --noreload --insecure
# После остановки Ctrl+C:
Remove-Item Env:DONOR_JSON_FILE
Remove-Item Env:DJANGO_DEBUG
```

Адрес: http://127.0.0.1:8001/registrations/. Две добавленные записи явно помечены
учебными в notes. Источник sample_data.json не изменяется. Свободных мест будет 49:
отменённая регистрация не занимает место. /nonexistent/ покажет собственную 404.
--insecure применяется только для локальной демонстрации static при DEBUG=False.
При обычном запуске на 8000 используется исходный JSON с пустым списком регистраций.

### Границы текущего этапа

Веб-часть предназначена для просмотра; создание, изменение и удаление через формы,
авторизация в интерфейсе и предметные модели Django ORM — следующие этапы. PostgreSQL-консоль сохранена отдельно;
она не синхронизирует свои записи с JSON веб-версии. PostgreSQL для веб-интерфейса не нужен. `python manage.py migrate` создаёт только служебные таблицы auth/contenttypes/sessions в локальном db.sqlite3; предметные данные в них не переносятся. Дата/статус исходного события отображаются
как хранятся в JSON; прошедшая дата не изменяет статус автоматически.

Материалы Яндекс Практикума и «Блогикум» в личном аккаунте не отмечались выполненными.
Git-коммиты ПР5 и ПР6 локальные; отправка на GitHub не выполнялась.

По п. 5.6.1 методички ПР5 выполнены встроенные миграции Django. В коммите PR5 служебная БД ещё не подключалась; настройка и проверка служебных миграций добавлены завершающим коммитом PR6. Веб-интерфейс не использует служебную БД как хранилище мероприятий.
