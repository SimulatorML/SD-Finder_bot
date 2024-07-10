import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

ENV = os.getenv("ENV", "local")

load_dotenv(Path(f".env.{ENV}"))


class Settings(BaseSettings):
    bot_token: str = os.getenv("BOT_TOKEN")
    finder_api_url: str = os.getenv("FINDER_API_URL")


settings = Settings()
