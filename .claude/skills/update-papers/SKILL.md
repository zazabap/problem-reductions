---
name: update-papers
description: Update the research paper collection — download new papers from references.bib, retry failed downloads, sync to Google Drive, and regenerate index.md
---

# Update Papers

Maintain the research paper collection in `docs/research/`. Downloads papers referenced in `docs/paper/references.bib`, manages the manifest, syncs to Google Drive, and keeps `docs/research/index.md` current.

## Prerequisites

- `rclone` installed and configured with a `gdrive` remote
- `PAPERS_REMOTE` env var set (e.g., `gdrive:problemreductions-papers`)

## Step 1: Check Current Status

```bash
make papers-status
```

Note the counts: total entries, PDFs on disk, pending downloads, missing papers.

## Step 2: Lookup New Papers

Run the lookup to find arxiv/OA URLs for any new entries in `references.bib` since the last run. This is incremental — it skips entries already found in the manifest.

```bash
make papers-lookup
```

Review the output:
- New arxiv papers found
- New OA (open access) papers found
- Papers with no free source (will need Sci-Hub in Step 4)

## Step 3: Download Free Papers

Download papers with known free URLs (arxiv + open access). Skips PDFs already on disk.

```bash
make papers-download
```

If some OA downloads fail with 403, that's expected — publisher paywalls. These will be picked up by Sci-Hub in the next step.

## Step 4: Fetch Remaining via Sci-Hub

For papers with DOIs that aren't on disk yet, try Sci-Hub mirrors. This is the slowest step (~5 seconds per paper).

```bash
make papers-scihub
```

The script tries multiple mirrors (`sci-hub.ru`, `sci-hub.do`, `sci-hub.it.nf`, `sci-hub.es.ht`). If all mirrors are down, retry later — the script is fully idempotent.

## Step 4b: Manual Web Search for Remaining Failures

After Sci-Hub, check `make papers-status` for papers still missing. For each one with a DOI that Sci-Hub couldn't find:

1. **Web search** for `"<title>" <first-author> PDF` — try:
   - Author homepages (Stanford, university pages)
   - Open-access publishers: LIPIcs/Dagstuhl (all free), HAL archives, ECCC
   - Preprint servers: arxiv (search by title), IACR ePrint
2. **Download manually** with `curl -L -o docs/research/raw/<key>.pdf "<url>"`
3. **Verify** the file is a real PDF: `file docs/research/raw/<key>.pdf`

Skip textbooks (garey1979, sipser2012, cormen2022, conway1967) — these aren't available as single PDFs.

## Step 5: Regenerate Index

Update `docs/research/index.md` with the latest paper collection, cross-referenced against reduction rules and problem definitions in `reductions.typ`.

```bash
make papers-index
```

Verify the index looks correct:
- Check the download count at the top
- Spot-check that new papers appear in the correct section (rules / problems / other)
- Confirm PDF links resolve for newly downloaded papers

## Step 6: Sync to Google Drive

Push updated PDFs and manifest to the shared Google Drive remote. Only uploads new/changed files.

First verify the remote is configured:

```bash
echo $PAPERS_REMOTE    # should show e.g. gdrive:problemreductions-papers
# If empty, set it:
export PAPERS_REMOTE=gdrive:problemreductions-papers
```

Then push:

```bash
make papers-push
```

## Step 7: Final Status

```bash
make papers-status
```

Report to the user:
- How many new papers were downloaded
- How many remain missing (and why: no DOI, textbooks, Sci-Hub mirrors down)
- Whether the Google Drive sync succeeded

## One-Liner

For a full update in one command:

```bash
make papers && make papers-index
```

This runs: lookup → download → scihub → status → index.

## Troubleshooting

**Sci-Hub mirrors all fail**: Mirrors rotate frequently. Update `SCIHUB_DOMAINS` in `scripts/fetch_papers.py` or retry later.

**rclone auth expired**: Run `rclone config reconnect gdrive:` to refresh the OAuth token.

**Manifest is stale**: Delete `docs/research/manifest.json` and re-run `make papers-lookup` to rebuild from scratch. Existing PDFs on disk are preserved.

**New bib entry not appearing**: Ensure the entry is in `docs/paper/references.bib` with proper formatting. The parser expects `@type{key, ... }` with fields like `title`, `doi`, `author`, `year`.
