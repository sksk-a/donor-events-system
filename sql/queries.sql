-- name: events_list
-- 1. Список мероприятий, стабильная сортировка по дате и идентификатору.
SELECT * FROM events ORDER BY event_date, id;

-- name: organizations_list
-- 2. Список организаций.
SELECT * FROM organizations ORDER BY name, id;

-- name: participants_list
-- 3. Список доноров.
SELECT * FROM participants ORDER BY full_name, id;

-- name: registrations_list
-- 4. Список всех регистраций.
SELECT * FROM registrations ORDER BY registration_date DESC, id;

-- name: events_capacity
-- 5. WHERE: мероприятия с вместимостью не меньше введённой.
SELECT * FROM events WHERE max_participants >= ? ORDER BY event_date, id;

-- name: active_registrations
-- 6. WHERE: зарегистрированные и подтверждённые записи на незавершённые акции.
SELECT r.*, e.title AS event_title, p.full_name AS participant_name
FROM registrations AS r
JOIN events AS e ON e.id = r.event_id
JOIN participants AS p ON p.id = r.participant_id
WHERE r.status IN ('REGISTERED', 'CONFIRMED') AND e.status IN ('PLANNED', 'OPEN')
ORDER BY e.event_date, r.id;

-- name: events_organizations
-- 7. JOIN: мероприятие вместе с организатором.
SELECT e.*, o.name AS organization_name
FROM events AS e JOIN organizations AS o ON o.id = e.organization_id
ORDER BY e.event_date, e.id;

-- name: registrations_related
-- 8. JOIN: участник, мероприятие и организация для каждой регистрации.
SELECT r.*, p.full_name AS participant_name, e.title AS event_title,
       e.event_date, o.name AS organization_name
FROM registrations AS r
JOIN participants AS p ON p.id = r.participant_id
JOIN events AS e ON e.id = r.event_id
JOIN organizations AS o ON o.id = e.organization_id
ORDER BY r.registration_date DESC, r.id;

-- name: available_events
-- 9. Свободные места на выбранную дату; отменённые регистрации не занимают места.
-- Параметры: YYYY-MM-DD, город (или ''), тот же город, минимальное число мест.
SELECT e.*, o.name AS organization_name,
       e.max_participants - COUNT(r.id) AS free_places
FROM events AS e
JOIN organizations AS o ON o.id = e.organization_id
LEFT JOIN registrations AS r ON r.event_id = e.id AND r.status <> 'CANCELLED'
WHERE e.event_date = ? AND e.status IN ('PLANNED', 'OPEN')
  AND (? = '' OR e.city = ?)
GROUP BY e.id
HAVING e.max_participants - COUNT(r.id) >= ?
ORDER BY free_places DESC, e.id;

-- name: registration_totals
-- 10. Агрегаты: количество всех регистраций и записей, занимающих места.
SELECT COUNT(*) AS total,
       COALESCE(SUM(CASE WHEN status <> 'CANCELLED' THEN 1 ELSE 0 END), 0) AS occupied
FROM registrations;

-- name: event_totals
-- 11. Агрегаты: число мероприятий, общая, средняя, минимальная и максимальная вместимость.
SELECT COUNT(*) AS total, COALESCE(SUM(max_participants), 0) AS capacity,
       COALESCE(AVG(max_participants), 0) AS average_capacity,
       COALESCE(MIN(max_participants), 0) AS min_capacity,
       COALESCE(MAX(max_participants), 0) AS max_capacity
FROM events;

-- name: registrations_by_event
-- 12. GROUP BY: регистрации по мероприятиям, включая мероприятия без записей.
SELECT e.id, e.title, COUNT(r.id) AS total,
       COALESCE(SUM(CASE WHEN r.status <> 'CANCELLED' THEN 1 ELSE 0 END), 0) AS occupied
FROM events AS e LEFT JOIN registrations AS r ON r.event_id = e.id
GROUP BY e.id ORDER BY total DESC, e.id;

-- name: events_by_organization
-- 13. GROUP BY: количество мероприятий у каждой организации, включая нулевое.
SELECT o.id, o.name, COUNT(e.id) AS total
FROM organizations AS o LEFT JOIN events AS e ON e.organization_id = o.id
GROUP BY o.id ORDER BY total DESC, o.id;

-- name: popular_events
-- 14. HAVING: мероприятия, у которых число неотменённых регистраций выше порога.
SELECT e.id, e.title, COUNT(r.id) AS total
FROM events AS e
LEFT JOIN registrations AS r ON r.event_id = e.id AND r.status <> 'CANCELLED'
GROUP BY e.id HAVING COUNT(r.id) > ?
ORDER BY total DESC, e.id;

-- name: event_detail
-- 15. Поиск мероприятия по идентификатору.
SELECT * FROM events WHERE id = ?;

-- name: organization_detail
-- 16. Поиск организации по идентификатору.
SELECT * FROM organizations WHERE id = ?;

-- name: participant_detail
-- 17. Поиск участника по идентификатору.
SELECT * FROM participants WHERE id = ?;

-- name: registration_detail
-- 18. Поиск регистрации по идентификатору.
SELECT * FROM registrations WHERE id = ?;

-- name: organization_events
-- 19. Мероприятия выбранной организации.
SELECT * FROM events WHERE organization_id = ? ORDER BY event_date, id;

-- name: occupied_places
-- 20. Занятые места выбранного мероприятия.
SELECT COUNT(*) AS total FROM registrations WHERE event_id = ? AND status <> 'CANCELLED';
