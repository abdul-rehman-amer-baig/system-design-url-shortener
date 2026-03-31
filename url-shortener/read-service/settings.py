from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5434/urlshortener"
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600
    INSTANCE_ID: str = "read-service-1"

    class Config:
        env_file = ".env"


settings = Settings()
