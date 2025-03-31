from pydantic_settings import BaseSettings

class Settings(BaseSettings):  
    
    DATABASE_URL: str
    REDIS_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SECRET_KEY: str
    ALGORITHM: str
    POSTGRES_USER:str
    POSTGRES_PASSWORD:str
    POSTGRES_DB:str

    class Config:
        env_file = ".env"  

settings = Settings()
