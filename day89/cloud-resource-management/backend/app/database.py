from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./resource_management.db")
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    base = os.path.dirname(os.path.abspath(__file__))
    for _ in range(2):
        base = os.path.dirname(base)
    path = os.path.join(base, "resource_management.db")
    DATABASE_URL = "sqlite:///" + path

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
