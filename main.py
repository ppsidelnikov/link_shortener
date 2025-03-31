from fastapi import FastAPI, Depends, status, HTTPException
import uvicorn
from app.api.endpoints import links, auth
from app.core.redis import redis_client
from fastapi.openapi.utils import get_openapi
from app.schemas.user import UserInDB
from app.api.deps import get_current_user
from app.core.tasks import scheduler


app = FastAPI()
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="URL Shortener API",
        version="1.0",
        routes=app.routes,
    )
    
    # Кастомизируем схему авторизации
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token in the format: Bearer <token>"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
app.include_router(links.router)
app.include_router(auth.router)

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

@app.get("/test-redis")
def test_redis():
    """Тестовый эндпоинт для проверки Redis"""
    redis_client.setex("api_test", 60, "works")  # Запись на 1 минуту
    value = redis_client.get("api_test")
    return {"status": "success", "value": value}

@app.get("/")
def read_root():
    return {"message": "URL Shortener API"}

@app.get("/me", response_model=UserInDB)
def get_current_user_info(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Возвращает информацию о текущем авторизованном пользователе.
    Используется для проверки авторизации.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return current_user


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", log_level="info")

