from collections import Counter
from urllib.parse import urlparse, urljoin
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
