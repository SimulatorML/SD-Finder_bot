import asyncio
import uuid

import aiohttp
from aiogram import Bot, types
from aiogram.enums.chat_action import ChatAction
from aiogram.fsm.context import FSMContext
from expiringdict import ExpiringDict
from loguru import logger

from src.config import messages, settings
from src.routers.schemas import DocumentSchema, Feedback, FinderResult, FindRequest
from src.services.base import BaseService
from src.utils.markup import back_menu, pagination_menu


class FinderService(BaseService):
    def __init__(self, base_url: str) -> None:
        self.service_name = "finder"
        self.base_url = base_url
        self.pagination_data = ExpiringDict(
            max_len=settings.pagination_max_len, max_age_seconds=settings.pagination_max_age_seconds
        )

    async def _fetch(self, method: str, url: str, json_data: dict | None = None) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                if method.lower() == "post":
                    async with session.post(url, json=json_data) as response:
                        response.raise_for_status()
                        return await response.json()
                elif method.lower() == "get":
                    async with session.get(url) as response:
                        response.raise_for_status()
                        return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            raise

    async def _find_documents(self, request: str, user_id: int) -> FinderResult:
        payload = FindRequest(user_id=user_id, request=request, source="telegram")
        result = await self._fetch("post", f"{self.base_url}/api/v1/find", json_data=payload.model_dump())
        return await self._prepare_finder_result(result)

    async def _get_results_by_query_id(self, query_id: uuid.UUID) -> FinderResult:
        result = await self._fetch("get", f"{self.base_url}/api/v1/query/{query_id}")
        return await self._prepare_finder_result(result)

    async def _prepare_finder_result(self, result: dict) -> FinderResult:
        docs = [DocumentSchema(**doc) for doc in result["documents"]]
        result["response"] = ""
        result["responses"] = self._prepare_responses(docs)
        return FinderResult(**result)

    def _prepare_responses(self, docs: list[DocumentSchema]) -> list[str]:
        responses = []
        for i in range(0, len(docs), settings.documents_per_page):
            response = []
            docs_slice = docs[i : i + settings.documents_per_page]
            for doc in docs_slice:
                line = (
                    f"*Company*: {doc.company}\n"
                    f"*Industry*: {doc.industry}\n"
                    f"*Description*: {doc.description}\n"
                    f"*Tags*: {doc.tags}\n"
                    f"[Read More]({doc.s3_link})"
                )
                response.append(line)
            responses.append("\n\n---\n\n".join(response))
        return responses

    async def process_request(self, message: types.Message, state: FSMContext, bot: Bot) -> None:
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

        request = message.text
        await state.update_data(request=request)

        logger.info(f"Request: {request}")
        result: FinderResult = await self._find_documents(request, message.from_user.id)
        logger.info(f"Result: {result}")

        self.pagination_data[result.query_id] = result.responses

        await message.answer(
            result.responses[0],
            parse_mode="markdown",
            reply_markup=pagination_menu(
                page=1, total_pages=len(result.responses), query_id=result.query_id, service_name=self.service_name
            ),
            disable_web_page_preview=True,
        )
        await asyncio.sleep(2)
        await message.answer(messages.request_followup_finder_input, reply_markup=back_menu)

    async def paginate(
        self, message: types.Message, query_id: uuid.UUID, page: int, show_feedback_buttons: bool
    ) -> None:
        responses = self.pagination_data.get(query_id)
        if not responses:
            logger.info(f"Fetching data for query_id {query_id} from finder service...")
            result = await self._get_results_by_query_id(query_id)
            if not result.responses:
                raise KeyError(f"Pagination data for query_id {query_id} has expired or does not exist")

            logger.info(f"Fetched data for query_id {query_id} from finder service")
            self.pagination_data[query_id] = result.responses
            responses = result.responses

        response_text = responses[page - 1]
        total_pages = len(responses)

        await message.edit_text(
            response_text,
            parse_mode="markdown",
            reply_markup=pagination_menu(
                page=page,
                total_pages=total_pages,
                query_id=query_id,
                service_name=self.service_name,
                show_feedback_buttons=show_feedback_buttons,
            ),
            disable_web_page_preview=True,
        )

    async def process_feedback(self, query_id: uuid.UUID, label: str) -> None:
        positive_label = "1"
        label = "like" if label == positive_label else "dislike"
        payload = Feedback(query_id=query_id, label=label)
        await self._fetch("post", f"{self.base_url}/api/v1/feedback", json_data=payload.model_dump())
