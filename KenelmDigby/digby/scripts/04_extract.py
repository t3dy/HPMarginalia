"""
Stage 4: Extract structured records from classified excerpts.

This is a semi-manual stage. For the seed phase, it provides
utility functions for creating records with proper validation
and citation linkage. Future phases may add automated extraction.
"""

import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.models import (
    LifeEvent, WorkRecord, MemoirEpisode, DigbyThemeRecord,
    Citation, HypnerotomachiaFinding, HypnerotomachiaEvidence,
    make_id, SourceMethod, ReviewStatus, Confidence
)
from src.validate import (
    validate_life_event, validate_work_record, validate_memoir_episode,
    validate_theme_record, validate_citation, validate_hp_finding,
    validate_hp_evidence
)
from src.db import init_db, insert_record


def create_citation(source_doc_id: str, page_or_location: str = None,
                    quote_fragment: str = None, context: str = None) -> str:
    """Create a citation and return its id."""
    cit = Citation(
        id=make_id("cit"),
        source_document_id=source_doc_id,
        page_or_location=page_or_location,
        quote_fragment=quote_fragment,
        context=context,
        created_at=datetime.now().isoformat(),
    )
    validate_citation(cit)
    insert_record("citations", cit.to_dict())
    return cit.id


def create_life_event(title: str, date_display: str, description: str,
                      citation_ids: str, **kwargs) -> str:
    """Create a life event and return its id."""
    evt = LifeEvent(
        id=make_id("evt"),
        title=title,
        date_display=date_display,
        description=description,
        citation_ids=citation_ids,
        **kwargs
    )
    validate_life_event(evt)
    insert_record("life_events", evt.to_dict())
    return evt.id


def create_work_record(title: str, citation_ids: str, **kwargs) -> str:
    """Create a work record and return its id."""
    wr = WorkRecord(
        id=make_id("wrk"),
        title=title,
        citation_ids=citation_ids,
        **kwargs
    )
    validate_work_record(wr)
    insert_record("work_records", wr.to_dict())
    return wr.id


def create_memoir_episode(title: str, summary: str, citation_ids: str,
                          **kwargs) -> str:
    """Create a memoir episode and return its id."""
    ep = MemoirEpisode(
        id=make_id("mem"),
        title=title,
        summary=summary,
        citation_ids=citation_ids,
        **kwargs
    )
    validate_memoir_episode(ep)
    insert_record("memoir_episodes", ep.to_dict())
    return ep.id


def create_theme_record(theme: str, title: str, summary: str,
                        citation_ids: str, **kwargs) -> str:
    """Create a theme record and return its id."""
    tr = DigbyThemeRecord(
        id=make_id("thm"),
        theme=theme,
        title=title,
        summary=summary,
        citation_ids=citation_ids,
        **kwargs
    )
    validate_theme_record(tr)
    insert_record("digby_theme_records", tr.to_dict())
    return tr.id


def create_hp_finding(title: str, claim: str, description: str,
                      citation_ids: str, **kwargs) -> str:
    """Create a Hypnerotomachia finding and return its id."""
    f = HypnerotomachiaFinding(
        id=make_id("hpf"),
        title=title,
        claim=claim,
        description=description,
        citation_ids=citation_ids,
        **kwargs
    )
    validate_hp_finding(f)
    insert_record("hypnerotomachia_findings", f.to_dict())
    return f.id


def create_hp_evidence(finding_id: str, excerpt: str, source: str,
                       **kwargs) -> str:
    """Create HP evidence and return its id."""
    e = HypnerotomachiaEvidence(
        id=make_id("hpe"),
        finding_id=finding_id,
        excerpt=excerpt,
        source=source,
        **kwargs
    )
    validate_hp_evidence(e)
    insert_record("hypnerotomachia_evidence", e.to_dict())
    return e.id


if __name__ == "__main__":
    print("Stage 4 provides extraction utilities.")
    print("Use seed_vertical_slice.py for the initial data seed.")
