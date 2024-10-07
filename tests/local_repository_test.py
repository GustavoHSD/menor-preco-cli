import unittest
from context import database_context
from database.local_repository import LocalRepository
from models import Local

class TestLocalRepository(unittest.TestCase):
    def setUp(self):
        self.repo = LocalRepository()
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
        local = self.repo.find_by_id(1)
        assert local is not None
        self.assertEqual(local.id, 1)
        self.assertEqual(local.geohash, 'ezs42')
        self.assertEqual(local.name, 'Local A')
        
        local = self.repo.find_by_id(10)
        self.assertIsNone(local)

    def test_find_all(self):
        locals = self.repo.find_all()
        self.assertEqual(len(locals), 3) 

        self.assertEqual(locals[0].id, 1)
        self.assertEqual(locals[0].geohash, 'ezs42')
        self.assertEqual(locals[0].name, 'Local A')

        self.assertEqual(locals[1].id, 2)
        self.assertEqual(locals[1].geohash, 'ezs43')
        self.assertEqual(locals[1].name, 'Local B')

        self.assertEqual(locals[2].id, 3)
        self.assertEqual(locals[2].geohash, 'ezs44')
        self.assertEqual(locals[2].name, 'Local C')

    def test_save(self):
        new_local = Local(id=None, geohash='ezs45', name='Local D')

        saved_local = self.repo.save(new_local)

        self.assertIsNotNone(saved_local)

        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT l.id, l.geohash, l.name FROM local AS l WHERE id = ?", (4,))
            row = cursor.fetchone()
            id, geohash, name = row

            self.assertIsNotNone(row)
            self.assertEqual(id, 4)  
            self.assertEqual(geohash, 'ezs45')
            self.assertEqual(name, 'Local D')  

    def test_delete_by_id(self):
        self.repo.delete_by_id(3) 
        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM local WHERE id = ?", (3,))
            row = cursor.fetchone()
            self.assertIsNone(row)

    def test_find_by_query_id(self):
        local = self.repo.find_by_query_id(1)

        self.assertEqual(len(local), 2)
        
        self.assertEqual(local[0].id, 1)
        self.assertEqual(local[0].geohash, 'ezs42')
        self.assertEqual(local[0].name, 'Local A')

        self.assertEqual(local[1].id, 2)
        self.assertEqual(local[1].geohash, 'ezs43')
        self.assertEqual(local[1].name, 'Local B')

