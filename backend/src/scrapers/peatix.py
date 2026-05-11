import json
import re
from datetime import date

import requests

from ..models import Event
from .base import EventScraper

SEARCH_URL = "https://peatix.com/search"
TIMEOUT = 10
_JSONLD_BLOCK = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL,
)


class PeatixScraper(EventScraper):
    def __init__(self, session: requests.Session | None = None) -> None:
        self._session = session or requests.Session()

    def fetch(self, keyword: str, category: str) -> list[Event]:
        try:
            resp = self._session.get(
                SEARCH_URL,
                params={"q": keyword, "l.country": "JP"},
                headers={"Accept-Language": "ja"},
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            html = resp.text
        except Exception:
            return []

        today = date.today().isoformat()
        events = []
        for block in _JSONLD_BLOCK.findall(html):
            try:
                data = json.loads(block)
            except json.JSONDecodeError:
                continue

            items = data if isinstance(data, list) else [data]
            for item in items:
                if item.get("@type") != "Event":
                    continue
                start_date = item.get("startDate", "")
                event_date = start_date[:10] if start_date else None
                if event_date and event_date < today:
                    continue
                event_time = start_date[11:16] if len(start_date) >= 16 else None
                location = item.get("location", {})
                loc_name = location.get("name") if isinstance(location, dict) else None

                events.append(Event(
                    event_title=item.get("name", ""),
                    event_date=event_date,
                    event_time=event_time,
                    event_location=loc_name,
                    event_description=(item.get("description") or "")[:100],
                    source_url=item.get("url", ""),
                    category=category,
                    is_event=True,
                ))
        return events
