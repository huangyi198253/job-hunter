from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


def _get_database_url():
    url = settings.DATABASE_URL
    # Render PostgreSQL uses "postgres://" prefix,
    # but SQLAlchemy needs "postgresql+psycopg://" for psycopg v3
    if url and url.startswith("postgres"):
        if "+psycopg" not in url and "psycopg2" not in url:
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


engine = create_engine(
    _get_database_url(),
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
    echo=settings.DEBUG,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    import app.models  # noqa
    Base.metadata.create_all(bind=engine)
