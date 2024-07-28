from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from loguru import logger

from src.config import messages
from src.routers.schemas import MenuCallback, PaginationMenu, RequestState
from src.services.base import ServiceFactory
from src.utils.markup import back_menu, main_menu

router = Router()


@router.callback_query(MenuCallback.filter(F.feature != "back_menu"))
async def handle_service(callback_query: CallbackQuery, callback_data: MenuCallback, state: FSMContext) -> None:
    service_name = callback_data.feature
    await state.update_data(service_name=service_name)
    await state.set_state(RequestState.request)

    logger.info(f"Selected service: {service_name}")

    await callback_query.message.edit_text(
        messages.request_finder_input,
        reply_markup=back_menu,
        parse_mode="markdown",
    )


@router.callback_query(MenuCallback.filter(F.feature == "back_menu"))
async def back_to_main_menu(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback_query.message.edit_text(messages.main_menu, reply_markup=main_menu)


@router.message(RequestState.request)
async def handle_request(message: types.Message, state: FSMContext, bot: Bot, service_factory: ServiceFactory) -> None:
    try:
        request = message.text
        await state.update_data(request=request)
        data = await state.get_data()
        service_name = data["service_name"]

        service = service_factory.get_service(service_name)
        await service.process_request(message, state, bot)
    except Exception as exp:
        logger.error(f"Error while handling finder request: {exp}")
        await message.answer(messages.finder_error, reply_markup=back_menu)


@router.callback_query(PaginationMenu.filter())
async def pagination(
    callback_query: CallbackQuery, callback_data: PaginationMenu, state: FSMContext, service_factory: ServiceFactory
) -> None:
    try:
        page = int(callback_data.page)
        data = await state.get_data()
        service_name = data["service_name"]
        service = service_factory.get_service(service_name)

        await service.send_documents_page(message=callback_query.message, state=state, page=page, edit=True)
    except Exception as exp:
        logger.error(f"Error while handling finder request: {exp}")
        await callback_query.answer(messages.finder_error)
