DROP TABLE IF EXISTS registrations, events, participants, organizations CASCADE;
CREATE TABLE organizations(
 id BIGSERIAL PRIMARY KEY,name VARCHAR(150) NOT NULL,city VARCHAR(100) NOT NULL,address VARCHAR(200) NOT NULL,
 phone VARCHAR(30) NOT NULL,email VARCHAR(150) UNIQUE);
CREATE TABLE participants(
 id BIGSERIAL PRIMARY KEY,full_name VARCHAR(180) NOT NULL,birth_date DATE NOT NULL,phone VARCHAR(30) NOT NULL,
 email VARCHAR(150) UNIQUE,blood_type VARCHAR(3) NOT NULL CHECK(blood_type IN('A+','A-','B+','B-','AB+','AB-','O+','O-')),
 active BOOLEAN NOT NULL DEFAULT TRUE);
CREATE TABLE events(
 id BIGSERIAL PRIMARY KEY,organization_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE RESTRICT,
 title VARCHAR(180) NOT NULL,event_date DATE NOT NULL,city VARCHAR(100) NOT NULL,address VARCHAR(200) NOT NULL,
 max_participants INTEGER NOT NULL CHECK(max_participants>0),status VARCHAR(20) NOT NULL CHECK(status IN('PLANNED','OPEN','COMPLETED','CANCELLED')),description TEXT);
CREATE TABLE registrations(
 id BIGSERIAL PRIMARY KEY,participant_id BIGINT NOT NULL REFERENCES participants(id) ON DELETE RESTRICT,
 event_id BIGINT NOT NULL REFERENCES events(id) ON DELETE RESTRICT,registration_date DATE NOT NULL DEFAULT CURRENT_DATE,
 status VARCHAR(20) NOT NULL CHECK(status IN('REGISTERED','CONFIRMED','ATTENDED','CANCELLED')),notes TEXT,
 UNIQUE(participant_id,event_id));
CREATE INDEX idx_registrations_event ON registrations(event_id);
CREATE INDEX idx_registrations_participant ON registrations(participant_id);
