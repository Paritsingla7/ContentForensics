import math

import nltk


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
