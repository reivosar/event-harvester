# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend (Python)

```bash
# First-time setup
cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
cp backend/.env.example backend/.env  # then fill in ANTHROPIC_API_KEY

# Run the full pipeline (fetches RSS, extracts events, writes output/events.json)
cd backend && python main.py

# Run all tests
cd backend && python -m pytest

# Run a single test file
cd backend && python -m pytest test_extract.py -v
```

### Frontend (React/TypeScript/Vite)

```bash
cd frontend && npm install   # first-time setup

npm run dev       # dev server at localhost:5173
npm test          # run all tests once
npm run test:watch  # watch mode
npx vitest run src/__tests__/EventCard.test.tsx  # single test file
npm run build     # type-check + Vite build -> dist/
npm run lint
```

### Pipeline to frontend

The frontend reads `events.json` as a static file served from `/events.json`. Copy the pipeline output before running or building:

```bash
cp backend/output/events.json frontend/public/events.json
```

`frontend/public/events.json` is gitignored.

## Architecture

This is a two-part application: a Python data pipeline that harvests Japanese event information from Google News RSS, and a React SPA that displays the results.

### Backend pipeline (`backend/`)

`main.py` is the entry point and orchestrates four stages:

1. **Fetch** (`src/rss_fetcher.py`) - Queries Google News RSS for 5 hard-coded categories (震災関連, 防災関連, アール・ブリュット関連, シンポジウム関連, 学会・サミット・フォーラム関連). Each category maps to a Japanese search query.

2. **Pre-deduplicate** (`main.py:deduplicate_articles`) - Deduplicates raw articles by URL and normalized title before extraction.

3. **Extract** (`extract.py:process_article`, parallelized with `ThreadPoolExecutor`) - For each article:
   - Decodes the Google News redirect URL via `googlenewsdecoder`
   - Scrapes the real page HTML and parses JSON-LD `Event` schema
   - Falls back to regex patterns to extract date, time, and location from body text
   - Falls back further to a DuckDuckGo web search (`ddgs`) for the official event page when location or date is still missing
   - Rate-limiting semaphores prevent hammering DDG and Google News decode endpoints

4. **Post-deduplicate + write** (`main.py:deduplicate`) - Deduplicates `Event` objects by `(title, date)` or by `(normalized_title, domain)`, then writes `output/events.json`.

`src/event_parser.py` contains an alternative Claude Haiku-based batch classifier (used in an earlier iteration; not called by the current `main.py`).

`src/models.py` defines the `Event` dataclass with fields: `event_title`, `event_date` (YYYY-MM-DD), `event_time` (HH:MM), `event_location`, `event_description`, `source_url`, `category`, `is_event`.

### Frontend (`frontend/`)

Static React SPA (no backend server). Loads `events.json` at startup via `useEvents` hook (`fetch('/events.json')`).

`App.tsx` composes the UI and applies three transforms in order:
1. `filterUpcomingEvents` - keeps only events where `event_date >= today` (null dates are excluded)
2. `filterByCategories` - respects the active category filter (all selected by default)
3. `sortByDate` - ascending by date

`constants.ts` holds the `CATEGORIES` array, which must stay in sync with `src/rss_fetcher.py::CATEGORIES`.

Components: `CategoryFilter` (toggle buttons), `EventList` (renders list or loading/error state), `EventCard` (single event card).

### Environment

`backend/.env` must contain `ANTHROPIC_API_KEY` (used by `src/event_parser.py`). The main pipeline (`main.py`) uses only public HTTP endpoints and DuckDuckGo, so the key is only required if calling `event_parser.py` directly.
