from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.link import LinkCreate, LinkResponse, LinkUpdate, LinkStats
from app.schemas.user import UserInDB
from app.crud import crud_link
from app.db.models import Link
from app.core.redis import cache_redirect, get_cached_url
from app.api.deps import get_current_user
from typing import Optional, List
from app.core.logger import logger
from app.core.redis import redis_client
import json
from datetime import datetime

router = APIRouter(prefix="/links", tags=["links"])

@router.post("/shorten", response_model=LinkResponse)
def create_short_link(
    link: LinkCreate,
    current_user: Optional[UserInDB] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создает короткую ссылку и записывает ее в БД. Работает для всех юзеров
    link: класс ссылки для сокращения
    current_user: текущий пользователь в сессии (опционально),
    если пользователь указан, то ссылка будет привязана к нему
    db: указание базы данных
    """
    try:
        owner_id = current_user.id if current_user else None
        return crud_link.create_link(db, link, owner_id=owner_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{short_code}", response_class=RedirectResponse, status_code=302)
def redirect_to_original(
    short_code: str,
    db: Session = Depends(get_db)
):
    """
    Редиректит на оригинальную ссылку по короткой. Работает для всех юзеров
    short_code: короткое название для ссылки
    db: указание базы данных
    """
    
    if cached_url := get_cached_url(short_code):
        return cached_url
    
    link = crud_link.get_link_by_short_code(db, short_code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    # Обновляем статистику и кэшируем
    crud_link.update_link_stats(db, link)
    cache_redirect(short_code, str(link.original_url))
    
    return link.original_url

@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(
    short_code: str,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удаляет ссылку, ранее созданную пользователем, из БД. Работает только для авторизованных пользователей
    short_code: короткое название для ссылки
    current_user: текущий пользователь в сессии
    db: указание базы данных
    """
    try:
        link = db.query(Link).filter(
            Link.short_code == short_code,
            Link.owner_id == current_user.id
        ).first()

        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Link not found"
            )
        
        db.delete(link)
        db.commit()

        redis_client.delete(f"redirect:{short_code}")
        redis_client.delete(f"stats:{short_code}:{current_user.id}")
        redis_client.delete(f"user_links:{current_user.id}")

        return {"message": "Link has been deleted successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found or you don't have permissions"
        )

@router.put("/{short_code}")
def update_link(
    short_code: str,
    link_update: LinkUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновляет ссылку, ранее созданную пользователем, из БД. Работает только для авторизованных пользователей
    short_code: короткое название для ссылки
    link_update: класс новой ссылки для замены
    current_user: текущий пользователь в сессии
    db: указание базы данных
    """
    try:
        updated_link = crud_link.update_link(
            db, 
            short_code, 
            str(link_update.new_url),
            current_user.id
        )
        
        if not updated_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Link not found or you don't have permissions"
            )
        redis_client.delete(f"redirect:{short_code}")
        redis_client.delete(f"stats:{short_code}:{current_user.id}")
        redis_client.delete(f"user_links:{current_user.id}")
        return updated_link
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found or you don't have permissions"
        )

@router.get("/{short_code}/stats", response_model=LinkStats)
def get_link_stats(
    short_code:str,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Возвращает статистику переходов по ссылкам для авторизованного пользователя.
    short_code: короткое название для ссылки
    current_user: текущий пользователь в сессии
    db: указание базы данных
    """
    try:
        cache_key = f"stats:{short_code}:{current_user.id}"
    
        # Проверяем кэш Redis
        cached_stats = redis_client.get(cache_key)
        if cached_stats:
            return json.loads(cached_stats)
        
        # Ищем ссылку в базе данных
        link = db.query(Link).filter(
            Link.short_code == short_code,
            Link.owner_id == current_user.id
        ).first()
        
        if not link:
            raise HTTPException(status_code=404, detail="Link not found or access denied")
        
        # Преобразуем даты в строки для корректной сериализации
        def format_datetime(dt: datetime | None) -> str | None:
            return dt.isoformat() if dt else None

        # Формируем статистику
        stats = {
            "id": link.id,
            "short_code": link.short_code,
            "original_url": link.original_url,
            "created_at": format_datetime(link.created_at),
            "expires_at": format_datetime(link.expires_at),
            "owner_id": link.owner_id,
            "access_count": link.access_count,
            "last_accessed": format_datetime(link.last_accessed)
        }
        
        # Кэшируем результат на 5 минут
        redis_client.setex(cache_key, 300, json.dumps(stats))
        return stats
    except Exception as e:
        logger.error(f"Failed to get link stats: {e}")
        raise

@router.get("/links/search", response_model=LinkResponse)
def search_link_by_url(
    original_url: str = Query(..., description="Оригинальный URL для поиска"),
    db: Session = Depends(get_db)
):
    """
    Поиск ссылки по оригинальному URL. Доступно всем пользователям
    original_url: оригинальная ссылка
    db: указание базы данных
    """
    cache_key = f"search:{original_url}"
    
    # Проверяем кэш Redis
    cached_link = redis_client.get(cache_key)
    if cached_link:
        return json.loads(cached_link)
    
    link = db.query(Link).filter(
        Link.original_url == original_url
    ).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    # Возвращаем информацию о ссылке
    response = {
                "short_code": link.short_code,
                "original_url": link.original_url,
                }
    redis_client.setex(cache_key, 300, json.dumps(response))
    return response
