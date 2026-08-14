from analyzer import check_readability


def test_check_readability_simple_text_scores_standard_or_higher():
    text = "The cat sat. It was warm. The dog ran fast. Birds sang songs."
    result = check_readability(text)
    assert result["score"] >= 60
    assert result["label"] == "Standard"


def test_check_readability_empty_text_returns_unknown():
    result = check_readability("")
    assert result["label"] == "Unknown"
