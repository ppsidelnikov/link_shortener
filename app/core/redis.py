"""
Конфигурация Redis
"""

import redis
from app.core.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)

def cache_redirect(short_code: str, original_url: str):
    """Кэширование ссылки на 1 час"""
    redis_client.setex(f"redirect:{short_code}", 3600, original_url)

def get_cached_url(short_code: str) -> str | None:
    """Получение URL из кэша"""
    return redis_client.get(f"redirect:{short_code}")