from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Sentiment Labeling Platform"
    api_prefix: str = "/api/platform"
    cors_origins: list[str] = ["http://localhost:8080", "http://localhost:5173"]
    import_storage_dir: str = "/tmp/sentiment-platform-imports"


settings = Settings()
