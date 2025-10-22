from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from services.settings import settings

engine = create_engine(settings.db_url or "sqlite:///./app.db", future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()