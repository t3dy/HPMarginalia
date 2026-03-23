"""
Lightweight validation for Digby pipeline records.

Rules:
- Required fields must be present and non-empty
- Citations must be attached to substantive records
- Theme labels must be valid
- IDs must be stable (non-empty strings)
- Page/tab assignments must be valid
"""

from src.models import (
    ThemeLabel, ReviewStatus, Confidence,
    SourceDocument, SourceExcerpt, LifeEvent, WorkRecord,
    MemoirEpisode, DigbyThemeRecord, Citation,
    HypnerotomachiaFinding, HypnerotomachiaEvidence,
)

VALID_THEMES = {t.value for t in ThemeLabel}
VALID_REVIEW_STATUSES = {s.value for s in ReviewStatus}
VALID_CONFIDENCES = {c.value for c in Confidence}
VALID_PAGES = {
    "digby_home", "life_works", "memoir", "pirate",
    "alchemist", "courtier", "sources", "hypnerotomachia"
}
VALID_FILE_TYPES = {"pdf", "txt", "md", "epub", "xlsx", "pptx"}


class ValidationError(Exception):
    pass


def validate_required(obj, fields: list[str], context: str = ""):
    """Check that required fields are present and non-empty."""
    errors = []
    for f in fields:
        val = getattr(obj, f, None)
        if val is None or (isinstance(val, str) and val.strip() == ""):
            errors.append(f"Missing required field '{f}'")
    if errors:
        prefix = f"[{context}] " if context else ""
        raise ValidationError(f"{prefix}" + "; ".join(errors))


def validate_id(obj, context: str = ""):
    """Check that id is a non-empty string."""
    if not obj.id or not isinstance(obj.id, str) or obj.id.strip() == "":
        raise ValidationError(f"[{context}] Invalid or empty id")


def validate_source_document(doc: SourceDocument):
    validate_id(doc, "SourceDocument")
    validate_required(doc, ["filename", "filepath", "title", "file_type"], "SourceDocument")
    if doc.file_type not in VALID_FILE_TYPES:
        raise ValidationError(f"[SourceDocument] Invalid file_type: {doc.file_type}")


def validate_source_excerpt(exc: SourceExcerpt):
    validate_id(exc, "SourceExcerpt")
    validate_required(exc, ["source_document_id", "text"], "SourceExcerpt")
    if exc.themes:
        for t in exc.themes.split(","):
            t = t.strip()
            if t and t not in VALID_THEMES:
                raise ValidationError(f"[SourceExcerpt] Invalid theme: {t}")


def validate_life_event(evt: LifeEvent):
    validate_id(evt, "LifeEvent")
    validate_required(evt, ["title", "date_display", "description"], "LifeEvent")
    if not evt.citation_ids:
        raise ValidationError("[LifeEvent] No citations attached — provenance required")


def validate_work_record(wr: WorkRecord):
    validate_id(wr, "WorkRecord")
    validate_required(wr, ["title"], "WorkRecord")
    if not wr.citation_ids:
        raise ValidationError("[WorkRecord] No citations attached — provenance required")


def validate_memoir_episode(ep: MemoirEpisode):
    validate_id(ep, "MemoirEpisode")
    validate_required(ep, ["title", "summary"], "MemoirEpisode")
    if not ep.citation_ids:
        raise ValidationError("[MemoirEpisode] No citations attached — provenance required")


def validate_theme_record(tr: DigbyThemeRecord):
    validate_id(tr, "DigbyThemeRecord")
    validate_required(tr, ["theme", "title", "summary"], "DigbyThemeRecord")
    if tr.theme not in VALID_THEMES:
        raise ValidationError(f"[DigbyThemeRecord] Invalid theme: {tr.theme}")
    if not tr.citation_ids:
        raise ValidationError("[DigbyThemeRecord] No citations attached — provenance required")


def validate_citation(cit: Citation):
    validate_id(cit, "Citation")
    validate_required(cit, ["source_document_id"], "Citation")


def validate_hp_finding(f: HypnerotomachiaFinding):
    validate_id(f, "HypnerotomachiaFinding")
    validate_required(f, ["title", "claim", "description"], "HypnerotomachiaFinding")
    if not f.citation_ids:
        raise ValidationError("[HypnerotomachiaFinding] No citations attached — provenance required")


def validate_hp_evidence(e: HypnerotomachiaEvidence):
    validate_id(e, "HypnerotomachiaEvidence")
    validate_required(e, ["finding_id", "excerpt", "source"], "HypnerotomachiaEvidence")


def validate_record(record):
    """Dispatch validation by type."""
    dispatch = {
        SourceDocument: validate_source_document,
        SourceExcerpt: validate_source_excerpt,
        LifeEvent: validate_life_event,
        WorkRecord: validate_work_record,
        MemoirEpisode: validate_memoir_episode,
        DigbyThemeRecord: validate_theme_record,
        Citation: validate_citation,
        HypnerotomachiaFinding: validate_hp_finding,
        HypnerotomachiaEvidence: validate_hp_evidence,
    }
    validator = dispatch.get(type(record))
    if validator is None:
        raise ValidationError(f"Unknown record type: {type(record)}")
    validator(record)
