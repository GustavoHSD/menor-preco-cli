from context import database_context
from database.repository_interface import Repository
from models import Category

class CategoryRepository(Repository[Category]):
    def find_by_id(self, id: int) -> Category | None: 
        category = None
        with database_context() as connection:
            cursor = connection.cursor()
            row = cursor.execute('''
                SELECT * 
                FROM category 
                WHERE id = ?
            ''', (str(id),)).fetchone()
            if row:
                id, nota_id, description = row
                category = Category(id=id, nota_id=nota_id, description=description)
            return category
            
    def find_all(self) -> list[Category]:
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
            return categories 

    def save(self, entity: Category) -> Category:
        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT 
                INTO category (nota_id, description)
                VALUES (?, ?)
            ''', (entity.nota_id, entity.description,)).fetchone()
            id = cursor.lastrowid

            entity.id = id 
            return entity 

    def delete_by_id(self, id: int):
        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM category WHERE id = ?", (str(id),))

    def exists_by_id(self, id: int):
        with database_context() as connection:
            cursor = connection.cursor()
            row = cursor.execute("SELECT * FROM category WHERE id = ?", (str(id),)).fetchone()
            if row is None:
                return False
            return True

    def find_by_query_id(self, id: int) -> Category | None:
        with database_context() as connection:
            cursor = connection.cursor()
            category_row = cursor.execute('''
                SELECT c.id, c.nota_id, c.description
                FROM category AS c
                JOIN query AS q ON c.id = q.category_id
                WHERE q.id = ?
            ''', (str(id),)).fetchone()

            if category_row is None:
                return None

            id, nota_id, description = category_row
            return Category(id=id, nota_id=nota_id, description=description)

    def find_by_nota_id(self, id: str) -> Category | None: 
        category = None
        with database_context() as connection:
            cursor = connection.cursor()
            row = cursor.execute('''
                SELECT id, nota_id, description 
                FROM category 
                WHERE nota_id = ?
            ''', (str(id),)).fetchone()
            if row:
                id, nota_id, description = row
                category = Category(id=int(id), nota_id=nota_id, description=description)
            return category

