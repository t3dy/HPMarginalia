"""Validate all export JSON files against schemas."""

import sys
from pathlib import Path

# Add project root to path
JONSON_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(JONSON_DIR.parent))

from jonson.src.models.validate import validate_json_file

EXPORTS = JONSON_DIR / "data" / "exports"

VALIDATIONS = [
    ("life_events.json", "LifeEvent"),
    ("annotations.json", "Annotation"),
    ("russell_findings.json", "RussellFinding"),
]


def main():
    all_ok = True
    for filename, record_type in VALIDATIONS:
        filepath = EXPORTS / filename
        if not filepath.exists():
            print(f"SKIP  {filename} (not found)")
            continue

        result = validate_json_file(filepath, record_type)
        status = "OK" if result["invalid"] == 0 else "FAIL"
        print(f"{status:5s} {filename}: {result['valid']}/{result['total']} valid")

        if result["errors"]:
            all_ok = False
            for err in result["errors"]:
                print(f"      [{err['record_id']}] {'; '.join(err['errors'])}")

    sources = JONSON_DIR / "data" / "raw" / "sources.json"
    if sources.exists():
        result = validate_json_file(sources, "SourceDocument")
        status = "OK" if result["invalid"] == 0 else "FAIL"
        print(f"{status:5s} sources.json: {result['valid']}/{result['total']} valid")
        if result["errors"]:
            all_ok = False
            for err in result["errors"]:
                print(f"      [{err['record_id']}] {'; '.join(err['errors'])}")

    print()
    if all_ok:
        print("All records valid.")
    else:
        print("Validation errors found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
