import unittest
from context import database_context
from database.local_repository import LocalRepository
from error.EntityNotDeleted import EntityNotDeleted
from error.EntityNotFound import EntityNotFound
from error.EntityNotSaved import EntityNotSaved
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
        local_result = self.repo.find_by_id(1)
        local = local_result.value
        assert local is not None
        assert local_result.error is None
        assert local.id == 1 
        assert local.geohash == 'ezs42'
        assert local.name == 'Local A'
        
        local_result = self.repo.find_by_id(10)
        local = local_result.value
        assert local is None
        assert isinstance(local_result.error, EntityNotFound) is True

    def test_find_all(self):
        locals_result = self.repo.find_all()
        locals = locals_result.value

        assert locals is not None
        assert len(locals) == 3

        assert locals[0].id == 1
        assert locals[0].geohash == 'ezs42'
        assert locals[0].name == 'Local A'

        assert locals[1].id == 2
        assert locals[1].geohash == 'ezs43'
        assert locals[1].name == 'Local B'

        assert locals[2].id == 3
        assert locals[2].geohash == 'ezs44'
        assert locals[2].name == 'Local C'

    def test_save(self):
        new_local = Local(id=None, geohash='ezs45', name='Local D')
        saved_local = self.repo.save(new_local)
        assert saved_local.value is not None

        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT l.id, l.geohash, l.name FROM local AS l WHERE id = ?", (4,))
            row = cursor.fetchone()
            id, geohash, name = row
            assert row is not None
            assert id == 4
            assert geohash == 'ezs45'
            assert name == 'Local D'

        new_local = Local(id=None, geohash='ezs45', name='Local D')
        saved_local = self.repo.save(new_local)
        assert saved_local.value is None
        assert isinstance(saved_local.error, EntityNotSaved) is True

    def test_delete_by_id(self):
        delete_result = self.repo.delete_by_id(3) 
        assert delete_result.value is not None
        assert delete_result.error is None
        
        with database_context() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM local WHERE id = ?", (3,))
            row = cursor.fetchone()
            assert row is None

        delete_result = self.repo.delete_by_id(10)
        assert delete_result.value is None
        assert isinstance(delete_result.error, EntityNotDeleted) is True

    def test_find_by_query_id(self):
        local_result = self.repo.find_by_query_id(1)
        locals = local_result.value

        assert locals is not None
        assert len(locals) == 2
        
        assert locals[0].id == 1
        assert locals[0].geohash == 'ezs42'
        assert locals[0].name == 'Local A'

        assert locals[1].id == 2
        assert locals[1].geohash == 'ezs43'
        assert locals[1].name == 'Local B'

        local_result = self.repo.find_by_query_id(10)
        locals = local_result.value

        assert locals is None
        assert isinstance(local_result.error, EntityNotFound) is True

