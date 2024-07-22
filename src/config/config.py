import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

ENV = os.getenv("ENV", "local")

load_dotenv(Path(f".env.{ENV}"))


class Settings(BaseSettings):
    bot_token: str = os.getenv("BOT_TOKEN")
    finder_api_url: str = os.getenv("FINDER_API_URL")
    messages_yaml_filepath: Path = Path("src/config/messages.yaml")


class Messages:
    def __init__(self, yaml_filepath: str) -> None:
        self.yaml_filepath = yaml_filepath

    def _load_messages(self) -> dict[str, str]:
        with open(self.yaml_filepath) as file:
            return yaml.safe_load(file)

    def __getattr__(self, name: str) -> str:
        messages = self._load_messages()
        if name in messages:
            return messages[name]
        raise AttributeError(f"'Messages' object has no attribute '{name}'")


settings = Settings()
messages = Messages(settings.messages_yaml_filepath)
