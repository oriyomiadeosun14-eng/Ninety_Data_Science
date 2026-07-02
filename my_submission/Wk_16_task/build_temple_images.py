"""
build_temple_images.py — populate lds_temple_images.json

Scrapes the og:image meta tag from each dedicated temple's page on
churchofjesuschristtemples.org. Resumable: re-running picks up where it
left off. Polite: 0.5s sleep between requests, sets a real User-Agent.

Run once locally after dropping new data into ../data/raw/:
    python build_temple_images.py

Output: lds_temple_images.json   { slug: og_image_url }

The notebook reads this file at render time and embeds the image URL in
each operating-temple popup. Temples not in the cache fall back to a
text-only popup, so the notebook works even if you skip running this
script — you just won't see photos.
"""

import json
import re
import time
import unicodedata
import urllib.request
from pathlib import Path

import polars as pl

TEMPLES_JSON = "../data/raw/lds_temples.json"
CACHE_PATH = Path("lds_temple_images.json")
SLEEP_SECONDS = 0.5
USER_AGENT = "Mozilla/5.0 (CS-11 academic project; one-time image cache build)"

OG_IMAGE_RE = re.compile(
    r'<meta\s+property="og:image"\s+content="([^"]+)"', re.IGNORECASE
)


def slugify(temple_name: str) -> str:
    """Convert 'Asunción Paraguay Temple' -> 'asuncion-paraguay-temple'."""
    # Strip accents
    nfkd = unicodedata.normalize("NFKD", temple_name)
    ascii_only = "".join(c for c in nfkd if not unicodedata.combining(c))
    # Lowercase, replace non-alphanumeric with hyphens, collapse
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")
    return slug


def fetch_og_image(slug: str) -> str | None:
    url = f"https://churchofjesuschristtemples.org/{slug}/"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ✗ {slug}: {type(e).__name__}: {e}")
        return None
    m = OG_IMAGE_RE.search(html)
    if not m:
        print(f"  ✗ {slug}: no og:image tag found")
        return None
    img_url = m.group(1)
    # Filter out the generic site logo (returned for missing temples)
    if "churchofjesuschristtemples-retina" in img_url or "/temples/" not in img_url:
        print(f"  ✗ {slug}: only generic site image (temple page may not exist)")
        return None
    return img_url


def main():
    temples = pl.read_json(TEMPLES_JSON)
    dedicated = temples.filter(pl.col("status") == "Dedicated")
    print(f"Found {dedicated.height} dedicated temples")

    cache = {}
    if CACHE_PATH.exists():
        cache = json.loads(CACHE_PATH.read_text())
        print(f"Loaded existing cache with {len(cache)} entries")

    new_count = 0
    for row in dedicated.iter_rows(named=True):
        slug = slugify(row["name"])
        if slug in cache:
            continue
        print(f"  → {row['name']!r}  ({slug})")
        img = fetch_og_image(slug)
        if img:
            cache[slug] = img
            new_count += 1
            # Save after every successful fetch so the run is resumable
            CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False))
        time.sleep(SLEEP_SECONDS)

    print(f"\nDone. Cached {len(cache)} temple images ({new_count} new this run).")
    print(f"Output: {CACHE_PATH.resolve()}")


if __name__ == "__main__":
    main()
