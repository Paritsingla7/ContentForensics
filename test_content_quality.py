from bs4 import BeautifulSoup
from config import Config
from analyzer import (
    check_readability,
    check_thin_content,
    check_repetitive_phrasing,
    analyze_seo_and_links,
)


def test_check_readability_simple_text_scores_standard_or_higher():
    text = "The cat sat. It was warm. The dog ran fast. Birds sang songs."
    result = check_readability(text)
    assert result["score"] >= 60
    assert result["label"] == "Standard"


def test_check_readability_empty_text_returns_unknown():
    result = check_readability("")
    assert result["label"] == "Unknown"


def test_check_thin_content_below_floor_flags_thin():
    config = Config(thin_content_word_floor=10)
    result = check_thin_content("only four words here", config)
    assert result["wordCount"] == 4
    assert result["thinContent"] is True


def test_check_thin_content_above_floor_not_flagged():
    config = Config(thin_content_word_floor=3)
    result = check_thin_content("this has five words total", config)
    assert result["wordCount"] == 5
    assert result["thinContent"] is False


def test_check_repetitive_phrasing_flags_repeated_phrase():
    config = Config(repetitive_phrase_ngram_size=3, repetitive_phrase_min_count=3)
    text = " ".join(["buy cheap shoes now"] * 4 + ["this text has no repeats at all"])
    result = check_repetitive_phrasing(text, config)
    phrases = [r["phrase"] for r in result]
    assert "buy cheap shoes" in phrases


def test_check_repetitive_phrasing_no_repeats_returns_empty():
    config = Config(repetitive_phrase_ngram_size=4, repetitive_phrase_min_count=5)
    result = check_repetitive_phrasing("every single word here is different from the rest", config)
    assert result == []


def test_analyze_seo_and_links_flags_anchor_overoptimization():
    html = """
    <a href="/a">buy cheap shoes</a>
    <a href="/b">buy cheap shoes</a>
    <a href="/c">buy cheap shoes</a>
    <a href="/d">contact us</a>
    """
    soup = BeautifulSoup(html, "html.parser")
    config = Config(anchor_overoptimization_ratio=0.5)
    result = analyze_seo_and_links(soup, "https://example.com", config)
    assert result["AnchorOverOptimization"]["topAnchorText"] == "buy cheap shoes"
    assert result["AnchorOverOptimization"]["flag"] is True


def test_analyze_seo_and_links_no_flag_when_varied():
    html = """
    <a href="/a">page one</a>
    <a href="/b">page two</a>
    <a href="/c">page three</a>
    """
    soup = BeautifulSoup(html, "html.parser")
    config = Config(anchor_overoptimization_ratio=0.5)
    result = analyze_seo_and_links(soup, "https://example.com", config)
    assert result["AnchorOverOptimization"]["flag"] is False
