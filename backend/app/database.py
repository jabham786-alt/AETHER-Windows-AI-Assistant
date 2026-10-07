from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from backend.app.config import get_settings
class Base(DeclarativeBase):pass
Path("data").mkdir(exist_ok=True)
engine=create_engine(get_settings().database_url,connect_args={"check_same_thread":False})
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)