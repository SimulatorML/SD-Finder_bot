from abc import ABC, abstractmethod

from src.routers.schemas import BaseResult


class BaseService(ABC):
    @abstractmethod
    async def api_call(self, request: str, user_id: int) -> BaseResult:
        raise NotImplementedError

    @abstractmethod
    async def process_request(self) -> None:
        raise NotImplementedError


class ServiceFactory:
    def __init__(self, services: dict[str, BaseService]) -> None:
        self.services = services

    def get_service(self, service_name: str) -> BaseService:
        return self.services.get(service_name)
