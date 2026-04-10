#!/usr/bin/env python3
"""
Batch lookup arxiv/open-access versions of papers in references.bib.

Usage:
    python scripts/fetch_papers.py lookup    # Find arxiv/OA URLs for all papers
    python scripts/fetch_papers.py download  # Download available PDFs to docs/research/raw/
    python scripts/fetch_papers.py scihub    # Fetch remaining papers via Sci-Hub (DOI-based)
    python scripts/fetch_papers.py status    # Show current manifest stats
    python scripts/fetch_papers.py push      # Push PDFs to remote (rclone)
    python scripts/fetch_papers.py pull      # Pull PDFs from remote (rclone)

Env vars:
    PAPERS_REMOTE  rclone remote path, e.g. gdrive:problemreductions-papers
"""

import os
import re
import subprocess
import sys
import json
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

BIB_PATH = Path("docs/paper/references.bib")
OUTPUT_DIR = Path("docs/research/raw")
MANIFEST_PATH = Path("docs/research/manifest.json")

# rclone remote for sharing PDFs with collaborators.
# Set via env var or configure in rclone: rclone config
# Example: PAPERS_REMOTE=gdrive:problemreductions-papers
PAPERS_REMOTE = os.environ.get("PAPERS_REMOTE", "")

# Rate limiting: Semantic Scholar allows ~1 req/sec unauthenticated,
# arxiv allows ~1 req/3sec. We use conservative defaults.
S2_DELAY = 1.2       # seconds between Semantic Scholar requests
ARXIV_DELAY = 3.5    # seconds between arxiv API requests
MAX_RETRIES = 3       # retries per API call on 429
DOWNLOAD_DELAY = 2.0  # seconds between PDF downloads
SCIHUB_DELAY = 5.0    # seconds between Sci-Hub requests (be polite)
SCIHUB_DOMAINS = ["sci-hub.se", "sci-hub.st", "sci-hub.ru"]


def parse_bib(path: Path) -> list[dict]:
    """Parse .bib file into list of entries with key, title, doi, url, year."""
    content = path.read_text()
    entries = []
    for match in re.finditer(r"@\w+\{(\w+),\s*(.*?)\n\}", content, re.DOTALL):
        key = match.group(1)
        body = match.group(2)

        def field(name):
            m = re.search(rf"{name}\s*=\s*\{{([^}}]+)\}}", body)
            return m.group(1).strip() if m else None

        # Clean LaTeX from title
        title = field("title")
        if title:
            title = re.sub(r"[{}]", "", title)

        entries.append(
            {
                "key": key,
                "title": title,
                "doi": field("doi"),
                "url": field("url"),
                "year": field("year"),
                "author": field("author"),
            }
        )
    return entries


def _fetch_with_retry(url: str, delay_after: float, timeout: int = 15) -> bytes | None:
    """Fetch URL with exponential backoff on 429 errors."""
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "problemreductions/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            time.sleep(delay_after)
            return data
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = delay_after * (2 ** (attempt + 1))
                print(f"  rate limited, waiting {wait:.0f}s...", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"  HTTP {e.code}: {e.reason}", file=sys.stderr)
                time.sleep(delay_after)
                return None
        except Exception as e:
            print(f"  error: {e}", file=sys.stderr)
            time.sleep(delay_after)
            return None
    print(f"  giving up after {MAX_RETRIES} retries", file=sys.stderr)
    return None


