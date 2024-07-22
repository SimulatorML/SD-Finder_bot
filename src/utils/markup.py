from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.routers.schemas import MenuCallback

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Design Finder", callback_data=MenuCallback(feature="design_finder").pack())],
        # [InlineKeyboardButton(text="Another Service", callback_data="service:another_service")],
    ]
)

back_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Back", callback_data=MenuCallback(feature="back_menu").pack())],
    ]
)
