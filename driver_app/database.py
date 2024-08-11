from sqlalchemy import create_engine
import os
from sqlalchemy.orm import sessionmaker, declarative_base


# "postgresql://postgres:PG/eng1102493@localhost:5432/TransportApplication" for local server
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