def search_arxiv(title: str, max_results: int = 3) -> list[dict]:
    """Search arxiv API by title. Returns list of {arxiv_id, title, pdf_url}."""
    query = urllib.parse.quote(f'ti:"{title}"')
    url = f"http://export.arxiv.org/api/query?search_query={query}&max_results={max_results}"

    xml_data = _fetch_with_retry(url, ARXIV_DELAY)
    if not xml_data:
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_data)
    results = []
    for entry in root.findall("atom:entry", ns):
        entry_title = entry.findtext("atom:title", "", ns).strip().replace("\n", " ")
        arxiv_id = entry.findtext("atom:id", "", ns).strip()
        aid = arxiv_id.split("/abs/")[-1] if "/abs/" in arxiv_id else arxiv_id
        pdf_url = f"https://arxiv.org/pdf/{aid}"
        abs_url = f"https://arxiv.org/abs/{aid}"
        results.append(
            {"arxiv_id": aid, "title": entry_title, "pdf_url": pdf_url, "abs_url": abs_url}
        )
    return results


def search_semantic_scholar(doi: str = None, title: str = None) -> dict | None:
    """Search Semantic Scholar for open-access PDF link."""
    if doi:
        url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,openAccessPdf,externalIds"
    elif title:
        encoded = urllib.parse.quote(title)
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={encoded}&limit=1&fields=title,openAccessPdf,externalIds"
    else:
        return None

    raw = _fetch_with_retry(url, S2_DELAY)
    if not raw:
        return None

    data = json.loads(raw)

    # For search endpoint, extract first result
    if "data" in data and data["data"]:
        data = data["data"][0]

    oa = data.get("openAccessPdf")
    ext = data.get("externalIds", {})
    arxiv_id = ext.get("ArXiv")

    result = {"title": data.get("title", "")}
    if oa and oa.get("url"):
        result["oa_url"] = oa["url"]
    if arxiv_id:
        result["arxiv_id"] = arxiv_id
        result["pdf_url"] = f"https://arxiv.org/pdf/{arxiv_id}"
        result["abs_url"] = f"https://arxiv.org/abs/{arxiv_id}"
    return result


def title_similarity(a: str, b: str) -> float:
    """Simple word-overlap similarity between two titles."""
    wa = set(re.findall(r"\w+", a.lower()))
    wb = set(re.findall(r"\w+", b.lower()))
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / max(len(wa), len(wb))


def load_manifest() -> dict[str, dict]:
    """Load existing manifest as {key: entry} dict. Returns empty dict if none."""
    if MANIFEST_PATH.exists():
        entries = json.loads(MANIFEST_PATH.read_text())
        return {e["key"]: e for e in entries}
    return {}


