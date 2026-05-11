from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest
import requests

from src.scrapers.connpass import ConnpassScraper
from src.scrapers.doorkeeper import DoorkeeperScraper
from src.scrapers import fetch_all_scrapers

FUTURE_DATE = (date.today() + timedelta(days=30)).isoformat()
PAST_DATE = (date.today() - timedelta(days=1)).isoformat()


def _mock_session(json_data=None, text=None, status_code=200):
    session = MagicMock()
    resp = MagicMock()
    resp.status_code = status_code
    if json_data is not None:
        resp.json.return_value = json_data
    if text is not None:
        resp.text = text
    if status_code >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError()
    else:
        resp.raise_for_status.return_value = None
    session.get.return_value = resp
    return session


class TestConnpassScraper:

    def test_fetch_returns_future_events(self):
        session = _mock_session(json_data={
            "events": [{
                "title": "テストシンポジウム",
                "catch": "テスト説明",
                "event_url": "https://connpass.com/event/1/",
                "started_at": f"{FUTURE_DATE}T14:00:00+09:00",
                "place": "渋谷ヒカリエ",
                "address": "東京都渋谷区渋谷2-21-1",
            }]
        })
        events = ConnpassScraper(session=session).fetch("シンポジウム", "シンポジウム関連")
        assert len(events) == 1
        e = events[0]
        assert e.event_title == "テストシンポジウム"
        assert e.event_date == FUTURE_DATE
        assert e.event_time == "14:00"
        assert e.event_location == "渋谷ヒカリエ"
        assert e.category == "シンポジウム関連"
        assert e.is_event is True

    def test_fetch_excludes_past_events(self):
        session = _mock_session(json_data={
            "events": [{
                "title": "過去のイベント",
                "event_url": "https://connpass.com/event/2/",
                "started_at": f"{PAST_DATE}T14:00:00+09:00",
                "place": "渋谷",
            }]
        })
        events = ConnpassScraper(session=session).fetch("テスト", "テスト")
        assert len(events) == 0

    def test_fetch_returns_empty_on_http_error(self):
        session = _mock_session(status_code=500)
        events = ConnpassScraper(session=session).fetch("テスト", "テスト")
        assert events == []

    def test_fetch_falls_back_to_address_when_place_missing(self):
        session = _mock_session(json_data={
            "events": [{
                "title": "テスト",
                "event_url": "https://connpass.com/event/3/",
                "started_at": f"{FUTURE_DATE}T10:00:00+09:00",
                "place": "",
                "address": "東京都新宿区",
            }]
        })
        events = ConnpassScraper(session=session).fetch("テスト", "テスト")
        assert events[0].event_location == "東京都新宿区"

    def test_fetch_truncates_description_to_100_chars(self):
        long_catch = "あ" * 200
        session = _mock_session(json_data={
            "events": [{
                "title": "テスト",
                "catch": long_catch,
                "event_url": "https://connpass.com/event/4/",
                "started_at": f"{FUTURE_DATE}T10:00:00+09:00",
                "place": "東京",
            }]
        })
        events = ConnpassScraper(session=session).fetch("テスト", "テスト")
        assert len(events[0].event_description) <= 100


class TestDoorkeeperScraper:

    def test_fetch_returns_future_events(self):
        session = _mock_session(json_data=[{
            "event": {
                "title": "防災シンポジウム",
                "description": "<p>テスト説明</p>",
                "public_url": "https://doorkeeper.jp/events/1",
                "starts_at": f"{FUTURE_DATE}T13:00:00.000+09:00",
                "venue_name": "東京国際フォーラム",
                "address": "東京都千代田区丸の内3-5-1",
            }
        }])
        events = DoorkeeperScraper(session=session).fetch("防災 シンポジウム", "防災関連")
        assert len(events) == 1
        e = events[0]
        assert e.event_title == "防災シンポジウム"
        assert e.event_date == FUTURE_DATE
        assert e.event_time == "13:00"
        assert e.event_location == "東京国際フォーラム"
        assert "テスト説明" in e.event_description
        assert "<p>" not in e.event_description

    def test_fetch_excludes_past_events(self):
        session = _mock_session(json_data=[{
            "event": {
                "title": "過去イベント",
                "public_url": "https://doorkeeper.jp/events/2",
                "starts_at": f"{PAST_DATE}T13:00:00.000+09:00",
                "venue_name": "東京",
            }
        }])
        events = DoorkeeperScraper(session=session).fetch("テスト", "テスト")
        assert len(events) == 0

    def test_fetch_returns_empty_on_http_error(self):
        session = _mock_session(status_code=503)
        events = DoorkeeperScraper(session=session).fetch("テスト", "テスト")
        assert events == []

    def test_fetch_falls_back_to_address_when_venue_missing(self):
        session = _mock_session(json_data=[{
            "event": {
                "title": "テスト",
                "public_url": "https://doorkeeper.jp/events/3",
                "starts_at": f"{FUTURE_DATE}T10:00:00.000+09:00",
                "venue_name": None,
                "address": "東京都渋谷区",
            }
        }])
        events = DoorkeeperScraper(session=session).fetch("テスト", "テスト")
        assert events[0].event_location == "東京都渋谷区"


class TestFetchAllScrapers:

    def test_aggregates_results_from_all_scrapers(self):
        categories = [{"name": "テスト", "query": "テスト キーワード"}]
        mock_event_a = MagicMock()
        mock_event_b = MagicMock()
        mock_event_c = MagicMock()
        scraper_a = MagicMock()
        scraper_a.fetch.return_value = [mock_event_a]
        scraper_b = MagicMock()
        scraper_b.fetch.return_value = [mock_event_b, mock_event_c]

        events = fetch_all_scrapers(categories, scrapers=[scraper_a, scraper_b])

        assert len(events) == 3
        scraper_a.fetch.assert_called_once_with("テスト キーワード", "テスト")
        scraper_b.fetch.assert_called_once_with("テスト キーワード", "テスト")

    def test_iterates_all_categories(self):
        categories = [
            {"name": "カテゴリA", "query": "クエリA"},
            {"name": "カテゴリB", "query": "クエリB"},
        ]
        scraper = MagicMock()
        scraper.fetch.return_value = []

        fetch_all_scrapers(categories, scrapers=[scraper])

        assert scraper.fetch.call_count == 2

    def test_returns_empty_when_no_categories(self):
        events = fetch_all_scrapers([], scrapers=[])
        assert events == []
