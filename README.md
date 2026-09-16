# Сервис организации донорских мероприятий

Учебная консольная информационная система для организаций, мероприятий, доноров и регистраций.
Основная сущность — `Registration`, связывающая `Participant` и `Event`.

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

## Типовые ошибки

- `connection refused`: запустите PostgreSQL и проверьте хост/порт в `.env`.
- `password authentication failed`: исправьте `DB_USER`/`DB_PASSWORD`.
- `database does not exist`: выполните `createdb`.
- `relation does not exist`: примените `schema.sql`, затем `seed.sql`.
- `ModuleNotFoundError`: активируйте `.venv` и выполните установку зависимостей.

ER-модель: [docs/er-diagram.md](docs/er-diagram.md).
