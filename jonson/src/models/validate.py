"""Validation utilities for Ben Jonson project records."""

import json
from pathlib import Path
from .schemas import (
    REQUIRED_FIELDS, ALLOWED_CATEGORIES, ALLOWED_ALCHEMICAL_CATEGORIES,
    ALLOWED_LIFE_CATEGORIES, ALLOWED_RUSSELL_CATEGORIES,
    ALLOWED_EXTRACTION_METHODS, ALLOWED_CONFIDENCE
)


def validate_record(record: dict, record_type: str) -> list[str]:
    """Validate a single record. Returns list of error strings (empty = valid)."""
    errors = []
    required = REQUIRED_FIELDS.get(record_type, [])

    for field in required:
        if field not in record or record[field] is None or record[field] == "":
            errors.append(f"Missing required field: {field}")

    # Type-specific validation
    if record_type == "SourceExcerpt" and "categories" in record:
        for cat in record["categories"]:
            if cat not in ALLOWED_CATEGORIES:
                errors.append(f"Invalid category: {cat}")

    if record_type == "Annotation":
        if "alchemical_category" in record and record["alchemical_category"]:
            if record["alchemical_category"] not in ALLOWED_ALCHEMICAL_CATEGORIES:
                errors.append(f"Invalid alchemical_category: {record['alchemical_category']}")
        if "extraction_method" in record:
            if record["extraction_method"] not in ALLOWED_EXTRACTION_METHODS:
                errors.append(f"Invalid extraction_method: {record['extraction_method']}")
        if "citations" in record:
            for cit in record["citations"]:
                cit_errors = validate_record(cit, "Citation")
                errors.extend(cit_errors)

    if record_type == "LifeEvent":
        if "category" in record and record["category"] not in ALLOWED_LIFE_CATEGORIES:
            errors.append(f"Invalid life category: {record['category']}")
        if "citations" in record:
            for cit in record["citations"]:
                cit_errors = validate_record(cit, "Citation")
                errors.extend(cit_errors)

    if record_type == "RussellFinding":
        if "category" in record and record["category"] not in ALLOWED_RUSSELL_CATEGORIES:
            errors.append(f"Invalid russell category: {record['category']}")
        if "citations" in record:
            for cit in record["citations"]:
                cit_errors = validate_record(cit, "Citation")
                errors.extend(cit_errors)

    if record_type in ("Annotation", "LifeEvent", "RussellFinding"):
        if "confidence" in record and record["confidence"]:
            if record["confidence"] not in ALLOWED_CONFIDENCE:
                errors.append(f"Invalid confidence: {record['confidence']}")

    return errors


def validate_json_file(filepath: Path, record_type: str) -> dict:
    """Validate all records in a JSON file. Returns summary."""
    with open(filepath, 'r', encoding='utf-8') as f:
        records = json.load(f)

    results = {"total": len(records), "valid": 0, "invalid": 0, "errors": []}
    for i, record in enumerate(records):
        errors = validate_record(record, record_type)
        if errors:
            results["invalid"] += 1
            results["errors"].append({"index": i, "record_id": record.get("source_id") or record.get("event_id") or record.get("finding_id") or record.get("annotation_id") or str(i), "errors": errors})
        else:
            results["valid"] += 1

    return results
