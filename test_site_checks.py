from config import Config
from site_checks import find_duplicates, find_scaled_pattern


def test_find_duplicates_flags_near_identical_pages():
    pages = [
        {"url": "https://example.com/a", "clean_text": "The quick brown fox jumps over the lazy dog today."},
        {"url": "https://example.com/b", "clean_text": "The quick brown fox jumps over the lazy dog today!"},
        {"url": "https://example.com/c", "clean_text": "Completely unrelated content about something else entirely."},
    ]
    config = Config(duplicate_similarity_threshold=0.9)
    result = find_duplicates(pages, config)
    assert len(result) == 1
    assert set(result[0]["urls"]) == {"https://example.com/a", "https://example.com/b"}


def test_find_duplicates_no_matches_below_threshold():
    pages = [
        {"url": "https://example.com/a", "clean_text": "Alpha bravo charlie delta echo."},
        {"url": "https://example.com/b", "clean_text": "Foxtrot golf hotel india juliet."},
    ]
    config = Config(duplicate_similarity_threshold=0.9)
    assert find_duplicates(pages, config) == []


def test_find_scaled_pattern_flags_when_most_pages_match():
    shared_text = "Buy our product now, limited time offer, act fast today."
    pages = [
        {"url": f"https://example.com/{i}", "clean_text": shared_text}
        for i in range(4)
    ] + [{"url": "https://example.com/unique", "clean_text": "A totally different unrelated page."}]
    config = Config(scaled_pattern_threshold=0.9, scaled_pattern_min_fraction=0.5)
    result = find_scaled_pattern(pages, config)
    assert result["flag"] is True
    assert result["totalPages"] == 5


def test_find_scaled_pattern_skips_when_fewer_than_two_pages():
    config = Config()
    result = find_scaled_pattern([{"url": "https://example.com/a", "clean_text": "solo page"}], config)
    assert result["flag"] is False
    assert result["totalPages"] == 1
