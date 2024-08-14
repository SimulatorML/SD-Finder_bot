from abc import ABC, abstractmethod


class BaseService(ABC):
    @abstractmethod
    async def process_request(self) -> None:
        raise NotImplementedError


class ServiceFactory:
    def __init__(self, services: dict[str, BaseService]) -> None:
        self.services = services

    def get_service(self, service_name: str) -> BaseService:
        return self.services.get(service_name)