def save_manifest(manifest: dict[str, dict]):
    """Save manifest dict back to file, sorted by key."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    entries = sorted(manifest.values(), key=lambda e: e["key"])
    MANIFEST_PATH.write_text(json.dumps(entries, indent=2))


def lookup_all(entries: list[dict]):
    """Look up arxiv/OA versions for all entries. Resumes from existing manifest."""
    manifest = load_manifest()
    skipped = 0

    for i, entry in enumerate(entries):
        key = entry["key"]
        title = entry["title"] or ""
        doi = entry["doi"]

        # Skip if already found in previous run
        existing = manifest.get(key)
        if existing and existing.get("pdf_url"):
            skipped += 1
            continue

        print(f"[{i+1}/{len(entries)}] {key}: {title[:60]}...")

        result = {
            "key": key,
            "title": title,
            "doi": doi,
            "year": entry["year"],
            "source": None,
            "pdf_url": None,
            "abs_url": None,
            "arxiv_id": None,
        }

        # Strategy 1: Semantic Scholar by DOI (most reliable)
        if doi:
            s2 = search_semantic_scholar(doi=doi)
            if s2:
                if s2.get("arxiv_id"):
                    result["arxiv_id"] = s2["arxiv_id"]
                    result["pdf_url"] = s2["pdf_url"]
                    result["abs_url"] = s2["abs_url"]
                    result["source"] = "arxiv_via_s2"
                    print(f"  -> arxiv (via S2): {s2['arxiv_id']}")
                elif s2.get("oa_url"):
                    result["pdf_url"] = s2["oa_url"]
                    result["source"] = "oa_via_s2"
                    print(f"  -> OA (via S2): {s2['oa_url'][:60]}")

        # Strategy 2: Search arxiv directly by title
        if not result["pdf_url"] and title:
            arxiv_results = search_arxiv(title)
            for ar in arxiv_results:
                sim = title_similarity(title, ar["title"])
                if sim > 0.6:
                    result["arxiv_id"] = ar["arxiv_id"]
                    result["pdf_url"] = ar["pdf_url"]
                    result["abs_url"] = ar["abs_url"]
                    result["source"] = "arxiv_direct"
                    print(f"  -> arxiv (direct): {ar['arxiv_id']} (sim={sim:.2f})")
                    break

        # Strategy 3: Semantic Scholar by title (fallback for no-DOI entries)
        if not result["pdf_url"] and title and not doi:
            s2 = search_semantic_scholar(title=title)
            if s2:
                if s2.get("arxiv_id"):
                    result["arxiv_id"] = s2["arxiv_id"]
                    result["pdf_url"] = s2["pdf_url"]
                    result["abs_url"] = s2["abs_url"]
                    result["source"] = "arxiv_via_s2_title"
                    print(f"  -> arxiv (S2 title): {s2['arxiv_id']}")
                elif s2.get("oa_url"):
                    result["pdf_url"] = s2["oa_url"]
                    result["source"] = "oa_via_s2_title"
                    print(f"  -> OA (S2 title): {s2['oa_url'][:60]}")

        if not result["pdf_url"]:
            print(f"  -> NOT FOUND")

        manifest[key] = result

        # Save incrementally every 10 entries
        if (i + 1) % 10 == 0:
            save_manifest(manifest)
            print(f"  (manifest saved, {i+1}/{len(entries)} processed)")

    save_manifest(manifest)

    if skipped:
        print(f"\nSkipped {skipped} entries already found in previous run")

    # Summary
    all_entries = list(manifest.values())
    found = [r for r in all_entries if r.get("pdf_url")]
    arxiv = [r for r in all_entries if r.get("arxiv_id")]
    oa_only = [r for r in found if not r.get("arxiv_id")]
    missing = [r for r in all_entries if not r.get("pdf_url")]

    print(f"\n=== SUMMARY ===")
    print(f"Total: {len(all_entries)}")
    print(f"Arxiv: {len(arxiv)}")
    print(f"OA (non-arxiv): {len(oa_only)}")
    print(f"Not found: {len(missing)}")

    if missing:
        print(f"\n=== NOT FOUND ({len(missing)}) ===")
        for r in missing:
            print(f"  {r['key']} ({r.get('year','?')}): {r.get('title','')[:60]}")


def download_pdfs(manifest_entries: list[dict]):
    """Download PDFs for entries that have a pdf_url. Skips existing files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    downloadable = [r for r in manifest_entries if r.get("pdf_url")]
    print(f"\n{len(downloadable)} papers have PDF URLs")

    downloaded = 0
    skipped = 0
    failed = 0

    for i, entry in enumerate(downloadable):
        key = entry["key"]
        url = entry["pdf_url"]
        dest = OUTPUT_DIR / f"{key}.pdf"

        if dest.exists() and dest.stat().st_size > 1000:
            skipped += 1
            continue

        print(f"[{downloaded+1}] {key}: {url[:70]}...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "problemreductions/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()

            # Sanity check: should look like a PDF
            if data[:5] == b"%PDF-" or len(data) > 10000:
                dest.write_bytes(data)
                print(f"  -> saved ({dest.stat().st_size // 1024} KB)")
                downloaded += 1
            else:
                print(f"  -> SKIP: response doesn't look like PDF ({len(data)} bytes)")
                failed += 1
        except Exception as e:
            print(f"  -> FAILED: {e}")
            failed += 1

        time.sleep(DOWNLOAD_DELAY)

    print(f"\n=== DOWNLOAD SUMMARY ===")
    print(f"Downloaded: {downloaded}")
    print(f"Already existed: {skipped}")
    print(f"Failed: {failed}")
    print(f"Total PDFs in {OUTPUT_DIR}/: {len(list(OUTPUT_DIR.glob('*.pdf')))}")


def _try_scihub_download(doi: str, dest: Path) -> bool:
    """Try downloading a paper from Sci-Hub using its DOI. Returns True on success."""
    for domain in SCIHUB_DOMAINS:
        url = f"https://{domain}/{doi}"
        try:
            # First request gets the page with embedded PDF link
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 Safari/537.36"
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = resp.read()

            # If we got a PDF directly
            if content[:5] == b"%PDF-":
                dest.write_bytes(content)
                return True

            # Parse page for embedded PDF iframe/link
            html = content.decode("utf-8", errors="ignore")
            # Look for iframe src or direct PDF link
            pdf_match = re.search(
                r'(?:iframe|embed)[^>]+src\s*=\s*["\']([^"\']*\.pdf[^"\']*)["\']',
                html, re.IGNORECASE
            )
            if not pdf_match:
                pdf_match = re.search(
                    r'(https?://[^\s"\'<>]+\.pdf(?:\?[^\s"\'<>]*)?)',
                    html, re.IGNORECASE
                )
            if not pdf_match:
                # Try //domain/path pattern (protocol-relative)
                pdf_match = re.search(
                    r'src\s*=\s*["\']?(//[^\s"\'<>]+\.pdf[^\s"\'<>]*)',
                    html, re.IGNORECASE
                )

            if pdf_match:
                pdf_url = pdf_match.group(1)
                if pdf_url.startswith("//"):
                    pdf_url = "https:" + pdf_url

                pdf_req = urllib.request.Request(pdf_url, headers={
                    "User-Agent": "Mozilla/5.0",
                    "Referer": url,
                })
                with urllib.request.urlopen(pdf_req, timeout=60) as pdf_resp:
                    pdf_data = pdf_resp.read()

                if pdf_data[:5] == b"%PDF-" or len(pdf_data) > 50000:
                    dest.write_bytes(pdf_data)
                    return True

        except Exception as e:
            print(f"    {domain}: {e}", file=sys.stderr)
            continue

    return False


def download_scihub(manifest_entries: list[dict]):
    """Download papers not yet on disk via Sci-Hub, using DOI."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Papers that have a DOI but no PDF on disk yet
    candidates = []
    for entry in manifest_entries:
        key = entry["key"]
        doi = entry.get("doi")
        dest = OUTPUT_DIR / f"{key}.pdf"
        if doi and not (dest.exists() and dest.stat().st_size > 1000):
            candidates.append(entry)

    if not candidates:
        print("No papers with DOIs need downloading.")
        return

    print(f"\nAttempting Sci-Hub download for {len(candidates)} papers...\n")

    downloaded = 0
    failed = 0

    for i, entry in enumerate(candidates):
        key = entry["key"]
        doi = entry["doi"]
        dest = OUTPUT_DIR / f"{key}.pdf"

        print(f"[{i+1}/{len(candidates)}] {key}: {doi}")
        if _try_scihub_download(doi, dest):
            size_kb = dest.stat().st_size // 1024
            print(f"  -> saved ({size_kb} KB)")
            downloaded += 1
        else:
            print(f"  -> FAILED (all mirrors)")
            failed += 1

        time.sleep(SCIHUB_DELAY)

    print(f"\n=== SCI-HUB SUMMARY ===")
    print(f"Downloaded: {downloaded}")
    print(f"Failed: {failed}")
    print(f"Total PDFs in {OUTPUT_DIR}/: {len(list(OUTPUT_DIR.glob('*.pdf')))}")


def show_status():
    """Show current manifest and download status."""
    manifest = load_manifest()
    if not manifest:
        print("No manifest found. Run 'lookup' first.")
        return

    all_entries = list(manifest.values())
    found = [r for r in all_entries if r.get("pdf_url")]
    arxiv = [r for r in all_entries if r.get("arxiv_id")]
    oa_only = [r for r in found if not r.get("arxiv_id")]
    missing = [r for r in all_entries if not r.get("pdf_url")]

    pdfs = list(OUTPUT_DIR.glob("*.pdf")) if OUTPUT_DIR.exists() else []
    pdf_keys = {p.stem for p in pdfs}
    total_size = sum(p.stat().st_size for p in pdfs)

    print(f"=== MANIFEST ===")
    print(f"Total entries: {len(all_entries)}")
    print(f"Arxiv: {len(arxiv)}")
    print(f"OA (non-arxiv): {len(oa_only)}")
    print(f"Not found: {len(missing)}")
    print()
    print(f"=== DOWNLOADS ===")
    print(f"PDFs on disk: {len(pdfs)}")
    print(f"Total size: {total_size / 1024 / 1024:.1f} MB")
    print(f"Pending download: {len(found) - len(pdf_keys & {e['key'] for e in found})}")

    if missing:
        print(f"\n=== NOT FOUND ({len(missing)}) ===")
        for r in sorted(missing, key=lambda r: r.get("year", "0")):
            doi_str = f" doi:{r.get('doi','')}" if r.get("doi") else ""
            print(f"  {r['key']} ({r.get('year','?')}): {r.get('title','')[:55]}{doi_str}")


def _require_remote() -> str:
    """Return PAPERS_REMOTE or exit with instructions."""
    if not PAPERS_REMOTE:
        print("PAPERS_REMOTE not set. Configure it:")
        print("  1. Install rclone: brew install rclone")
        print("  2. Configure a remote: rclone config")
        print("  3. Set the env var: export PAPERS_REMOTE=gdrive:problemreductions-papers")
        print("     Or pass inline: PAPERS_REMOTE=gdrive:papers make papers-push")
        sys.exit(1)
    return PAPERS_REMOTE


def sync_push():
    """Push local PDFs + manifest to remote via rclone."""
    remote = _require_remote()
    print(f"Pushing docs/research/ -> {remote}/")
    # Sync both raw/ (PDFs) and manifest.json
    subprocess.run(
        ["rclone", "sync", str(OUTPUT_DIR), f"{remote}/raw/",
         "--progress", "--transfers", "4"],
        check=True,
    )
    if MANIFEST_PATH.exists():
        subprocess.run(
            ["rclone", "copy", str(MANIFEST_PATH), f"{remote}/",
             "--progress"],
            check=True,
        )
    print("Push complete.")


def sync_pull():
    """Pull PDFs + manifest from remote via rclone."""
    remote = _require_remote()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Pulling {remote}/ -> docs/research/")
    subprocess.run(
        ["rclone", "sync", f"{remote}/raw/", str(OUTPUT_DIR),
         "--progress", "--transfers", "4"],
        check=True,
    )
    subprocess.run(
        ["rclone", "copy", f"{remote}/manifest.json",
         str(MANIFEST_PATH.parent), "--progress"],
        check=True,
    )
    print("Pull complete.")
    show_status()


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("lookup", "download", "scihub", "status", "push", "pull"):
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "lookup":
        entries = parse_bib(BIB_PATH)
        print(f"Parsed {len(entries)} entries from {BIB_PATH}\n")
        lookup_all(entries)
        print(f"\nManifest saved to {MANIFEST_PATH}")

    elif cmd == "download":
        manifest = load_manifest()
        if not manifest:
            print("Run 'lookup' first to generate manifest.json")
            sys.exit(1)
        download_pdfs(list(manifest.values()))

    elif cmd == "scihub":
        manifest = load_manifest()
        if not manifest:
            print("Run 'lookup' first to generate manifest.json")
            sys.exit(1)
        download_scihub(list(manifest.values()))

    elif cmd == "push":
        sync_push()

    elif cmd == "pull":
        sync_pull()

    elif cmd == "status":
        show_status()


if __name__ == "__main__":
    main()
