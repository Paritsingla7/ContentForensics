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
