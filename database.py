from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# 1. Database URL (SQLite file 'todos.db' isi folder me banegi)
DATABASE_URL = "sqlite:///./todos.db"

# 2. Engine: Database connection pool create karta hai
# check_same_thread=False SQLite ke liye zaroori hai kyunki FastAPI multi-threaded hota hai
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. SessionLocal: Database se baat karne ke liye session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base class: Hamare saare tables (models) is class ko inherit karenge (SQLAlchemy 2.0 style)
class Base(DeclarativeBase):
    pass

# 5. Dependency: Har request ke liye fresh database session dega aur kaam hone par safely close karega
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
