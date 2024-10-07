import unittest
from context import database_context
from database.query_repository import QueryRepository
from models import Category, Query


class TestQueryRepository(unittest.TestCase):
    def setUp(self):
        self.repo = QueryRepository()
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

        assert query is not None
        self.assertIsNotNone(query)
        self.assertEqual(query.id, 1)
        self.assertEqual(query.term, 'refri 2l')
        self.assertEqual(query.radius, 5.0)

    def test_find_all(self):
        queries = self.repo.find_all()
        self.assertEqual(len(queries), 2) 

        query_0 = queries[0]
        self.assertEqual(query_0.id, 1)
        self.assertEqual(query_0.term, 'refri 2l')
        self.assertEqual(query_0.radius, 5.0)

        query_1 = queries[1]
        self.assertEqual(query_1.id, 2)
        self.assertEqual(query_1.term, 'refri lata')
        self.assertEqual(query_1.radius, 10.0)

    def test_save(self):
        new_query = Query(id=None, term='pizza', locals=[], radius=5.0, category=Category(id=1, nota_id='55', description='Bebidas'))

        saved_query = self.repo.save(new_query)

        self.assertIsNotNone(saved_query.id)

        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT q.id, q.term, q.radius FROM query AS q WHERE id = ?", (3,))
            row = cursor.fetchone()
            id, term, radius = row

            self.assertIsNotNone(row)
            self.assertEqual(id, 3)  
            self.assertEqual(term, 'pizza')  
            self.assertEqual(radius, 5.0)  

    def test_delete_by_id(self):
        self.repo.delete_by_id(3)
        
        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM query WHERE id = ?", (3,))
            row = cursor.fetchone()
            self.assertIsNone(row)

    def test_exists_by_id(self):
        exists = self.repo.exists_by_id(1)
        dont_exists = self.repo.exists_by_id(5)
        
        self.assertTrue(exists)
        self.assertFalse(dont_exists)
