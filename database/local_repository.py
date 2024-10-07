from context import database_context
from database.repository_interface import Repository
from models import Local

class LocalRepository(Repository[Local]):
    def find_by_id(self, id: int) -> Local | None: 
        local = None
        with database_context() as connection:
            cursor = connection.cursor()
            row = cursor.execute('''
                SELECT * FROM local WHERE id = ?
            ''', (str(id),)).fetchone()
            if row:
                id, geohash, name = row
                local = Local(id=id, geohash=geohash, name=name)
            return local
            
    def find_all(self) -> list[Local]:
        with database_context() as connection:
            cursor = connection.cursor()
            rows = cursor.execute('''
                SELECT * 
                FROM local
            ''').fetchall()
            locals = []
            for row in rows:
                id, geohash, name = row
                locals.append(Local(id=id, geohash=geohash, name=name))
            return locals 

    def save(self, entity: Local) -> Local:
        with database_context() as connection:
            cursor = connection.cursor()
            if entity.id is None:
                cursor.execute('''
                    INSERT 
                    INTO local (geohash, name)
                    VALUES (?, ?)
                ''', (entity.geohash, entity.name)).fetchone()
            else:
                cursor.execute('''
                    UPDATE local
                    SET geohash = ?, name = ?
                ''', (entity.geohash, entity.name))
            id = cursor.lastrowid
            if id:
                entity.id = id 
            return entity 

    def delete_by_id(self, id: int):
        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM local WHERE id = ?", (str(id),))

    def find_by_query_id(self, id: int) -> list[Local]:
        with database_context() as connection:
            cursor = connection.cursor()
            rows = cursor.execute('''
                SELECT l.id, l.geohash, l.name
                FROM local AS l
                JOIN query_local AS ql ON ql.local_id = l.id
                WHERE ql.query_id = ?
            ''', (str(id))).fetchall()
            locals = []
            for row in rows:
                local_id, geohash, name = row
                locals.append(Local(local_id, geohash, name))
            return locals

    def find_by_name(self, name: str) -> Local | None:
        local = None
        with database_context() as connection:
            cursor = connection.cursor()
            row = cursor.execute('''
                SELECT  l.id, l.geohash, l.name 
                FROM local AS l
                WHERE l.name = ? COLLATE NOCASE
            ''', (name,)).fetchone()
            if row:
                id, geohash, name = row
                local = Local(id=id, geohash=geohash, name=name) 
            return local

