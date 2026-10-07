from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# 1. Database URL (SQLite file 'todos.db' is created in the local project directory)
DATABASE_URL = "sqlite:///./todos.db"

# 2. Engine: Database connection pool
# check_same_thread=False is required for SQLite in multi-threaded FastAPI environments
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. SessionLocal: Database session factory for database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Declarative Base: All models inherit from this base class (SQLAlchemy 2.0 style)
class Base(DeclarativeBase):
    pass

# 5. Dependency: Yields a fresh database session per request and cleanly closes it on completion
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
