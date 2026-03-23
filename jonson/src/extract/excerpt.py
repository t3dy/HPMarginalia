"""Layer 6: Extract page-level excerpts from converted markdown sources.

Splits each source markdown on ## Page N / ## Slide N / ## Chapter N headers.
Preserves source_id and page_ref for every excerpt.
"""

import json
import re
from pathlib import Path

JONSON_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = JONSON_DIR.parent
MD_DIR = BASE_DIR / "Ben Jonson Life" / "md"
SOURCES_PATH = JONSON_DIR / "data" / "raw" / "sources.json"
OUTPUT = JONSON_DIR / "data" / "processed" / "excerpts.json"

# Min chars for an excerpt to be kept (skip near-empty pages)
MIN_TEXT_LENGTH = 20


def split_on_headers(text: str) -> list[tuple[str, str]]:
    """Split markdown text on ## headers. Returns [(header, body), ...]."""
    pattern = r'^## (.+)$'
    parts = []
    current_header = "preamble"
    current_body = []

    for line in text.split('\n'):
        m = re.match(pattern, line)
        if m:
            # Save previous section
            body = '\n'.join(current_body).strip()
            if body:
                parts.append((current_header, body))
            current_header = m.group(1).strip()
            current_body = []
        else:
            current_body.append(line)

    # Save last section
    body = '\n'.join(current_body).strip()
    if body:
        parts.append((current_header, body))

    return parts


def header_to_page_ref(header: str) -> str:
    """Convert a header like 'Page 42' or 'Slide 5' to a page_ref."""
    # Match Page N, Slide N, Chapter/Section N
    m = re.match(r'(Page|Slide|Chapter/Section|Chapter|Section)\s+(\d+)', header, re.IGNORECASE)
    if m:
        kind = m.group(1).lower()
        num = m.group(2)
        if 'page' in kind:
            return f"p. {num}"
        elif 'slide' in kind:
            return f"slide {num}"
        else:
            return f"sec. {num}"
    return header


def make_excerpt_id(source_id: str, page_ref: str) -> str:
    """Create a stable excerpt ID."""
    slug = re.sub(r'[^a-z0-9]+', '-', page_ref.lower()).strip('-')
    return f"{source_id}-{slug}"


def extract_excerpts(sources: list[dict]) -> list[dict]:
    """Extract all excerpts from all sources."""
    all_excerpts = []

    for source in sources:
        md_path = MD_DIR / source["md_filename"]
        if not md_path.exists():
            print(f"  SKIP {source['source_id']}: markdown not found")
            continue

        text = md_path.read_text(encoding='utf-8')
        sections = split_on_headers(text)

        source_excerpts = []
        for header, body in sections:
            # Skip preamble/metadata sections
            if header == "preamble":
                continue
            if body.startswith("*Source:"):
                continue

            # Clean the body text
            clean = body.strip()
            if len(clean) < MIN_TEXT_LENGTH:
                continue

            page_ref = header_to_page_ref(header)
            excerpt_id = make_excerpt_id(source["source_id"], page_ref)

            # Handle duplicate IDs (multiple sections with same header)
            existing_ids = {e["excerpt_id"] for e in all_excerpts + source_excerpts}
            if excerpt_id in existing_ids:
                suffix = 2
                while f"{excerpt_id}-{suffix}" in existing_ids:
                    suffix += 1
                excerpt_id = f"{excerpt_id}-{suffix}"

            source_excerpts.append({
                "excerpt_id": excerpt_id,
                "source_id": source["source_id"],
                "page_ref": page_ref,
                "text": clean,
            })

        all_excerpts.extend(source_excerpts)
        print(f"  {source['source_id']}: {len(source_excerpts)} excerpts")

    return all_excerpts


def merge_short_excerpts(excerpts: list[dict], min_length: int = 50) -> list[dict]:
    """Merge consecutive excerpts from same source if text is very short."""
    if not excerpts:
        return excerpts

    result = []
    i = 0
    while i < len(excerpts):
        current = excerpts[i].copy()
        # Look ahead and merge short consecutive excerpts from same source
        while (i + 1 < len(excerpts)
               and excerpts[i + 1]["source_id"] == current["source_id"]
               and len(current["text"]) < min_length):
            next_exc = excerpts[i + 1]
            current["text"] += "\n\n" + next_exc["text"]
            current["page_ref"] += f", {next_exc['page_ref']}"
            i += 1
        result.append(current)
        i += 1

    return result


def run():
    """Main entry point."""
    with open(SOURCES_PATH, 'r', encoding='utf-8') as f:
        sources = json.load(f)

    print(f"Extracting excerpts from {len(sources)} sources...\n")
    excerpts = extract_excerpts(sources)
    excerpts = merge_short_excerpts(excerpts)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(excerpts, f, indent=2, ensure_ascii=False)

    print(f"\nTotal: {len(excerpts)} excerpts -> {OUTPUT}")
    return excerpts


if __name__ == "__main__":
    run()
