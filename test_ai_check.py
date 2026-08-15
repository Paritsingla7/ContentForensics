from config import Config
from ai_check import check_burstiness, check_vocabulary_diversity


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
