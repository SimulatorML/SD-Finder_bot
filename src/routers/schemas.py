import uuid

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from pydantic import BaseModel


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
    score: float
    metadata: dict | None


class BaseResult(BaseModel):
    request: str
    response: str


class FinderResult(BaseResult):
    documents: list[DocumentSchema]
    responses: list[str]


class MenuCallback(CallbackData, prefix="menu"):
    feature: str


class PaginationMenu(CallbackData, prefix="page"):
    page: str


class RequestState(StatesGroup):
    service_name = State()
    request = State()
    responses = State()
    current_page = State()
    total_pages = State()
