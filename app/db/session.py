from sqlalchemy import create_engine, text
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
    with engine.begin() as connection:
        columns = connection.execute(text("PRAGMA table_info(games)")).fetchall()
        column_names = {column[1] for column in columns}
        if "is_ranked" not in column_names:
            connection.execute(text("ALTER TABLE games ADD COLUMN is_ranked BOOLEAN NOT NULL DEFAULT 1"))
    return engine
