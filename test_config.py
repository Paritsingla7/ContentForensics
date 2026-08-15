import json
import os
import tempfile
from config import Config, load_config


def test_load_config_defaults():
    cfg = load_config(None)
    assert cfg.max_pages == 30
    assert cfg.duplicate_similarity_threshold == 0.85


def test_load_config_with_overrides():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"max_pages": 5}, f)
        path = f.name
    try:
        cfg = load_config(path)
        assert cfg.max_pages == 5
        assert cfg.duplicate_similarity_threshold == 0.85  # untouched default
    finally:
        os.remove(path)


def test_load_config_ai_check_defaults():
    cfg = load_config(None)
    assert cfg.ai_weight_perplexity == 0.4
    assert cfg.ai_weight_burstiness == 0.3
    assert cfg.ai_weight_vocab_diversity == 0.2
    assert cfg.ai_weight_cliche == 0.1
    assert cfg.ai_burstiness_human_reference == 6.0
    assert cfg.ai_burstiness_ai_reference == 2.0
    assert cfg.ai_perplexity_human_reference == 60.0
    assert cfg.ai_perplexity_ai_reference == 20.0
    assert cfg.ai_vocab_diversity_human_reference == 0.5
    assert cfg.ai_vocab_diversity_ai_reference == 0.3
    assert cfg.ai_cliche_score_per_match == 20.0
