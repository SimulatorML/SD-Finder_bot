import aiohttp

from src.routers.schemas import FinderResult, FindRequest
from src.services.base import BaseService


class FinderService(BaseService):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    async def process_request(self, request: str, user_id: int) -> FinderResult:
        payload = FindRequest(user_id=user_id, request=request, source="telegram_bot")
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/v1/find", json=payload.model_dump()) as response:
                result = await response.json()
                return FinderResult(**result).response
