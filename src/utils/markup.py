from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.routers.schemas import MenuCallback, PaginationMenu

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


def pagination_menu(page: int, total_pages: int) -> InlineKeyboardMarkup:
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(text="◀️ Previous", callback_data=PaginationMenu(page=str(page - 1)).pack())
        )
    pagination_buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="kek"))
    if page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(text="Next ▶️", callback_data=PaginationMenu(page=str(page + 1)).pack())
        )
    return InlineKeyboardMarkup(inline_keyboard=[pagination_buttons])
