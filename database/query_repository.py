from sqlite3 import DatabaseError
from context import database_context
from database.category_repository import CategoryRepository
from database.local_repository import LocalRepository
from database.repository_interface import Repository
from error.EntityNotDeleted import EntityNotDeleted
from error.EntityNotFound import EntityNotFound
from error.EntityNotSaved import EntityNotSaved
from error.Result import Result
from models import Query

class QueryRepository(Repository[Query]):    
    def __init__(self) -> None:
        self.local_repo = LocalRepository()
        self.category_repo = CategoryRepository()

    def find_by_id(self, id: int) -> Result[Query, EntityNotFound]:
        with database_context() as connection:
            cursor = connection.cursor()
            query_row = cursor.execute('''
                SELECT q.id, q.term, q.radius
                FROM query AS q 
                WHERE id = ?
            ''', (str(id))).fetchone()

            if query_row is None:
                return Result(None, EntityNotFound(f"Could not find query of id: {id}")) 

            id, term, radius = query_row
            locals = self.local_repo.find_by_query_id(id)
            category = self.category_repo.find_by_query_id(id)
            query = Query(id=id, term=term, locals=locals, category=category, radius=radius)
            return Result(query, None) 

    def find_all(self) -> list[Query]:
        with database_context() as connection:
            cursor = connection.cursor()
            rows = cursor.execute('''
                SELECT q.id, q.term, q.radius
                FROM query AS q
            ''').fetchall()
            queries = []
            for row in rows:
                id, term, radius = row
                locals = self.local_repo.find_by_query_id(id)
                category = self.category_repo.find_by_query_id(id)
                queries.append(Query(id=id, term=term, locals=locals, category=category, radius=radius))
            return queries 

    def save(self, entity: Query) -> Result[Query, EntityNotSaved]:
        with database_context() as connection:
            if entity.category is None or entity.category.id is None:
                return Result(None, EntityNotSaved("Could category should be defined"))
            cursor = connection.cursor()       

            if entity.id and self.exists_by_id(entity.id):
                try:
                    cursor.execute('''
                        UPDATE query
                        SET term = ?
                        WHERE id = ?
                    ''', (entity.term, entity.id))
                except Exception as err:
                    return Result(None, EntityNotSaved("Could not update query", err))
            else:
                try:
                    cursor.execute('''
                        INSERT 
                        INTO query (term, radius, category_id)
                        VALUES (?, ?, ?)
                    ''', (entity.term, entity.radius, entity.category.id))
                    query_id = cursor.lastrowid
                    if query_id:
                        entity.id = query_id
                except Exception as err:
                    return Result(None, EntityNotSaved("Could not save query"))
                try:  
                    locals = self.local_repo.find_all()

                    for local in locals:
                        if local in entity.locals:
                            cursor.execute('''
                                INSERT 
                                INTO query_local (query_id, local_id) 
                                VALUES (?, ?)
                            ''', (query_id, local.id))
                except Exception as err:
                    return Result(entity, None)
            return Result(entity, None)

    def delete_by_id(self, id: int) -> Result[int, EntityNotDeleted]:
        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM query WHERE id = ?", (str(id)))
        return Result(id, None)

    def exists_by_id(self, id: int) -> bool:
        with database_context() as connection:
            cursor = connection.cursor()
            row = cursor.execute("SELECT * FROM query WHERE id = ?", (str(id))).fetchone()
            if row is None:
                return False
            return True
            

    def find_by_spreadsheet_id(self, id: int) -> Result[Query, EntityNotFound | DatabaseError]:
        try:
            with database_context() as connection:
                cursor = connection.cursor()
                query_row = cursor.execute('''
                    SELECT q.id, q.term, q.radius
                    FROM query AS q
                    JOIN spreadsheet AS s ON s.query_id = q.id 
                    WHERE s.id = ?
                ''', (str(id))).fetchone()

                if query_row:
                    query_id, term, radius = query_row
                    locals = self.local_repo.find_by_query_id(query_id)
                    category = self.category_repo.find_by_query_id(query_id)
                    query = Query(id=query_id, term=term,locals=locals, category=category, radius=radius)
                    return Result(query, None)
                else:
                    return Result(None, EntityNotFound(f"Could not find spreadsheet of query id: {id}"))
        except DatabaseError as err:
            return Result(None, err)


