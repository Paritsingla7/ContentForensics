from collections import Counter
from urllib.parse import urlparse, urljoin
import nltk
from spacytextblob.spacytextblob import SpacyTextBlob  # Ensures component is registered

# --- Constants ---
GENERIC_ANCHOR_TEXT = ["click here", "read more", "learn more", "here"]


# --- Helper Function (moved from utils.py) ---
def get_sentiment_label(polarity):
    """
    Classifies polarity score into a human-readable label.
    """
    if polarity > 0.15:
        return f"Positive (Score: {polarity:.2f})"
    elif polarity < -0.1:
        return f"Negative (Score: {polarity:.2f})"
    else:
        return f"Neutral (Score: {polarity:.2f})"


# --- Analysis Functions ---

def _count_syllables(word):
    word = word.lower()
    vowels = "aeiouy"
    count = 0
    prev_was_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_was_vowel:
            count += 1
        prev_was_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def check_readability(clean_text):
    """
    Flesch Reading Ease score computed from sentence/word/syllable counts.
    """
    if not clean_text.strip():
        return {"score": 0.0, "label": "Unknown"}

    sentences = nltk.sent_tokenize(clean_text)
    words = [w for w in nltk.word_tokenize(clean_text) if w.isalpha()]

    if not sentences or not words:
        return {"score": 0.0, "label": "Unknown"}

    total_syllables = sum(_count_syllables(w) for w in words)
    words_per_sentence = len(words) / len(sentences)
    syllables_per_word = total_syllables / len(words)

    score = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
    score = round(score, 1)

    if score >= 60:
        label = "Standard"
    elif score >= 30:
        label = "Difficult"
    else:
        label = "Very Difficult"

    return {"score": score, "label": label}


def check_thin_content(clean_text, config):
    words = [w for w in clean_text.split() if any(c.isalpha() for c in w)]
    word_count = len(words)
    return {
        "wordCount": word_count,
        "thinContent": word_count < config.thin_content_word_floor,
    }


def analyze_content(clean_text, nlp_model):
    """
    Analyzes clean text for Sentiment and Named Entities.
    (Based on Program 6 and Program 4)
    """
    print("Analyzing text with spaCy...")
    # Ensure we are using the model passed from main.py, which has the pipe registered
    doc = nlp_model(clean_text)

    # 1. Sentiment Analysis (using spacytextblob)
    # Access sentiment through the blob attribute
    polarity = doc._.blob.polarity
    subjectivity = doc._.blob.subjectivity
    sentiment_label = get_sentiment_label(polarity)

    sentiment_results = {
        "Sentiment": sentiment_label,
        "Subjectivity": f"{subjectivity:.2f} (0=Objective, 1=Subjective)"
    }

    # 2. Named Entity Recognition (NER)
    entity_counts = Counter()
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE"]:  # Person, Organization, Geo-Political Entity
            entity_counts[f"{ent.text.strip()} ({ent.label_})"] += 1

    return sentiment_results, entity_counts.most_common(10)


def analyze_seo_and_links(full_soup, base_url):
    """
    Analyzes the full HTML for link structure and anchor text quality.
    (Based on Program 9)
    """
    print("Analyzing links...")
    links = full_soup.find_all("a", href=True)
    base_domain = urlparse(base_url).netloc

    link_counts = {
        "Internal": 0,
        "External": 0,
        "Generic Anchor Text": 0
    }

    if not links:
        return link_counts

    for link in links:
        href = link.get('href')
        if not href or href.startswith("#") or href.startswith("mailto:"):
            continue

        full_link = urljoin(base_url, href)
        link_domain = urlparse(full_link).netloc

        if link_domain == base_domain:
            link_counts["Internal"] += 1
        else:
            link_counts["External"] += 1

        anchor_text = link.get_text(strip=True).lower()
        if anchor_text in GENERIC_ANCHOR_TEXT:
            link_counts["Generic Anchor Text"] += 1

    return link_counts
