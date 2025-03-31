"""
Конфигурацмя шедулера для регулярного удаления устаревших ссылок
"""

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud import crud_link
from datetime import datetime
from app.core.logger import logger

scheduler = BackgroundScheduler()

def delete_expired_links():
    """Удаляет ссылки с истёкшим сроком действия."""
    db: Session = next(get_db())
    try:
        expired_links = crud_link.delete_expired_links(db)
        
        if expired_links:
            deleted_links_info = [
                f"ID: {link.id}, Short Code: {link.short_code}, Original URL: {link.original_url}, Expires At: {link.expires_at}"
                for link in expired_links
            ]
            logger.info(f"Deleted {len(expired_links)} expired links:\n" + "\n".join(deleted_links_info))
        else:
            logger.info("No expired links found.")
    except Exception as e:
        logger.error(f"Failed to delete expired links: {e}")
    finally:
        db.close()

scheduler.add_job(delete_expired_links, 'interval', minutes=1)

scheduler.start()
