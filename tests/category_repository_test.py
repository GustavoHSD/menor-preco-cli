import unittest

from context import database_context
from database.category_repository import CategoryRepository
from error.EntityNotDeleted import EntityNotDeleted
from error.EntityNotFound import EntityNotFound
from error.EntityNotSaved import EntityNotSaved
from models import Category

class TestCategoryRepository(unittest.TestCase):
    def setUp(self):
        self.repo = CategoryRepository()
        with open('schema.sql', 'r') as file:
            script = file.read()
            with database_context() as connection:
                cursor = connection.cursor()
                cursor.executescript(script)
        with open('test_insertions.sql', 'r') as file:
            script = file.read()
            with database_context() as connection:
                   cursor = connection.cursor()
                   cursor.executescript(script)

    def tearDown(self):
        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("DROP TABLE IF EXISTS spreadsheet")
            cursor.execute("DROP TABLE IF EXISTS query_local")
            cursor.execute("DROP TABLE IF EXISTS query")
            cursor.execute("DROP TABLE IF EXISTS local")
            cursor.execute("DROP TABLE IF EXISTS category")

    def test_find_by_id(self):
        category_result = self.repo.find_by_id(1)
        category = category_result.value
        assert category is not None
        assert category_result.error is None
        assert category.id == 1
        assert category.description == 'Bebidas'

        category_result = self.repo.find_by_id(10)
        category = category_result.value
        assert category is None
        assert isinstance(category_result.error, EntityNotFound) is True

    def test_find_all(self):
        categories_result = self.repo.find_all()
        categories = categories_result.value
        assert categories is not None
        assert categories_result.error is None

        assert len(categories) == 2

        assert categories[0].id == 1
        assert categories[0].nota_id == '55'
        assert categories[0].description == 'Bebidas'

        assert categories[1].id == 2
        assert categories[1].nota_id == '57'
        assert categories[1].description == 'Alimentos'

    def test_save(self):
        new_category = Category(id=None, nota_id='60', description='Outros')
        saved_category_result = self.repo.save(new_category)
        saved_category = saved_category_result.value

        assert saved_category is not None
        assert saved_category_result.error is None

        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT q.id, q.nota_id, q.description FROM category AS q WHERE id = ?", (3,))
            row = cursor.fetchone()

            self.assertIsNotNone(row)
            id, nota_id, description = row

            assert id == 3
            assert nota_id == '60'
            assert description == 'Outros'

        new_category = Category(id=None, nota_id='60', description='Outros')
        saved_category_result = self.repo.save(new_category)
        saved_category = saved_category_result.value

        assert saved_category is None
        assert isinstance(saved_category_result.error, EntityNotSaved) is True

    def test_delete_by_id(self):
        delete_result = self.repo.delete_by_id(2)  
        assert delete_result.value == 2
        assert delete_result.error is None

        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM category WHERE id = ?", (2,))
            row = cursor.fetchone()
            assert row is None

        delete_result = self.repo.delete_by_id(2)  
        assert delete_result.value is None
        assert isinstance(delete_result.error, EntityNotDeleted) is True

    def test_find_by_query_id(self):
        category_result = self.repo.find_by_query_id(1)  
        category = category_result.value 
        assert category is not None
        assert category_result.error is None

        assert category.id == 1
        assert category.nota_id == '55'
        assert category.description == 'Bebidas'

        category_result = self.repo.find_by_query_id(10)
        category = category_result.value 
        assert category is None
        assert isinstance(category_result.error, EntityNotFound) is True

    def test_find_by_nota_id(self):
        category_result = self.repo.find_by_nota_id('55')  
        category = category_result.value 
        assert category is not None
        assert category_result.error is None

        assert category.id == 1
        assert category.nota_id == '55'
        assert category.description == 'Bebidas'

        category_result = self.repo.find_by_nota_id('invalid-id')
        category = category_result.value 
        assert category is None
        assert isinstance(category_result.error, EntityNotFound) is True

