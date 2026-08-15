from config import Config
from ai_check import check_burstiness, check_vocabulary_diversity, check_cliche_phrases


def test_check_burstiness_uniform_sentences_scores_high():
    config = Config()
    text = "One two three four five. One two three four five. One two three four five."
    result = check_burstiness(text, config)
    assert result["score"] > 50


def test_check_burstiness_insufficient_data_for_single_sentence():
    config = Config()
    result = check_burstiness("Only one sentence here.", config)
    assert result == {"insufficientData": True}


def test_check_vocabulary_diversity_repeated_words_scores_high():
    config = Config()
    text = "buy buy buy buy buy buy. buy buy buy buy."
    result = check_vocabulary_diversity(text, config)
    assert result["score"] > 50


def test_check_vocabulary_diversity_varied_words_scores_low():
    config = Config()
    text = "The quick brown fox jumps. Over lazy dogs near rivers today."
    result = check_vocabulary_diversity(text, config)
    assert result["score"] < 50


def test_check_vocabulary_diversity_insufficient_data_for_single_sentence():
    config = Config()
    result = check_vocabulary_diversity("Only one sentence here.", config)
    assert result == {"insufficientData": True}


def test_check_cliche_phrases_counts_matches():
    config = Config(ai_cliche_score_per_match=20.0)
    text = "In today's fast-paced world, we need to delve into this topic."
    result = check_cliche_phrases(text, config)
    assert result["count"] == 2
    assert result["score"] == 40.0


def test_check_cliche_phrases_no_matches():
    config = Config()
    result = check_cliche_phrases("A perfectly ordinary sentence about cats.", config)
    assert result["count"] == 0
    assert result["score"] == 0.0


def test_check_cliche_phrases_caps_score_at_100():
    config = Config(ai_cliche_score_per_match=20.0)
    text = (
        "In today's fast-paced world, it's important to note that we must "
        "delve into, unlock the potential of, and dive into this realm, "
        "harnessing the power of cutting-edge tools as a game-changer."
    )
    result = check_cliche_phrases(text, config)
    assert result["score"] == 100.0
