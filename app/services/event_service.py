from datetime import date
from app.models import Event,EventStatus
from app.exceptions import BusinessRuleError,EntityNotFoundError,ValidationError
from app.repositories import EventRepository,OrganizationRepository


class EventService:
    def __init__(self,repo:EventRepository,organizations:OrganizationRepository)->None:self.repo=repo;self.organizations=organizations
    def list_all(self)->list[Event]:return self.repo.get_all()
    def get(self,entity_id:int)->Event:
        item=self.repo.get_by_id(entity_id)
        if not item:raise EntityNotFoundError("Мероприятие не найдено")
        return item
    def save(self,e:Event)->Event:
        if not self.organizations.get_by_id(e.organization_id):raise EntityNotFoundError("Организация не найдена")
        if not e.title.strip() or e.max_participants<=0:raise ValidationError("Название обязательно, лимит должен быть больше нуля")
        if e.id is None and e.event_date<date.today():raise BusinessRuleError("Дата нового мероприятия не может быть в прошлом")
        if e.id and self.repo.registration_count(e.id)>e.max_participants:raise BusinessRuleError("Лимит меньше числа действующих регистраций")
        return self.repo.update(e) if e.id else self.repo.create(e)
    def delete(self,entity_id:int)->None:
        self.get(entity_id)
        if self.repo.has_registrations(entity_id):raise BusinessRuleError("Нельзя удалить мероприятие с регистрациями")
        self.repo.delete(entity_id)
