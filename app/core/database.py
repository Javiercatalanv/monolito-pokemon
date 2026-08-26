from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# SQLite solo sobrevive como fallback offline (tests sin red / sin contenedor).
# El motor real del proyecto es PostgreSQL 16 via psycopg 3.
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if _is_sqlite else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.SQL_ECHO,
    # Descarta conexiones muertas antes de usarlas: el contenedor de Postgres
    # puede reiniciarse por debajo de un servidor de desarrollo de larga vida.
    pool_pre_ping=not _is_sqlite,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa de SQLAlchemy 2.0 para todos los modelos del dominio."""


def get_db() -> Iterator[Session]:
    """Sesion de base de datos por request, para inyeccion de dependencias en FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
