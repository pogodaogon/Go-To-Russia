from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def migrate_schema() -> None:
    """Apply small additive migrations needed by existing local deployments."""
    inspector = inspect(engine)
    if "programs" not in inspector.get_table_names():
        return
    tables = set(inspector.get_table_names())
    columns = {column["name"] for column in inspector.get_columns("programs")}
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    university_columns = {column["name"] for column in inspector.get_columns("universities")}
    with engine.begin() as connection:
        additions = {
            "users": {
                "ui_language": "VARCHAR(8) NOT NULL DEFAULT 'ru'", "age": "INTEGER",
                "current_education": "VARCHAR(80)", "graduation_year": "INTEGER",
                "russian_level": "VARCHAR(30)", "budget_currency": "VARCHAR(8) NOT NULL DEFAULT 'RUB'",
                "interested_in_quota": "BOOLEAN NOT NULL DEFAULT FALSE",
            },
            "programs": {
                "listed": "BOOLEAN NOT NULL DEFAULT FALSE", "dormitory_confirmed": "BOOLEAN NOT NULL DEFAULT FALSE",
                "categories": "TEXT NOT NULL DEFAULT ''", "admission_routes": "TEXT NOT NULL DEFAULT ''",
            },
            "universities": {
                "university_type": "VARCHAR(60) NOT NULL DEFAULT 'university'", "study_fields": "TEXT NOT NULL DEFAULT ''",
                "tuition_min": "FLOAT", "tuition_max": "FLOAT", "foreign_programs": "BOOLEAN",
                "admissions_url": "VARCHAR(500) NOT NULL DEFAULT ''", "catalog_level": "VARCHAR(20) NOT NULL DEFAULT 'overview'",
                "verified_at": "DATE",
                "source_url": "VARCHAR(500) NOT NULL DEFAULT ''",
            },
            "application_steps": {"source_url": "VARCHAR(500) NOT NULL DEFAULT ''"},
        }
        known = {"users": user_columns, "programs": columns, "universities": university_columns}
        for table in ("application_steps",):
            if table in tables:
                known[table] = {column["name"] for column in inspector.get_columns(table)}
        if "documents" in tables:
            known["documents"] = {column["name"] for column in inspector.get_columns("documents")}
            additions["documents"] = {"verified_at": "DATE"}
        for table, table_additions in additions.items():
            if table not in tables:
                continue
            for column, definition in table_additions.items():
                if column not in known[table]:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
