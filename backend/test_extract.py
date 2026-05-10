import pytest
from extract import (
    validate_location,
    extract_location,
    extract_date,
    extract_time,
    extract_from_jsonld,
    clean_title,
    decode_google_url,
    _search_official_fields,
)


# ── validate_location ─────────────────────────────────────

class TestValidateLocation:

    def test_generic_venue_names_rejected(self):
        assert validate_location("イベントホール") is None
        assert validate_location("会議室") is None
        assert validate_location("ホール") is None
        assert validate_location("センター") is None

    def test_street_address_rejected(self):
        assert validate_location("東京都港区東新橋一丁目5番2号汐留シティセンター") is None

    def test_sentence_fragment_rejected(self):
        assert validate_location("市主催の犠牲者追悼式が大町の市民ホール") is None
        assert validate_location("26～」を3月7～11日に東京都港区の汐留シオサイト・プラザ") is None
        assert validate_location("新地町の東日本大震災追悼式は町文化交流センター") is None

    def test_person_name_rejected(self):
        assert validate_location("平松昂希さん（２１）＝同県西宮市＝は大学") is None
        assert validate_location("笹山市長による記者会見（第一会議室") is None

    def test_too_long_rejected(self):
        assert validate_location("あ" * 33) is None

    def test_no_japanese_rejected(self):
        assert validate_location("ABC Hall") is None

    def test_placeholder_rejected(self):
        assert validate_location("〇〇会場") is None
        assert validate_location("場所未定") is None
        assert validate_location("TBD") is None

    def test_none_input(self):
        assert validate_location(None) is None

    def test_empty_string_rejected(self):
        assert validate_location("") is None

    def test_valid_venue_passes(self):
        assert validate_location("神戸朝日ホール") == "神戸朝日ホール"
        assert validate_location("汐留シオサイト") == "汐留シオサイト"
        assert validate_location("若林区文化センター") == "若林区文化センター"
        assert validate_location("益城町地域共生センター") == "益城町地域共生センター"
        assert validate_location("上野の森美術館") == "上野の森美術館"
        assert validate_location("那覇商工会議所") == "那覇商工会議所"
        assert validate_location("観音寺市ハイスタッフホール") == "観音寺市ハイスタッフホール"
        assert validate_location("盛岡市民文化会館") == "盛岡市民文化会館"

    def test_venue_with_no_suffix_passes(self):
        assert validate_location("汐留シオサイト") == "汐留シオサイト"

    # -- particle prefix --

    def test_ni_prefix_rejected(self):
        assert validate_location("に本学片平キャンパス") is None
        assert validate_location("に吹田キャンパス") is None
        assert validate_location("に八王子キャンパス") is None
        assert validate_location("に県内の各会場") is None

    def test_no_prefix_rejected(self):
        assert validate_location("の夢一つくらい叶えてやろうかと思って薬科大学") is None

    # -- verb / adverb --

    def test_verb_suru_prefix_stripped_to_valid_venue(self):
        # "隣接する" is stripped as a leading modifier; the remaining venue passes
        assert validate_location("隣接する桜美林大学") == "桜美林大学"

    def test_verb_shita_rejected(self):
        assert validate_location("メディアに登場した獨協大学") is None

    def test_adverb_hajimete_stripped_to_valid_venue(self):
        # "初めて" is stripped as a leading modifier; the remaining venue passes
        assert validate_location("初めて釜石市民ホール") == "釜石市民ホール"

    def test_verb_toiawase_rejected(self):
        assert validate_location("問い合わせ先熊本大学") is None

    def test_niaru_rejected(self):
        assert validate_location("フィラデルフィアにあるペンシルバニア大学") is None

    # -- symbols / ASCII / emoji --

    def test_bullet_symbol_rejected(self):
        assert validate_location("●岡山会場") is None

    def test_emoji_rejected(self):
        assert validate_location("🌟各住民センター") is None

    def test_ascii_json_garbage_rejected(self):
        assert validate_location('anization"}}]}初めての方へ会場') is None

    # -- corporate names --

    def test_kabushiki_rejected(self):
        assert validate_location("株式会社モノクローム") is None

    # -- functional departments / generic centers --

    def test_functional_centers_rejected(self):
        assert validate_location("コールセンター") is None
        assert validate_location("リスクセンター") is None
        assert validate_location("視聴者サービスセンター") is None
        assert validate_location("地域包括支援センター") is None
        assert validate_location("自治体や地域包括支援センター") is None

    def test_open_campus_rejected(self):
        assert validate_location("オープンキャンパス") is None

    # -- quantity prefixes / incomplete expressions --

    def test_quantity_kasho_rejected(self):
        assert validate_location("か所の会場") is None

    def test_quantity_tsu_rejected(self):
        assert validate_location("つの会場") is None

    def test_floor_prefix_rejected(self):
        assert validate_location("階多目的ホール") is None

    def test_adverb_chokusetsu_rejected(self):
        assert validate_location("直接会場") is None

    def test_adverb_zehi_rejected(self):
        assert validate_location("ぜひ会場") is None

    def test_next_no_rejected(self):
        assert validate_location("次のヘルプセンター") is None

    # -- foreign / mixed-language text --

    def test_chinese_mixed_rejected(self):
        assert validate_location("学，这所大学曾被公认为首个国际卓越研究型大学") is None

    # -- too generic --

    def test_placeholder_pattern_rejected(self):
        # 〇〇 is a placeholder pattern and must be rejected
        assert validate_location("〇〇ホール") is None

    def test_no_proper_noun_plaza_rejected(self):
        assert validate_location("ショッピングプラザ") is None
        assert validate_location("会員ホテル") is None

    # -- ya / oyobi noun enumeration --

    def test_ya_separator_rejected(self):
        assert validate_location("ドームやアリーナ") is None
        assert validate_location("訓練や会場") is None
        assert validate_location("お店のレジやイベント会場") is None

    def test_oyobi_conjunction_rejected(self):
        assert validate_location("しあわせプラザホールおよび那珂湊体育館") is None
        assert validate_location("社の企業空間および特設会場") is None

    # -- adverb / modifier prefix --

    def test_sarani_prefix_stripped_to_valid_venue(self):
        # "さらに" is stripped as a leading modifier; the stadium name passes
        assert validate_location("さらにノエビアスタジアム") == "ノエビアスタジアム"

    def test_tatoeba_prefix_rejected(self):
        assert validate_location("例えば街なかのカフェや公民館") is None

    def test_sono_prefix_strips_to_verb_rejected(self):
        # "その" stripped → "する会場" which is caught by the verb filter
        assert validate_location("そのする会場") is None

    def test_hongaku_prefix_stripped_to_valid_venue(self):
        # "本学" is stripped as a leading modifier; the venue name passes
        assert validate_location("本学片平キャンパスさくらホール") == "片平キャンパスさくらホール"

    def test_kaku_prefix_rejected(self):
        assert validate_location("各家族ごとに体育館") is None
        assert validate_location("市内各大学") is None

    def test_adjective_prefix_rejected(self):
        assert validate_location("新しい会場") is None
        assert validate_location("高級ホテル") is None
        assert validate_location("ウルトララグジュアリーホテル") is None

    # -- symbols / brackets --

    def test_square_meter_symbol_rejected(self):
        assert validate_location("㎡の境内") is None

    def test_slash_prefix_rejected(self):
        assert validate_location("／国立成育医療研究センター") is None

    def test_hash_prefix_rejected(self):
        assert validate_location("#滋賀県長寿社会福祉センター") is None

    def test_parenthesis_stripped(self):
        # parenthetical notes are stripped; the venue name itself is returned
        assert validate_location("日本学術会議講堂（ハイブリッド開催）") == "日本学術会議講堂"
        assert validate_location("東御市中央公民館（長野県東御市）") == "東御市中央公民館"

    # -- date fragment prefix --

    def test_nen_ni_prefix_rejected(self):
        assert validate_location("年に日本財団より滋賀県立美術館") is None

    def test_nichi_ni_prefix_rejected(self):
        assert validate_location("日に広島県立広島産業会館") is None

    def test_tsuki_ni_prefix_rejected(self):
        assert validate_location("月に長崎市内のホテル") is None

    # -- additional generic venue / center labels --

    def test_generic_venue_labels_rejected(self):
        assert validate_location("コンタクトセンター") is None
        assert validate_location("トレーニングセンター") is None
        assert validate_location("活動センター") is None
        assert validate_location("防災センター") is None

    def test_generic_kaijo_rejected(self):
        assert validate_location("メイン会場") is None
        assert validate_location("現地会場") is None
        assert validate_location("対面会場") is None
        assert validate_location("展示会場") is None
        assert validate_location("受賞会場") is None

    def test_generic_hall_rejected(self):
        assert validate_location("コンサートホール") is None
        assert validate_location("交流ホール") is None
        assert validate_location("ダンスホール") is None

    # -- full-width brackets --

    def test_zenkakku_bracket_prefix_rejected(self):
        assert validate_location("【佐野美術館") is None
        assert validate_location("〔会場〕東京ビッグサイト") is None

    def test_zenakku_bracket_middle_rejected(self):
        assert validate_location("日】国連大学") is None

    # -- regression: valid venues that must still pass --

    def test_valid_venues_still_pass(self):
        assert validate_location("マシタ広場") == "マシタ広場"
        assert validate_location("沖縄ハーバービューホテル") == "沖縄ハーバービューホテル"
        assert validate_location("東京国際フォーラム") == "東京国際フォーラム"
        assert validate_location("TKP熊本カンファレンスセンター") == "TKP熊本カンファレンスセンター"
        assert validate_location("JR東日本総合研修センター") == "JR東日本総合研修センター"
        assert validate_location("加古川市役所庁舎前広場") == "加古川市役所庁舎前広場"
        assert validate_location("洋野町民文化会館セシリアホール") == "洋野町民文化会館セシリアホール"


