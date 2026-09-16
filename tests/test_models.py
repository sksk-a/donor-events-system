from datetime import date
from app.models import Organization, Event, Participant
from app.models.enums import EventStatus, BloodType


class TestOrganization:
    def test_create_organization(self):
        org = Organization(
            name="Красный Крест",
            city="Москва",
            address="ул. Пушкина, д. 1",
            phone="+7 (495) 123-45-67",
            email="info@redcross.ru"
        )
        assert org.name == "Красный Крест"
        assert org.city == "Москва"
        assert org.id is None

    def test_organization_without_email(self):
        org = Organization(
            name="Донор",
            city="Санкт-Петербург",
            address="Невский пр., 10",
            phone="+7 (812) 987-65-43",
            email=None
        )
        assert org.email is None


class TestEvent:
    def test_create_event(self):
        event = Event(
            organization_id=1,
            title="День донора",
            event_date=date(2026, 10, 15),
            city="Москва",
            address="пр. Мира, 20",
            max_participants=50,
            status=EventStatus.PLANNED,
            description="Донорская акция"
        )
        assert event.title == "День донора"
        assert event.max_participants == 50
        assert event.status == EventStatus.PLANNED

    def test_event_default_status(self):
        event = Event(
            organization_id=1,
            title="Акция",
            event_date=date(2026, 11, 1),
            city="Казань",
            address="ул. Баумана, 5",
            max_participants=30
        )
        assert event.status == EventStatus.PLANNED


class TestParticipant:
    def test_create_participant(self):
        participant = Participant(
            full_name="Иванов Иван Иванович",
            birth_date=date(1990, 5, 15),
            phone="+7 (999) 123-45-67",
            email="ivanov@mail.ru",
            blood_type=BloodType.A_POS
        )
        assert participant.full_name == "Иванов Иван Иванович"
        assert participant.blood_type == BloodType.A_POS
        assert participant.active is True

    def test_participant_blood_types(self):
        for bt in [BloodType.A_POS, BloodType.B_NEG, BloodType.O_POS]:
            p = Participant(
                full_name="Test",
                birth_date=date(1995, 1, 1),
                phone="1234567890",
                email=None,
                blood_type=bt
            )
            assert p.blood_type == bt
