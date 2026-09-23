from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def add_member_columns() -> None:
    if not settings.database_url.startswith("sqlite"):
        return
    with engine.begin() as connection:
        tables = inspect(engine).get_table_names()
        for table in ("sales", "purchases", "expenses"):
            if table in tables and "member" not in {column["name"] for column in inspect(engine).get_columns(table)}:
                connection.execute(text(f"ALTER TABLE {table} ADD COLUMN member VARCHAR(30) DEFAULT 'bhai-1'"))
        if "products" in tables:
            columns = {column["name"] for column in inspect(engine).get_columns("products")}
            if "wood_type" not in columns:
                connection.execute(text("ALTER TABLE products ADD COLUMN wood_type VARCHAR(80) DEFAULT 'General'"))
            if "dimensions" not in columns:
                connection.execute(text("ALTER TABLE products ADD COLUMN dimensions VARCHAR(80)"))
            if "pieces_per_bundle" not in columns:
                connection.execute(text("ALTER TABLE products ADD COLUMN pieces_per_bundle INTEGER DEFAULT 350"))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
