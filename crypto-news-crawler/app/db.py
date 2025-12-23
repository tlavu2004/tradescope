from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=False,        # bật True nếu muốn xem SQL log
    future=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)