import json
import feedparser
from urllib.parse import quote
from pathlib import Path

RSS_BASE = "https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"

CATEGORIES = [
    {"name": "震災関連",              "query": "震災 イベント OR 講演 OR 追悼"},
    {"name": "防災関連",              "query": "防災 シンポジウム OR 講座 OR 訓練"},
    {"name": "アール・ブリュット関連", "query": "アール・ブリュット"},
    {"name": "シンポジウム関連",       "query": "シンポジウム 開催"},
    {"name": "学会・サミット・フォーラム関連", "query": "学術 OR 研究 OR 医学 OR 福祉 サミット OR フォーラム OR 学会"},
]

output_path = Path(__file__).parent / "output" / "raw_articles.json"
output_path.parent.mkdir(exist_ok=True)

all_articles = []

for cat in CATEGORIES:
    url = RSS_BASE.format(query=quote(cat["query"]))
    feed = feedparser.parse(url)
    for entry in feed.entries:
        article = {"category": cat["name"]}
        for key in entry.keys():
            val = entry[key]
            try:
                json.dumps(val)
                article[key] = val
            except (TypeError, ValueError):
                article[key] = str(val)
        all_articles.append(article)
    print(f"[{cat['name']}] {len(feed.entries)} articles fetched")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_articles, f, ensure_ascii=False, indent=2)

print(f"\nOutput written: {output_path}")
print(f"Total: {len(all_articles)} articles")