# ── extract_date ──────────────────────────────────────────

class TestExtractDate:

    def test_reiwa_format(self):
        assert extract_date("令和8年5月25日に開催", 2026) == "2026-05-25"

    def test_western_year_format(self):
        assert extract_date("2026年3月11日 追悼式", 2026) == "2026-03-11"

    def test_bracket_slash_format(self):
        assert extract_date("【5/25】沖縄開催！シンポジウム", 2026) == "2026-05-25"

    def test_month_day_format(self):
        assert extract_date("5月30日（土）に開催", 2026) == "2026-05-30"

    def test_dot_separated_date(self):
        assert extract_date("2026.05.10 sun", 2026) == "2026-05-10"

    def test_slash_separated_date(self):
        assert extract_date("2026/5/10 開催", 2026) == "2026-05-10"

    def test_no_date_returns_none(self):
        assert extract_date("日付のないタイトル", 2026) is None

    def test_reiwa_year_calculation(self):
        # Reiwa 1 = 2019
        assert extract_date("令和1年4月1日", 2019) == "2019-04-01"
        # Reiwa 7 = 2025
        assert extract_date("令和7年12月31日", 2025) == "2025-12-31"


# ── extract_time ──────────────────────────────────────────

class TestExtractTime:

    def test_afternoon_time(self):
        assert extract_time("午後2時開催") == "14:00"

    def test_afternoon_time_with_minutes(self):
        assert extract_time("午後1時30分開始") == "13:30"

    def test_morning_time(self):
        assert extract_time("午前10時から") == "10:00"

    def test_colon_format(self):
        assert extract_time("13:30開場") == "13:30"

    def test_bare_hour(self):
        assert extract_time("10時-20時（最終日は18時まで）") == "10:00"

    def test_bare_hour_with_minutes(self):
        assert extract_time("13時30分開場") == "13:30"

    def test_day_number_not_confused_with_time(self):
        # must not mistake the 11 in "11日" for an hour
        assert extract_time("2026年5月11日(月)開催") is None

    def test_no_time_returns_none(self):
        assert extract_time("時刻のないタイトル") is None


