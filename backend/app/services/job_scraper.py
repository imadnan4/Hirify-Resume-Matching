from __future__ import annotations

import re
from html import unescape
from urllib.request import Request, urlopen


def scrape_job_url(url: str) -> dict[str, str]:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 HirifyBot/1.0"})
    with urlopen(request, timeout=15) as response:
        html = response.read().decode("utf-8", errors="ignore")

    title_match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    title = unescape(title_match.group(1)).strip() if title_match else "Scraped Job"
    body_text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    body_text = re.sub(r"<[^>]+>", " ", body_text)
    body_text = re.sub(r"\s+", " ", unescape(body_text)).strip()
    description = body_text[:5000]
    return {"title": title[:255], "description": description, "source_url": url}
