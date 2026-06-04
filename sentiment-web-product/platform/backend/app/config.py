from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Sentiment Labeling Platform"
    api_prefix: str = "/api/platform"
    cors_origins: list[str] = ["http://localhost:8080", "http://localhost:5173"]


settings = Settings()
