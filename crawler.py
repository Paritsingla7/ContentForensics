import time
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests

from scraper import scrape_content

SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
USER_AGENT = "SEOAnalyzerBot/1.0"


def can_fetch(url, user_agent):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
    except Exception:
        return True
    return rp.can_fetch(user_agent, url)


def discover_from_sitemap(base_url, config):
    parsed = urlparse(base_url)
    sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
    try:
        response = requests.get(sitemap_url, timeout=10)
        if response.status_code != 200:
            return []
        root = ET.fromstring(response.content)
        urls = [
            loc.text.strip()
            for loc in root.findall(".//sm:loc", SITEMAP_NS)
            if loc.text
        ]
        return urls[: config.max_pages]
    except Exception:
        return []


def _discover_via_bfs(start_url, config):
    visited = set()
    queue = [(start_url, 0)]
    discovered = []
    base_domain = urlparse(start_url).netloc

    while queue and len(discovered) < config.max_pages:
        url, depth = queue.pop(0)
        if url in visited or depth > config.max_depth:
            continue
        visited.add(url)

        if not can_fetch(url, USER_AGENT):
            continue

        clean_text, full_soup, _ = scrape_content(url)
        time.sleep(config.request_delay_seconds)

        if clean_text is None:
            continue

        discovered.append(url)

        if depth < config.max_depth:
            for link in full_soup.find_all("a", href=True):
                next_url = urljoin(url, link["href"])
                if urlparse(next_url).netloc == base_domain and next_url not in visited:
                    queue.append((next_url, depth + 1))

    return discovered


def _try_start_url(start_url, config):
    attempts = 0
    while True:
        clean_text, _, _ = scrape_content(start_url)
        if clean_text is not None:
            return True
        attempts += 1
        if attempts > config.start_url_retry_attempts:
            return False
        time.sleep(config.start_url_retry_delay_seconds)


def discover_pages(start_url, config):
    """
    Discovers page URLs to analyze. Retries the start URL, falls back to
    sitemap.xml (fetched independently of the start URL) if it still
    fails, then falls back to a BFS crawl. Returns (urls, warning).
    """
    start_ok = _try_start_url(start_url, config)
    sitemap_urls = discover_from_sitemap(start_url, config)

    if start_ok:
        if sitemap_urls:
            return sitemap_urls, None
        return _discover_via_bfs(start_url, config), None

    if sitemap_urls:
        return sitemap_urls, f"Start URL '{start_url}' was unreachable; used sitemap.xml instead."

    bfs_urls = _discover_via_bfs(start_url, config)
    if bfs_urls:
        return bfs_urls, f"Start URL '{start_url}' was unreachable initially but was reached via crawl."

    return [], f"Start URL '{start_url}' and its sitemap were both unreachable; crawl aborted."
