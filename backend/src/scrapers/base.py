from abc import ABC, abstractmethod

from ..models import Event


class EventScraper(ABC):
    @abstractmethod
    def fetch(self, keyword: str, category: str) -> list[Event]:
        ...
