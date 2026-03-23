"""Master build script for the Ben Jonson project.

Runs: ingest -> validate -> build site pages.
"""

import sys
from pathlib import Path

JONSON_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(JONSON_DIR.parent))

from jonson.src.ingest.ingest import run as ingest
from jonson.src.site.build_jonson import build_all
from jonson.src.models.validate import validate_json_file

EXPORTS = JONSON_DIR / "data" / "exports"


def validate():
    """Validate all export files."""
    validations = [
        ("life_events.json", "LifeEvent"),
        ("annotations.json", "Annotation"),
        ("russell_findings.json", "RussellFinding"),
    ]
    all_ok = True
    for filename, record_type in validations:
        filepath = EXPORTS / filename
        if not filepath.exists():
            continue
        result = validate_json_file(filepath, record_type)
        status = "OK" if result["invalid"] == 0 else "FAIL"
        print(f"  {status} {filename}: {result['valid']}/{result['total']} valid")
        if result["errors"]:
            all_ok = False
            for err in result["errors"]:
                print(f"      [{err['record_id']}] {'; '.join(err['errors'])}")
    return all_ok


def main():
    print("=== INGEST ===")
    ingest()

    print("\n=== VALIDATE ===")
    if not validate():
        print("\nValidation failed. Fix errors before building.")
        sys.exit(1)

    print("\n=== BUILD SITE ===")
    build_all()

    print("\nDone.")


if __name__ == "__main__":
    main()
