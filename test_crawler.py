from unittest.mock import patch, Mock
from bs4 import BeautifulSoup
from config import Config
from crawler import can_fetch, discover_from_sitemap, discover_pages


def _soup_with_links(links):
    html = "".join(f'<a href="{href}">link</a>' for href in links)
    return BeautifulSoup(html, "html.parser")


def test_can_fetch_returns_true_when_robots_txt_missing():
    with patch("crawler.RobotFileParser") as MockParser:
        instance = MockParser.return_value
        instance.read.side_effect = Exception("no robots.txt")
        assert can_fetch("https://example.com/page", "TestBot/1.0") is True


SITEMAP_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/a</loc></url>
  <url><loc>https://example.com/b</loc></url>
</urlset>
"""


def test_discover_from_sitemap_parses_urls():
    config = Config(max_pages=10)
    mock_response = Mock(status_code=200, content=SITEMAP_XML)
    with patch("crawler.requests.get", return_value=mock_response):
        urls = discover_from_sitemap("https://example.com/start", config)
    assert urls == ["https://example.com/a", "https://example.com/b"]


def test_discover_from_sitemap_returns_empty_on_404():
    config = Config()
    mock_response = Mock(status_code=404, content=b"")
    with patch("crawler.requests.get", return_value=mock_response):
        urls = discover_from_sitemap("https://example.com/start", config)
    assert urls == []


def test_discover_pages_uses_sitemap_when_start_url_works():
    config = Config(max_pages=10, start_url_retry_attempts=0)
    with patch("crawler.scrape_content", return_value=("some text", _soup_with_links([]), "https://example.com")), \
         patch("crawler.discover_from_sitemap", return_value=["https://example.com/a", "https://example.com/b"]):
        urls, warning = discover_pages("https://example.com", config)
    assert urls == ["https://example.com/a", "https://example.com/b"]
    assert warning is None


def test_discover_pages_falls_back_to_bfs_when_start_url_works_but_no_sitemap():
    config = Config(max_pages=10, max_depth=1, start_url_retry_attempts=0, request_delay_seconds=0)
    soup = _soup_with_links(["https://example.com/only-link"])
    with patch("crawler.scrape_content", return_value=("some text", soup, "https://example.com")), \
         patch("crawler.discover_from_sitemap", return_value=[]), \
         patch("crawler.can_fetch", return_value=True):
        urls, warning = discover_pages("https://example.com", config)
    assert "https://example.com" in urls
    assert warning is None


def test_discover_pages_reports_unreachable_start_url_with_working_sitemap():
    config = Config(start_url_retry_attempts=1, start_url_retry_delay_seconds=0)
    with patch("crawler.scrape_content", return_value=(None, None, None)), \
         patch("crawler.discover_from_sitemap", return_value=["https://example.com/a"]):
        urls, warning = discover_pages("https://example.com/dead-page", config)
    assert urls == ["https://example.com/a"]
    assert "unreachable" in warning


def test_discover_pages_returns_empty_when_nothing_reachable():
    config = Config(start_url_retry_attempts=1, start_url_retry_delay_seconds=0)
    with patch("crawler.scrape_content", return_value=(None, None, None)), \
         patch("crawler.discover_from_sitemap", return_value=[]):
        urls, warning = discover_pages("https://example.com/dead-page", config)
    assert urls == []
    assert "aborted" in warning
