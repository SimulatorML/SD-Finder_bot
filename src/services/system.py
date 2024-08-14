import aiohttp

from src.routers.schemas import UserCreateSchema


class SystemService:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    async def register_user(self, telegram_id: int, username: str | None) -> None:
        payload = UserCreateSchema(telegram_id=telegram_id, username=username, email=None, password=None)
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/v1/register", json=payload.model_dump()) as response:
                return
