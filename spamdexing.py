import nltk
from collections import Counter

# --- Constants ---
KEYWORD_STUFFING_THRESHOLD = 0.05  # 5% density


def detect_spamdexing(clean_text, full_soup):
    """
    Detects Keyword Stuffing and Hidden Text.
    (Based on Program 10)
    """
    print("Checking for spamdexing...")
    spam_report = {}

    # 1. Keyword Stuffing Detection
    try:
        words = nltk.word_tokenize(clean_text.lower())
        cleaned_words = [word for word in words if word.isalpha() and len(word) > 2]

        if cleaned_words:
            total_words = len(cleaned_words)
            word_counts = Counter(cleaned_words)

            stuffed_keywords = []
            for word, count in word_counts.most_common(10):
                density = count / total_words
                if density > KEYWORD_STUFFING_THRESHOLD:
                    stuffed_keywords.append(f"'{word}' ({density * 100:.1f}%)")

            if stuffed_keywords:
                spam_report["Keyword Stuffing"] = ", ".join(stuffed_keywords)

    except Exception as e:
        print(f"Could not perform keyword analysis: {e}")

    # 2. Hidden Text Detection
    hidden_texts = []
    # Find all tags that have a 'style' attribute
    for tag in full_soup.find_all(style=True):
        # Read the style attribute, make it lowercase, and remove spaces
        style = tag['style'].lower().replace(' ', '')

        # Check for common hiding techniques
        if 'display:none' in style or 'visibility:hidden' in style or 'font-size:0' in style:
            hidden_text = tag.get_text(strip=True)
            if hidden_text:
                # Add a snippet of the hidden text to the report (max 80 chars)
                snippet = hidden_text[:80] + '...' if len(hidden_text) > 80 else hidden_text
                hidden_texts.append(snippet)

    if hidden_texts:
        spam_report["Hidden Text"] = hidden_texts

    return spam_report
