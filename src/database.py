import os

from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, MetaData

load_dotenv()

_DB_PORT = os.getenv('DB_PORT')
_USER = os.getenv('MYSQL_USER')
_MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD')
_DATABASE = os.getenv('DATABASE')

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{_USER}:{_PASSWORD}@{_MYSQL_DATABASE}:{_DB_PORT}/{_DATABASE}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

meta = MetaData()
conn = engine.connect()

Base = declarative_base()
