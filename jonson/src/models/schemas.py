"""Data models for the Ben Jonson project.

All records are plain dicts validated by the functions in validate.py.
These constants define the allowed values and required fields.
"""

ALLOWED_CATEGORIES = {"jonson_life", "alchemist_alchemy", "hypnerotomachia_jonson"}

ALLOWED_ALCHEMICAL_CATEGORIES = {
    "substances", "processes", "metals_planets", "transmutation",
    "projection", "fraud", "laboratory", "symbolic"
}

ALLOWED_LIFE_CATEGORIES = {
    "literary", "theatrical", "biographical", "religious", "political"
}

ALLOWED_RUSSELL_CATEGORIES = {
    "ownership", "signature", "hand_characteristics",
    "reading_practices", "alchemist_links", "attribution"
}

ALLOWED_EXTRACTION_METHODS = {"MANUAL", "DETERMINISTIC", "LLM_ASSISTED"}
ALLOWED_CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}

# Required fields per record type
REQUIRED_FIELDS = {
    "SourceDocument": ["source_id", "title", "filename", "md_filename", "doc_type"],
    "SourceExcerpt": ["excerpt_id", "source_id", "page_ref", "text"],
    "PlayPassage": ["passage_id", "act", "scene", "line_start", "text", "source_id"],
    "Annotation": ["annotation_id", "passage_id", "title", "explanation", "citations", "extraction_method"],
    "LifeEvent": ["event_id", "date", "date_sort", "title", "description", "category", "citations"],
    "RussellFinding": ["finding_id", "title", "description", "category", "citations"],
    "Citation": ["source_id"],
}
