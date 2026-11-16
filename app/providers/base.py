from abc import ABC, abstractmethod
from app.models import Resource

class Provider(ABC):
    name: str
    @abstractmethod
    def test_connection(self) -> dict: ...
    @abstractmethod
    def list_resources(self) -> list[Resource]: ...
    @abstractmethod
    def act(self, resource_id: str, action: str) -> dict: ...
