import sys
import spacy
import nltk
import json
import os
from dataclasses import asdict
from spacytextblob.spacytextblob import SpacyTextBlob
from spacy.language import Language

# Import functions from our other files
from scraper import scrape_content
from analyzer import (
    analyze_content,
    analyze_seo_and_links,
    check_readability,
    check_thin_content,
    check_repetitive_phrasing,
)
from spamdexing import detect_spamdexing
from config import load_config
from crawler import discover_pages
from site_checks import find_duplicates, find_scaled_pattern
from ai_check import load_perplexity_model, compute_ai_likelihood


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
    Main execution function that controls the crawl + analysis workflow.
    """
    if len(sys.argv) < 2:
        print("Usage: python main.py <url_to_analyze> [config.json]")
        sys.exit(1)

    url_to_analyze = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else None
    config = load_config(config_path)

    report_data = {
        "start_url": url_to_analyze,
        "pages_crawled": 0,
        "config_used": asdict(config),
        "pages": [],
        "site_issues": {},
        "error": None,
        "warning": None,
    }

    # Setup (NLTK and spaCy)
    download_nltk_data()
    nlp = load_spacy_model()
    if nlp is None:
        report_data["error"] = "Failed to load spaCy model."
        save_report(report_data)
        sys.exit(1)

    print("Loading AI-likelihood perplexity model (distilgpt2)...")
    ai_model, ai_tokenizer = load_perplexity_model()
    if ai_model is None:
        print("[!] Perplexity signal unavailable this run; continuing with the other three AI-likelihood signals.")

    print(f"Discovering pages from {url_to_analyze}...")
    page_urls, warning = discover_pages(url_to_analyze, config)
    report_data["warning"] = warning

    if not page_urls:
        report_data["error"] = warning or "No pages could be crawled."
        save_report(report_data)
        sys.exit(1)

    pages_for_site_checks = []

    for page_url in page_urls:
        print(f"Analyzing {page_url}...")
        clean_text, full_soup, base_url = scrape_content(page_url)

        if clean_text is None:
            report_data["pages"].append({"url": page_url, "error": "Failed to scrape or extract content."})
            continue

        # Content Analysis (Sentiment & NER)
        sentiment_results, entity_results = analyze_content(clean_text, nlp)

        # Parse entities correctly - entity_results is a list of tuples like ("Python (ORG)", count)
        entities_list = []
        for entity_with_label, count in entity_results:
            if ' (' in entity_with_label and entity_with_label.endswith(')'):
                name, label = entity_with_label.rsplit(' (', 1)
                label = label.rstrip(')')
                entities_list.append({"name": name, "type": label, "count": count})
            else:
                entities_list.append({"name": entity_with_label, "type": "UNKNOWN", "count": count})

        # Link Analysis
        link_results = analyze_seo_and_links(full_soup, base_url, config)

        # Spamdexing Detection
        spam_results = detect_spamdexing(clean_text, full_soup)
        spam_details = {}
        if "Keyword Stuffing" in spam_results:
            spam_details["keywordStuffing"] = spam_results['Keyword Stuffing']
        if "Hidden Text" in spam_results:
            hidden_texts = spam_results['Hidden Text']
            spam_details["hiddenText"] = {
                "count": len(hidden_texts),
                "instances": hidden_texts,
            }

        content_quality = {
            **check_thin_content(clean_text, config),
            "readability": check_readability(clean_text),
            "repetitivePhrasing": check_repetitive_phrasing(clean_text, config),
            "anchorOverOptimization": link_results.get("AnchorOverOptimization"),
        }

        ai_likelihood = compute_ai_likelihood(clean_text, ai_model, ai_tokenizer, config)

        report_data["pages"].append({
            "url": page_url,
            "sentiment": sentiment_results,
            "entities": entities_list,
            "links": {
                "internal": link_results.get("Internal", 0),
                "external": link_results.get("External", 0),
            },
            "genericAnchors": link_results.get("Generic Anchor Text", 0),
            "spam": spam_details or None,
            "content_quality": content_quality,
            "ai_likelihood": ai_likelihood,
        })
        pages_for_site_checks.append({"url": page_url, "clean_text": clean_text})

    report_data["pages_crawled"] = len(pages_for_site_checks)

    if len(pages_for_site_checks) >= 2:
        report_data["site_issues"] = {
            "duplicates": find_duplicates(pages_for_site_checks, config),
            "scaledPattern": find_scaled_pattern(pages_for_site_checks, config),
        }
    else:
        report_data["site_issues"] = {
            "note": "Fewer than 2 pages crawled successfully; site-level checks skipped."
        }

    print("Analysis Complete.")
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
