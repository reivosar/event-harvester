from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Event:
    event_title: str
    event_date: Optional[str]        # YYYY-MM-DD
    event_time: Optional[str]        # HH:MM
    event_location: Optional[str]
    event_description: str
    source_url: str
    category: str
    is_event: bool

    def to_dict(self) -> dict:
        return asdict(self)
