import aiohttp

from src.routers.schemas import DocumentSchema, FinderResult, FindRequest
from src.services.base import BaseService


class FinderService(BaseService):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    async def process_request(self, request: str, user_id: int) -> FinderResult:
        payload = FindRequest(user_id=user_id, request=request, source="telegram_bot")
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/v1/find", json=payload.model_dump()) as response:
                result = await response.json()
                docs = [DocumentSchema(**doc) for doc in result["documents"]]
                result["response"] = self._prepare_response(docs)

                return FinderResult(**result).response

    def _prepare_response(self, docs: list[DocumentSchema]) -> str:
        response_lines = []
        for doc in docs:
            line = (
                f"*Company*: {doc.company}\n"
                f"*Industry*: {doc.industry}\n"
                f"*Description*: {doc.description}\n"
                f"*Tags*: {doc.tags}\n"
                f"[Read More]({doc.s3_link})"
            )
            response_lines.append(line)

        return "\n\n---\n\n".join(response_lines)
