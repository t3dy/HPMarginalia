"""
Data models for the Kenelm Digby digital humanities module.

Nine record types supporting biography, memoir, thematic showcases,
Hypnerotomachia research, and source provenance.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List
from enum import Enum
import json
import uuid
from datetime import datetime


# --- Enums ---

class ThemeLabel(str, Enum):
    BIOGRAPHY = "biography"
    MEMOIR = "memoir"
    PIRATE = "pirate"
    ALCHEMIST_NATURAL_PHILOSOPHER = "alchemist_natural_philosopher"
    COURTIER_LEGAL_THINKER = "courtier_legal_thinker"
    WORKS = "works"
    BIBLIOGRAPHY = "bibliography"
    HYPNEROTOMACHIA_DIGBY = "hypnerotomachia_digby"


class ReviewStatus(str, Enum):
    DRAFT = "DRAFT"
    REVIEWED = "REVIEWED"
    VERIFIED = "VERIFIED"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SourceMethod(str, Enum):
    DETERMINISTIC = "DETERMINISTIC"
    CORPUS_EXTRACTION = "CORPUS_EXTRACTION"
    LLM_ASSISTED = "LLM_ASSISTED"
    HUMAN_VERIFIED = "HUMAN_VERIFIED"


# --- Utility ---

def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# --- Core Models ---

@dataclass
class SourceDocument:
    """A PDF, text file, or other source in the Digby corpus."""
    id: str
    filename: str
    filepath: str
    title: str
    file_type: str  # pdf, txt, md, epub, xlsx, pptx
    author: Optional[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    page_count: Optional[int] = None
    text_extracted: bool = False
    extracted_text_path: Optional[str] = None
    ingested_at: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class SourceExcerpt:
    """An excerpt from a source document with page reference."""
    id: str
    source_document_id: str
    text: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    section_heading: Optional[str] = None
    themes: Optional[str] = None  # comma-separated ThemeLabel values
    source_method: str = SourceMethod.CORPUS_EXTRACTION.value
    review_status: str = ReviewStatus.DRAFT.value
    created_at: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class LifeEvent:
    """A structured event in Digby's life."""
    id: str
    title: str
    date_display: str  # human-readable date string
    year: Optional[int] = None
    description: str = ""
    life_phase: Optional[str] = None  # e.g. "youth", "voyage", "exile", "restoration"
    location: Optional[str] = None
    people_involved: Optional[str] = None  # comma-separated
    citation_ids: Optional[str] = None  # comma-separated Citation ids
    source_method: str = SourceMethod.CORPUS_EXTRACTION.value
    review_status: str = ReviewStatus.DRAFT.value
    confidence: str = Confidence.MEDIUM.value

    def to_dict(self):
        return asdict(self)


@dataclass
class WorkRecord:
    """A work by or closely associated with Digby."""
    id: str
    title: str
    year: Optional[int] = None
    work_type: Optional[str] = None  # treatise, memoir, recipe_book, letter, poem
    subject: Optional[str] = None
    description: str = ""
    significance: Optional[str] = None
    citation_ids: Optional[str] = None
    source_method: str = SourceMethod.CORPUS_EXTRACTION.value
    review_status: str = ReviewStatus.DRAFT.value

    def to_dict(self):
        return asdict(self)


@dataclass
class MemoirEpisode:
    """A structured unit for summarizing Digby's memoir."""
    id: str
    title: str
    episode_number: Optional[int] = None
    date_display: Optional[str] = None
    year: Optional[int] = None
    summary: str = ""
    key_events: Optional[str] = None  # comma-separated
    people: Optional[str] = None  # comma-separated
    places: Optional[str] = None  # comma-separated
    themes: Optional[str] = None  # comma-separated
    citation_ids: Optional[str] = None
    source_method: str = SourceMethod.CORPUS_EXTRACTION.value
    review_status: str = ReviewStatus.DRAFT.value

    def to_dict(self):
        return asdict(self)


@dataclass
class DigbyThemeRecord:
    """A thematic record for pirate, alchemist, or courtier showcases."""
    id: str
    theme: str  # ThemeLabel value (pirate, alchemist_natural_philosopher, courtier_legal_thinker)
    title: str
    summary: str = ""
    key_details: Optional[str] = None
    people: Optional[str] = None
    places: Optional[str] = None
    date_display: Optional[str] = None
    year: Optional[int] = None
    significance: Optional[str] = None
    citation_ids: Optional[str] = None
    source_method: str = SourceMethod.CORPUS_EXTRACTION.value
    review_status: str = ReviewStatus.DRAFT.value
    confidence: str = Confidence.MEDIUM.value

    def to_dict(self):
        return asdict(self)


@dataclass
class Citation:
    """Provenance record tying claims to source materials."""
    id: str
    source_document_id: str
    excerpt_id: Optional[str] = None
    page_or_location: Optional[str] = None
    quote_fragment: Optional[str] = None  # short identifying fragment
    context: Optional[str] = None  # what this citation supports
    created_at: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class HypnerotomachiaFinding:
    """A structured finding about Digby's connection to the Hypnerotomachia."""
    id: str
    title: str
    claim: str
    description: str = ""
    evidence_excerpt: Optional[str] = None
    related_concepts: Optional[str] = None  # comma-separated (e.g. "Jupiter/Tin, Mercury")
    significance: Optional[str] = None
    citation_ids: Optional[str] = None
    source_method: str = SourceMethod.CORPUS_EXTRACTION.value
    review_status: str = ReviewStatus.DRAFT.value
    confidence: str = Confidence.MEDIUM.value

    def to_dict(self):
        return asdict(self)


@dataclass
class HypnerotomachiaEvidence:
    """Supporting evidence for a Hypnerotomachia finding."""
    id: str
    finding_id: str
    excerpt: str
    source: str  # source document title or reference
    page_or_location: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self):
        return asdict(self)
