from ..models import Event
from .base import EventScraper
from .connpass import ConnpassScraper
from .doorkeeper import DoorkeeperScraper

_DEFAULT_SCRAPERS: list[EventScraper] = [
    ConnpassScraper(),
    DoorkeeperScraper(),
]


def fetch_all_scrapers(
    categories: list[dict],
    scrapers: list[EventScraper] | None = None,
) -> list[Event]:
    active = scrapers if scrapers is not None else _DEFAULT_SCRAPERS
    events: list[Event] = []
    for cat in categories:
        keyword = cat["query"]
        name = cat["name"]
        for scraper in active:
            events.extend(scraper.fetch(keyword, name))
    return events
