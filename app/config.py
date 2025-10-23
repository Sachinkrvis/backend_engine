# app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SYNC_DATABASE_URL: str
    REDIS_URL: str
    FCM_CREDENTIALS_JSON: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
