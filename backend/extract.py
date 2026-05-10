import json
import re
import time
import threading
import urllib.request
import html as html_mod
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from googlenewsdecoder import gnewsdecoder
from ddgs import DDGS

# limit concurrent DDG requests to avoid rate limiting
_ddg_semaphore = threading.Semaphore(2)
# limit concurrent Google News decode requests to avoid rate limiting
_decode_semaphore = threading.Semaphore(3)

INPUT_PATH = Path(__file__).parent / "output" / "raw_articles.json"
OUTPUT_DIR = Path(__file__).parent / "output"

PAYWALLED_DOMAINS = {
    "nikkei.com", "yomiuri.co.jp", "sankei.com",
    "asahi.com", "mainichi.jp", "chunichi.co.jp",
    "nishinippon.co.jp", "kahoku.com",
}

NEWS_DOMAINS = {
    "yahoo.co.jp", "nhk.or.jp", "nikkei.com", "asahi.com",
    "yomiuri.co.jp", "mainichi.jp", "jiji.com", "kyodonews.jp",
}

# domains that never contain venue information
USELESS_DOMAINS = {
    "youtube.com", "youtu.be", "twitter.com", "x.com",
    "facebook.com", "instagram.com", "mixi.jp", "tiktok.com",
    "google.com", "wikipedia.org", "amazon.co.jp", "amazon.com",
}

VENUE_SUFFIXES = (
    '会館', 'ホール', 'センター', 'ドーム', 'アリーナ', 'プラザ',
    'シアター', 'キャンパス', 'スタジアム', 'ホテル', '大学',
    '図書館', '博物館', '美術館', '体育館', '公会堂', '劇場',
    '公民館', '集会所', '記念館', 'フォーラム', 'ギャラリー',
    '広場', '公園', '神社', '寺院', '境内', '会議所', '会場', '講堂',
)

INVALID_LOCATIONS = {
    'イベントホール', '会議室', 'ホール', 'センター', '大学', 'キャンパス',
    '会館', 'アリーナ', 'プラザ', 'シアター', '劇場', '図書館',
    'フォーラム', 'ギャラリー',
    # functional departments / service names
    'オープンキャンパス', 'コンタクトセンター', 'トレーニングセンター',
    '活動センター', '防災センター',
    # generic hall / venue labels
    'メイン会場', '現地会場', '対面会場', '展示会場', '受賞会場',
    'コンサートホール', '交流ホール', 'ダンスホール',
    # generic names without a proper noun
    'ショッピングプラザ', '会員ホテル',
}

_FUNCTIONAL_DEPT_PAT = re.compile(
    r'地域包括支援センター|視聴者サービスセンター|リスクセンター'
    r'|コールセンター|ヘルプセンター'
)

_suffix_pat = '|'.join(VENUE_SUFFIXES)
LOCATION_PATTERNS = [
    r'会場[：:]\s*([^\s。、\n<]{3,25})',
    r'場所[：:]\s*([^\s。、\n<]{3,25})',
    r'開催場所[：:]\s*([^\s。、\n<]{3,25})',
    r'開催地[：:]\s*([^\s。、\n<]{3,25})',
    r'開催会場[：:]\s*([^\s。、\n<]{3,25})',
    r'会場名[：:]\s*([^\s。、\n<]{3,25})',
    r'開催地点[：:]\s*([^\s。、\n<]{3,25})',
    r'【(?:会場|場所|開催場所|開催地|開催会場|会場名)】\s*([^\s。、\n【】<]{3,25})',
    r'(?:■|●|◆|▶|・)\s*(?:会場|場所|開催場所|開催地|開催会場)\s*[　 ]\s*([^\s。、\n【】：:<]{3,25})',
    r'場[　 ]所[：:]\s*([^\s。、\n<]{3,25})',
    rf'([^\s。、「」（）：:\d【】〔〕]{{2,24}}(?:{_suffix_pat}))(?=[\s　にてでのおいを。、」）]|$)',
]


