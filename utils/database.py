from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from utils.config import DATABASE_URL


# ---------------------------------------------------------
# DATABASE ENGINE
# ---------------------------------------------------------

connect_args = {}

# SQLite needs this option when Streamlit uses
# more than one execution context/thread.
if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    future=True,
)


# ---------------------------------------------------------
# SESSION
# ---------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ---------------------------------------------------------
# BASE MODEL
# ---------------------------------------------------------

Base = declarative_base()


# ---------------------------------------------------------
# INITIALIZE DATABASE
# ---------------------------------------------------------

def init_db():
    """
    Create all database tables defined by SQLAlchemy models.
    """

    # Import here to avoid circular imports.
    from utils import models

    Base.metadata.create_all(
        bind=engine
    )


# ---------------------------------------------------------
# DATABASE SESSION
# ---------------------------------------------------------

@contextmanager
def get_db():
    """
    Provide a database session and automatically
    close it after use.
    """

    db = SessionLocal()

    try:
        yield db
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
