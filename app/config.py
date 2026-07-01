from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional
from urllib.parse import quote_plus


class Settings(BaseSettings):
    # Option 1: full URL (local dev via .env)
    database_url: Optional[str] = None

    # Option 2: individual fields (ECS via Secrets Manager)
    db_host: Optional[str] = None
    db_port: Optional[int] = 5432
    db_name: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    redis_url: str = "redis://localhost:6379"

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    @model_validator(mode="after")
    def assemble_db_url(self) -> "Settings":
        if self.database_url:
            return self
        if all([self.db_host, self.db_name, self.db_user, self.db_password]):
            password = quote_plus(self.db_password)
            self.database_url = (
                f"postgresql://{self.db_user}:{password}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )
            return self
      redis_url: str = "REDIS_URL=redis://statusnest-dev-redis.b8x2ra.0001.use1.cache.amazonaws.com:6379"  # ← add here
    class Config:
        env_file = ".env"


settings = Settings()
