from app.models import Participant, BloodType
from .base_repository import BaseRepository


class ParticipantRepository(BaseRepository[Participant]):
    @staticmethod
    def _map(r:dict)->Participant:
        r["blood_type"]=BloodType(r["blood_type"]);return Participant(**r)
    def create(self,e:Participant)->Participant:
        with self._database.connection() as c,c.cursor() as q:
            q.execute("INSERT INTO participants(full_name,birth_date,phone,email,blood_type,active) VALUES(%s,%s,%s,%s,%s,%s) RETURNING id,full_name,birth_date,phone,email,blood_type,active",(e.full_name,e.birth_date,e.phone,e.email,e.blood_type.value,e.active));r=self._map(q.fetchone());c.commit();return r
    def get_all(self)->list[Participant]:
        with self._database.connection() as c,c.cursor() as q:
            q.execute("SELECT id,full_name,birth_date,phone,email,blood_type,active FROM participants ORDER BY full_name");return [self._map(x) for x in q.fetchall()]
    def get_by_id(self,entity_id:int)->Participant|None:
        with self._database.connection() as c,c.cursor() as q:
            q.execute("SELECT id,full_name,birth_date,phone,email,blood_type,active FROM participants WHERE id=%s",(entity_id,));r=q.fetchone();return self._map(r) if r else None
    def update(self,e:Participant)->Participant:
        with self._database.connection() as c,c.cursor() as q:
            q.execute("UPDATE participants SET full_name=%s,birth_date=%s,phone=%s,email=%s,blood_type=%s,active=%s WHERE id=%s RETURNING id,full_name,birth_date,phone,email,blood_type,active",(e.full_name,e.birth_date,e.phone,e.email,e.blood_type.value,e.active,e.id));r=q.fetchone();c.commit();return self._map(r) if r else e
    def delete(self,entity_id:int)->bool:
        with self._database.connection() as c,c.cursor() as q:
            q.execute("UPDATE participants SET active=FALSE WHERE id=%s",(entity_id,));ok=q.rowcount>0;c.commit();return ok
