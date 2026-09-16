"""
Классы для демонстрации принципов ООП.
Используются традиционные классы с явными __init__, __str__, __repr__,
наследованием и полиморфизмом.
"""
from datetime import date
from typing import Optional


class Person:
    """Базовый класс для всех людей в системе."""

    def __init__(self, full_name: str, phone: str, email: Optional[str] = None):
        self._full_name = full_name
        self._phone = phone
        self._email = email

    @property
    def full_name(self) -> str:
        """Получить полное имя."""
        return self._full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        """Установить полное имя с валидацией."""
        if not value or not value.strip():
            raise ValueError("Имя не может быть пустым")
        self._full_name = value.strip()

    @property
    def phone(self) -> str:
        """Получить телефон."""
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        """Установить телефон."""
        self._phone = value

    @property
    def email(self) -> Optional[str]:
        """Получить email."""
        return self._email

    @email.setter
    def email(self, value: Optional[str]) -> None:
        """Установить email."""
        self._email = value

    def get_contact_info(self) -> str:
        """Получить контактную информацию (полиморфный метод)."""
        email_part = f", email: {self._email}" if self._email else ""
        return f"Телефон: {self._phone}{email_part}"

    def __str__(self) -> str:
        """Строковое представление для пользователя."""
        return f"{self._full_name} ({self.get_contact_info()})"

    def __repr__(self) -> str:
        """Строковое представление для разработчика."""
        return f"Person(full_name='{self._full_name}', phone='{self._phone}', email={self._email!r})"


class Donor(Person):
    """Класс донора, наследуется от Person."""

    def __init__(self, full_name: str, phone: str, birth_date: date,
                 blood_type: str, email: Optional[str] = None):
        super().__init__(full_name, phone, email)
        self._birth_date = birth_date
        self._blood_type = blood_type
        self._donation_count = 0

    @property
    def birth_date(self) -> date:
        """Получить дату рождения."""
        return self._birth_date

    @property
    def blood_type(self) -> str:
        """Получить группу крови."""
        return self._blood_type

    @property
    def donation_count(self) -> int:
        """Получить количество донаций."""
        return self._donation_count

    def register_donation(self) -> None:
        """Зарегистрировать донацию."""
        self._donation_count += 1

    def get_age(self) -> int:
        """Вычислить возраст донора."""
        today = date.today()
        return today.year - self._birth_date.year - (
            (today.month, today.day) < (self._birth_date.month, self._birth_date.day)
        )

    def can_donate(self) -> bool:
        """Проверить, может ли донор сдавать кровь (возраст 18-60)."""
        age = self.get_age()
        return 18 <= age <= 60

    def get_contact_info(self) -> str:
        """Переопределенный метод получения контактов (полиморфизм)."""
        base_info = super().get_contact_info()
        return f"{base_info}, группа крови: {self._blood_type}, донаций: {self._donation_count}"

    def __str__(self) -> str:
        """Строковое представление донора."""
        age = self.get_age()
        status = "активен" if self.can_donate() else "неактивен (возраст)"
        return f"Донор {self._full_name}, {age} лет, {self._blood_type}, {status} ({self._donation_count} донаций)"

    def __repr__(self) -> str:
        """Строковое представление для разработчика."""
        return (f"Donor(full_name='{self._full_name}', phone='{self._phone}', "
                f"birth_date={self._birth_date!r}, blood_type='{self._blood_type}', "
                f"email={self._email!r}, donation_count={self._donation_count})")


class Organizer(Person):
    """Класс организатора мероприятий, наследуется от Person."""

    def __init__(self, full_name: str, phone: str, organization_name: str,
                 email: Optional[str] = None):
        super().__init__(full_name, phone, email)
        self._organization_name = organization_name
        self._events_organized = 0

    @property
    def organization_name(self) -> str:
        """Получить название организации."""
        return self._organization_name

    @property
    def events_organized(self) -> int:
        """Получить количество организованных мероприятий."""
        return self._events_organized

    def add_event(self) -> None:
        """Добавить организованное мероприятие."""
        self._events_organized += 1

    def get_experience_level(self) -> str:
        """Определить уровень опыта организатора."""
        if self._events_organized == 0:
            return "новичок"
        elif self._events_organized < 5:
            return "начинающий"
        elif self._events_organized < 15:
            return "опытный"
        else:
            return "эксперт"

    def get_contact_info(self) -> str:
        """Переопределенный метод получения контактов (полиморфизм)."""
        base_info = super().get_contact_info()
        return f"{base_info}, организация: {self._organization_name}, опыт: {self.get_experience_level()}"

    def __str__(self) -> str:
        """Строковое представление организатора."""
        experience = self.get_experience_level()
        return f"Организатор {self._full_name} ({self._organization_name}), {experience}, {self._events_organized} мероприятий"

    def __repr__(self) -> str:
        """Строковое представление для разработчика."""
        return (f"Organizer(full_name='{self._full_name}', phone='{self._phone}', "
                f"organization_name='{self._organization_name}', email={self._email!r}, "
                f"events_organized={self._events_organized})")


class ContactManager:
    """Класс для управления контактами разных типов людей (полиморфизм)."""

    def __init__(self):
        self._contacts: list[Person] = []

    def add_contact(self, person: Person) -> None:
        """Добавить контакт любого типа Person."""
        self._contacts.append(person)

    def list_all_contacts(self) -> list[str]:
        """Получить список всех контактов (демонстрация полиморфизма)."""
        return [person.get_contact_info() for person in self._contacts]

    def find_by_phone(self, phone: str) -> Optional[Person]:
        """Найти контакт по телефону."""
        for person in self._contacts:
            if person.phone == phone:
                return person
        return None

    def __str__(self) -> str:
        """Строковое представление менеджера контактов."""
        return f"ContactManager с {len(self._contacts)} контактами"

    def __repr__(self) -> str:
        """Строковое представление для разработчика."""
        return f"ContactManager(contacts={len(self._contacts)})"
