from context import database_context
from database.query_repository import QueryRepository
from database.repository_interface import Repository
from error.EntityNotDeleted import EntityNotDeleted
from error.EntityNotFound import EntityNotFound
from error.EntityNotSaved import EntityNotSaved
from error.Result import Result
from lib.util import to_date
from models import Spreadsheet

class SpreadsheetRepository(Repository[Spreadsheet]):        
    def __init__(self):
        self.query_repo = QueryRepository()

    def find_by_id(self, id: int) -> Result[Spreadsheet, EntityNotFound]:
        try:
            with database_context() as context:
                cursor = context.cursor()
                row = cursor.execute('''
                    SELECT s.id, s.google_id, s.is_populated, s.last_populated 
                    FROM spreadsheet AS s 
                    WHERE s.id = ?
                ''', (str(id),)).fetchone()
                if row is None:
                    return Result(None, EntityNotFound(f"Could not find query of id: {id}"))
                s_id, google_id, is_populated, last_populated = row
                query = self.query_repo.find_by_spreadsheet_id(id) 
                if query.value:
                    query = query.value
                else: 
                    return Result(None, EntityNotFound(f"Could not find spreadsheet of id: {id} query"))

                spreadsheet = Spreadsheet(id=s_id, google_id=google_id, query=query, is_populated=bool(is_populated), last_populated=to_date(last_populated))
                return Result(spreadsheet, None)
        except Exception as err:
            return Result(None, EntityNotFound(f"Something went wrong, could not find spreadsheet of id: {id}", err))

    def find_all(self) -> Result[list[Spreadsheet], EntityNotFound]:
        try:
            with database_context() as context:
                cursor = context.cursor()
                rows = cursor.execute("SELECT s.id, s.google_id, s.is_populated, s.last_populated FROM spreadsheet AS s").fetchall()
                spreadsheets = []
                for row in rows:
                    id, google_id, is_populated, last_populated = row
                    query = self.query_repo.find_by_spreadsheet_id(id)
                    if query.value:
                        query = query.value
                    else:
                        # TODO: add logging
                        continue

                    spreadsheets.append(Spreadsheet(id=id, google_id=google_id, query=query, is_populated=bool(is_populated), last_populated=to_date(last_populated)))
                return Result(spreadsheets, None)
        except Exception as err:
            return Result(None, EntityNotFound("Something went wrong, no spreadsheets were found", err))

    def save(self, entity: Spreadsheet) -> Result[Spreadsheet, EntityNotSaved]:
        try:
            with database_context() as context:
                cursor = context.cursor()

                is_populated = 1 if entity.is_populated else 0
                if not entity.query:
                    return Result(None, EntityNotSaved("Query missing"))

                if entity.id and self.exists_by_id(entity.id):
                    try:
                        cursor.execute("""
                            UPDATE spreadsheet
                            SET google_id = ?, query_id = ?, is_populated = ?, last_populated = ?
                            WHERE id = ?
                        """, (entity.google_id, entity.query.id, is_populated, entity.last_populated, entity.id))                
                    except Exception as err:
                        return Result(None, EntityNotSaved(f"Could not update spreadsheet of id: {entity.id}", err))
                else: 
                    try:
                        cursor.execute('''
                            INSERT
                            INTO spreadsheet (google_id, query_id, is_populated) 
                            VALUES (?, ?, ?)
                        ''', (entity.google_id, entity.query.id, is_populated))
                    except Exception as err:
                        return Result(None, EntityNotSaved("Could not save spreadsheet", err))
                entity.id = cursor.lastrowid
        except Exception as err:
            return Result(None, EntityNotSaved("Something went wrong, could not save spreadsheet", err))
        return Result(entity, None)

    def delete_by_id(self, id: int) -> Result[int, EntityNotDeleted]:
        try:
            with database_context() as context:
                cursor = context.cursor()
                cursor.execute("DELETE FROM spreadsheet WHERE id = ?", (str(id)))
        except Exception as err:
            return Result(None, EntityNotDeleted(f"Could not delete spreadsheet of id: {id}", err))
        return Result(id, None)

    def exists_by_id(self, id: int) -> bool:
        with database_context() as context:
            cursor = context.cursor()
            row = cursor.execute("SELECT * FROM spreadsheet WHERE id = ?", (str(id))).fetchone()
            if row is None:
                return False
            return True 

    def find_by_google_id(self, google_id: str) -> Result[Spreadsheet, EntityNotFound]:
        spreadsheet = None
        try:
            with database_context() as context:
                cursor = context.cursor()
                row = cursor.execute('''
                    SELECT s.id, s.google_id, s.is_populated, s.last_populated 
                    FROM spreadsheet AS s 
                    WHERE s.google_id = ?''', (str(google_id),)).fetchone()
                if row:
                    id, google_id, is_populated, last_populated = row
                    query = self.query_repo.find_by_spreadsheet_id(id)
                    if query.value:
                        query = query.value
                    else:
                        return Result(None, EntityNotFound(f"Could not find spreadsheet of google_id: {google_id} query"))

                    spreadsheet = Spreadsheet(id=id, google_id=google_id, query=query, is_populated=bool(is_populated) ,last_populated=to_date(last_populated))
                    return Result(spreadsheet, None)
                else: 
                    return Result(None, EntityNotFound(f"Could not find spreadsheet of google id: {google_id}"))
        except Exception as err:
            return Result(None, EntityNotFound(f"Something went wrong, could not find spreadsheet", err))

