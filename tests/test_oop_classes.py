import pytest
from datetime import date
from app.models.oop_classes import Person, Donor, Organizer, ContactManager


class TestPerson:
    def test_create_person(self):
        person = Person("Иванов Иван", "+79991234567", "ivan@test.ru")
        assert person.full_name == "Иванов Иван"
        assert person.phone == "+79991234567"
        assert person.email == "ivan@test.ru"

    def test_person_without_email(self):
        person = Person("Петров Петр", "+79997654321")
        assert person.email is None

    def test_person_str(self):
        person = Person("Сидоров Сидор", "+79995556677", "sidorov@test.ru")
        result = str(person)
        assert "Сидоров Сидор" in result
        assert "+79995556677" in result

    def test_person_repr(self):
        person = Person("Test User", "1234567890")
        result = repr(person)
        assert "Person" in result
        assert "Test User" in result

    def test_person_property_setter(self):
        person = Person("Old Name", "1111111111")
        person.full_name = "New Name"
        assert person.full_name == "New Name"

    def test_person_empty_name_raises_error(self):
        person = Person("Valid Name", "1234567890")
        with pytest.raises(ValueError, match="Имя не может быть пустым"):
            person.full_name = ""


class TestDonor:
    def test_create_donor(self):
        donor = Donor("Донор Тест", "+79991112233", date(1990, 5, 15), "A+", "donor@test.ru")
        assert donor.full_name == "Донор Тест"
        assert donor.blood_type == "A+"
        assert donor.donation_count == 0

    def test_donor_age_calculation(self):
        # Донор родился 30 лет назад
        birth = date(1994, 1, 1)
        donor = Donor("Test", "123", birth, "O+")
        age = donor.get_age()
        assert age >= 30  # Может быть 30 или 31 в зависимости от текущей даты

    def test_donor_can_donate(self):
        young_donor = Donor("Молодой", "111", date(2005, 1, 1), "A+")
        adult_donor = Donor("Взрослый", "222", date(1990, 1, 1), "B+")
        old_donor = Donor("Пожилой", "333", date(1950, 1, 1), "AB+")

        assert young_donor.can_donate() is True  # ~21 год
        assert adult_donor.can_donate() is True  # ~36 лет
        assert old_donor.can_donate() is False  # ~76 лет

    def test_donor_register_donation(self):
        donor = Donor("Test", "123", date(1990, 1, 1), "O-")
        assert donor.donation_count == 0
        donor.register_donation()
        assert donor.donation_count == 1
        donor.register_donation()
        donor.register_donation()
        assert donor.donation_count == 3

    def test_donor_polymorphism_get_contact_info(self):
        donor = Donor("Донор", "+71234567890", date(1990, 1, 1), "AB+")
        info = donor.get_contact_info()
        assert "AB+" in info
        assert "донаций: 0" in info

    def test_donor_str(self):
        donor = Donor("Тестовый Донор", "123", date(1995, 1, 1), "O-")
        result = str(donor)
        assert "Донор" in result
        assert "O-" in result

    def test_donor_repr(self):
        donor = Donor("Test", "123", date(1990, 5, 15), "A+")
        result = repr(donor)
        assert "Donor" in result
        assert "A+" in result


class TestOrganizer:
    def test_create_organizer(self):
        org = Organizer("Организатор Тест", "+79998887766", "Красный Крест", "org@test.ru")
        assert org.full_name == "Организатор Тест"
        assert org.organization_name == "Красный Крест"
        assert org.events_organized == 0

    def test_organizer_add_event(self):
        org = Organizer("Test", "123", "Test Org")
        assert org.events_organized == 0
        org.add_event()
        assert org.events_organized == 1
        org.add_event()
        org.add_event()
        assert org.events_organized == 3

    def test_organizer_experience_levels(self):
        novice = Organizer("Новичок", "111", "Org1")
        beginner = Organizer("Начинающий", "222", "Org2")
        experienced = Organizer("Опытный", "333", "Org3")
        expert = Organizer("Эксперт", "444", "Org4")

        assert novice.get_experience_level() == "новичок"

        for _ in range(3):
            beginner.add_event()
        assert beginner.get_experience_level() == "начинающий"

        for _ in range(10):
            experienced.add_event()
        assert experienced.get_experience_level() == "опытный"

        for _ in range(20):
            expert.add_event()
        assert expert.get_experience_level() == "эксперт"

    def test_organizer_polymorphism_get_contact_info(self):
        org = Organizer("Org Test", "+71112223344", "Донор Плюс")
        for _ in range(7):
            org.add_event()
        info = org.get_contact_info()
        assert "Донор Плюс" in info
        assert "опыт:" in info

    def test_organizer_str(self):
        org = Organizer("Главный Организатор", "123", "Лучшая Организация")
        result = str(org)
        assert "Организатор" in result
        assert "Лучшая Организация" in result

    def test_organizer_repr(self):
        org = Organizer("Test", "123", "Test Org")
        result = repr(org)
        assert "Organizer" in result
        assert "Test Org" in result


class TestContactManager:
    def test_create_contact_manager(self):
        manager = ContactManager()
        assert len(manager.list_all_contacts()) == 0

    def test_add_different_types(self):
        manager = ContactManager()
        person = Person("Человек", "111")
        donor = Donor("Донор", "222", date(1990, 1, 1), "A+")
        organizer = Organizer("Организатор", "333", "Орг")

        manager.add_contact(person)
        manager.add_contact(donor)
        manager.add_contact(organizer)

        contacts = manager.list_all_contacts()
        assert len(contacts) == 3

    def test_polymorphism_in_list(self):
        """Демонстрация полиморфизма: разные типы, один метод."""
        manager = ContactManager()
        donor = Donor("Донор", "111", date(1990, 1, 1), "O+")
        donor.register_donation()
        organizer = Organizer("Организатор", "222", "Орг")
        organizer.add_event()

        manager.add_contact(donor)
        manager.add_contact(organizer)

        contacts = manager.list_all_contacts()
        assert "O+" in contacts[0]
        assert "Орг" in contacts[1]

    def test_find_by_phone(self):
        manager = ContactManager()
        person = Person("Test", "+79991234567")
        manager.add_contact(person)

        found = manager.find_by_phone("+79991234567")
        assert found is not None
        assert found.full_name == "Test"

        not_found = manager.find_by_phone("+70000000000")
        assert not_found is None

    def test_contact_manager_str(self):
        manager = ContactManager()
        manager.add_contact(Person("P1", "111"))
        manager.add_contact(Person("P2", "222"))
        result = str(manager)
        assert "ContactManager" in result
        assert "2" in result
