import unittest

from context import database_context
from database.category_repository import CategoryRepository
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
        query = self.repo.find_by_id(1)

        self.assertIsNotNone(query)
        self.assertEqual(query.id, 1)
        self.assertEqual(query.description, 'Bebidas')

    def test_find_all(self):
        categories = self.repo.find_all()
        self.assertEqual(len(categories), 2) 

        category_0 = categories[0]
        self.assertEqual(category_0.id, 1)
        self.assertEqual(category_0.nota_id, '55')
        self.assertEqual(category_0.description, 'Bebidas')

        category_1 = categories[1]
        self.assertEqual(category_1.id, 2)
        self.assertEqual(category_1.nota_id, '57')
        self.assertEqual(category_1.description, 'Alimentos')

    def test_save(self):
        new_category = Category(id=None, nota_id='60', description='Outros')
        saved_category = self.repo.save(new_category)

        self.assertIsNotNone(saved_category)

        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT q.id, q.nota_id, q.description FROM category AS q WHERE id = ?", (3,))
            row = cursor.fetchone()

            self.assertIsNotNone(row)
            id, nota_id, description = row

            self.assertEqual(id, 3)  
            self.assertEqual(nota_id, '60')  
            self.assertEqual(description, 'Outros')  

    def test_delete_by_id(self):
        self.repo.delete_by_id(3) 
        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM category WHERE id = ?", (3,))
            row = cursor.fetchone()
            self.assertIsNone(row)

    def test_find_by_query_id(self):
        category = self.repo.find_by_query_id(1)
        
        assert category is not None
        self.assertIsNotNone(category)
        self.assertEqual(category.id, 1)
        self.assertEqual(category.nota_id, '55')
        self.assertEqual(category.description, 'Bebidas') 

    def test_find_by_nota_id(self):
        category = self.repo.find_by_nota_id('55')

        assert category is not None
        self.assertIsNotNone(category)
        self.assertEqual(category.id, 1)
        self.assertEqual(category.nota_id, '55')
        self.assertEqual(category.description, 'Bebidas')


