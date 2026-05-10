import json
import anthropic
from .models import Event

BATCH_SIZE = 10

SYSTEM_PROMPT = """You are an assistant that extracts event information from Japanese news articles.
Classify an article as is_event: true if it announces or describes an upcoming or ongoing event of any kind,
including: lectures, exhibitions, workshops, symposiums, festivals, community events, memorial ceremonies,
training drills, academic conferences, competitions, concerts, and cultural events.
When in doubt, set is_event: true — err on the side of inclusion.
Only set is_event: false when the article is clearly a news report about a past event,
a column or opinion piece, or a product/service announcement with no event component."""

USER_PROMPT_TEMPLATE = """Analyze the following list of articles and determine whether each one is about an event. Return structured data.

Articles:
{articles}

Return a JSON array in the following format (no other text):
[
  {{
    "index": 1,
    "is_event": true,
    "event_title": "event name",
    "event_date": "YYYY-MM-DD or null",
    "event_time": "HH:MM or null",
    "event_location": "venue name or null",
    "event_description": "summary (100 chars or less)"
  }}
]"""


def extract_events(articles: list[dict], client: anthropic.Anthropic) -> list[Event]:
    events = []
    for i in range(0, len(articles), BATCH_SIZE):
        batch = articles[i:i + BATCH_SIZE]
        batch_events = _process_batch(batch, client)
        events.extend(batch_events)
        print(f"  Batch {i // BATCH_SIZE + 1}: {len(batch)} processed -> {len(batch_events)} events extracted")
    return events


def _build_prompt(batch: list[dict]) -> str:
    articles_text = "\n".join(
        f"[{j + 1}] title: {a['title']} / summary: {a['summary'][:400]}"
        for j, a in enumerate(batch)
    )
    return USER_PROMPT_TEMPLATE.format(articles=articles_text)


def _parse_response(response_text: str, batch: list[dict]) -> list[Event]:
    try:
        results = json.loads(response_text)
    except json.JSONDecodeError:
        return []
    events = []
    for item in results:
        if not item.get("is_event"):
            continue
        idx = item.get("index", 1) - 1
        if idx < 0 or idx >= len(batch):
            continue
        article = batch[idx]
        events.append(Event(
            event_title=item.get("event_title", article["title"]),
            event_date=item.get("event_date") or None,
            event_time=item.get("event_time") or None,
            event_location=item.get("event_location") or None,
            event_description=item.get("event_description", ""),
            source_url=article["url"],
            category=article["category"],
            is_event=True,
        ))
    return events


def _process_batch(batch: list[dict], client: anthropic.Anthropic) -> list[Event]:
    prompt = _build_prompt(batch)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        response_text = response.content[0].text
    except IndexError:
        return []
    return _parse_response(response_text, batch)
