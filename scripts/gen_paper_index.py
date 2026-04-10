#!/usr/bin/env python3
"""Generate docs/research/index.md from references.bib, manifest, and reductions.typ."""

import json
import re
from pathlib import Path

BIB_PATH = Path("docs/paper/references.bib")
MANIFEST_PATH = Path("docs/research/manifest.json")
RAW_DIR = Path("docs/research/raw")
PAPER_PATH = Path("docs/paper/reductions.typ")
INDEX_PATH = Path("docs/research/index.md")


def parse_bib(path: Path) -> dict[str, dict]:
    content = path.read_text()
    entries = {}
    for match in re.finditer(r"@\w+\{(\w+),\s*(.*?)\n\}", content, re.DOTALL):
        key = match.group(1)
        body = match.group(2)

        def field(name):
            m = re.search(rf"{name}\s*=\s*\{{([^}}]+)\}}", body)
            return m.group(1).strip() if m else None

        title = field("title")
        if title:
            title = re.sub(r"[{}]", "", title)

        author = field("author")
        if author:
            parts = re.split(r"\s+and\s+", author)
            last = re.split(r",", parts[0])[0].strip()
            author = f"{last} et al." if len(parts) > 1 else last

        entries[key] = {
            "title": title or "?",
            "author": author or "?",
            "year": field("year") or "?",
            "doi": field("doi"),
        }
    return entries


def parse_citations(paper_path: Path, bib_keys: set) -> tuple[dict, dict]:
    """Parse reductions.typ for rule and problem citations."""
    text = paper_path.read_text()

    rule_citations: dict[str, set[str]] = {}
    for m in re.finditer(
        r'#reduction-rule\(\s*"([^"]+)"\s*,\s*"([^"]+)"', text
    ):
        source, target = m.group(1), m.group(2)
        chunk = text[m.end() : m.end() + 3000]
        for cite in re.finditer(r"@(\w+)", chunk):
            ckey = cite.group(1)
            if ckey in bib_keys:
                rule_citations.setdefault(ckey, set()).add(
                    f"{source} -> {target}"
                )

    problem_citations: dict[str, set[str]] = {}
    for m in re.finditer(r'#problem-def\(\s*"([^"]+)"', text):
        problem = m.group(1)
        chunk = text[m.end() : m.end() + 3000]
        for cite in re.finditer(r"@(\w+)", chunk):
            ckey = cite.group(1)
            if ckey in bib_keys:
                problem_citations.setdefault(ckey, set()).add(problem)

    return rule_citations, problem_citations


def generate_index():
    bib = parse_bib(BIB_PATH)
    pdfs = {p.stem for p in RAW_DIR.glob("*.pdf") if p.stat().st_size > 1000}
    rule_cites, problem_cites = parse_citations(PAPER_PATH, set(bib.keys()))

    lines = []
    lines.append("# Research Papers Index\n")
    n_missing = sum(1 for k in bib if k not in pdfs)
    lines.append(
        f"**{len(pdfs)}/{len(bib)}** papers downloaded"
        f" ({n_missing} missing)\n"
    )

    lines.append("## Legend\n")
    lines.append("- **Key**: citation key in `references.bib`")
    lines.append("- **Rules**: reduction rules citing this paper (Source -> Target)")
    lines.append("- **Problems**: problem definitions citing this paper")
    lines.append("- **PDF**: local file in `raw/` (or _missing_)\n")

    # Categorize
    with_rules = sorted(
        [k for k in bib if k in rule_cites],
        key=lambda k: bib[k]["year"],
    )
    with_problems_only = sorted(
        [k for k in bib if k in problem_cites and k not in rule_cites],
        key=lambda k: bib[k]["year"],
    )
    uncited = sorted(
        [k for k in bib if k not in problem_cites and k not in rule_cites],
        key=lambda k: bib[k]["year"],
    )

    def fmt(key: str) -> str:
        e = bib[key]
        title = e["title"][:70]
        ref = f"{e['author']} ({e['year']}). _{title}_"

        if key in pdfs:
            pdf = f"[{key}.pdf](raw/{key}.pdf)"
        else:
            pdf = "_missing_"

        rules = sorted(rule_cites.get(key, set()))
        probs = sorted(problem_cites.get(key, set()))

        rcol = ", ".join(f"`{r}`" for r in rules) if rules else "---"
        pcol = ", ".join(f"`{p}`" for p in probs) if probs else "---"

        return f"| `{key}` | {ref} | {rcol} | {pcol} | {pdf} |"

    def section(heading: str, keys: list[str]):
        lines.append(f"## {heading} ({len(keys)})\n")
        lines.append("| Key | Reference | Rules | Problems | PDF |")
        lines.append("|-----|-----------|-------|----------|-----|")
        for k in keys:
            lines.append(fmt(k))
        lines.append("")

    section("Papers cited in reduction rules", with_rules)
    section("Papers cited in problem definitions only", with_problems_only)
    section("Other references", uncited)

    INDEX_PATH.write_text("\n".join(lines))
    print(f"Wrote {INDEX_PATH} ({len(bib)} entries)")
    print(f"  Rules section: {len(with_rules)}")
    print(f"  Problems section: {len(with_problems_only)}")
    print(f"  Other section: {len(uncited)}")


if __name__ == "__main__":
    generate_index()
