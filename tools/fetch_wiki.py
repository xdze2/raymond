#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""Fetch Wikipedia summary, lead image, and Wikidata facts for a catalogue entry.

Usage:
    uv run tools/fetch_wiki.py --wiki data_atlas --slug cgm-readings
    uv run tools/fetch_wiki.py --wiki data_atlas --slug cgm-readings --query "Continuous glucose monitor"

Writes:
    wikis/<wiki>/enrichments/<slug>.json
    wikis/<wiki>/media/<slug>/<image-filename>
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
USER_AGENT = "data_atlas-wiki-fetcher/0.1 (https://github.com/xdze2/data_atlas)"
HEADERS = {"User-Agent": USER_AGENT}
TIMEOUT = 20


def find_catalogue_entry(wiki: str, slug: str) -> dict | None:
    """Scan wikis/<wiki>/catalogue/*.jsonl for the slug. First match wins."""
    cat_dir = REPO_ROOT / "wikis" / wiki / "catalogue"
    for jsonl in sorted(cat_dir.glob("*.jsonl")):
        for line in jsonl.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("slug") == slug:
                return row
    return None


def wiki_search(query: str) -> str | None:
    """Return the best-matching Wikipedia page title."""
    r = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": 1,
            "format": "json",
        },
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    hits = r.json().get("query", {}).get("search", [])
    return hits[0]["title"] if hits else None


def wiki_summary(title: str) -> dict:
    """REST summary: extract, canonical URL, lead image, wikidata id."""
    r = requests.get(
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title, safe='')}",
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    data = r.json()
    return {
        "title": data.get("title"),
        "extract": data.get("extract"),
        "url": data.get("content_urls", {}).get("desktop", {}).get("page"),
        "thumbnail": data.get("thumbnail", {}).get("source"),
        "originalimage": data.get("originalimage", {}).get("source"),
        "wikibase_item": data.get("wikibase_item"),
    }


