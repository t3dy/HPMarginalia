"""Layer 7: Classify excerpts into content buckets.

Categories:
  - jonson_life: biographical material about Ben Jonson
  - alchemist_alchemy: alchemical content related to The Alchemist
  - hypnerotomachia_jonson: Jonson's HP annotations / Russell's findings

Uses deterministic keyword matching. No LLM needed for seed phase.
"""

import json
import re
from pathlib import Path

JONSON_DIR = Path(__file__).resolve().parent.parent.parent
EXCERPTS_PATH = JONSON_DIR / "data" / "processed" / "excerpts.json"
OUTPUT = JONSON_DIR / "data" / "processed" / "classified.json"

# Keyword patterns for each category (case-insensitive)
PATTERNS = {
    "jonson_life": [
        r'\bjonson\b.*\b(born|died|death|married|prison|killed|duel|convert|catholic|brick)',
        r'\b(westminster|stepfather|camden|drummond|conversations|pension)',
        r'\bjonson\b.*\b(1572|1573|1598|1616|1637|folio)',
        r'\b(sons of ben|mermaid tavern|apollo room)',
        r'\bjonson\'?s?\b.*\b(life|biography|career|youth|education)',
        r'\b(ben jonson|b\.\s*jonson)\b.*\b(london|city|court)',
    ],
    "alchemist_alchemy": [
        r'\b(mercury|mercurius|sol|luna|sulph[ua]r|salt|vitriol|antimony)\b',
        r'\b(transmut|project(ion)?|elixir|tincture|quintessence|magisterium)\b',
        r'\b(philosopher.?s?\s+stone|lapis|chrysopoeia)\b',
        r'\b(calcin|distill|sublim|coagul|dissolv|putrefact|ferment)\b',
        r'\b(alchemist|alchem|chymical|chymist)\b',
        r'\b(subtle|face|mammon|dapper|drugger|surly|lovewit)\b',
        r'\b(base metal|gold|silver|lead|copper|tin|iron)\b.*\b(transmut|convert|turn)',
        r'\b(furnace|athanor|alembic|crucible|retort|pelican)\b',
        r'\b(red lion|green lion|white eagle|black crow|phoenix)\b',
        r'\b(fraud|coz[ae]n|gull|trick|cheat|impostor)\b.*\b(alchem|projec)',
        r'\b(paracels|geber|hermes|flamel|lull|ripley|norton)\b',
    ],
    "hypnerotomachia_jonson": [
        r'\bhypnerotomachia\b',
        r'\bpoliphil[io]\b',
        r'\b(BL|british library)\s+C\.60\.o\.12\b',
        r'\bcolonna\b',
        r'\b(aldine|aldus)\b.*\b1545\b',
        r'\bjonson\b.*\b(marginali|annotat|hand|signature|motto)\b',
        r'\btanquam\s+explorator\b',
        r'\bsum\s+ben\b',
        r'\bionsonii\b',
        r'\b(alchemical\s+hand|second\s+hand|third\s+hand)\b',
        r'\b(digby|bourne)\b.*\b(hand|annotat|marginali)\b',
        r'\bpanton\s+tokadi\b',
        r'\bd.espagnet\b',
        r'\bmagisteri\s+mercurii\b',
        r'\b(russell|o.neill)\b.*\b(finding|research|presentation)\b',
    ],
}


def classify_excerpt(excerpt: dict) -> list[str]:
    """Classify an excerpt into categories using keyword matching."""
    text = excerpt["text"].lower()
    source_id = excerpt["source_id"]
    categories = []

    # Source-based priors: some sources are strongly associated with categories
    source_priors = {
        "russell-pptx": "hypnerotomachia_jonson",
        "hart-alchemist": "alchemist_alchemy",
        "arden-critical-reader": "alchemist_alchemy",
    }

    for cat, patterns in PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                categories.append(cat)
                break

    # Apply source priors if no keyword match but source is strongly typed
    if not categories and source_id in source_priors:
        categories.append(source_priors[source_id])

    # Deduplicate
    return list(dict.fromkeys(categories))


def run():
    """Classify all excerpts."""
    with open(EXCERPTS_PATH, 'r', encoding='utf-8') as f:
        excerpts = json.load(f)

    counts = {"jonson_life": 0, "alchemist_alchemy": 0, "hypnerotomachia_jonson": 0, "unclassified": 0}

    for exc in excerpts:
        cats = classify_excerpt(exc)
        exc["categories"] = cats if cats else ["unclassified"]
        exc["classification_method"] = "DETERMINISTIC"

        for cat in exc["categories"]:
            counts[cat] = counts.get(cat, 0) + 1

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(excerpts, f, indent=2, ensure_ascii=False)

    print(f"Classified {len(excerpts)} excerpts -> {OUTPUT}")
    print(f"  jonson_life:             {counts['jonson_life']}")
    print(f"  alchemist_alchemy:       {counts['alchemist_alchemy']}")
    print(f"  hypnerotomachia_jonson:  {counts['hypnerotomachia_jonson']}")
    print(f"  unclassified:            {counts['unclassified']}")

    return excerpts


if __name__ == "__main__":
    run()
