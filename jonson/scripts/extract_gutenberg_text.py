"""Extract the clean Alchemist text from Gutenberg into structured JSON.

Splits on ACT/SCENE boundaries, extracts speaker names and dialogue.
"""

import json
import re
from pathlib import Path

JONSON_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = JONSON_DIR.parent
GUTENBERG = BASE_DIR / "Ben Jonson Life" / "gutenberg_alchemist.txt"
OUTPUT = JONSON_DIR / "data" / "exports" / "alchemist_text.json"


def extract_text():
    """Extract structured play text from Gutenberg file."""
    text = GUTENBERG.read_text(encoding='utf-8')

    # Find start of play proper (after introduction)
    start_marker = "ACT 1. SCENE 1.1."
    start_idx = text.find(start_marker)
    if start_idx == -1:
        print("ERROR: Could not find start of play")
        return

    # Find end of play (before Gutenberg footer)
    end_marker = "*** END OF THE PROJECT GUTENBERG"
    end_idx = text.find(end_marker)
    if end_idx == -1:
        end_idx = len(text)

    play_text = text[start_idx:end_idx].strip()

    # Also extract the introduction for life events
    intro_text = text[:start_idx].strip()

    # Split into scenes
    scene_pattern = r'(?:ACT (\d+)\. )?SCENE (\d+)\.(\d+)\.'
    parts = re.split(r'((?:ACT \d+\. )?SCENE \d+\.\d+\.)', play_text)

    scenes = []
    current_act = 0
    i = 0
    while i < len(parts):
        part = parts[i].strip()
        m = re.match(scene_pattern, part)
        if m:
            if m.group(1):
                current_act = int(m.group(1))
            scene_num = int(m.group(3))
            # Next part is the scene content
            if i + 1 < len(parts):
                content = parts[i + 1].strip()
                scenes.append({
                    "act": current_act,
                    "scene": scene_num,
                    "header": part,
                    "text": content,
                    "line_count": len(content.split('\n'))
                })
                i += 2
            else:
                i += 1
        else:
            i += 1

    # Write structured output
    output = {
        "source": "Project Gutenberg EBook #4081",
        "license": "Public domain in the United States",
        "total_scenes": len(scenes),
        "total_acts": max(s["act"] for s in scenes) if scenes else 0,
        "scenes": scenes,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(scenes)} scenes from Gutenberg text")
    for sc in scenes:
        print(f"  Act {sc['act']}, Scene {sc['scene']}: {sc['line_count']} lines")

    # Also save the introduction as a separate excerpt for life events
    intro_path = JONSON_DIR / "data" / "processed" / "gutenberg_intro.txt"
    intro_path.write_text(intro_text, encoding='utf-8')
    print(f"\nSaved Gutenberg introduction ({len(intro_text)} chars) for life event extraction")


if __name__ == "__main__":
    extract_text()
