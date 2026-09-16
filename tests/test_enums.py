import pytest
from app.models.enums import EventStatus, RegistrationStatus, BloodType


class TestEnums:
    def test_event_status_values(self):
        assert EventStatus.PLANNED.value == "PLANNED"
        assert EventStatus.OPEN.value == "OPEN"
        assert EventStatus.COMPLETED.value == "COMPLETED"
        assert EventStatus.CANCELLED.value == "CANCELLED"

    def test_registration_status_values(self):
        assert RegistrationStatus.REGISTERED.value == "REGISTERED"
        assert RegistrationStatus.CONFIRMED.value == "CONFIRMED"
        assert RegistrationStatus.ATTENDED.value == "ATTENDED"
        assert RegistrationStatus.CANCELLED.value == "CANCELLED"

    def test_blood_type_values(self):
        assert BloodType.A_POS.value == "A+"
        assert BloodType.O_NEG.value == "O-"
        assert BloodType.AB_POS.value == "AB+"

    def test_enum_membership(self):
        assert EventStatus.PLANNED in EventStatus
        assert "PLANNED" == EventStatus.PLANNED.value

    def test_create_enum_from_string(self):
        status = EventStatus("OPEN")
        assert status == EventStatus.OPEN

    def test_invalid_enum_value_raises_error(self):
        with pytest.raises(ValueError):
            EventStatus("INVALID_STATUS")
