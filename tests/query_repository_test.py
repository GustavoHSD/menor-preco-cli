import unittest
from context import database_context
from database.query_repository import QueryRepository
from error.EntityNotDeleted import EntityNotDeleted
from error.EntityNotFound import EntityNotFound
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
        query_result = self.repo.find_by_id(1)
        query = query_result.value

        assert query is not None
        assert query_result.error is None

        assert query is not None
        assert query.id == 1
        assert query.term == 'refri 2l'
        assert query.radius == 5.0

        query_result = self.repo.find_by_id(10)
        query = query_result.value

        assert query is None
        assert isinstance(query_result.error, EntityNotFound) is True

    def test_find_all(self):
        queries_result = self.repo.find_all()
        queries = queries_result.value

        assert queries is not None
        assert queries_result.error is None

        assert len(queries) == 2

        assert queries[0].id == 1
        assert queries[0].term == 'refri 2l'
        assert queries[0].radius == 5.0

        assert queries[1].id == 2
        assert queries[1].term == 'refri lata'
        assert queries[1].radius == 10.0

    def test_save(self):
        new_query = Query(id=None, term='pizza', locals=[], radius=5.0, category=Category(id=1, nota_id='55', description='Bebidas'))
        saved_query_result = self.repo.save(new_query)
        saved_query = saved_query_result.value

        assert saved_query is not None
        assert saved_query_result.error is None

        self.assertIsNotNone(saved_query.id)

        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT q.id, q.term, q.radius FROM query AS q WHERE id = ?", (3,))
            row = cursor.fetchone()
            id, term, radius = row

            assert row is not None
            assert id == 3
            assert term == 'pizza'
            assert radius == 5.0

    def test_delete_by_id(self):
        delete_result = self.repo.delete_by_id(3) 

        assert delete_result.value == 3
        assert delete_result.error is None
        
        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM query WHERE id = ?", (3,))
            row = cursor.fetchone()
            assert row is None 

        delete_result = self.repo.delete_by_id(10)
        assert delete_result.value is None
        assert isinstance(delete_result.error, EntityNotDeleted) is True

    def test_exists_by_id(self):
        exists = self.repo.exists_by_id(1)
        dont_exists = self.repo.exists_by_id(5)
        
        assert exists is True
        assert dont_exists is False

    def test_find_by_spreadsheet_id(self):
        query_result = self.repo.find_by_spreadsheet_id(1)
        query = query_result.value

        assert query is not None
        assert query_result.error is None

        assert query is not None
        assert query.id == 1
        assert query.term == 'refri 2l'
        assert query.radius == 5.0

        query_result = self.repo.find_by_spreadsheet_id(10)
        query = query_result.value

        assert query is None
        assert isinstance(query_result.error, EntityNotFound) is True

