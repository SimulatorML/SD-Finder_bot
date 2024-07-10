import asyncio

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from loguru import logger

from src.routers.schemas import FinderResult, MenuCallback, RequestState
from src.services.base import ServiceFactory
from src.utils.markup import back_menu, main_menu

router = Router()


@router.callback_query(MenuCallback.filter(F.feature != "back_menu"))
async def handle_service(callback_query: CallbackQuery, callback_data: MenuCallback, state: FSMContext) -> None:
    # bot = callback_query.bot
    service_name = callback_data.feature
    await state.update_data(service_name=service_name)
    await state.set_state(RequestState.request)

    logger.info(f"Selected service: {service_name}")

    await callback_query.message.edit_text(
        "Tell me what you're looking for!",
        reply_markup=back_menu,
        parse_mode="markdown",
    )


@router.callback_query(MenuCallback.filter(F.feature == "back_menu"))
async def back_to_main_menu(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback_query.message.edit_text("What do you want to do?", reply_markup=main_menu)


@router.message(RequestState.request)
async def handle_request(message: types.Message, state: FSMContext, service_factory: ServiceFactory) -> None:
    request = message.text
    await state.update_data(request=request)
    data = await state.get_data()
    service_name = data["service_name"]

    logger.info(f"Request: {request}")

    service = service_factory.get_service(service_name)
    result: FinderResult = await service.process_request(request, message.from_user.id)

    logger.info(f"Result: {result}")

    await message.answer(result, parse_mode="markdown", disable_web_page_preview=True)
    await asyncio.sleep(2)
    await message.answer("Found what you needed? Don't hesitate to ask for more!", reply_markup=back_menu)
