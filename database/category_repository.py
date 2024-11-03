from context import database_context
from database.repository_interface import Repository
from error.EntityNotDeleted import EntityNotDeleted
from error.EntityNotFound import EntityNotFound
from error.EntityNotSaved import EntityNotSaved
from error.Result import Result
from models import Category

class CategoryRepository(Repository[Category]):
    def find_by_id(self, id: int) -> Result[Category, EntityNotFound]: 
        try:
            with database_context() as connection:
                cursor = connection.cursor()
                row = cursor.execute('''
                    SELECT * 
                    FROM category 
                    WHERE id = ?
                ''', (str(id),)).fetchone()

                if row is None:
                    return Result(None, EntityNotFound(f"Could not find category of id: {id}"))

                id, nota_id, description = row
                category = Category(id=id, nota_id=nota_id, description=description)
                return Result(category, None)
        except Exception as err:
            return Result(None, EntityNotFound(f"Something went wrong, could not find category of id: {id}", err))
            
    def find_all(self) -> Result[list[Category], EntityNotFound]:
        try:
            with database_context() as connection:
                cursor = connection.cursor()
                rows = cursor.execute('''
                    SELECT id, description, nota_id 
                    FROM category
                ''').fetchall()
                categories = []
                for row in rows:
                    id, description, nota_id = row
                    categories.append(Category(id=id, nota_id=nota_id, description=description))
                return Result(categories, None)
        except Exception as err:
            return Result(None, EntityNotFound("Something went wrong, could not find categories", err))

    def save(self, entity: Category) -> Result[Category, EntityNotSaved]:
        try:
            with database_context() as connection:
                cursor = connection.cursor()
                if entity.id and self.exists_by_id(entity.id):
                    try:
                        cursor.execute('''
                            UPDATE category
                            SET description = ?
                            WHERE id = ?
                        ''', (entity.description, entity.id))
                    except Exception as err:
                        return Result(None, EntityNotSaved("Could not update query", err))
                else:
                    try:
                        cursor.execute('''
                            INSERT 
                            INTO category (nota_id, description)
                            VALUES (?, ?)
                        ''', (entity.nota_id, entity.description,)).fetchone()
                    except Exception as err:
                        return Result(None, EntityNotSaved("Could not update query", err))
                    entity.id = cursor.lastrowid
        except Exception as err:
            return Result(None, EntityNotSaved("Something went wrong, could not save category", err))
        return Result(entity, None)

    def delete_by_id(self, id: int) -> Result[int, EntityNotDeleted]:
        try:
            with database_context() as connection:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM category WHERE id = ?", (str(id)))
                if cursor.rowcount == 0:
                    return Result(None, EntityNotDeleted(f"Could not delete entity of id {id}"))
        except Exception as err:
            return Result(None, EntityNotDeleted(f"Could not delete entity of id {id}", err))
        return Result(id, None)

    def exists_by_id(self, id: int) -> bool:
        with database_context() as connection:
            cursor = connection.cursor()
            row = cursor.execute("SELECT * FROM category WHERE id = ?", (str(id))).fetchone()
            if row is None:
                return False
            return True

    def find_by_query_id(self, id: int) -> Result[Category, EntityNotFound]:
        try:
            with database_context() as connection:
                cursor = connection.cursor()
                row = cursor.execute('''
                    SELECT c.id, c.nota_id, c.description
                    FROM category AS c
                    JOIN query AS q ON c.id = q.category_id
                    WHERE q.id = ?
                ''', (str(id),)).fetchone()

                if row is None:
                    return Result(None, EntityNotFound(f"Could not found category of query id: {id}"))

                id, nota_id, description = row
                return Result(Category(id=id, nota_id=nota_id, description=description), None)
        except Exception as err:
            return Result(None, EntityNotFound(f"Something went wrong, could not find category of query id: {id}", err))

    def find_by_nota_id(self, id: str) -> Result[Category, EntityNotFound]: 
        try:
            with database_context() as connection:
                cursor = connection.cursor()
                row = cursor.execute('''
                    SELECT id, nota_id, description 
                    FROM category 
                    WHERE nota_id = ?
                ''', (str(id),)).fetchone()
                if row is None:
                    return Result(None, EntityNotFound(f"Could not find category of nota id: {id}"))
                id, nota_id, description = row
                category = Category(id=int(id), nota_id=nota_id, description=description)
                return Result(category, None)
        except Exception as err:
            return Result(None, EntityNotFound(f"Something went wrong, could not find category of nota id: {id}", err))



