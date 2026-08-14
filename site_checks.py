from difflib import SequenceMatcher
from itertools import combinations


def find_duplicates(pages, config):
    duplicates = []
    for a, b in combinations(pages, 2):
        ratio = SequenceMatcher(None, a["clean_text"], b["clean_text"]).ratio()
        if ratio >= config.duplicate_similarity_threshold:
            duplicates.append({"urls": [a["url"], b["url"]], "similarity": round(ratio, 2)})
    return duplicates


def find_scaled_pattern(pages, config):
    total = len(pages)
    if total < 2:
        return {"flag": False, "affectedPages": 0, "totalPages": total}

    affected = set()
    for a, b in combinations(pages, 2):
        ratio = SequenceMatcher(None, a["clean_text"], b["clean_text"]).ratio()
        if ratio >= config.scaled_pattern_threshold:
            affected.add(a["url"])
            affected.add(b["url"])

    fraction = len(affected) / total
    return {
        "flag": fraction >= config.scaled_pattern_min_fraction,
        "affectedPages": len(affected),
        "totalPages": total,
    }
