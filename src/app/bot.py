import asyncio

from aiogram import Bot, Dispatcher, Router
from aiogram.types import BotCommand
from loguru import logger

from src.config import settings
from src.routers.callbacks import router as router_callbacks
from src.routers.commands import router as router_commands
from src.services.base import ServiceFactory
from src.services.finder import FinderService
from src.services.system import SystemService


class AssistantBot:
    def __init__(
        self, bot_token: str, service_factory: ServiceFactory, router_commands: Router, router_callbacks: Router
    ) -> None:
        """
        Initializes the object and registers the startup and shutdown events.
        Also includes the specified routers for commands, callbacks, and dialog.
        """
        self.bot = Bot(token=bot_token)
        self.dp = Dispatcher()

        self.dp.startup.register(self.startup_event)
        self.dp.shutdown.register(self.shutdown_event)

        self.dp.include_router(router_commands)
        self.dp.include_router(router_callbacks)

        self.dp["service_factory"] = service_factory
        self.dp["bot"] = self.bot

    async def start(self) -> None:
        """
        Starts the bot by polling the dispatcher.
        """
        await self.dp.start_polling(self.bot)

    async def startup_event(self) -> None:
        """
        An asynchronous function to handle the startup event. It sets the bot commands and logs a warning message.
        """
        bot_commands = [
            BotCommand(command="/help", description="ℹ️ About me"),  # noqa: RUF001
        ]
        await self.bot.set_my_commands(bot_commands)

        logger.warning("Registered commands")
        logger.warning("Bot started")

    async def shutdown_event(self) -> None:
        """
        Asynchronous function to handle the shutdown event of the bot.
        """
        logger.warning("Bot stopped")


if __name__ == "__main__":
    design_finder_service = FinderService(base_url=settings.finder_api_url)
    system_service = SystemService(base_url=settings.finder_api_url)
    service_factory = ServiceFactory(
        {
            "finder": design_finder_service,
            "system": system_service,
        }
    )

    bot = AssistantBot(
        bot_token=settings.bot_token,
        service_factory=service_factory,
        router_commands=router_commands,
        router_callbacks=router_callbacks,
    )
    asyncio.run(bot.start())