def validate_location(loc: str | None) -> str | None:
    if not loc:
        return None
    loc = loc.strip()
    # strip parenthetical notes (format, address, etc.)
    loc = re.sub(r'[（(][^）)]*[）)]', '', loc).strip()
    if not loc:
        return None
    if len(loc) > 32:
        return None
    if loc in INVALID_LOCATIONS:
        return None
    if not re.search(r'[ぁ-んァ-ン一-龥]', loc):
        return None
    if re.search(r'[がをはも]', loc):
        return None
    # starts with a particle (に, の, で, etc.)
    if re.match(r'^[にのでをがはも]', loc):
        return None
    if re.search(r'丁目|番地|番[0-9号]', loc):
        return None
    if re.search(r'さん|氏|君|）＝|＝|主催|市長|会見', loc):
        return None
    if re.search(r'[〇□◯▢]{2}|〇〇|未定|TBD|TBA', loc):
        return None
    # strip leading adverbs/modifiers before further validation
    loc = re.sub(r'^(?:初めて|隣接する?|さらに|例えば|その|本学)\s*', '', loc).strip()
    if not loc:
        return None
    # contains a verb, adverb, or modifier — sentence fragment or false match
    if re.search(
        r'する|した|している|隣接|問い合わせ|直接|ぜひ|次の|にある'
        r'|および|ならびに|新しい|高級|ウルトラ|ごとに',
        loc
    ):
        return None
    # starts with a date unit — fragment of a date expression
    if re.match(r'^[年月日]に', loc):
        return None
    # ya between nouns — enumeration pattern
    if re.search(r'[ァ-ン一-龥]や[ァ-ン一-龥]', loc):
        return None
    # kaku + generic noun — multi-venue enumeration
    if re.search(r'各[地会大家学校]', loc):
        return None
    # JSON structural characters — corrupt extraction artifact
    if re.search(r'["{}\[\]【】〔〕]', loc):
        return None
    # special symbols
    if re.search(r'[㎡#／＆]', loc):
        return None
    # emoji and special bullet characters
    if re.search(r'[●■▲◆★☆♦♠♣♥🌟🎵]', loc):
        return None
    # supplementary plane characters (emoji, etc.)
    if any(ord(c) > 0xFFFF for c in loc):
        return None
    # Chinese full-width comma — Japanese uses 、not ，
    if '，' in loc:
        return None
    # corporate entity names
    if re.search(r'株式会社|有限会社|合同会社', loc):
        return None
    # quantity prefix or incomplete expression (か所, つの, 階)
    if re.match(r'^[かつ階]', loc):
        return None
    # functional department name (partial match)
    if _FUNCTIONAL_DEPT_PAT.search(loc):
        return None
    return loc


def get_pub_year(published: str) -> int:
    try:
        return datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z").year
    except Exception:
        return datetime.now().year


def clean_title(title: str) -> str:
    t = title
    t = re.sub(r'\s*-\s*[^-]+$', '', t)
    t = re.sub(r'\s*[｜|][^｜|]+$', '', t)
    t = re.sub(r'[（(]\d{4}年\d{1,2}月\d{1,2}日掲載[）)]', '', t)
    t = re.sub(r'\s+$', '', t)
    return t.strip()


def is_paywalled(url: str) -> bool:
    domain = urlparse(url).netloc.lstrip("www.")
    return any(domain.endswith(d) for d in PAYWALLED_DOMAINS)


def decode_google_url(url: str) -> str:
    try:
        with _decode_semaphore:
            result = gnewsdecoder(url).get("decoded_url", url)
            time.sleep(0.5)
            return result
    except Exception:
        return url


def fetch_html(url: str, timeout: int = 8) -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.read().decode("utf-8", errors="ignore")
    except Exception:
        return None


