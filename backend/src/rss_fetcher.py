import feedparser
from urllib.parse import quote

RSS_BASE = "https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"

CATEGORIES = [
    {
        "name": "震災関連",
        "query": "震災 イベント OR 講演 OR 追悼",
    },
    {
        "name": "防災関連",
        "query": "防災 シンポジウム OR 講座 OR 訓練",
    },
    {
        "name": "アール・ブリュット関連",
        "query": "アール・ブリュット",
    },
    {
        "name": "シンポジウム関連",
        "query": "シンポジウム 開催",
    },
    {
        "name": "学会・サミット・フォーラム関連",
        "query": "学術 OR 研究 OR 医学 OR 福祉 サミット OR フォーラム OR 学会",
    },
]


def fetch_all() -> list[dict]:
    articles = []
    for cat in CATEGORIES:
        url = RSS_BASE.format(query=quote(cat["query"]))
        feed = feedparser.parse(url)
        for entry in feed.entries:
            articles.append({
                "category": cat["name"],
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "url": entry.get("link", ""),
                "published": entry.get("published", ""),
            })
        print(f"[{cat['name']}] {len(feed.entries)} articles fetched")
    return articles
