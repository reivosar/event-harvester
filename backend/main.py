import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

from extract import process_article
from src.rss_fetcher import fetch_all
from src.models import Event

OUTPUT_PATH = Path(__file__).parent / "output" / "events.json"


def _normalize_title(title: str) -> str:
    stripped = re.sub(r'\s*[-|｜][^-|｜]+$', '', title).strip()
    return stripped.lower() if len(stripped) >= 8 else title.strip().lower()


def deduplicate_articles(articles: list[dict]) -> list[dict]:
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    result = []
    for a in articles:
        url = a.get("url", "")
        title_norm = _normalize_title(a.get("title", ""))
        if url in seen_urls or title_norm in seen_titles:
            continue
        seen_urls.add(url)
        if title_norm:
            seen_titles.add(title_norm)
        result.append(a)
    return result


def articles_to_events(articles: list[dict]) -> list[Event]:
    if not articles:
        return []
    total = len(articles)

    def _process(idx_article: tuple[int, dict]) -> tuple[int, dict, dict]:
        idx, a = idx_article
        result = process_article(a, idx, total)
        loc = result["event_location"] or "-"
        print(f"  [{idx}/{total}] {result['title'][:35]}... -> {loc}")
        return idx, result, a

    indexed: list[tuple[int, dict, dict]] = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(_process, (i + 1, a)): i for i, a in enumerate(articles)}
        for future in as_completed(futures):
            indexed.append(future.result())

    indexed.sort(key=lambda x: x[0])
    return [
        Event(
            event_title=result["title"],
            event_date=result["event_date"],
            event_time=result["event_time"],
            event_location=result["event_location"],
            event_description=article.get("summary", "")[:100],
            source_url=result["url"],
            category=result["category"],
            is_event=True,
        )
        for _, result, article in indexed
    ]


def _event_dedup_key(e: Event) -> tuple:
    if e.event_date:
        return (e.event_title, e.event_date)
    domain = urlparse(e.source_url).netloc.lstrip("www.")
    return (_normalize_title(e.event_title), domain)


def deduplicate(events: list[Event]) -> list[Event]:
    seen_urls: set[str] = set()
    seen_keys: set[tuple] = set()
    result = []
    for e in events:
        key = _event_dedup_key(e)
        if e.source_url in seen_urls or key in seen_keys:
            continue
        seen_urls.add(e.source_url)
        seen_keys.add(key)
        result.append(e)
    return result


def main():
    print("=== Fetching RSS ===")
    articles = fetch_all()
    print(f"Fetched {len(articles)} articles")
    articles = deduplicate_articles(articles)
    print(f"After pre-dedup: {len(articles)} articles\n")

    events = articles_to_events(articles)
    events = deduplicate(events)
    print(f"After deduplication: {len(events)} events\n")

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump([e.to_dict() for e in events], f, ensure_ascii=False, indent=2)

    print("=== Done ===")
    print(f"Output: {OUTPUT_PATH}")

    by_category: dict[str, int] = {}
    for e in events:
        by_category.setdefault(e.category, 0)
        by_category[e.category] += 1
    for cat, count in by_category.items():
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
