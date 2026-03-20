"""Compile all BL image reading data into staging/bl_complete_reading.json.

Data from reading 55 BL photographs (13 front matter + 42 text pages)
covering pages 1-176 at sampling intervals of 2-10 pages.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STAGING_DIR = BASE_DIR / "staging"

READINGS = {
    # Front matter
    1: {"type": "COVER", "desc": "Blank endpaper"},
    2: {"type": "GUARD", "desc": "Flyleaf recto: Bourne provenance 1641", "annotations": "HEAVY"},
    3: {"type": "GUARD", "desc": "Flyleaf verso: Master Mercury declaration", "annotations": "HEAVY", "alchemical": True},
    4: {"type": "OTHER", "desc": "Title page 1545 RISTAMPATO, Aldine anchor, Sum Ben Ionsonij"},
    5: {"type": "OTHER", "desc": "Dedication Crasso, MUSEUM BRITANNICUM stamp"},
    6: {"type": "OTHER", "desc": "Prefatory verse Scita pt1"},
    7: {"type": "OTHER", "desc": "Prefatory verse Scita pt2 Finis", "annotations": "HEAVY"},
    8: {"type": "OTHER", "desc": "Argomento/summary", "annotations": "HEAVY"},
    9: {"type": "OTHER", "desc": "Prefatory poem", "annotations": "MODERATE"},
    10: {"type": "OTHER", "desc": "Prefatory verse Finis"},
    11: {"type": "OTHER", "desc": "Verse Andreas Maro"},
    12: {"type": "OTHER", "desc": "Half-title POLIPHILI HYPNEROTOMACHIA"},
    13: {"type": "OTHER", "desc": "Poliphilus dedication to Polia Vale"},
    # Text pages
    14: {"page": 1, "woodcut": None, "annotations": "HEAVY", "notes": "a1r POLIPHILO INCOMINCIA historiated initial"},
    15: {"page": 2, "annotations": "MODERATE"},
    16: {"page": 3, "annotations": "HEAVY", "notes": "sig a iii visible"},
    17: {"page": 4, "woodcut": "Dark forest (selva oscura)", "annotations": "MODERATE"},
    18: {"page": 5, "annotations": "HEAVY", "notes": "a3r Chapter heading POLIPHILO TEMENDO"},
    19: {"page": 6, "annotations": "HEAVY"},
    20: {"page": 7, "annotations": "HEAVY"},
    21: {"page": 8, "woodcut": "Landscape with reclining figure", "annotations": "MODERATE"},
    22: {"page": 9, "annotations": "HEAVY"},
    23: {"page": 10, "woodcut": "Poliphilo sleeping - DREAM WITHIN DREAM", "annotations": "MODERATE"},
    24: {"page": 11, "woodcut": "Poliphilo in garden with palms and well", "annotations": "HEAVY"},
    25: {"page": 12, "annotations": "HEAVY"},
    26: {"page": 13, "annotations": "HEAVY", "notes": "Porphyry Corinthio mentioned"},
    28: {"page": 15, "annotations": "MODERATE", "notes": "Pyramide Babylonica"},
    30: {"page": 17, "annotations": "HEAVY"},
    32: {"page": 19, "annotations": "HEAVY"},
    33: {"page": 20, "annotations": "HEAVY", "alchemical": True, "notes": "Alchemical ideograms in left margin"},
    35: {"page": 22, "woodcut": "Horse and rider on sarcophagus", "annotations": "MODERATE"},
    36: {"page": 23, "woodcut": "Twin inscribed monuments D.AMBIG.D.D.", "annotations": "HEAVY"},
    40: {"page": 27, "woodcut": "Inscription monument GONOS KAI ETOUSIA", "annotations": "HEAVY"},
    41: {"page": 28, "woodcut": "ELEPHANT AND OBELISK", "annotations": "HEAVY", "alchemical": True},
    42: {"page": 29, "woodcut": "Figure on monument with Greek inscription", "annotations": "HEAVY"},
    45: {"page": 32, "annotations": "HEAVY", "notes": "Geometric diagram in margin sig c ii"},
    46: {"page": 33, "annotations": "HEAVY"},
    48: {"page": 35, "annotations": "HEAVY", "notes": "Porphyry Trophyis sig c iii"},
    50: {"page": 37, "annotations": "LIGHT"},
    52: {"page": 39, "annotations": "HEAVY"},
    55: {"page": 42, "annotations": "HEAVY", "alchemical": True, "notes": "Greek Aphrodite/Dionysos inscription alchemical symbols bottom"},
    56: {"page": 43, "annotations": "HEAVY", "notes": "Corinthio Apollo columns"},
    60: {"page": 47, "annotations": "MODERATE", "notes": "Eurythmia in margin"},
    65: {"page": 52, "woodcut": "Poliphilo at portal with dragon", "annotations": "MODERATE"},
    70: {"page": 57, "annotations": "LIGHT"},
    75: {"page": 62, "annotations": "MODERATE", "alchemical": True, "notes": "PANTA TOKADI inscription"},
    77: {"page": 64, "annotations": "MODERATE", "notes": "Cynara Alcachissa botanical"},
    78: {"page": 65, "annotations": "MODERATE", "notes": "SEMPER FESTINA TARDE motto"},
    80: {"page": 67, "annotations": "MODERATE"},
    85: {"page": 72, "annotations": "MODERATE"},
    90: {"page": 77, "annotations": "LIGHT"},
    95: {"page": 82, "annotations": "LIGHT"},
    100: {"page": 87, "woodcut": "Grotesque frieze with hybrid figures", "annotations": "MODERATE"},
    105: {"page": 92, "woodcut": "Circular medallion/deity figure", "annotations": "HEAVY", "alchemical": True},
    110: {"page": 97, "annotations": "MODERATE", "notes": "sig g ii confirming quire structure"},
    115: {"page": 102, "woodcut": "Ornate candelabrum/fountain structure", "annotations": "MODERATE"},
    120: {"page": 107, "annotations": "MODERATE"},
    125: {"page": 112, "annotations": "HEAVY", "notes": "THELEMIA Logistica passage multiple hands"},
    130: {"page": 117, "annotations": "HEAVY", "notes": "Thelema hieroglyphica"},
    135: {"page": 122, "woodcut": "Circular medallion/cameo with figure", "annotations": "HEAVY"},
    140: {"page": 127, "woodcut": "Figures at portal/doorway", "annotations": "HEAVY", "alchemical": True},
    145: {"page": 132, "woodcut": "Garden scene with pergola and nymph", "annotations": "MODERATE"},
    150: {"page": 137, "annotations": "MODERATE"},
    155: {"page": 142, "annotations": "LIGHT"},
    160: {"page": 147, "annotations": "LIGHT", "notes": "sig K iii visible"},
    170: {"page": 157, "woodcut": "Triumphal procession with soldiers and flags", "annotations": "MODERATE"},
    175: {"page": 162, "woodcut": "Triumph scene PARS ANTIQVA ET POSTERIOR", "annotations": "MODERATE"},
    185: {"page": 172, "annotations": "LIGHT"},
    189: {"page": 176, "annotations": "LIGHT", "notes": "Last photo in sequence"},
}


def main():
    text_pages = {k: v for k, v in READINGS.items() if v.get("page")}
    woodcuts = {k: v for k, v in text_pages.items() if v.get("woodcut")}
    alchemical = {k: v for k, v in READINGS.items() if v.get("alchemical")}
    heavy = sum(1 for v in READINGS.values() if v.get("annotations") == "HEAVY")
    moderate = sum(1 for v in READINGS.values() if v.get("annotations") == "MODERATE")
    light = sum(1 for v in READINGS.values() if v.get("annotations") == "LIGHT")

    print(f"Total pages read: {len(READINGS)}")
    print(f"Text pages verified: {len(text_pages)}")
    print(f"Woodcuts detected: {len(woodcuts)}")
    print(f"Alchemical sites found: {len(alchemical)}")
    print(f"Annotation density: HEAVY={heavy}, MODERATE={moderate}, LIGHT={light}")
    print(f"Signature marks confirmed: a iii, c ii, c iii, g ii, K iii")

    for k, v in sorted(woodcuts.items()):
        print(f"  Woodcut photo {k} (p.{v['page']}): {v['woodcut']}")

    gt = {
        "offset": 13,
        "total_read": len(READINGS),
        "text_pages_verified": len(text_pages),
        "woodcuts_detected": len(woodcuts),
        "alchemical_sites": len(alchemical),
        "annotation_density": {"HEAVY": heavy, "MODERATE": moderate, "LIGHT": light},
        "signatures_confirmed": ["a iii", "c ii", "c iii", "g ii", "K iii"],
        "photo_range": "001-189",
        "page_range": "1-176 (38% of book)",
        "readings": {str(k): v for k, v in READINGS.items()},
    }

    out = STAGING_DIR / "bl_complete_reading.json"
    with open(out, "w") as f:
        json.dump(gt, f, indent=2)
    print(f"\nWritten to {out}")


if __name__ == "__main__":
    main()
