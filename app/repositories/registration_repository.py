from datetime import date
from app.models import Registration, RegistrationStatus, RegistrationView
from .base_repository import BaseRepository

FIELDS="""r.id,r.participant_id,r.event_id,r.registration_date,r.status,r.notes"""
VIEW_FIELDS="""r.id,r.participant_id,p.full_name AS participant_name,r.event_id,e.title AS event_title,
o.name AS organization_name,e.event_date,e.city,r.registration_date,r.status,e.status AS event_status,r.notes"""
JOINS=""" FROM registrations r JOIN participants p ON p.id=r.participant_id
JOIN events e ON e.id=r.event_id JOIN organizations o ON o.id=e.organization_id """


class RegistrationRepository(BaseRepository[Registration]):
    @staticmethod
    def _map(r:dict)->Registration:
        r["status"]=RegistrationStatus(r["status"]);return Registration(**r)
    @staticmethod
    def _view(r:dict)->RegistrationView:
        r["status"]=RegistrationStatus(r["status"]);return RegistrationView(**r)
    def create(self,e:Registration)->Registration:
        with self._database.connection() as c,c.cursor() as q:
            q.execute("INSERT INTO registrations(participant_id,event_id,registration_date,status,notes) VALUES(%s,%s,%s,%s,%s) RETURNING "+FIELDS,(e.participant_id,e.event_id,e.registration_date,e.status.value,e.notes));r=self._map(q.fetchone());c.commit();return r
    def get_all(self)->list[Registration]:
        with self._database.connection() as c,c.cursor() as q:
            q.execute("SELECT "+FIELDS+" FROM registrations r ORDER BY r.id");return [self._map(x) for x in q.fetchall()]
    def get_views(self)->list[RegistrationView]:
        with self._database.connection() as c,c.cursor() as q:
            q.execute("SELECT "+VIEW_FIELDS+JOINS+" ORDER BY r.id");return [self._view(x) for x in q.fetchall()]
    def get_by_id(self,entity_id:int)->Registration|None:
        with self._database.connection() as c,c.cursor() as q:
            q.execute("SELECT "+FIELDS+" FROM registrations r WHERE r.id=%s",(entity_id,));r=q.fetchone();return self._map(r) if r else None
    def update(self,e:Registration)->Registration:
        with self._database.connection() as c,c.cursor() as q:
            q.execute("UPDATE registrations r SET participant_id=%s,event_id=%s,registration_date=%s,status=%s,notes=%s WHERE id=%s RETURNING "+FIELDS,(e.participant_id,e.event_id,e.registration_date,e.status.value,e.notes,e.id));r=q.fetchone();c.commit();return self._map(r) if r else e
    def delete(self,entity_id:int)->bool:
        with self._database.connection() as c,c.cursor() as q:
            q.execute("DELETE FROM registrations WHERE id=%s",(entity_id,));ok=q.rowcount>0;c.commit();return ok
    def exists(self,participant_id:int,event_id:int,exclude_id:int|None=None)->bool:
        sql="SELECT EXISTS(SELECT 1 FROM registrations WHERE participant_id=%s AND event_id=%s"+(" AND id<>%s" if exclude_id else "")+") AS value"
        params=(participant_id,event_id,exclude_id) if exclude_id else (participant_id,event_id)
        with self._database.connection() as c,c.cursor() as q:q.execute(sql,params);return q.fetchone()["value"]
    def search(self,term:str)->list[RegistrationView]:
        sql="SELECT "+VIEW_FIELDS+JOINS+" WHERE p.full_name ILIKE %s OR e.title ILIKE %s OR o.name ILIKE %s ORDER BY e.event_date"
        pattern=f"%{term}%"
        with self._database.connection() as c,c.cursor() as q:q.execute(sql,(pattern,pattern,pattern));return [self._view(x) for x in q.fetchall()]
    def filter(self,registration_status:RegistrationStatus|None=None,event_status:str|None=None,organization_id:int|None=None,city:str|None=None,date_from:date|None=None,date_to:date|None=None)->list[RegistrationView]:
        clauses=[];params=[]
        for condition,value in [("r.status=%s",registration_status.value if registration_status else None),("e.status=%s",event_status),("o.id=%s",organization_id),("e.city ILIKE %s",f"%{city}%" if city else None),("e.event_date>=%s",date_from),("e.event_date<=%s",date_to)]:
            if value is not None:clauses.append(condition);params.append(value)
        sql="SELECT "+VIEW_FIELDS+JOINS+(" WHERE "+" AND ".join(clauses) if clauses else "")+" ORDER BY e.event_date"
        with self._database.connection() as c,c.cursor() as q:q.execute(sql,tuple(params));return [self._view(x) for x in q.fetchall()]
    def statistics(self)->dict:
        sql="""SELECT (SELECT COUNT(*) FROM organizations) organizations,(SELECT COUNT(*) FROM events) events,
        (SELECT COUNT(*) FROM participants) participants,(SELECT COUNT(*) FROM registrations) registrations,
        COUNT(*) FILTER(WHERE status='CONFIRMED') confirmed,COUNT(*) FILTER(WHERE status='CANCELLED') cancelled,
        COUNT(*) FILTER(WHERE status='ATTENDED') attended FROM registrations"""
        with self._database.connection() as c,c.cursor() as q:
            q.execute(sql);data=dict(q.fetchone())
            q.execute("SELECT status,COUNT(*) count FROM registrations GROUP BY status ORDER BY status");data["by_status"]={x["status"]:x["count"] for x in q.fetchall()}
            q.execute("SELECT COALESCE(AVG(count),0)::numeric(10,2) average FROM (SELECT COUNT(r.id) count FROM events e LEFT JOIN registrations r ON r.event_id=e.id GROUP BY e.id) s");data["average_per_event"]=q.fetchone()["average"]
            q.execute("SELECT e.title,COUNT(r.id) count FROM events e LEFT JOIN registrations r ON r.event_id=e.id GROUP BY e.id ORDER BY count DESC,e.title LIMIT 1");data["top_event"]=dict(q.fetchone())
            q.execute("SELECT o.name,COUNT(e.id) count FROM organizations o LEFT JOIN events e ON e.organization_id=o.id GROUP BY o.id ORDER BY o.name");data["events_by_organization"]={x["name"]:x["count"] for x in q.fetchall()}
            q.execute("SELECT e.title,GREATEST(e.max_participants-COUNT(r.id) FILTER(WHERE r.status<>'CANCELLED'),0) free FROM events e LEFT JOIN registrations r ON r.event_id=e.id WHERE e.status='OPEN' GROUP BY e.id ORDER BY e.title");data["free_places"]={x["title"]:x["free"] for x in q.fetchall()};return data