# ── extract_location ──────────────────────────────────────

class TestExtractLocation:

    def test_venue_label_colon(self):
        result = extract_location("会場：神戸朝日ホール 定員500名")
        assert result == "神戸朝日ホール"

    def test_venue_label_full_colon(self):
        result = extract_location("場所：渋谷文化センター大和田")
        assert result == "渋谷文化センター大和田"

    def test_venue_suffix_pattern(self):
        result = extract_location("東京国際フォーラムにて開催予定")
        assert result == "東京国際フォーラム"

    def test_generic_venue_not_extracted(self):
        # rejected by validate_location
        result = extract_location("会場：イベントホール 詳細は後日")
        assert result is None

    def test_hiroba_venue(self):
        result = extract_location("新橋駅前SL広場")
        assert result == "新橋駅前SL広場"

    def test_koen_venue(self):
        result = extract_location("日比谷公園にて開催")
        assert result == "日比谷公園"

    def test_no_venue_returns_none(self):
        result = extract_location("開催日は5月25日です。詳細はWebサイトをご覧ください。")
        assert result is None

    def test_venue_in_title_style_text(self):
        assert extract_location("白百合女子大学で5月30日に開催") == "白百合女子大学"
        assert extract_location("国連大学で日本の国連加盟70周年記念シンポジウム開催") == "国連大学"

    def test_bracket_prefix_not_matched(self):
        # date bracket prefix must not prevent matching the venue that follows it
        assert extract_location("【5月18日】国連大学で開催") == "国連大学"

    def test_kaisai_kaijo_pattern(self):
        assert extract_location("開催会場：東京国際フォーラム") == "東京国際フォーラム"

    def test_kaijo_mei_pattern(self):
        assert extract_location("会場名：仙台サンプラザホール") == "仙台サンプラザホール"

    def test_kaisai_chiten_pattern(self):
        assert extract_location("開催地点：名古屋国際会議場") == "名古屋国際会議場"


