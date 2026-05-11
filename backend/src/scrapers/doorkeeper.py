import re
from datetime import date

import requests

from ..models import Event
from .base import EventScraper

ENDPOINT = "https://api.doorkeeper.jp/events"
TIMEOUT = 10
_HTML_TAG = re.compile(r"<[^>]+>")


class DoorkeeperScraper(EventScraper):
    def __init__(self, session: requests.Session | None = None) -> None:
        self._session = session or requests.Session()

    def fetch(self, keyword: str, category: str) -> list[Event]:
        try:
            resp = self._session.get(
                ENDPOINT,
                params={"q": keyword, "locale": "ja"},
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return []

        today = date.today().isoformat()
        events = []
        for item in data:
            ev = item.get("event", {})
            starts_at = ev.get("starts_at", "")
            event_date = starts_at[:10] if starts_at else None
            if event_date and event_date < today:
                continue
            event_time = starts_at[11:16] if len(starts_at) >= 16 else None
            location = ev.get("venue_name") or ev.get("address") or None
            desc = _HTML_TAG.sub("", ev.get("description") or "")[:100]

            events.append(Event(
                event_title=ev.get("title", ""),
                event_date=event_date,
                event_time=event_time,
                event_location=location,
                event_description=desc,
                source_url=ev.get("public_url", ""),
                category=category,
                is_event=True,
            ))
        return events
