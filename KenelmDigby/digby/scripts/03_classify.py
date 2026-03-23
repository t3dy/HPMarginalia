"""
Stage 3: Classify excerpts by theme.

Assigns theme labels to source_excerpts based on keyword matching.
Multiple themes can be assigned to a single excerpt.
"""

import os
import sys
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.models import ThemeLabel
from src.db import get_connection, init_db

# Keyword patterns for each theme
THEME_KEYWORDS = {
    ThemeLabel.BIOGRAPHY.value: [
        r'\b(?:born|died|birth|death|married|wife|children|father|mother)\b',
        r'\b(?:youth|childhood|education|Oxford|Cambridge)\b',
        r'\b(?:career|life|biography|biographical)\b',
        r'\b(?:Venetia|Stanley|Gunpowder Plot)\b',
    ],
    ThemeLabel.MEMOIR.value: [
        r'\b(?:memoir|memoirs|private memoirs|journal|diary)\b',
        r'\b(?:recollection|reminiscence|autobiography)\b',
        r'\b(?:bedchamber|gentleman of)\b',
    ],
    ThemeLabel.PIRATE.value: [
        r'\b(?:pirate|piracy|privateer|privateering|corsair)\b',
        r'\b(?:voyage|sailing|fleet|ship|naval|maritime)\b',
        r'\b(?:Mediterranean|Algiers|Scanderoon|Iskenderun)\b',
        r'\b(?:battle|fought|plunder|prize|cannon)\b',
        r'\b(?:sea[-\s]?fight|Venetian)\b',
    ],
    ThemeLabel.ALCHEMIST_NATURAL_PHILOSOPHER.value: [
        r'\b(?:alchem|alchemist|alchemy|alchemical)\b',
        r'\b(?:experiment|laboratory|chemical|chymical)\b',
        r'\b(?:natural philosoph|philosopher|philosophy)\b',
        r'\b(?:powder of sympathy|weapon salve|sympathetic)\b',
        r'\b(?:mercury|sulphur|vitriol|distill|transmut)\b',
        r'\b(?:Two Treatises|vegetation of plants|Gresham)\b',
        r'\b(?:Royal Society|F\.R\.S)\b',
        r'\b(?:matter|spirit|atoms|corpuscul)\b',
    ],
    ThemeLabel.COURTIER_LEGAL_THINKER.value: [
        r'\b(?:court|courtier|king|Charles|queen|Henrietta)\b',
        r'\b(?:patron|patronage|ambassador|diplomat)\b',
        r'\b(?:law|legal|property|real property)\b',
        r'\b(?:politic|parliament|civil war|royalist)\b',
        r'\b(?:Catholic|recusant|religion|conversion)\b',
        r'\b(?:Buckingham|Cromwell|exile)\b',
    ],
    ThemeLabel.WORKS.value: [
        r'\b(?:published|publication|treatise|wrote|writing)\b',
        r'\b(?:book|volume|text|manuscript|work)\b',
        r'\b(?:Observations|Closet|Receipts|Bibliotheca)\b',
        r'\b(?:Two Treatises|Conference|Discourse)\b',
    ],
    ThemeLabel.BIBLIOGRAPHY.value: [
        r'\b(?:bibliograph|reference|citation|source)\b',
        r'\b(?:edited by|trans\.|published)\b',
        r'\b(?:journal|vol\.|pp\.|issue)\b',
    ],
    ThemeLabel.HYPNEROTOMACHIA_DIGBY.value: [
        r'\b(?:Hypnerotomachia|Poliphili|Poliphilo)\b',
        r'\b(?:alchemical annot|marginalia|annotator)\b',
        r'\b(?:Jupiter|Tin|universal spirit)\b',
        r'\b(?:Ben Jonson|Russell)\b',
        r'\b(?:woodcut|emblem)\b',
    ],
}

# Compile patterns
COMPILED_PATTERNS = {
    theme: [re.compile(p, re.IGNORECASE) for p in patterns]
    for theme, patterns in THEME_KEYWORDS.items()
}

SCORE_THRESHOLD = 2  # Minimum keyword matches to assign a theme


def classify_excerpt(text: str) -> list[str]:
    """Return list of theme labels for the given text."""
    themes = []
    for theme, patterns in COMPILED_PATTERNS.items():
        score = sum(1 for p in patterns if p.search(text))
        if score >= SCORE_THRESHOLD:
            themes.append(theme)
        elif score >= 1 and theme in (
            ThemeLabel.MEMOIR.value,
            ThemeLabel.HYPNEROTOMACHIA_DIGBY.value,
        ):
            # Lower threshold for distinctive themes
            themes.append(theme)
    return themes


def classify_all():
    """Classify all unclassified excerpts."""
    init_db()
    conn = get_connection()
    excerpts = conn.execute(
        "SELECT id, text FROM source_excerpts WHERE themes IS NULL OR themes = ''"
    ).fetchall()

    classified = 0
    for exc in excerpts:
        themes = classify_excerpt(exc["text"])
        if themes:
            theme_str = ",".join(themes)
            conn.execute(
                "UPDATE source_excerpts SET themes = ? WHERE id = ?",
                (theme_str, exc["id"])
            )
            classified += 1

    conn.commit()
    conn.close()
    print(f"Classified {classified}/{len(excerpts)} excerpts.")


if __name__ == "__main__":
    classify_all()
