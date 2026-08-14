import sys
import spacy
import nltk
import json
import os
from spacytextblob.spacytextblob import SpacyTextBlob
from spacy.language import Language

# Import functions from our other files
from scraper import scrape_content
from analyzer import analyze_content, analyze_seo_and_links
from spamdexing import detect_spamdexing


# --- Helper Functions (for setup) ---


def download_nltk_data():
    """
    Downloads NLTK 'punkt' tokenizer if not already present.
    """
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading NLTK 'punkt' tokenizer...")
        nltk.download('punkt', quiet=True)
        print("Download complete.")


def load_spacy_model():
    """
    Loads the spaCy model and adds the sentiment pipe.
    """
    print("Loading spaCy model (en_core_web_sm)...")
    try:
        nlp = spacy.load("en_core_web_sm")

        # Check if the factory is registered
        if not Language.has_factory("spacytextblob"):
            print("\n[!] Error: 'spacytextblob' factory not found.")
            print("This usually means the library is not installed correctly or there's an import issue.")
            print("Please ensure you have run: pip install spacytextblob")
            return None

        if "spacytextblob" not in nlp.pipe_names:
            nlp.add_pipe("spacytextblob")

        print("Model loaded successfully.")
        return nlp
    except OSError:
        print("\n[!] Error: spaCy model 'en_core_web_sm' not found.")
        print("Please run: python -m spacy download en_core_web_sm")
        return None


# --- Main Execution ---

def main():
    """
    Main execution function that controls the analysis workflow.
    """
    if len(sys.argv) < 2:
        print("Usage: python main.py <url_to_analyze>")
        sys.exit(1)

    url_to_analyze = sys.argv[1]

    # This dictionary will hold all our results
    report_data = {
        "url": url_to_analyze,
        "error": None,
        "sentiment": {},
        "entities": [],
        "links": {},
        "spam": None,
        "genericAnchors": 0
    }

    # 2. Setup (NLTK and spaCy)
    download_nltk_data()
    nlp = load_spacy_model()
    if nlp is None:
        report_data["error"] = "Failed to load spaCy model."
        save_report(report_data)
        sys.exit(1)

    # 3. Phase 1: Scrape
    print(f"Analyzing {url_to_analyze}...")
    clean_text, full_soup, base_url = scrape_content(url_to_analyze)

    # 4. Run Analysis (only if scraping was successful)
    if clean_text:

        # 5. Phase 2: Content Analysis (Sentiment & NER)
        sentiment_results, entity_results = analyze_content(clean_text, nlp)
        report_data["sentiment"] = sentiment_results

        # Parse entities correctly - entity_results is a list of tuples like ("Python (ORG)", count)
        entities_list = []
        for entity_with_label, count in entity_results:
            # Split the entity name and label - e.g., "Python (ORG)" -> ["Python", "(ORG)"]
            if ' (' in entity_with_label and entity_with_label.endswith(')'):
                name, label = entity_with_label.rsplit(' (', 1)
                label = label.rstrip(')')
                entities_list.append({"name": name, "type": label, "count": count})
            else:
                entities_list.append({"name": entity_with_label, "type": "UNKNOWN", "count": count})

        report_data["entities"] = entities_list

        # 6. Phase 2: Link Analysis
        from config import load_config
        config = load_config(None)
        link_results = analyze_seo_and_links(full_soup, base_url, config)
        report_data["links"] = {
            "internal": link_results.get("Internal", 0),
            "external": link_results.get("External", 0)
        }
        report_data["genericAnchors"] = link_results.get("Generic Anchor Text", 0)

        # 7. Phase 3: Spamdexing Detection
        spam_results = detect_spamdexing(clean_text, full_soup)

        spam_details = {}

        if "Keyword Stuffing" in spam_results:
            spam_details["keywordStuffing"] = spam_results['Keyword Stuffing']

        if "Hidden Text" in spam_results:
            # Hidden Text is now a list of strings
            hidden_texts = spam_results['Hidden Text']
            spam_details["hiddenText"] = {
                "count": len(hidden_texts),
                "instances": hidden_texts
            }

        if spam_details:
            report_data["spam"] = spam_details
        else:
            report_data["spam"] = None

        print("Analysis Complete.")

    else:
        print("Analysis aborted due to scraping error.")
        report_data["error"] = "Analysis aborted due to scraping error."

    # 8. Save the report to a JSON file
    save_report(report_data)


def save_report(data):
    """Saves the final report data to report.json"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        report_path = os.path.join(script_dir, "report.json")

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Successfully saved report to {report_path}")
    except Exception as e:
        print(f"Error saving report: {e}")


if __name__ == "__main__":
    main()
