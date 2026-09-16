# ER-диаграмма

```mermaid
erDiagram
    ORGANIZATIONS ||--o{ EVENTS : organizes
    PARTICIPANTS ||--o{ REGISTRATIONS : makes
    EVENTS ||--o{ REGISTRATIONS : has
    ORGANIZATIONS { bigint id PK string name string city string address string phone string email UK }
    EVENTS { bigint id PK bigint organization_id FK string title date event_date string city string address int max_participants string status string description }
    PARTICIPANTS { bigint id PK string full_name date birth_date string phone string email UK string blood_type boolean active }
    REGISTRATIONS { bigint id PK bigint participant_id FK bigint event_id FK date registration_date string status string notes }
```

`organizations.id -> events.organization_id`, `participants.id -> registrations.participant_id` и
`events.id -> registrations.event_id` — внешние ключи связей 1:N. Участники и мероприятия имеют
отношение M:N через таблицу-связку `registrations`. Составное ограничение
`UNIQUE(participant_id, event_id)` запрещает повторную регистрацию.
