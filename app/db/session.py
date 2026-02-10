from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.config import DB_PATH
from app.db.models import Base


def get_engine():
    return create_engine(f"sqlite:///{DB_PATH}", future=True)


SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=get_engine()))


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    return engine
