from context import database_context
from database.category_repository import CategoryRepository
from database.local_repository import LocalRepository
from database.repository_interface import Repository
from models import Query

class QueryRepository(Repository[Query]):    
    def __init__(self) -> None:
        self.local_repo = LocalRepository()
        self.category_repo = CategoryRepository()

    def find_by_id(self, id: int) -> Query | None:
        query = None
        with database_context() as connection:
            cursor = connection.cursor()
            query_row = cursor.execute('''
                SELECT q.id, q.term, q.radius
                FROM query AS q 
                WHERE id = ?
            ''', (str(id))).fetchone()
            if query_row is None:
                raise Exception(f"Query of id {id} not found")
            if query_row:
                id, term, radius = query_row
                locals = self.local_repo.find_by_query_id(id)
                category = self.category_repo.find_by_query_id(id)
                query = Query(id=id, term=term, locals=locals, category=category, radius=radius)
            return query

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

    def save(self, entity: Query) -> Query:
        with database_context() as connection:
            if entity.category is None or entity.category.id is None:
                raise Exception("Category should be defined")
            cursor = connection.cursor()       

            if entity.id and self.exists_by_id(entity.id):
                cursor.execute('''
                    UPDATE query
                    SET term = ?
                    WHERE id = ?
                ''', (entity.term, entity.id))
            else:
                cursor.execute('''
                    INSERT 
                    INTO query (term, radius, category_id)
                    VALUES (?, ?, ?)
                ''', (entity.term, entity.radius, entity.category.id))
                query_id = cursor.lastrowid
                if query_id:
                    entity.id = query_id
                
                locals = self.local_repo.find_all()

                for local in locals:
                    if local in entity.locals:
                        cursor.execute('''
                            INSERT 
                            INTO query_local (query_id, local_id) 
                            VALUES (?, ?)
                        ''', (query_id, local.id))
            return entity

    def delete_by_id(self, id: int):
        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM query WHERE id = ?", (str(id)))

    def exists_by_id(self, id: int):
        with database_context() as connection:
            cursor = connection.cursor()
            row = cursor.execute("SELECT * FROM query WHERE id = ?", (str(id))).fetchone()
            if row is None:
                return False
            return True
            

    def find_by_spreadsheet_id(self, id: int) -> Query | None:
        query = None
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
            return query

