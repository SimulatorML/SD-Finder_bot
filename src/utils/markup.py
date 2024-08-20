import uuid

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.routers.schemas import FeedbackCallback, MenuCallback, PaginationMenu

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Design Finder", callback_data=MenuCallback(feature="finder").pack())],
        # [InlineKeyboardButton(text="Another Service", callback_data="service:another_service")],
    ]
)

back_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Back", callback_data=MenuCallback(feature="back_menu").pack())],
    ]
)


def pagination_menu(
    page: int, total_pages: int, query_id: uuid.UUID, service_name: str, show_feedback_buttons: bool = True
) -> InlineKeyboardMarkup:
    base_data = {
        "query_id": query_id,
        "service_name": service_name,
        "total_pages": str(total_pages),
        "show_feedback_buttons": show_feedback_buttons,
    }
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="◀️ Previous",
                callback_data=PaginationMenu(
                    **base_data,
                    page=str(page - 1),
                ).pack(),
            )
        )
    pagination_buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="kek"))
    if page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(
                text="Next ▶️",
                callback_data=PaginationMenu(
                    **base_data,
                    page=str(page + 1),
                ).pack(),
            )
        )

    if show_feedback_buttons:
        like_dislike_buttons = [
            InlineKeyboardButton(
                text="👎",
                callback_data=FeedbackCallback(
                    **base_data,
                    page=str(page),
                    label="0",
                ).pack(),
            ),
            InlineKeyboardButton(
                text="👍",
                callback_data=FeedbackCallback(
                    **base_data,
                    page=str(page),
                    label="1",
                ).pack(),
            ),
        ]
        return InlineKeyboardMarkup(inline_keyboard=[pagination_buttons, like_dislike_buttons])

    return InlineKeyboardMarkup(inline_keyboard=[pagination_buttons])
