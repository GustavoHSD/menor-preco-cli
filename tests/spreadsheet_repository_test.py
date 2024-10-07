import unittest
from context import database_context
from lib.util import to_date
from models import Category, Spreadsheet, Query
from database.spreadsheet_repository import SpreadsheetRepository

class TestSpreadsheetRepository(unittest.TestCase):
    def setUp(self):
        self.repo = SpreadsheetRepository()
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
        spreadsheet = self.repo.find_by_id(1)
        assert spreadsheet is not None 

        self.assertIsNotNone(spreadsheet)
        self.assertEqual(spreadsheet.id, 1)
        self.assertEqual(spreadsheet.google_id, 'google-id-123')

        spreadsheet = self.repo.find_by_id(10) 
        self.assertIsNone(spreadsheet)

    def test_find_all(self):
        spreadsheets = self.repo.find_all()
        self.assertEqual(len(spreadsheets), 2) 

        spreadsheet_0 = spreadsheets[0]
        self.assertEqual(spreadsheet_0.id, 1)
        self.assertEqual(spreadsheet_0.google_id, 'google-id-123')

        spreadsheet_1 = spreadsheets[1]
        self.assertEqual(spreadsheet_1.id, 2)
        self.assertEqual(spreadsheet_1.google_id, 'google-id-456')

    def test_save(self):
        repo = SpreadsheetRepository()

        query = Query(id=1, term='pizza', locals=[], radius=5, category=Category(id=None, nota_id='55', description='Bebidas'))

        new_spreadsheet = Spreadsheet(id=None, google_id='google-id-789', query=query)

        saved_spreadsheet = repo.save(new_spreadsheet)

        self.assertIsNotNone(saved_spreadsheet.id)

        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM spreadsheet WHERE google_id = ?", ('google-id-789',))
            row = cursor.fetchone()

            self.assertIsNotNone(row)
            self.assertEqual(row[1], 'google-id-789') 
            self.assertEqual(row[2], 1) 

    def test_delete_by_id(self):
        self.repo.delete_by_id(3)
        
        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM spreadsheet WHERE id = ?", (3,))
            row = cursor.fetchone()
            self.assertIsNone(row)

    def test_exists_by_id(self):
        exists = self.repo.exists_by_id(1)
        dont_exist = self.repo.exists_by_id(5)

        self.assertTrue(exists)
        self.assertFalse(dont_exist)

    def test_find_by_google_id(self):
        spreadsheet = self.repo.find_by_google_id('google-id-123')
        assert spreadsheet is not None
        assert spreadsheet.query is not None

        self.assertEqual(spreadsheet.id, 1)
        self.assertEqual(spreadsheet.google_id, 'google-id-123')
        self.assertEqual(spreadsheet.query.id, 1)
        self.assertTrue(spreadsheet.is_populated)
        self.assertEqual(spreadsheet.last_populated, to_date('22-11-2024'))

        spreadsheet = self.repo.find_by_google_id('invalid-id')
        self.assertIsNone(spreadsheet) 

