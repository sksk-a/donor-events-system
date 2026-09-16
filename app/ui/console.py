from dataclasses import asdict
from app.exceptions import AppError
from app.models import Organization,Event,Participant,BloodType,EventStatus,RegistrationStatus
from app.repositories import OrganizationRepository,EventRepository,ParticipantRepository,RegistrationRepository
from app.services import OrganizationService,EventService,ParticipantService,RegistrationService
from app.utils.database import Database
from app.utils.input_utils import InputUtils as I
from app.utils.excel_exporter import ExcelExporter


class ConsoleApp:
    """Cyclic console UI; delegates business logic and SQL to lower layers."""
    def __init__(self)->None:
        db=Database();self.org_repo=OrganizationRepository(db);self.event_repo=EventRepository(db);self.part_repo=ParticipantRepository(db);self.reg_repo=RegistrationRepository(db)
        self.organizations=OrganizationService(self.org_repo);self.events=EventService(self.event_repo,self.org_repo);self.participants=ParticipantService(self.part_repo);self.registrations=RegistrationService(self.reg_repo,self.part_repo,self.event_repo)
    @staticmethod
    def _print(items:list)->None:
        if not items:print("Результаты не найдены.");return
        rows=[asdict(x) for x in items];headers=list(rows[0]);widths={h:min(32,max(len(h),*(len(str(r[h])) for r in rows))) for h in headers}
        print(" | ".join(h.ljust(widths[h]) for h in headers));print("-+-".join("-"*widths[h] for h in headers))
        for row in rows:print(" | ".join(str(row[h].value if hasattr(row[h],"value") else row[h] if row[h] is not None else "").ljust(widths[h])[:widths[h]] for h in headers))
    def run(self)->None:
        actions={"1":self._organizations,"2":self._events,"3":self._participants,"4":self._registrations,"5":self._search,"6":self._filter,"7":self._sort,"8":self._statistics,"9":self._export,"10":self._tables}
        while True:
            try:
                print("\n================ СЕРВИС ДОНОРСКИХ МЕРОПРИЯТИЙ ================\n1. Организации\n2. Мероприятия\n3. Участники\n4. Регистрации\n5. Поиск регистраций\n6. Фильтрация регистраций\n7. Сортировка регистраций\n8. Статистика\n9. Экспорт данных в Excel\n10. Вывести таблицы базы данных\n0. Выход")
                choice=input("Выберите действие: ").strip()
                if choice=="0":print("До свидания!");return
                action=actions.get(choice)
                if action:action()
                else:print("Нет такого пункта.")
            except (AppError,ValueError) as exc:print(f"Ошибка: {exc}")
            except (EOFError,KeyboardInterrupt):print("\nРабота завершена.");return
    def _organizations(self)->None:
        while True:
            print("\nОрганизации: 1-все 2-по ID 3-создать 4-изменить 5-удалить 0-назад");c=input("> ").strip()
            if c=="0":return
            if c=="1":self._print(self.organizations.list_all())
            elif c=="2":self._print([self.organizations.get(I.read_int("ID: ",1))])
            elif c in {"3","4"}:
                old=self.organizations.get(I.read_int("ID: ",1)) if c=="4" else None
                e=Organization(I.read_non_empty("Название: ",old.name if old else None),I.read_non_empty("Город: ",old.city if old else None),I.read_non_empty("Адрес: ",old.address if old else None),I.read_non_empty("Телефон: ",old.phone if old else None),input("Email (можно пусто): ").strip() or (old.email if old else None),old.id if old else None);self._print([self.organizations.save(e)])
            elif c=="5":self.organizations.delete(I.read_int("ID: ",1));print("Удалено.")
    def _events(self)->None:
        while True:
            print("\nМероприятия: 1-все 2-по ID 3-создать 4-изменить 5-удалить 0-назад");c=input("> ").strip()
            if c=="0":return
            if c=="1":self._print(self.events.list_all())
            elif c=="2":self._print([self.events.get(I.read_int("ID: ",1))])
            elif c in {"3","4"}:
                old=self.events.get(I.read_int("ID: ",1)) if c=="4" else None
                e=Event(I.read_int("ID организации: ",1,old.organization_id if old else None),I.read_non_empty("Название: ",old.title if old else None),I.read_date("Дата YYYY-MM-DD: ",old.event_date if old else None),I.read_non_empty("Город: ",old.city if old else None),I.read_non_empty("Адрес: ",old.address if old else None),I.read_int("Лимит: ",1,old.max_participants if old else None),I.read_enum("Статус",EventStatus,old.status if old else EventStatus.PLANNED),input("Описание: ").strip() or (old.description if old else None),old.id if old else None);self._print([self.events.save(e)])
            elif c=="5":self.events.delete(I.read_int("ID: ",1));print("Удалено.")
    def _participants(self)->None:
        while True:
            print("\nУчастники: 1-все 2-по ID 3-создать 4-изменить 5-деактивировать 0-назад");c=input("> ").strip()
            if c=="0":return
            if c=="1":self._print(self.participants.list_all())
            elif c=="2":self._print([self.participants.get(I.read_int("ID: ",1))])
            elif c in {"3","4"}:
                old=self.participants.get(I.read_int("ID: ",1)) if c=="4" else None
                e=Participant(I.read_non_empty("ФИО: ",old.full_name if old else None),I.read_date("Дата рождения: ",old.birth_date if old else None),I.read_non_empty("Телефон: ",old.phone if old else None),input("Email: ").strip() or (old.email if old else None),I.read_enum("Группа крови",BloodType,old.blood_type if old else None),old.active if old else True,old.id if old else None);self._print([self.participants.save(e)])
            elif c=="5":self.participants.delete(I.read_int("ID: ",1));print("Участник деактивирован.")
    def _registrations(self)->None:
        while True:
            print("\nРегистрации: 1-все 2-по ID 3-создать 4-изменить статус 5-удалить 0-назад");c=input("> ").strip()
            if c=="0":return
            if c=="1":self._print(self.registrations.list_all())
            elif c=="2":self._print([self.registrations.get(I.read_int("ID: ",1))])
            elif c=="3":self._print([self.registrations.create(I.read_int("ID участника: ",1),I.read_int("ID мероприятия: ",1),input("Примечание: ").strip() or None)])
            elif c=="4":self._print([self.registrations.change_status(I.read_int("ID регистрации: ",1),I.read_enum("Новый статус",RegistrationStatus),input("Примечание (пусто = не менять): ").strip() or None)])
            elif c=="5":self.registrations.delete(I.read_int("ID: ",1));print("Удалено.")
    def _search(self)->None:
        raw=input("ID регистрации или текст (ФИО/мероприятие/организация): ").strip()
        self._print([self.registrations.get(int(raw))] if raw.isdigit() else self.registrations.search(raw))
    def _filter(self)->None:
        print("Пустое поле означает 'любой'.")
        rs=input("Статус регистрации: ").strip().upper();es=input("Статус мероприятия: ").strip().upper();org=input("ID организации: ").strip();city=input("Город: ").strip()
        self._print(self.registrations.filter(registration_status=RegistrationStatus(rs) if rs else None,event_status=EventStatus(es).value if es else None,organization_id=int(org) if org else None,city=city or None))
    def _sort(self)->None:
        key=input("Ключ (registration_date/event_date/participant/event): ").strip();reverse=input("По убыванию? (д/н): ").strip().lower()=="д"
        self._print(self.registrations.sort_python(self.registrations.list_all(),key,reverse))
    def _statistics(self)->None:
        s=self.registrations.statistics();print(f"Организаций: {s['organizations']}\nМероприятий: {s['events']}\nУчастников: {s['participants']}\nРегистраций: {s['registrations']}\nПодтверждено: {s['confirmed']}\nОтменено: {s['cancelled']}\nПосетили: {s['attended']}\nСреднее на мероприятие: {s['average_per_event']}\nЛидер: {s['top_event']}\nПо статусам: {s['by_status']}\nМероприятий по организациям: {s['events_by_organization']}\nСвободные места: {s['free_places']}")
    def _export(self)->None:
        path=ExcelExporter.export({"Organizations":self.organizations.list_all(),"Events":self.events.list_all(),"Participants":self.participants.list_all(),"Registrations":self.registrations.list_all()});print(f"Создан файл: {path}")
    def _tables(self)->None:
        choice=input("1-organizations 2-events 3-participants 4-registrations: ").strip();items={"1":self.organizations.list_all,"2":self.events.list_all,"3":self.participants.list_all,"4":self.registrations.list_all}.get(choice);self._print(items() if items else [])
