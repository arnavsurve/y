from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    app_port: int
    chroma_port: int
    groq_api_key: str
    xai_api_key: str
    gemini_api_key: str
    chroma_global_store: str
    chroma_user_store: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
