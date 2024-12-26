import pathlib
from settings.vars import db_name
from sqlmodel import SQLModel, create_engine, Session, select

class DatabaseManager:
    _db_instance = None

    @classmethod
    def get_db_instance(self):
        if self._db_instance is None:
            self._db_instance = self._create_db_instance()
        return self._db_instance

    @staticmethod
    def _create_db_instance():
        root_dir = pathlib.Path(__file__).parent.parent
        db_path = root_dir / db_name
        if not db_path.exists():
            engine = create_engine(f'sqlite:///{db_name}')
            SQLModel.metadata.create_all(engine)
        else:
            engine = create_engine(f'sqlite:///{db_path}')
        return engine

    @classmethod
    def get_session(self):
        engine = self.get_db_instance()
        return Session(engine)

    @classmethod
    def execute_query(self, query):
        with self.get_session() as session:
            result = session.exec(query)
            return result.all()