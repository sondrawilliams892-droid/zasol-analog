from bot.models import SessionLocal, User, PhoneSearch, CreditScoreEntry
from sqlalchemy.orm import Session

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_user(db: Session, telegram_id: int, username: str = None, first_name: str = None, last_name: str = None):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def increment_search_count(db: Session, telegram_id: int):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        user.search_count += 1
        db.commit()

def save_phone_search(db: Session, user_id: int, phone: str, result: dict):
    entry = PhoneSearch(
        user_id=user_id,
        phone_number=phone,
        result_name=result.get("name", ""),
        result_address=result.get("address", ""),
        result_emails=", ".join(result.get("emails", [])),
        result_phones=", ".join(result.get("phones", [])),
        raw_json=str(result)
    )
    db.add(entry)
    db.commit()

def get_user_search_history(db: Session, user_id: int, limit: int = 10):
    return db.query(PhoneSearch).filter(PhoneSearch.user_id == user_id).order_by(PhoneSearch.created_at.desc()).limit(limit).all()

def save_credit_score(db: Session, user_id: int, score: int, bureau: str, note: str = ""):
    entry = CreditScoreEntry(
        user_id=user_id,
        score=score,
        bureau=bureau,
        note=note
    )
    db.add(entry)
    db.commit()

def get_credit_history(db: Session, user_id: int):
    return db.query(CreditScoreEntry).filter(CreditScoreEntry.user_id == user_id).order_by(CreditScoreEntry.created_at.desc()).all()
