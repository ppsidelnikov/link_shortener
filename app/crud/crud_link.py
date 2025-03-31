"""
Функции для взаимодействия с БД. Обновление данных по ссылкам
"""

from sqlalchemy.orm import Session
from app.db.models import Link
from app.schemas.link import LinkCreate
import random
import string
from app.core.logger import logger
from typing import Optional
from datetime import datetime, timedelta

def generate_short_code(length: int = 6) -> str:
    """Генерация случайного кода для короткой ссылки"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def create_link(
        db: Session, 
        link: LinkCreate, 
        owner_id: int | None = None) -> Link:
    """Создание новой короткой ссылки"""
    try:
        short_code = link.custom_alias or generate_short_code()

        expires_at = None
        if link.expires_in_minutes:
            expires_at = datetime.utcnow() + timedelta(minutes=link.expires_in_minutes)

        db_link = Link(
            original_url=str(link.original_url),
            short_code=short_code,
            expires_at=expires_at,
            owner_id=owner_id
        )
        
        db.add(db_link)
        db.commit()
        db.refresh(db_link)
        logger.info(
                f"Link created: id={db_link.id}, short_code={db_link.short_code}, "
                f"owner_id={db_link.owner_id}"
            )
        return db_link
    except Exception as e:
        logger.error(f"Failed to create link: {e}")
        raise


def get_link_by_short_code(db: Session, short_code: str) -> Link | None:
    """Получение ссылки по короткому коду"""
    return db.query(Link).filter(Link.short_code == short_code).first()

def update_link(db: Session, short_code: str, new_url: str, owner_id: int) -> Link | None:
    """Обновляет оригинальный URL ссылки"""
    try:
        link = db.query(Link).filter(
            Link.short_code == short_code,
            Link.owner_id == owner_id
        ).first()
        
        if link:
            link.original_url = new_url
            db.commit()
            db.refresh(link)
        return link 
    except Exception as e:
        logger.error(f"Failed to update link: {e}")
        raise

def delete_link(db: Session, short_code: str, owner_id: int) -> bool:
    """Удаляет ссылку, если пользователь является владельцем"""
    try:   
        link = db.query(Link).filter(
            Link.short_code == short_code,
            Link.owner_id == owner_id
        ).first()
        
        if link:
            db.delete(link)
            db.commit()
            logger.info(
                f"Link deleted: id={link.id}, short_code={link.short_code}, "
                f"owner_id={link.owner_id}"
            )
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete link: {e}")
        raise


def update_link_stats(db: Session, link: Link) -> Link:
    """Обновляет статистику переходов по ссылке."""
    link.access_count += 1
    link.last_accessed = datetime.utcnow()
    db.commit()
    db.refresh(link)
    return link

def delete_expired_links(db: Session) -> int:
    """Удаляет ссылки с истёкшим сроком действия."""
    now = datetime.utcnow()
    expired_links = db.query(Link).filter(Link.expires_at < now).all()
    for link in expired_links:
        db.delete(link)
    db.commit()
    return expired_links