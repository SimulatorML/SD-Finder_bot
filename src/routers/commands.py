from aiogram import Bot, Router, types
from aiogram.enums.chat_action import ChatAction
from aiogram.filters import Command, CommandObject
from loguru import logger

from src.config import messages
from src.routers.schemas import FinderResult
from src.services.base import ServiceFactory
from src.services.system import SystemService
from src.utils.markup import main_menu

router = Router()


@router.message(Command(commands=["start"]))
async def welcome(message: types.Message, service_factory: ServiceFactory) -> None:
    await message.answer(messages.welcome.format(message.from_user.full_name), reply_markup=main_menu)

    system_service: SystemService = service_factory.get_service("system")
    await system_service.register_user(telegram_id=message.from_user.id, username=message.from_user.username)


@router.message(Command(commands=["help"]))
async def help(message: types.Message) -> None:
    await message.answer(
        messages.help,
        reply_markup=main_menu,
    )


@router.message(Command(commands=["find"]))
async def find(message: types.Message, command: CommandObject, bot: Bot, service_factory: ServiceFactory) -> None:
    try:
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

        request = command.args
        logger.info(f"Request: {request}")

        service = service_factory.get_service("finder")
        result: FinderResult = await service.process_request(request, message.from_user.id)

        logger.info(f"Result: {result}")

        await message.answer(result, parse_mode="markdown", disable_web_page_preview=True)
    except Exception as exp:
        logger.error(f"Error while handling finder request: {exp}")
        await message.answer(messages.finder_error)
