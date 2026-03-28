from __future__ import annotations

import urllib.parse
from typing import Any

import httpx


def wikipedia_thumbnail(query: str, thumb_size: int = 640) -> dict[str, str | None]:
    q = query.strip()
    if not q:
        return {"url": None, "title": None, "attribution": None}

    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "redirects": "1",
        "prop": "pageimages|pageterms",
        "piprop": "thumbnail",
        "pithumbsize": str(thumb_size),
        "wbptterms": "description",
        "titles": q,
    }
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    timeout = httpx.Timeout(15.0)
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url, headers={"User-Agent": "TinyFishTravelAgent/1.0 (educational demo)"})
            response.raise_for_status()
            payload: dict[str, Any] = response.json()
    except httpx.HTTPError:
        return {"url": None, "title": None, "attribution": None}

    pages = payload.get("query", {}).get("pages", [])
    if not pages or pages[0].get("missing"):
        return {"url": None, "title": None, "attribution": None}

    page = pages[0]
    title = page.get("title")
    thumb = page.get("thumbnail", {}) or {}
    image_url = thumb.get("source")
    terms = page.get("terms", {}) or {}
    desc = None
    if isinstance(terms.get("description"), list) and terms["description"]:
        desc = terms["description"][0]

    attribution = "Wikipedia / Wikimedia Commons"
    if title:
        attribution = f"Wikipedia: {title}"

    return {"url": image_url, "title": title, "description": desc, "attribution": attribution}