# ── clean_title ───────────────────────────────────────────

class TestCleanTitle:

    def test_removes_source_suffix(self):
        assert clean_title("震災追悼と教訓継承の場に、福島県復興祈念公園が開園 - 山陽新聞") \
            == "震災追悼と教訓継承の場に、福島県復興祈念公園が開園"

    def test_no_suffix_unchanged(self):
        assert clean_title("アール・ブリュット展示会") == "アール・ブリュット展示会"


# ── extract_from_jsonld ───────────────────────────────────

class TestExtractFromJsonld:

    def test_event_schema(self):
        html = '''
        <script type="application/ld+json">
        {
            "@type": "Event",
            "name": "防災シンポジウム2026",
            "startDate": "2026-06-01T13:00:00",
            "location": {"@type": "Place", "name": "神戸国際会議場"}
        }
        </script>
        '''
        result = extract_from_jsonld(html)
        assert result["date"] == "2026-06-01"
        assert result["time"] == "13:00"
        assert result["location"] == "神戸国際会議場"

    def test_non_event_schema_ignored(self):
        html = '''
        <script type="application/ld+json">
        {"@type": "Organization", "name": "株式会社テスト"}
        </script>
        '''
        result = extract_from_jsonld(html)
        assert result == {}

    def test_string_location(self):
        html = '''
        <script type="application/ld+json">
        {"@type": "Event", "startDate": "2026-05-10", "location": "大阪城ホール"}
        </script>
        '''
        result = extract_from_jsonld(html)
        assert result["location"] == "大阪城ホール"

    def test_street_address_not_extracted(self):
        # only location.name is extracted, not streetAddress
        html = '''
        <script type="application/ld+json">
        {
            "@type": "Event",
            "location": {
                "@type": "Place",
                "address": {"streetAddress": "東京都港区東新橋1-5-2"}
            }
        }
        </script>
        '''
        result = extract_from_jsonld(html)
        assert result.get("location") is None

    def test_invalid_json_ignored(self):
        html = '<script type="application/ld+json">{invalid json}</script>'
        result = extract_from_jsonld(html)
        assert result == {}

    def test_no_jsonld_returns_empty(self):
        result = extract_from_jsonld("<html><body>本文</body></html>")
        assert result == {}

    def test_startdate_as_list_returns_first_element(self):
        html = '''
        <script type="application/ld+json">
        {"@type": "Event", "startDate": ["2026-06-01T14:00:00"]}
        </script>
        '''
        result = extract_from_jsonld(html)
        assert result["date"] == "2026-06-01"
        assert result["time"] == "14:00"

    def test_startdate_as_empty_list_returns_none(self):
        html = '''
        <script type="application/ld+json">
        {"@type": "Event", "startDate": []}
        </script>
        '''
        result = extract_from_jsonld(html)
        assert result["date"] is None
        assert result["time"] is None

    def test_startdate_as_non_string_returns_none(self):
        html = '''
        <script type="application/ld+json">
        {"@type": "Event", "startDate": 12345}
        </script>
        '''
        result = extract_from_jsonld(html)
        assert result["date"] is None
        assert result["time"] is None


