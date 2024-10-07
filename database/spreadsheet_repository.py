from context import database_context
from database.query_repository import QueryRepository
from database.repository_interface import Repository
from lib.util import to_date
from models import Spreadsheet

class SpreadsheetRepository(Repository[Spreadsheet]):        
    def __init__(self):
        self.query_repo = QueryRepository()

    def find_by_id(self, id: int) -> Spreadsheet | None:
        spreadsheet = None
        with database_context() as context:
            cursor = context.cursor()
            row = cursor.execute("SELECT s.id, s.google_id, s.is_populated, s.last_populated FROM spreadsheet AS s WHERE s.id = ?", (str(id),)).fetchone()
            if row:
                s_id, google_id, is_populated, last_populated = row
                query = self.query_repo.find_by_spreadsheet_id(id) 
                spreadsheet = Spreadsheet(id=s_id, google_id=google_id, query=query, is_populated=bool(is_populated), last_populated=to_date(last_populated))
            return spreadsheet

    def find_all(self) -> list[Spreadsheet]:
        with database_context() as context:
            cursor = context.cursor()
            rows = cursor.execute("SELECT s.id, s.google_id, s.is_populated, s.last_populated FROM spreadsheet AS s").fetchall()
            spreadsheets = []
            for row in rows:
                id, google_id, is_populated, last_populated = row
                query = self.query_repo.find_by_spreadsheet_id(id)
                spreadsheets.append(Spreadsheet(id=id, google_id=google_id, query=query, is_populated=bool(is_populated), last_populated=to_date(last_populated)))
            return spreadsheets

    def save(self, entity: Spreadsheet) -> Spreadsheet:
        with database_context() as context:
            cursor = context.cursor()
            is_populated = 1 if entity.is_populated else 0
            if not entity.query:
                raise Exception("Query should be defined")
            if entity.id is None:
                cursor.execute('''
                    INSERT
                    INTO spreadsheet (google_id, query_id, is_populated) 
                    VALUES (?, ?, ?)
                ''', (entity.google_id, entity.query.id, is_populated))
            else: 
                cursor.execute("""
                    UPDATE spreadsheet
                    SET google_id = ?, query_id = ?, is_populated = ?, last_populated = ?
                    WHERE id = ?
                """, (entity.google_id, entity.query.id, is_populated, entity.last_populated, entity.id))                
            id = cursor.lastrowid
            if id:
                entity.id = id 
            return entity 

    def delete_by_id(self, id: int):
        with database_context() as context:
            cursor = context.cursor()
            cursor.execute("DELETE FROM spreadsheet WHERE id = ?", (str(id)))

    def exists_by_id(self, id: int) -> bool:
        with database_context() as context:
            cursor = context.cursor()
            row = cursor.execute("SELECT * FROM spreadsheet WHERE id = ?", (str(id))).fetchone()
            if row is None:
                return False
            return True 

    def find_by_google_id(self, google_id: str) -> Spreadsheet | None:
        spreadsheet = None
        with database_context() as context:
            cursor = context.cursor()
            row = cursor.execute("SELECT s.id, s.google_id, s.is_populated, s.last_populated FROM spreadsheet AS s WHERE s.google_id = ?", (str(google_id),)).fetchone()
            if row:
                id, google_id, is_populated, last_populated = row
                query = self.query_repo.find_by_spreadsheet_id(id) 
                spreadsheet = Spreadsheet(id=id, google_id=google_id, query=query, is_populated=bool(is_populated) ,last_populated=to_date(last_populated))
            return spreadsheet

