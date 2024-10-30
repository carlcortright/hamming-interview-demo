from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    OPENAI_API_KEY: str
    HAMMING_API_TOKEN: str
    WEBHOOK_URL: str
    TEST_PHONE_NUMBER: str = "+14153580761"

    # API endpoints
    START_CALL_URL: str = "https://app.hamming.ai/api/rest/exercise/start-call"
    MEDIA_URL: str = "https://app.hamming.ai/api/media/exercise"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Create settings instance
settings = Settings()