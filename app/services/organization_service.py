from app.models import Organization
from app.exceptions import BusinessRuleError,EntityNotFoundError,ValidationError
from app.repositories import OrganizationRepository


class OrganizationService:
    def __init__(self,repo:OrganizationRepository)->None:self.repo=repo
    def list_all(self)->list[Organization]:return self.repo.get_all()
    def get(self,entity_id:int)->Organization:
        item=self.repo.get_by_id(entity_id)
        if not item:raise EntityNotFoundError("Организация не найдена")
        return item
    def save(self,e:Organization)->Organization:
        if not all((e.name.strip(),e.city.strip(),e.address.strip(),e.phone.strip())):raise ValidationError("Заполните обязательные поля организации")
        return self.repo.update(e) if e.id else self.repo.create(e)
    def delete(self,entity_id:int)->None:
        self.get(entity_id)
        if self.repo.has_events(entity_id):raise BusinessRuleError("Нельзя удалить организацию, у которой есть мероприятия")
        self.repo.delete(entity_id)
