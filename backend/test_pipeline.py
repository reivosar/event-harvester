import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from unittest.mock import patch
from src.rss_fetcher import CATEGORIES
from src.event_parser import SYSTEM_PROMPT, _build_prompt
from main import _normalize_title, articles_to_events

EXPECTED_CATEGORIES = [
    "震災関連",
    "防災関連",
    "アール・ブリュット関連",
    "シンポジウム関連",
    "学会・サミット・フォーラム関連",
]


# ── rss_fetcher ───────────────────────────────────────────

class TestCategories:

    def test_exactly_five_categories(self):
        assert len(CATEGORIES) == 5

    def test_category_names_match_expected(self):
        names = [c["name"] for c in CATEGORIES]
        assert names == EXPECTED_CATEGORIES

    def test_no_english_category_names(self):
        names = [c["name"] for c in CATEGORIES]
        for name in names:
            assert not name.isascii(), f"Unexpected English category: {name}"


# ── event_parser ──────────────────────────────────────────

class TestSystemPrompt:

    def test_prompt_biases_toward_inclusion(self):
        # Prompt must instruct the model to lean toward is_event: true
        assert "doubt" in SYSTEM_PROMPT or "when in doubt" in SYSTEM_PROMPT.lower()

    def test_prompt_lists_expanded_event_types(self):
        lower = SYSTEM_PROMPT.lower()
        assert "festival" in lower or "祭" in SYSTEM_PROMPT
        assert "workshop" in lower or "ワークショップ" in SYSTEM_PROMPT
        assert "exhibition" in lower or "展示" in SYSTEM_PROMPT


class TestBuildPrompt:

    def test_uses_400_chars_of_summary(self):
        long_summary = "A" * 500
        article = {"title": "Test", "summary": long_summary}
        prompt = _build_prompt([article])
        # 400 A's must appear; 401st must not be present as a full sequence
        assert "A" * 400 in prompt
        assert "A" * 401 not in prompt

    def test_summary_shorter_than_400_included_in_full(self):
        article = {"title": "Test", "summary": "Short summary"}
        prompt = _build_prompt([article])
        assert "Short summary" in prompt


# ── main._normalize_title ─────────────────────────────────

class TestNormalizeTitle:

    def test_strips_source_suffix_from_long_title(self):
        # "防災シンポジウムが開催されます" (15 chars) - 長いので除去する
        title = "防災シンポジウムが開催されます - NHKニュース"
        assert _normalize_title(title) == "防災シンポジウムが開催されます"

    def test_preserves_full_short_title_with_suffix(self):
        # "避難訓練" is 4 chars after strip — below threshold, keep full title so
        # "避難訓練 - 東京" and "避難訓練 - 大阪" get distinct dedup keys
        title = "避難訓練 - 毎日新聞"
        result = _normalize_title(title)
        assert result == "避難訓練 - 毎日新聞"

    def test_lowercases_result(self):
        assert _normalize_title("ABC Event - Source") == "abc event"

    def test_title_without_suffix_unchanged_except_lowercase(self):
        assert _normalize_title("防災訓練") == "防災訓練"

    def test_empty_string(self):
        assert _normalize_title("") == ""


# ── articles_to_events ────────────────────────────────────

_SAMPLE_PROCESS_RESULT = {
    "title": "防災シンポジウム開催",
    "event_date": "2026-06-01",
    "event_time": "14:00",
    "event_location": "東京国際フォーラム",
    "category": "防災関連",
    "url": "https://example.com/real",
}


class TestArticlesToEvents:

    def _article(self, **kwargs):
        base = {
            "title": "防災シンポジウム開催",
            "summary": "内容の説明",
            "url": "https://news.google.com/article",
            "category": "防災関連",
            "published": "Mon, 01 Jan 2024 00:00:00 GMT",
        }
        base.update(kwargs)
        return base

    def _result(self, **kwargs):
        r = dict(_SAMPLE_PROCESS_RESULT)
        r.update(kwargs)
        return r

    def test_uses_process_article_title(self):
        with patch("main.process_article", return_value=self._result(title="抽出タイトル")):
            events = articles_to_events([self._article()])
        assert events[0].event_title == "抽出タイトル"

    def test_uses_process_article_date(self):
        with patch("main.process_article", return_value=self._result(event_date="2026-07-10")):
            events = articles_to_events([self._article()])
        assert events[0].event_date == "2026-07-10"

    def test_uses_process_article_time(self):
        with patch("main.process_article", return_value=self._result(event_time="10:30")):
            events = articles_to_events([self._article()])
        assert events[0].event_time == "10:30"

    def test_uses_process_article_location(self):
        with patch("main.process_article", return_value=self._result(event_location="大阪城ホール")):
            events = articles_to_events([self._article()])
        assert events[0].event_location == "大阪城ホール"

    def test_uses_original_summary_for_description(self):
        with patch("main.process_article", return_value=self._result()):
            events = articles_to_events([self._article(summary="要約テキスト")])
        assert events[0].event_description == "要約テキスト"

    def test_truncates_summary_to_100_chars(self):
        with patch("main.process_article", return_value=self._result()):
            events = articles_to_events([self._article(summary="あ" * 200)])
        assert len(events[0].event_description) == 100

    def test_uses_process_article_url_as_source(self):
        with patch("main.process_article", return_value=self._result(url="https://real.com/page")):
            events = articles_to_events([self._article()])
        assert events[0].source_url == "https://real.com/page"

    def test_maps_category(self):
        with patch("main.process_article", return_value=self._result(category="震災関連")):
            events = articles_to_events([self._article(category="震災関連")])
        assert events[0].category == "震災関連"

    def test_is_event_true(self):
        with patch("main.process_article", return_value=self._result()):
            events = articles_to_events([self._article()])
        assert events[0].is_event is True

    def test_multiple_articles_returns_all(self):
        with patch("main.process_article", return_value=self._result()):
            articles = [self._article(title=f"Event {i}") for i in range(5)]
            events = articles_to_events(articles)
        assert len(events) == 5

    def test_empty_list(self):
        assert articles_to_events([]) == []
