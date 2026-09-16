from app.models import Organization
from .base_repository import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    @staticmethod
    def _map(row: dict) -> Organization:
        return Organization(**row)

    def create(self, entity: Organization) -> Organization:
        sql = """INSERT INTO organizations(name,city,address,phone,email) VALUES(%s,%s,%s,%s,%s)
                 RETURNING id,name,city,address,phone,email"""
        with self._database.connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (entity.name, entity.city, entity.address, entity.phone, entity.email))
            result = self._map(cur.fetchone()); conn.commit(); return result

    def get_all(self) -> list[Organization]:
        with self._database.connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT id,name,city,address,phone,email FROM organizations ORDER BY id")
            return [self._map(row) for row in cur.fetchall()]

    def get_by_id(self, entity_id: int) -> Organization | None:
        with self._database.connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT id,name,city,address,phone,email FROM organizations WHERE id=%s", (entity_id,))
            row = cur.fetchone(); return self._map(row) if row else None

    def update(self, e: Organization) -> Organization:
        sql = """UPDATE organizations SET name=%s,city=%s,address=%s,phone=%s,email=%s WHERE id=%s
                 RETURNING id,name,city,address,phone,email"""
        with self._database.connection() as conn, conn.cursor() as cur:
            cur.execute(sql, (e.name,e.city,e.address,e.phone,e.email,e.id)); row=cur.fetchone(); conn.commit()
            return self._map(row) if row else e

    def delete(self, entity_id: int) -> bool:
        with self._database.connection() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM organizations WHERE id=%s", (entity_id,)); ok=cur.rowcount>0; conn.commit(); return ok

    def has_events(self, entity_id: int) -> bool:
        with self._database.connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT EXISTS(SELECT 1 FROM events WHERE organization_id=%s) AS value", (entity_id,))
            return bool(cur.fetchone()["value"])
