import math

import nltk
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def _normalize(value, human_reference, ai_reference):
    """
    Maps `value` to a 0-100 AI-likelihood contribution. At or above the
    human reference scores 0; at or below the AI reference scores 100;
    linear in between.
    """
    if human_reference == ai_reference:
        return 0.0
    ratio = (human_reference - value) / (human_reference - ai_reference)
    return round(max(0.0, min(1.0, ratio)) * 100, 1)


def check_burstiness(clean_text, config):
    sentences = nltk.sent_tokenize(clean_text)
    if len(sentences) < 2:
        return {"insufficientData": True}

    lengths = [len(nltk.word_tokenize(s)) for s in sentences]
    mean_length = sum(lengths) / len(lengths)
    variance = sum((length - mean_length) ** 2 for length in lengths) / len(lengths)
    stdev = math.sqrt(variance)

    score = _normalize(stdev, config.ai_burstiness_human_reference, config.ai_burstiness_ai_reference)
    return {"value": round(stdev, 2), "score": score}


def check_vocabulary_diversity(clean_text, config):
    sentences = nltk.sent_tokenize(clean_text)
    if len(sentences) < 2:
        return {"insufficientData": True}

    words = [w.lower() for w in nltk.word_tokenize(clean_text) if w.isalpha()]
    if not words:
        return {"insufficientData": True}

    ttr = len(set(words)) / len(words)
    score = _normalize(ttr, config.ai_vocab_diversity_human_reference, config.ai_vocab_diversity_ai_reference)
    return {"value": round(ttr, 3), "score": score}


CLICHE_PHRASES = [
    "in today's fast-paced world",
    "it's important to note",
    "in conclusion",
    "delve into",
    "unlock the potential of",
    "in summary",
    "furthermore",
    "moreover",
    "it is worth noting",
    "navigate the complexities of",
    "in the realm of",
    "harness the power of",
    "harnessing the power of",
    "seamless integration",
    "dive into",
    "let's explore",
    "at the end of the day",
    "cutting-edge",
    "game-changer",
    "unleash the power",
    "as an ai language model",
]


def check_cliche_phrases(clean_text, config):
    lowered = clean_text.lower()
    matches = [phrase for phrase in CLICHE_PHRASES if phrase in lowered]
    count = len(matches)
    score = min(100.0, count * config.ai_cliche_score_per_match)
    return {"matches": matches, "count": count, "score": score}


def load_perplexity_model():
    """
    Loads distilgpt2 once. Returns (None, None) on failure (e.g. no
    internet, download issue) so the rest of the run can continue without
    the perplexity signal.
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
        model = AutoModelForCausalLM.from_pretrained("distilgpt2")
        model.eval()
        return model, tokenizer
    except Exception as e:
        print(f"[!] Could not load perplexity model: {e}")
        return None, None


def check_perplexity(clean_text, model, tokenizer, config):
    if model is None or tokenizer is None:
        return {"available": False}

    try:
        encoding = tokenizer(clean_text, return_tensors="pt", truncation=True, max_length=512)
        input_ids = encoding.input_ids
        if input_ids.shape[1] < 2:
            return {"available": False}

        with torch.no_grad():
            outputs = model(input_ids, labels=input_ids)
        perplexity = math.exp(outputs.loss.item())

        score = _normalize(perplexity, config.ai_perplexity_human_reference, config.ai_perplexity_ai_reference)
        return {"value": round(perplexity, 2), "score": score, "available": True}
    except Exception as e:
        print(f"[!] Perplexity computation failed: {e}")
        return {"available": False}
