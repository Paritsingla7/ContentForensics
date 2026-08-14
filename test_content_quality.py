from config import Config
from analyzer import check_readability, check_thin_content


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
