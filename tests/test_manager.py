import unittest
from db.manager import DatabaseManager
from settings.vars import db_name
from sqlmodel import SQLModel, create_engine, Session


class TestDatabaseManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(f'sqlite:///../{db_name}')
        SQLModel.metadata.create_all(cls.engine)

    def test_get_db_instance(self):
        db_instance = DatabaseManager.get_db_instance()
        self.assertIsNotNone(db_instance)

    def test_get_session(self):
        session = DatabaseManager.get_session()
        self.assertIsInstance(session, Session)


if __name__ == '__main__':
    unittest.main()