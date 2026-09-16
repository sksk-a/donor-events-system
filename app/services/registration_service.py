from datetime import date
from app.models import Registration,RegistrationStatus,RegistrationView,EventStatus
from app.exceptions import BusinessRuleError,EntityNotFoundError
from app.repositories import RegistrationRepository,ParticipantRepository,EventRepository


class RegistrationService:
    TRANSITIONS={RegistrationStatus.REGISTERED:{RegistrationStatus.CONFIRMED,RegistrationStatus.CANCELLED},RegistrationStatus.CONFIRMED:{RegistrationStatus.ATTENDED,RegistrationStatus.CANCELLED},RegistrationStatus.ATTENDED:set(),RegistrationStatus.CANCELLED:set()}
    def __init__(self,repo:RegistrationRepository,participants:ParticipantRepository,events:EventRepository)->None:self.repo=repo;self.participants=participants;self.events=events
    def list_all(self)->list[RegistrationView]:return self.repo.get_views()
    def get(self,entity_id:int)->Registration:
        item=self.repo.get_by_id(entity_id)
        if not item:raise EntityNotFoundError("Регистрация не найдена")
        return item
    def create(self,participant_id:int,event_id:int,notes:str|None=None)->Registration:
        participant=self.participants.get_by_id(participant_id)
        if not participant:raise EntityNotFoundError("Участник не существует")
        event=self.events.get_by_id(event_id)
        if not event:raise EntityNotFoundError("Мероприятие не существует")
        if not participant.active:raise BusinessRuleError("Неактивного участника регистрировать нельзя")
        if event.status in {EventStatus.CANCELLED,EventStatus.COMPLETED}:raise BusinessRuleError("Регистрация на отмененное или завершенное мероприятие запрещена")
        if self.repo.exists(participant_id,event_id):raise BusinessRuleError("Участник уже зарегистрирован на это мероприятие")
        if self.events.registration_count(event_id)>=event.max_participants:raise BusinessRuleError("Свободных мест нет")
        return self.repo.create(Registration(participant_id,event_id,date.today(),notes=notes))
    def change_status(self,entity_id:int,new_status:RegistrationStatus,notes:str|None=None)->Registration:
        item=self.get(entity_id)
        if new_status!=item.status and new_status not in self.TRANSITIONS[item.status]:raise BusinessRuleError(f"Переход {item.status.value} -> {new_status.value} запрещен")
        item.status=new_status
        if notes is not None:item.notes=notes
        return self.repo.update(item)
    def delete(self,entity_id:int)->None:self.get(entity_id);self.repo.delete(entity_id)
    def search(self,term:str)->list[RegistrationView]:return self.repo.search(term)
    def filter(self,**kwargs)->list[RegistrationView]:return self.repo.filter(**kwargs)
    def sort_python(self,items:list[RegistrationView],key:str,reverse:bool=False)->list[RegistrationView]:
        keys={"registration_date":lambda x:x.registration_date,"event_date":lambda x:x.event_date,"participant":lambda x:x.participant_name.casefold(),"event":lambda x:x.event_title.casefold()}
        return sorted(items,key=keys.get(key,keys["event_date"]),reverse=reverse)
    def statistics(self)->dict:return self.repo.statistics()