def extract_text(html_body: str) -> str:
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html_body, re.DOTALL)
    return ' '.join(html_mod.unescape(re.sub(r'<[^>]+>', '', p)) for p in paragraphs)[:3000]


def extract_from_jsonld(html_body: str) -> dict:
    scripts = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html_body, re.DOTALL | re.IGNORECASE
    )
    for s in scripts:
        try:
            data = json.loads(s.strip())
            if isinstance(data, list):
                data = data[0]
            if data.get("@type") in ("Event", "SocialEvent", "EducationEvent", "BusinessEvent"):
                loc = data.get("location") or {}
                if isinstance(loc, str):
                    location = loc
                else:
                    location = loc.get("name") if isinstance(loc, dict) else None
                start = data.get("startDate", "")
                if isinstance(start, list):
                    start = start[0] if start else ""
                if not isinstance(start, str):
                    start = ""
                return {
                    "date": start[:10] if start else None,
                    "time": start[11:16] if len(start) > 10 else None,
                    "location": location,
                }
        except Exception:
            continue
    return {}


def extract_date(text: str, pub_year: int) -> str | None:
    m = re.search(r'令和(\d+)年(\d{1,2})月(\d{1,2})日', text)
    if m:
        return f"{2018 + int(m.group(1))}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.search(r'(20\d{2})年(\d{1,2})月(\d{1,2})日', text)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    # dot- or slash-separated format: 2026.05.10 / 2026/05/10
    m = re.search(r'(20\d{2})[./](\d{1,2})[./](\d{1,2})', text)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.search(r'【(\d{1,2})[/／](\d{1,2})】', text)
    if m:
        return f"{pub_year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    m = re.search(r'(\d{1,2})月(\d{1,2})日', text)
    if m:
        return f"{pub_year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    return None


def extract_time(text: str) -> str | None:
    m = re.search(r'午後(\d{1,2})時(?:(\d{2})分)?', text)
    if m:
        return f"{int(m.group(1)) + 12:02d}:{int(m.group(2)) if m.group(2) else 0:02d}"
    m = re.search(r'午前(\d{1,2})時(?:(\d{2})分)?', text)
    if m:
        return f"{int(m.group(1)):02d}:{int(m.group(2)) if m.group(2) else 0:02d}"
    m = re.search(r'(\d{1,2}):(\d{2})', text)
    if m:
        return f"{int(m.group(1)):02d}:{m.group(2)}"
    # bare hour form (10時, 10時30分) — must not follow a date digit
    m = re.search(r'(?<![月日年第\d])(\d{1,2})時(?:(\d{2})分)?(?![間])', text)
    if m:
        h = int(m.group(1))
        mi = int(m.group(2)) if m.group(2) else 0
        if 0 <= h <= 23:
            return f"{h:02d}:{mi:02d}"
    return None


def extract_location(text: str) -> str | None:
    for pat in LOCATION_PATTERNS:
        m = re.search(pat, text)
        if m:
            result = validate_location(m.group(1))
            if result:
                return result
    return None


def _is_blocked_domain(url: str) -> bool:
    domain = urlparse(url).netloc.lstrip("www.")
    return (
        any(domain.endswith(d) for d in PAYWALLED_DOMAINS)
        or any(domain.endswith(d) for d in USELESS_DOMAINS)
    )


def search_event_pages(event_title: str) -> list[str]:
    query = event_title
    with _ddg_semaphore:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, region="jp-jp", max_results=10))
            return [r["href"] for r in results if not _is_blocked_domain(r["href"])]
        except Exception:
            return []


def _extract_fields_from_html(html_body: str, pub_year: int) -> dict:
    jld = extract_from_jsonld(html_body)
    date = jld.get("date")
    time = jld.get("time")
    location = validate_location(jld["location"]) if jld.get("location") else None
    if not date or not location:
        body_text = extract_text(html_body)
        if not date:
            date = extract_date(body_text, pub_year)
        if not location:
            location = extract_location(body_text)
    return {"date": date, "time": time, "location": location}


