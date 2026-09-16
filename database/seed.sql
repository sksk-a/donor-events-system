INSERT INTO organizations(name,city,address,phone,email) VALUES
('Центр крови Москвы','Москва','ул. Поликарпова, 14','+7-495-111-11-11','moscow@donor.ru'),
('Доброе сердце','Казань','ул. Баумана, 20','+7-843-222-22-22','heart@donor.ru'),
('Фонд Жизнь','Санкт-Петербург','Невский пр., 50','+7-812-333-33-33','life@donor.ru');
INSERT INTO participants(full_name,birth_date,phone,email,blood_type,active) VALUES
('Иванов Иван Иванович','1995-04-12','+7-900-001-01-01','ivanov@example.ru','A+',TRUE),
('Петрова Анна Сергеевна','1992-08-21','+7-900-002-02-02','petrova@example.ru','O-',TRUE),
('Сидоров Максим Олегович','1988-01-10','+7-900-003-03-03','sidorov@example.ru','B+',TRUE),
('Кузнецова Мария Игоревна','2000-11-03','+7-900-004-04-04','kuznetsova@example.ru','AB+',TRUE),
('Смирнов Алексей Павлович','1997-06-15','+7-900-005-05-05','smirnov@example.ru','A-',FALSE);
INSERT INTO events(organization_id,title,event_date,city,address,max_participants,status,description) VALUES
(1,'Донорская суббота','2027-03-15','Москва','ул. Поликарпова, 14',50,'OPEN','Городская акция'),
(2,'Капля надежды','2027-04-20','Казань','ул. Баумана, 20',30,'OPEN','Весенняя акция'),
(3,'Подари жизнь','2027-05-10','Санкт-Петербург','Невский пр., 50',40,'PLANNED','Выездная акция'),
(1,'День донора в университете','2025-10-05','Москва','Ленинский пр., 6',25,'COMPLETED','Студенческая акция'),
(2,'Зимний марафон добра','2027-12-12','Казань','ул. Кремлевская, 1',20,'CANCELLED','Отменено организатором');
INSERT INTO registrations(participant_id,event_id,registration_date,status,notes) VALUES
(1,1,'2026-08-01','CONFIRMED','Позвонить за день'),(2,1,'2026-08-02','REGISTERED',NULL),
(3,1,'2026-08-03','CANCELLED','Командировка'),(4,1,'2026-08-04','CONFIRMED',NULL),
(1,2,'2026-08-05','REGISTERED',NULL),(2,2,'2026-08-06','CONFIRMED',NULL),
(3,2,'2026-08-07','REGISTERED','Первый визит'),(4,3,'2026-08-08','REGISTERED',NULL),
(1,4,'2025-09-01','ATTENDED','Успешная донация'),(2,4,'2025-09-02','ATTENDED','Успешная донация');
