from datetime import date

import requests

from ..models import Event
from .base import EventScraper

ENDPOINT = "https://connpass.com/api/v1/event/"
TIMEOUT = 10


class ConnpassScraper(EventScraper):
    def __init__(self, session: requests.Session | None = None) -> None:
        self._session = session or requests.Session()

    def fetch(self, keyword: str, category: str) -> list[Event]:
        try:
            resp = self._session.get(
                ENDPOINT,
                params={"keyword": keyword, "count": 100, "order": 2},
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return []

        today = date.today().isoformat()
        events = []
        for item in data.get("events", []):
            started_at = item.get("started_at", "")
            event_date = started_at[:10] if started_at else None
            if event_date and event_date < today:
                continue
            event_time = started_at[11:16] if len(started_at) >= 16 else None
            location = item.get("place") or item.get("address") or None

            events.append(Event(
                event_title=item.get("title", ""),
                event_date=event_date,
                event_time=event_time,
                event_location=location,
                event_description=(item.get("catch") or "")[:100],
                source_url=item.get("event_url", ""),
                category=category,
                is_event=True,
            ))
        return events
