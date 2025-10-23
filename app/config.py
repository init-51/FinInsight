from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str = "finuser"
    POSTGRES_PASSWORD: str = "finpass"
    POSTGRES_DB: str = "fininsight"
    POSTGRES_HOST: str = "fininsight-db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql://finuser:finpass@fininsight-db:5432/fininsight"

    REDIS_URL: str = "redis://fininsight-redis:6379/0"


    JWT_SECRET: str = "supersecretkey"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENV: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
