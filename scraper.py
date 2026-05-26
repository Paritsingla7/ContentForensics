import requests
from bs4 import BeautifulSoup
from readability import Document

# --- Constants & Configuration ---
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def scrape_content(url):
    """
    Scrapes the URL and extracts clean text and full HTML.
    (Based on Program 1)
    """
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=10)

        if response.status_code != 200:
            print(f"Error: Failed to retrieve content. Status Code: {response.status_code}")
            return None, None, None

        doc = Document(response.text)
        clean_html = doc.summary()

        # Soups for both clean and full content
        article_soup = BeautifulSoup(clean_html, 'html.parser')
        full_soup = BeautifulSoup(response.text, 'html.parser')

        # Get clean text from the readable article
        clean_text = article_soup.get_text(separator=" ", strip=True)

        if not clean_text:
            print("Error: Could not extract readable text from the page.")
            return None, None, None

        print("Scraping successful.")
        return clean_text, full_soup, url

    except requests.exceptions.RequestException as e:
        print(f"Error: Request failed. {e}")
        return None, None, None
