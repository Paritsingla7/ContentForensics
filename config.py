from dataclasses import dataclass, asdict
import json


@dataclass
class Config:
    max_pages: int = 30
    max_depth: int = 2
    request_delay_seconds: float = 0.5
    duplicate_similarity_threshold: float = 0.85
    scaled_pattern_threshold: float = 0.75
    scaled_pattern_min_fraction: float = 0.5
    thin_content_word_floor: int = 300
    repetitive_phrase_min_count: int = 5
    repetitive_phrase_ngram_size: int = 4
    anchor_overoptimization_ratio: float = 0.3
    start_url_retry_attempts: int = 2
    start_url_retry_delay_seconds: float = 1.0


def load_config(path):
    """Loads a Config, applying JSON overrides from `path` if given."""
    defaults = asdict(Config())
    if path:
        with open(path, "r", encoding="utf-8") as f:
            overrides = json.load(f)
        defaults.update(overrides)
    return Config(**defaults)
