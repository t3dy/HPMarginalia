"""Ingest: catalog source markdown files into data/raw/sources.json."""

import json
import re
from pathlib import Path

JONSON_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = JONSON_DIR.parent
MD_DIR = BASE_DIR / "Ben Jonson Life" / "md"
OUTPUT = JONSON_DIR / "data" / "raw" / "sources.json"

# Manual metadata for our 5 source documents
SOURCE_METADATA = [
    {
        "source_id": "hart-alchemist",
        "title": "The Alchemist, edited by H.C. Hart",
        "author": "Ben Jonson; ed. H.C. Hart",
        "md_filename": "The_Alchemist_by_Ben_J_Onson_Newly_Edited_by.md",
        "doc_type": "pdf",
        "page_count": 255,
        "content_focus": ["alchemist_text", "alchemist_notes"],
        "notes": "1903 De La More Press edition. OCR has artifacts from scanned original."
    },
    {
        "source_id": "arden-critical-reader",
        "title": "The Alchemist: A Critical Reader (Arden Early Modern Drama)",
        "author": "ed. Erin Julian and Helen Ostovich",
        "md_filename": "Jonson_Ben_Ostovich_Helen_Julian_Erin_-_The_alchemist_a.md",
        "doc_type": "epub",
        "page_count": None,
        "content_focus": ["alchemist_criticism", "alchemist_performance", "alchemist_alchemy"],
        "notes": "2013 Bloomsbury/Arden. Critical essays on The Alchemist."
    },
    {
        "source_id": "mardock-london",
        "title": "Our Scene is London: Ben Jonson's City and the Space of the Author",
        "author": "James D. Mardock",
        "md_filename": "Mardock_James_D_Jonson_Ben_-_Our_scene_is.md",
        "doc_type": "pdf",
        "page_count": 175,
        "content_focus": ["jonson_biography", "jonson_london", "theatrical_context"],
        "notes": "2008 Routledge. Jonson's relationship to London."
    },
    {
        "source_id": "linden-darke-hierogliphicks",
        "title": "Darke Hierogliphicks: Alchemy in English Literature (Maier extract)",
        "author": "Stanton J. Linden",
        "md_filename": "Darke_Hierogliphicks_Alchemy_in_English_Literature_from_Chaucer.md",
        "doc_type": "txt",
        "page_count": None,
        "content_focus": ["alchemy_literature", "alchemist_alchemy", "maier"],
        "notes": "University Press of Kentucky. Extract focused on Michael Maier chapter."
    },
    {
        "source_id": "russell-pptx",
        "title": "The HP of Ben Jonson and Kenelm Digby (Russell & O'Neill presentation)",
        "author": "James Russell and James O'Neill",
        "md_filename": "The_HP_of_Ben_Jonson_and_Kenelm_Digby.md",
        "doc_type": "pptx",
        "page_count": 46,
        "content_focus": ["jonson_hp_annotations", "alchemical_hand", "digby_attribution", "russell_findings"],
        "notes": "Presentation slides. Primary source for Russell findings on Jonson's HP copy."
    },
]


def run():
    """Catalog sources and write to JSON."""
    records = []
    for meta in SOURCE_METADATA:
        md_path = MD_DIR / meta["md_filename"]
        record = {
            "source_id": meta["source_id"],
            "title": meta["title"],
            "author": meta.get("author"),
            "filename": meta["md_filename"].replace(".md", ""),
            "md_filename": meta["md_filename"],
            "doc_type": meta["doc_type"],
            "page_count": meta.get("page_count"),
            "content_focus": meta.get("content_focus", []),
            "notes": meta.get("notes"),
            "md_exists": md_path.exists(),
            "md_size": md_path.stat().st_size if md_path.exists() else 0,
        }
        records.append(record)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Cataloged {len(records)} sources -> {OUTPUT}")
    for r in records:
        status = "OK" if r["md_exists"] else "MISSING"
        print(f"  [{status}] {r['source_id']}: {r['title']}")

    return records


if __name__ == "__main__":
    run()
