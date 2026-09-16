import pytest
from unittest.mock import Mock
from app.services import OrganizationService
from app.models import Organization
from app.exceptions import EntityNotFoundError, ValidationError, BusinessRuleError


class TestOrganizationService:
    def setup_method(self):
        self.repo = Mock()
        self.service = OrganizationService(self.repo)

    def test_list_all(self):
        expected = [
            Organization("Org1", "City1", "Addr1", "Phone1", "email1@test.ru", 1),
            Organization("Org2", "City2", "Addr2", "Phone2", None, 2)
        ]
        self.repo.get_all.return_value = expected
        result = self.service.list_all()
        assert result == expected
        self.repo.get_all.assert_called_once()

    def test_get_existing_organization(self):
        org = Organization("Test Org", "Moscow", "Addr", "Phone", None, 1)
        self.repo.get_by_id.return_value = org
        result = self.service.get(1)
        assert result == org
        self.repo.get_by_id.assert_called_once_with(1)

    def test_get_nonexistent_organization_raises_error(self):
        self.repo.get_by_id.return_value = None
        with pytest.raises(EntityNotFoundError, match="Организация не найдена"):
            self.service.get(999)

    def test_save_new_organization(self):
        org = Organization("New Org", "Kazan", "Address", "+7123456", "test@test.ru")
        self.repo.create.return_value = Organization("New Org", "Kazan", "Address", "+7123456", "test@test.ru", 10)
        result = self.service.save(org)
        assert result.id == 10
        self.repo.create.assert_called_once_with(org)

    def test_save_organization_with_empty_fields_raises_error(self):
        org = Organization("", "City", "Address", "Phone", None)
        with pytest.raises(ValidationError, match="Заполните обязательные поля"):
            self.service.save(org)

    def test_delete_organization_with_events_raises_error(self):
        self.repo.get_by_id.return_value = Organization("Org", "City", "Addr", "Phone", None, 5)
        self.repo.has_events.return_value = True
        with pytest.raises(BusinessRuleError, match="Нельзя удалить организацию"):
            self.service.delete(5)
        self.repo.delete.assert_not_called()

    def test_delete_organization_without_events(self):
        self.repo.get_by_id.return_value = Organization("Org", "City", "Addr", "Phone", None, 5)
        self.repo.has_events.return_value = False
        self.service.delete(5)
        self.repo.delete.assert_called_once_with(5)
