import asyncio

import aiohttp
from aiogram import Bot, types
from aiogram.enums.chat_action import ChatAction
from aiogram.fsm.context import FSMContext
from loguru import logger

from src.config import messages, settings
from src.routers.schemas import DocumentSchema, FinderResult, FindRequest
from src.services.base import BaseService
from src.utils.markup import back_menu, pagination_menu


class FinderService(BaseService):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    async def api_call(self, request: str, user_id: int) -> FinderResult:
        payload = FindRequest(user_id=user_id, request=request, source="telegram")
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/v1/find", json=payload.model_dump()) as response:
                result = await response.json()
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

    async def process_request(self, message: types.Message, state: FSMContext, bot: Bot) -> FinderResult:
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

        request = message.text
        await state.update_data(request=request)

        logger.info(f"Request: {request}")

        result = await self.api_call(request, message.from_user.id)

        logger.info(f"Result: {result}")

        await state.update_data(responses=result.responses)
        await state.update_data(current_page=1)
        await state.update_data(total_pages=len(result.responses))

        await self.send_documents_page(message, state, 1)
        await asyncio.sleep(2)
        await message.answer(messages.request_followup_finder_input, reply_markup=back_menu)

    async def send_documents_page(
        self, message: types.Message, state: FSMContext, page: int, edit: bool = False
    ) -> None:
        data = await state.get_data()
        responses = data["responses"]
        response_text = responses[page - 1]
        total_pages = data["total_pages"]

        if edit:
            await message.edit_text(
                response_text,
                parse_mode="markdown",
                reply_markup=pagination_menu(page, total_pages),
                disable_web_page_preview=True,
            )
        else:
            await message.answer(
                response_text,
                parse_mode="markdown",
                reply_markup=pagination_menu(page, total_pages),
                disable_web_page_preview=True,
            )
