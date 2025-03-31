"""
Функции для авторизации пользователя и проверки его в БД
"""

from sqlalchemy.orm import Session
from app.db.models import User
from app.core.security import get_password_hash
from app.schemas.user import UserCreate

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_data: UserCreate) -> User:
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
