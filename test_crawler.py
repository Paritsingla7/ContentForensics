from unittest.mock import patch, Mock
from config import Config
from crawler import can_fetch, discover_from_sitemap


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