def _search_official_fields(title: str, pub_year: int) -> dict:
    result = {"location": None, "date": None}
    for url in search_event_pages(title):
        html_body = fetch_html(url)
        if not html_body:
            continue
        jld = extract_from_jsonld(html_body)
        if jld.get("location") and not result["location"]:
            loc = validate_location(jld["location"])
            if loc:
                result["location"] = loc
        if jld.get("date") and not result["date"]:
            result["date"] = jld["date"]
        body_text = extract_text(html_body)
        if not result["location"]:
            loc = extract_location(body_text)
            if loc:
                result["location"] = loc
        if not result["date"]:
            date = extract_date(body_text, pub_year)
            if date:
                result["date"] = date
        if result["location"] and result["date"]:
            break
    return result


def process_article(a: dict, index: int, total: int) -> dict:
    title_raw = a.get("title", "")
    published = a.get("published", "")
    gn_url = a.get("link", a.get("url", ""))
    category = a.get("category", "")
    pub_year = get_pub_year(published)

    title = clean_title(title_raw)
    event_date = extract_date(title_raw, pub_year)
    event_time = extract_time(title_raw)
    event_location = extract_location(title)

    real_url = decode_google_url(gn_url)
    paywalled = is_paywalled(real_url)
    body_scraped = False

    if not paywalled:
        html_body = fetch_html(real_url)
        if html_body:
            body_scraped = True
            scraped = _extract_fields_from_html(html_body, pub_year)
            if not event_date and scraped["date"]:
                event_date = scraped["date"]
            if not event_time and scraped["time"]:
                event_time = scraped["time"]
            if scraped["location"]:
                event_location = scraped["location"]

    official = _search_official_fields(title, pub_year)
    if official["location"]:
        event_location = official["location"]
    if not event_date and official["date"]:
        event_date = official["date"]

    return {
        "category": category,
        "title": title,
        "event_date": event_date,
        "event_time": event_time,
        "event_location": event_location,
        "location_available": event_location is not None,
        "paywalled": paywalled,
        "published": published,
        "source": a.get("source", {}).get("title", ""),
        "url": real_url,
        "body_scraped": body_scraped,
    }


_print_lock = threading.Lock()


def process_article_indexed(args):
    a, index, total = args
    result = process_article(a, index, total)
    with _print_lock:
        loc = result["event_location"] or "-"
        print(f"  [{index}/{total}] {result['title'][:35]}... -> {loc}")
    return (index, result)


def main():
    with open(INPUT_PATH, encoding="utf-8") as f:
        articles = json.load(f)

    by_category: dict[str, list] = {}
    for a in articles:
        cat = a.get("category", "その他")
        by_category.setdefault(cat, []).append(a)

    OUTPUT_DIR.mkdir(exist_ok=True)

    for category, cat_articles in by_category.items():
        print(f"\n=== {category} ({len(cat_articles)} articles) ===")

        args = [(a, i + 1, len(cat_articles)) for i, a in enumerate(cat_articles)]
        results_indexed = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_article_indexed, arg): arg for arg in args}
            for future in as_completed(futures):
                results_indexed.append(future.result())

        results = [r for _, r in sorted(results_indexed)]

        safe_name = re.sub(r'[\\/:*?"<>|]', '_', category)
        out_path = OUTPUT_DIR / f"{safe_name}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        total = len(results)
        has_date = sum(1 for r in results if r["event_date"])
        has_loc = sum(1 for r in results if r["event_location"])
        paywalled = sum(1 for r in results if r["paywalled"])
        print(f"  -> {out_path.name}: {total} articles / date {has_date}({has_date*100//total}%) / location {has_loc}({has_loc*100//total}%) / paywalled {paywalled}")

    print("\n=== All categories complete ===")


if __name__ == "__main__":
    main()