def commons_image_info(image_url: str) -> dict | None:
    """Resolve a Commons file URL to its license metadata via the Commons API."""
    # Commons URLs come in two forms:
    #   .../commons/<a>/<ab>/<File>                          (full size)
    #   .../commons/thumb/<a>/<ab>/<File>/<NNNpx-File>       (thumbnail)
    # The File: title is the segment before the trailing thumb spec, not the last segment.
    from urllib.parse import unquote

    parts = image_url.rstrip("/").split("/")
    if "thumb" in parts:
        # second-to-last segment is the original filename
        filename = unquote(parts[-2])
    else:
        filename = unquote(parts[-1])
    r = requests.get(
        "https://commons.wikimedia.org/w/api.php",
        params={
            "action": "query",
            "titles": f"File:{filename}",
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|mime|size",
            "format": "json",
        },
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", {})
    for _, page in pages.items():
        infos = page.get("imageinfo")
        if not infos:
            continue
        info = infos[0]
        ext = info.get("extmetadata", {})

        def _val(key: str) -> str | None:
            v = ext.get(key, {}).get("value")
            return v if v else None

        return {
            "filename": filename,
            "url": info.get("url"),
            "mime": info.get("mime"),
            "width": info.get("width"),
            "height": info.get("height"),
            "license_short": _val("LicenseShortName"),
            "license_url": _val("LicenseUrl"),
            "artist": _val("Artist"),
            "credit": _val("Credit"),
            "description": _val("ImageDescription"),
        }
    return None


def shrink_image(path: Path) -> Path | None:
    """Run tools/shrink_image.sh on the file. Return the web_*.{jpg,png} path."""
    script = REPO_ROOT / "tools" / "shrink_image.sh"
    if not script.exists():
        return None
    try:
        subprocess.run(
            ["bash", str(script), str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"  shrink failed: {e.stderr.strip()}", file=sys.stderr)
        return None
    # shrink_image.sh names the output web_<slugified-stem>.{jpg,png} in the same dir
    stem = path.stem.lower()
    import re
    slug = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    for ext in ("jpg", "png"):
        candidate = path.parent / f"web_{slug}.{ext}"
        if candidate.exists():
            return candidate
    return None


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True) as r:
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_content(chunk_size=64 * 1024):
                f.write(chunk)


def wikidata_facts(qid: str) -> dict:
    """Fetch a Wikidata entity and extract a few useful claims."""
    r = requests.get(
        f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json",
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    entity = r.json().get("entities", {}).get(qid, {})

    labels = entity.get("labels", {})
    descriptions = entity.get("descriptions", {})
    claims = entity.get("claims", {})

    def _claim_values(prop: str) -> list:
        out = []
        for c in claims.get(prop, []):
            dv = c.get("mainsnak", {}).get("datavalue")
            if dv:
                out.append(dv.get("value"))
        return out

    # A small, opinionated slice. Add more PIDs as needed.
    interesting = {
        "instance_of": "P31",
        "subclass_of": "P279",
        "country": "P17",
        "inception": "P571",
        "official_website": "P856",
        "coordinate_location": "P625",
        "described_at_url": "P973",
    }
    facts = {name: _claim_values(pid) for name, pid in interesting.items()}
    facts = {k: v for k, v in facts.items() if v}

    return {
        "qid": qid,
        "url": f"https://www.wikidata.org/wiki/{qid}",
        "label": labels.get("en", {}).get("value"),
        "description": descriptions.get("en", {}).get("value"),
        "claims": facts,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--wiki", required=True, help="Wiki name under wikis/")
    ap.add_argument("--slug", required=True, help="Catalogue entry slug")
    ap.add_argument(
        "--query",
        help="Override the Wikipedia search query (defaults to entry title)",
    )
    ap.add_argument(
        "--no-image",
        action="store_true",
        help="Skip downloading the lead image",
    )
    ap.add_argument(
        "--no-shrink",
        action="store_true",
        help="Skip running shrink_image.sh on the downloaded image",
    )
    ap.add_argument(
        "--no-wikidata",
        action="store_true",
        help="Skip Wikidata facts",
    )
    args = ap.parse_args()

    entry = find_catalogue_entry(args.wiki, args.slug)
    if entry is None:
        print(f"error: slug {args.slug!r} not found in wikis/{args.wiki}/catalogue/", file=sys.stderr)
        return 1

    query = args.query or entry.get("title") or args.slug
    print(f"searching wikipedia: {query!r}")
    title = wiki_search(query)
    if not title:
        print("no wikipedia match found", file=sys.stderr)
        return 2

    print(f"  -> {title}")
    summary = wiki_summary(title)

    result: dict = {
        "slug": args.slug,
        "query": query,
        "wikipedia": {
            "title": summary["title"],
            "url": summary["url"],
            "extract": summary["extract"],
        },
    }

    image_url = summary.get("originalimage") or summary.get("thumbnail")
    if image_url and not args.no_image:
        print(f"  image: {image_url}")
        info = commons_image_info(image_url)
        media_dir = REPO_ROOT / "wikis" / args.wiki / "media" / args.slug
        local_path = None
        try:
            src = info["url"] if info and info.get("url") else image_url
            filename = src.rsplit("/", 1)[-1]
            from urllib.parse import unquote
            filename = unquote(filename)
            local_path = media_dir / filename
            download(src, local_path)
            print(f"  saved: {local_path.relative_to(REPO_ROOT)}")
        except Exception as e:
            print(f"  image download failed: {e}", file=sys.stderr)

        web_path = None
        if local_path and local_path.exists() and not args.no_shrink:
            web = shrink_image(local_path)
            if web:
                web_path = str(web.relative_to(REPO_ROOT))
                print(f"  shrunk: {web_path}")
                local_path.unlink()
                print(f"  removed original: {local_path.relative_to(REPO_ROOT)}")
                local_path = None

        result["image"] = {
            "source_url": image_url,
            "local_path": str(local_path.relative_to(REPO_ROOT)) if local_path and local_path.exists() else None,
            "web_path": web_path,
            **(info or {}),
        }

    qid = summary.get("wikibase_item")
    if qid and not args.no_wikidata:
        print(f"  wikidata: {qid}")
        try:
            result["wikidata"] = wikidata_facts(qid)
        except Exception as e:
            print(f"  wikidata fetch failed: {e}", file=sys.stderr)

    out_path = REPO_ROOT / "wikis" / args.wiki / "enrichments" / f"{args.slug}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"wrote {out_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
