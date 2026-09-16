from app.models import Participant
from app.exceptions import EntityNotFoundError,ValidationError
from app.repositories import ParticipantRepository


class ParticipantService:
    def __init__(self,repo:ParticipantRepository)->None:self.repo=repo
    def list_all(self)->list[Participant]:return self.repo.get_all()
    def get(self,entity_id:int)->Participant:
        item=self.repo.get_by_id(entity_id)
        if not item:raise EntityNotFoundError("Участник не найден")
        return item
    def save(self,e:Participant)->Participant:
        if not e.full_name.strip() or not e.phone.strip():raise ValidationError("ФИО и телефон обязательны")
        return self.repo.update(e) if e.id else self.repo.create(e)
    def delete(self,entity_id:int)->None:self.get(entity_id);self.repo.delete(entity_id)
