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
    ai_burstiness_human_reference: float = 6.0
    ai_burstiness_ai_reference: float = 2.0
    ai_perplexity_human_reference: float = 60.0
    ai_perplexity_ai_reference: float = 20.0
    ai_vocab_diversity_human_reference: float = 0.5
    ai_vocab_diversity_ai_reference: float = 0.3
    ai_cliche_score_per_match: float = 20.0
    ai_weight_perplexity: float = 0.4
    ai_weight_burstiness: float = 0.3
    ai_weight_vocab_diversity: float = 0.2
    ai_weight_cliche: float = 0.1


def load_config(path):
    """Loads a Config, applying JSON overrides from `path` if given."""
    defaults = asdict(Config())
    if path:
        with open(path, "r", encoding="utf-8") as f:
            overrides = json.load(f)
        defaults.update(overrides)
    return Config(**defaults)
