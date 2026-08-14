import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


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
