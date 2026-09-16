from app.models import Event, EventStatus
from .base_repository import BaseRepository


class EventRepository(BaseRepository[Event]):
    @staticmethod
    def _map(row: dict) -> Event:
        row["status"] = EventStatus(row["status"]); return Event(**row)

    def create(self, e: Event) -> Event:
        sql="""INSERT INTO events(organization_id,title,event_date,city,address,max_participants,status,description)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id,organization_id,title,event_date,city,address,max_participants,status,description"""
        with self._database.connection() as c, c.cursor() as q:
            q.execute(sql,(e.organization_id,e.title,e.event_date,e.city,e.address,e.max_participants,e.status.value,e.description)); r=self._map(q.fetchone()); c.commit(); return r

    def get_all(self) -> list[Event]:
        with self._database.connection() as c, c.cursor() as q:
            q.execute("SELECT id,organization_id,title,event_date,city,address,max_participants,status,description FROM events ORDER BY event_date,id")
            return [self._map(x) for x in q.fetchall()]

    def get_by_id(self, entity_id: int) -> Event | None:
        with self._database.connection() as c, c.cursor() as q:
            q.execute("SELECT id,organization_id,title,event_date,city,address,max_participants,status,description FROM events WHERE id=%s",(entity_id,)); r=q.fetchone(); return self._map(r) if r else None

    def update(self,e: Event)->Event:
        sql="""UPDATE events SET organization_id=%s,title=%s,event_date=%s,city=%s,address=%s,max_participants=%s,status=%s,description=%s WHERE id=%s
        RETURNING id,organization_id,title,event_date,city,address,max_participants,status,description"""
        with self._database.connection() as c,c.cursor() as q:
            q.execute(sql,(e.organization_id,e.title,e.event_date,e.city,e.address,e.max_participants,e.status.value,e.description,e.id)); r=q.fetchone(); c.commit(); return self._map(r) if r else e

    def delete(self,entity_id:int)->bool:
        with self._database.connection() as c,c.cursor() as q:
            q.execute("DELETE FROM events WHERE id=%s",(entity_id,)); ok=q.rowcount>0;c.commit();return ok

    def registration_count(self,event_id:int)->int:
        with self._database.connection() as c,c.cursor() as q:
            q.execute("SELECT COUNT(*) AS count FROM registrations WHERE event_id=%s AND status<>'CANCELLED'",(event_id,));return q.fetchone()["count"]

    def has_registrations(self,event_id:int)->bool:
        with self._database.connection() as c,c.cursor() as q:
            q.execute("SELECT EXISTS(SELECT 1 FROM registrations WHERE event_id=%s) AS value",(event_id,));return q.fetchone()["value"]
