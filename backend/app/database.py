from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import Config

DATABASE_URL = Config.get_database_url()
ENGINE_OPTIONS = Config.get_engine_options()

engine = create_engine(DATABASE_URL, **ENGINE_OPTIONS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
