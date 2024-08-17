import uuid

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from pydantic import BaseModel

# ---pydantic models---


class UserCreateSchema(BaseModel):
    telegram_id: int | None
    username: str | None
    email: str | None
    password: str | None


class FindRequest(BaseModel):
    user_id: int
    request: str
    source: str


class DocumentSchema(BaseModel):
    doc_id: uuid.UUID
    company: str | None
    industry: str | None
    title: str | None
    description: str | None
    summarization: str | None
    tags: str | None
    year: int | None
    source: str | None
    status: str | None
    s3_link: str
    score: float | None
    metadata: dict | None


class BaseResult(BaseModel):
    request: str
    response: str


class FinderResult(BaseResult):
    query_id: uuid.UUID
    documents: list[DocumentSchema]
    responses: list[str]


class Feedback(BaseModel):
    query_id: uuid.UUID
    label: str

    def model_dump(self, *args, **kwargs):  # noqa: ANN201, ANN002, ANN003
        data = super().model_dump(*args, **kwargs)
        data["query_id"] = str(data["query_id"])
        return data


# ---callback data---


class MenuCallback(CallbackData, prefix="menu"):
    feature: str


class PaginationMenu(CallbackData, prefix="page"):
    query_id: uuid.UUID
    service_name: str
    page: str
    total_pages: str
    show_feedback_buttons: bool


class FeedbackCallback(PaginationMenu, prefix="feedback"):
    label: str


# ---states---


class RequestState(StatesGroup):
    service_name = State()
    request = State()
