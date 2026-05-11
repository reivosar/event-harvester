# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Event Harvester is a two-part system:

1. **Backend pipeline** (Python): fetches Japanese event articles from Google News RSS, enriches each article with date/time/venue by scraping the article page and searching DuckDuckGo for the official event page, then writes a structured JSON file.
2. **Frontend** (React + TypeScript + Vite): reads that JSON file as a static asset and renders a filterable, date-sorted event list.

The frontend and backend share no runtime connection — the only coupling is `events.json`.

## Commands

### Backend

```bash
cd backend
python -m venv .venv          # first time only
source .venv/bin/activate
pip install -r requirements.txt

python main.py                 # full pipeline: RSS fetch → extract → output/events.json
python dump_raw.py             # RSS fetch only → output/raw_articles.json
python extract.py              # extract from existing output/raw_articles.json
```

Run tests:

```bash
cd backend
python -m pytest test_extract.py -v
python -m pytest test_extract.py::TestValidateLocation::test_generic_venue_names_rejected -v  # single test
python -m pytest test_pipeline.py -v
```

### Frontend

```bash
cd frontend
npm install                    # first time only

npm run dev                    # dev server at http://localhost:5173
npm run build                  # type-check + Vite build → dist/
npm run lint                   # ESLint
npm test                       # Vitest (run once)
npm run test:watch             # Vitest (watch mode)
```

### Connecting pipeline output to the frontend

After running the backend pipeline, copy the output to the frontend public directory:

```bash
cp backend/output/events.json frontend/public/events.json
```

`frontend/public/events.json` is gitignored; it must be regenerated locally.

## Environment

Backend requires `backend/.env`:

```
ANTHROPIC_API_KEY=your_key_here
```

Copy `backend/.env.example` to `backend/.env` and fill in the key.

## Architecture

### Backend pipeline (`backend/`)

```
main.py           — orchestrates the full pipeline
dump_raw.py       — standalone RSS fetcher; writes raw_articles.json
extract.py        — article enrichment; importable as process_article()
src/
  rss_fetcher.py  — fetch_all(): queries Google News RSS for 5 categories
  models.py       — Event dataclass with to_dict()
output/           — pipeline output (gitignored)
```

Pipeline flow in `main.py`:

1. `fetch_all()` — queries Google News RSS for each of the 5 categories, returns list of `{category, title, summary, url, published}` dicts
2. `deduplicate_articles()` — deduplicates by URL and normalized title before extraction
3. `articles_to_events()` — runs `process_article()` on each article with 10 threads
4. `deduplicate()` — deduplicates extracted `Event` objects by `(title, date)` or `(normalized_title, domain)`
5. Writes `output/events.json`

`process_article()` in `extract.py` enriches a single article:
- Decodes the Google News redirect URL via `googlenewsdecoder`
- If not paywalled: fetches the article HTML and extracts JSON-LD structured data, then falls back to regex patterns for date/time/location
- Always searches DuckDuckGo for an official event page and extracts fields from there (overrides scraped location if found)
- Returns a flat dict with `event_date` (YYYY-MM-DD), `event_time` (HH:MM), `event_location`, etc.

Concurrency limits: DDG semaphore (max 2 concurrent), Google News decode semaphore (max 3 concurrent).

### Categories

Defined in both `backend/src/rss_fetcher.py` and `frontend/src/constants.ts` (must stay in sync):

| Category | RSS query |
|---|---|
| 震災関連 | 震災 イベント OR 講演 OR 追悼 |
| 防災関連 | 防災 シンポジウム OR 講座 OR 訓練 |
| アール・ブリュット関連 | アール・ブリュット |
| シンポジウム関連 | シンポジウム 開催 |
| 学会・サミット・フォーラム関連 | 学術 OR 研究 OR 医学 OR 福祉 サミット OR フォーラム OR 学会 |

### Frontend (`frontend/`)

```
src/
  App.tsx              — root: composes filter + list, owns selected-categories state
  types.ts             — HarvestEvent interface (mirrors Event.to_dict() shape)
  constants.ts         — CATEGORIES list (must match backend)
  hooks/useEvents.ts   — fetches /events.json; returns {events, loading, error}
  components/
    CategoryFilter.tsx — category toggle buttons
    EventList.tsx      — renders EventCard list with loading/error/empty states
    EventCard.tsx      — single event card
  utils/eventHelpers.ts — sortByDate(), filterByCategories()
  __tests__/           — Vitest tests
```

The frontend is a pure static SPA — no API calls, no server-side rendering. `useEvents` fetches `/events.json` once on mount.

## Key Constraints

- `extract.py` has two entry points: `main()` (standalone, reads `output/raw_articles.json`) and `process_article()` (imported by `main.py`). Changes to extraction logic affect both.
- Location extraction is strictly validated in `validate_location()` — many plausible-looking strings are intentionally rejected. The validation rules encode hard-won empirical constraints; do not loosen them without understanding the rejection reason.
- Paywalled domains (`PAYWALLED_DOMAINS` in `extract.py`) are never scraped for body content; they are still URL-decoded and searched via DuckDuckGo.
- Adding a new category requires changes in both `backend/src/rss_fetcher.py` and `frontend/src/constants.ts`.
