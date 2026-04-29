from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from bot.config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    search_count = Column(Integer, default=0)
    is_premium = Column(Integer, default=0)  # 0 = free, 1 = premium

class PhoneSearch(Base):
    __tablename__ = "phone_searches"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    phone_number = Column(String, nullable=False)
    result_name = Column(String)
    result_address = Column(String)
    result_emails = Column(String)  # comma separated
    result_phones = Column(String)  # comma separated
    raw_json = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class CreditScoreEntry(Base):
    __tablename__ = "credit_scores"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    score = Column(Integer)
    bureau = Column(String)  # Experian / Equifax / TransUnion
    note = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(engine)
