from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from loguru import logger

from src.config import messages
from src.routers.schemas import FeedbackCallback, MenuCallback, PaginationMenu, RequestState
from src.services.base import ServiceFactory
from src.utils.markup import back_menu, main_menu, pagination_menu

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
        data = await state.get_data()
        service_name = data["service_name"]
        service = service_factory.get_service(service_name)
        await service.process_request(message, state, bot)
    except Exception as exp:
        logger.error(f"Error while handling finder request: {exp}")
        await message.answer(messages.finder_error, reply_markup=back_menu)


@router.callback_query(PaginationMenu.filter())
async def pagination(
    callback_query: CallbackQuery, callback_data: PaginationMenu, service_factory: ServiceFactory
) -> None:
    try:
        query_id = callback_data.query_id
        page = int(callback_data.page)
        show_feedback_buttons = callback_data.show_feedback_buttons
        service_name = callback_data.service_name
        service = service_factory.get_service(service_name)

        await service.paginate(
            message=callback_query.message, query_id=query_id, page=page, show_feedback_buttons=show_feedback_buttons
        )
    except KeyError:
        logger.info(f"Could not find pagination data for {query_id}")
        await callback_query.answer(messages.finder_pagination_expired_error)
    except Exception as exp:
        logger.error(f"Error while handling pagination for {query_id}: {exp}")
        await callback_query.answer(messages.finder_error)


@router.callback_query(FeedbackCallback.filter())
async def finder_feedback(
    callback_query: CallbackQuery, callback_data: FeedbackCallback, service_factory: ServiceFactory
) -> None:
    page = int(callback_data.page)
    total_pages = int(callback_data.total_pages)
    query_id = callback_data.query_id
    label = callback_data.label
    service_name = callback_data.service_name

    service = service_factory.get_service(service_name)

    try:
        await service.process_feedback(query_id=query_id, label=label)
    except Exception as exp:
        logger.error(f"Error while processing finder feedback: {exp}")
    finally:
        await callback_query.answer(messages.feedback_thanks_message)
        await callback_query.message.edit_reply_markup(
            reply_markup=pagination_menu(
                page=page,
                total_pages=total_pages,
                query_id=query_id,
                service_name=service_name,
                show_feedback_buttons=False,
            )
        )
