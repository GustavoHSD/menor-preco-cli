from context import database_context
from database.repository_interface import Repository
from error.EntityNotDeleted import EntityNotDeleted
from error.EntityNotFound import EntityNotFound
from error.EntityNotSaved import EntityNotSaved
from error.Result import Result
from models import Local

class LocalRepository(Repository[Local]):
    def find_by_id(self, id: int) -> Result[Local, EntityNotFound]: 
        with database_context() as connection:
            cursor = connection.cursor()
            try:
                row = cursor.execute('''
                    SELECT * FROM local WHERE id = ?
                ''', (str(id),)).fetchone()
                if row is None:
                    return Result(None, EntityNotFound(f"Could not find local of id: {id}"))
            except Exception as err:
                return Result(None, EntityNotFound(f"Could not find local of id: {id}", err))

            id, geohash, name = row
            local = Local(id=id, geohash=geohash, name=name)
            return Result(local, None)
            
    def find_all(self) -> Result[list[Local], EntityNotFound]:
        with database_context() as connection:
            cursor = connection.cursor()
            try:
                rows = cursor.execute('''
                    SELECT * 
                    FROM local
                ''').fetchall()
                if len(rows) == 0:
                    return Result(None, EntityNotFound("No locals found"))
            except Exception as err:
                return Result(None, EntityNotFound(f"No locals found", err))
            locals = []
            for row in rows:
                id, geohash, name = row
                locals.append(Local(id=id, geohash=geohash, name=name))
            return Result(locals, None)

    def save(self, entity: Local) -> Result[Local, EntityNotSaved]:
        with database_context() as connection:
            cursor = connection.cursor()
            if entity.id and self.exists_by_id(entity.id):
                try:
                    cursor.execute('''
                        UPDATE local
                        SET geohash = ?, name = ?
                    ''', (entity.geohash, entity.name))
                except Exception as err:
                    return Result(None, EntityNotSaved(f"Could not update local of id: {entity.id}", err))
            else:
                try:
                    cursor.execute('''
                        INSERT 
                        INTO local (geohash, name)
                        VALUES (?, ?)
                    ''', (entity.geohash, entity.name)).fetchone()
                except Exception as err:
                    return Result(None, EntityNotSaved("Could not save", err))
            return Result(entity, None)

    def delete_by_id(self, id: int) -> Result[int, EntityNotDeleted]:
        with database_context() as connection:
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM local WHERE id = ?", (str(id),))
                if cursor.rowcount == 0:
                    return Result(None, EntityNotDeleted(f"Could not delete entity of id {id}"))
            except Exception as err:
                return Result(None, EntityNotDeleted(f"Could not delete entity of id {id}", err))
        return Result(id, None)

    def find_by_query_id(self, id: int) -> Result[list[Local], EntityNotFound]:
        with database_context() as connection:
            cursor = connection.cursor()
            rows = cursor.execute('''
                SELECT l.id, l.geohash, l.name
                FROM local AS l
                JOIN query_local AS ql ON ql.local_id = l.id
                WHERE ql.query_id = ?
            ''', (str(id),)).fetchall()
            if not rows:
                return Result(None, EntityNotFound(f"No locals found for the query of id: {id}"))
            locals = []
            for row in rows:
                local_id, geohash, name = row
                locals.append(Local(local_id, geohash, name))
            return Result(locals, None)

    def exists_by_id(self, id: int) -> bool:
        with database_context() as connection:
            cursor = connection.cursor()
            row = cursor.execute("SELECT * FROM local WHERE id = ?", (str(id),)).fetchone()
            if row is None:
                return False
            return True
        
    def find_by_name(self, name: str) -> Result[Local, EntityNotFound]:
        local = None
        with database_context() as connection:
            cursor = connection.cursor()
            row = cursor.execute('''
                SELECT  l.id, l.geohash, l.name 
                FROM local AS l
                WHERE l.name = ? COLLATE NOCASE
            ''', (name,)).fetchone()
            if row is None:
                return Result(None, EntityNotFound(f"Could not find local of name: {name}"))

            id, geohash, name = row
            local = Local(id=id, geohash=geohash, name=name) 

        return Result(local, None)

