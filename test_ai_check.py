import math
from unittest.mock import MagicMock
import torch
from config import Config
from ai_check import (
    check_burstiness,
    check_vocabulary_diversity,
    check_cliche_phrases,
    check_perplexity,
    compute_ai_likelihood,
)


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


class _FakeEncoding:
    def __init__(self, input_ids):
        self.input_ids = input_ids


def _fake_tokenizer(num_tokens=10):
    def tokenizer(text, return_tensors="pt", truncation=True, max_length=512):
        return _FakeEncoding(torch.ones((1, num_tokens), dtype=torch.long))
    return tokenizer


def _fake_model(loss_value):
    model = MagicMock()
    output = MagicMock()
    output.loss.item.return_value = loss_value
    model.return_value = output
    return model


def test_check_perplexity_returns_unavailable_when_model_is_none():
    config = Config()
    result = check_perplexity("Some text.", None, None, config)
    assert result["available"] is False


def test_check_perplexity_computes_score_from_mocked_model():
    config = Config(ai_perplexity_human_reference=60.0, ai_perplexity_ai_reference=20.0)
    model = _fake_model(loss_value=math.log(20.0))
    tokenizer = _fake_tokenizer()
    result = check_perplexity("Some text here.", model, tokenizer, config)
    assert result["available"] is True
    assert result["value"] == 20.0
    assert result["score"] == 100.0


def test_check_perplexity_unavailable_on_computation_error():
    config = Config()
    tokenizer = _fake_tokenizer()

    def broken_model(*args, **kwargs):
        raise RuntimeError("out of memory")

    result = check_perplexity("Some text here.", broken_model, tokenizer, config)
    assert result["available"] is False


def test_compute_ai_likelihood_combines_weighted_scores():
    config = Config()
    model = _fake_model(loss_value=math.log(20.0))
    tokenizer = _fake_tokenizer()
    text = "This is one sentence. This is another quite different one indeed."

    result = compute_ai_likelihood(text, model, tokenizer, config)

    assert result["score"] is not None
    assert 0 <= result["score"] <= 100
    assert result["breakdown"]["perplexity"]["available"] is True


def test_compute_ai_likelihood_renormalizes_when_perplexity_unavailable():
    config = Config()
    text = "This is one sentence. This is another quite different one indeed."

    result = compute_ai_likelihood(text, None, None, config)

    assert result["breakdown"]["perplexity"]["available"] is False
    assert result["score"] is not None
