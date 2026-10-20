# Сервис организации донорских мероприятий

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

## Стек и архитектура

Python 3.11+, PostgreSQL, psycopg 3, openpyxl, python-dotenv, pytest, flake8. Поток вызова:
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

Проект включает 49 автоматических тестов с использованием pytest:

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


## Веб-версия: ПР5

Django 5.2 добавлен к существующему проекту. PostgreSQL нужен только консольной версии.
Веб-версия читает `data/sample_data.json` существующим `JsonHandler`; адаптер
`app/utils/web_data.py` создаёт прежние dataclass `Event`, `Organization`, `Participant`,
`Registration`, преобразуя даты и Enum. Исходные записи не изменены.
В исходном JSON нет ключа registrations: список регистраций пока пуст, данные не выдумываются.
Страницы предназначены для просмотра; ORM, миграции и формы не используются.

### Запуск из корня репозитория (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
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
В ПР5 общий HTML собирает `homepage.views.page()`, подключающий Bootstrap 5.3.3 через CDN.
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