class TestNewLocationPatterns:

    def test_bracket_kaijo_pattern(self):
        html = '<p>【会場】東京大学中島董一郎記念ホール</p>'
        assert extract_location(html) == "東京大学中島董一郎記念ホール"

    def test_bullet_kaijo_space_pattern(self):
        html = '<p>■会場　浜松町コンベンションホール</p>'
        assert extract_location(html) == "浜松町コンベンションホール"

    def test_basho_fullwidth_colon_pattern(self):
        html = '<p>場　所：わにホール室蘭市民会館</p>'
        assert extract_location(html) == "わにホール室蘭市民会館"

    def test_kodo_venue_suffix(self):
        html = '<p>会場：茨城県庁講堂</p>'
        assert extract_location(html) == "茨城県庁講堂"


class TestDecodeGoogleUrl:

    def test_decode_returns_decoded_url(self):
        from unittest.mock import patch
        with patch('extract.gnewsdecoder', return_value={'decoded_url': 'https://example.com/article'}):
            result = decode_google_url('https://news.google.com/rss/articles/CB...')
        assert result == 'https://example.com/article'

    def test_decode_falls_back_on_exception(self):
        from unittest.mock import patch
        url = 'https://news.google.com/rss/articles/CB...'
        with patch('extract.gnewsdecoder', side_effect=Exception('rate limited')):
            result = decode_google_url(url)
        assert result == url


class TestSearchOfficialFields:

    def test_returns_location_and_date(self):
        from unittest.mock import patch
        html = '<p>会場：東京国際フォーラム</p><p>2026年6月15日に開催</p>'
        with patch('extract.search_event_pages', return_value=['https://example.com/event']):
            with patch('extract.fetch_html', return_value=html):
                result = _search_official_fields('テストイベント', 2026)
        assert result['location'] == '東京国際フォーラム'
        assert result['date'] == '2026-06-15'

    def test_returns_none_fields_when_no_results(self):
        from unittest.mock import patch
        with patch('extract.search_event_pages', return_value=[]):
            result = _search_official_fields('テストイベント', 2026)
        assert result == {'location': None, 'date': None}

    def test_returns_location_without_date(self):
        from unittest.mock import patch
        html = '<p>会場：大阪城ホール</p>'
        with patch('extract.search_event_pages', return_value=['https://example.com/event']):
            with patch('extract.fetch_html', return_value=html):
                result = _search_official_fields('テストイベント', 2026)
        assert result['location'] == '大阪城ホール'
        assert result['date'] is None

