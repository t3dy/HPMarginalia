"""
Expand Hypnerotomachia findings based on Russell/O'Neill PPTX research.

All findings grounded in the slide content from:
'The HP of Ben Jonson and Kenelm Digby' by Dr. James O'Neill and Dr. James Russell
"""

import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.db import init_db, insert_record, get_connection
from src.models import (
    Citation, HypnerotomachiaFinding, HypnerotomachiaEvidence,
    make_id, Confidence
)
from src.validate import validate_record


def expand_hp():
    init_db()
    conn = get_connection()
    existing = {r["id"] for r in conn.execute("SELECT id FROM hypnerotomachia_findings").fetchall()}
    existing_ev = {r["id"] for r in conn.execute("SELECT id FROM hypnerotomachia_evidence").fetchall()}
    existing_cits = {r["id"] for r in conn.execute("SELECT id FROM citations").fetchall()}
    conn.close()

    # Additional citations for HP section
    new_cits = [
        Citation(id="cit_russell_slide25", source_document_id="sdoc_russell_pptx",
                 page_or_location="Slide 25",
                 context="Attribution arguments: proximity to Jonson, handwriting, Chymical Secrets parallels"),
        Citation(id="cit_russell_slide32", source_document_id="sdoc_russell_pptx",
                 page_or_location="Slides 32-36",
                 context="Jupiter/Tin parallels between marginalia and Chymical Secrets"),
        Citation(id="cit_russell_slide37", source_document_id="sdoc_russell_pptx",
                 page_or_location="Slides 37-41",
                 context="Le Fevre influence, Universal Spirit, Mercury as master element"),
        Citation(id="cit_russell_slide42", source_document_id="sdoc_russell_pptx",
                 page_or_location="Slides 42-43",
                 context="Thomas Bourne hand, dating, book provenance"),
        Citation(id="cit_russell_slide44", source_document_id="sdoc_russell_pptx",
                 page_or_location="Slide 44",
                 context="Significance of the attribution"),
        Citation(id="cit_russell_slide21", source_document_id="sdoc_russell_pptx",
                 page_or_location="Slides 20-24",
                 context="Characteristics of the alchemical hand"),
        Citation(id="cit_russell_slide28", source_document_id="sdoc_russell_pptx",
                 page_or_location="Slides 28-31",
                 context="Handwriting analysis"),
        Citation(id="cit_dobbs_1973", source_document_id="sdoc_dobbs_ii",
                 page_or_location="p. 156-157",
                 context="Le Fevre's influence on Digby's alchemy, Universal Spirit"),
    ]

    added_cits = 0
    for c in new_cits:
        if c.id not in existing_cits:
            c.created_at = datetime.now().isoformat()
            validate_record(c)
            insert_record("citations", c.to_dict())
            added_cits += 1
    print(f"Added {added_cits} new citations.")

    # New HP Findings
    new_findings = [
        HypnerotomachiaFinding(
            id="hpf_jupiter_tin",
            title="Jupiter/Tin Parallels: Marginalia and Chymical Secrets",
            claim="The alchemical annotator pays particular attention to Jupiter's titles in the HP, transcribing them into the flyleaf in a hierarchical scheme. Digby's posthumous Chymical Secrets (1682) contains multiple operations specifically involving Jupiter/Tin, including a cancer cure using an amalgam of Jupiter/Tin and Mercury.",
            description="Early in the HP, Poliphilo invokes Jupiter under multiple titles. The annotator transcribes these into the flyleaf as a hierarchical list with brackets: 'Maximum, optimum, omnipotentem and opitulatorem' and 'sumum patrem, supererum, medioximorum & inferum.' Digby's Chymical Secrets contains 'An Operation upon Jupiter' and a cure for cancer using Jupiter/Tin amalgamated with Mercury, demonstrating the same alchemical interest in Jupiter/Tin that the marginalia display.",
            evidence_excerpt="The annotator transcribes Jupiter's titles into the flyleaf; Chymical Secrets contains 'An Operation upon Jupiter' and a cancer cure using Jupiter/Tin and Mercury amalgam",
            related_concepts="Jupiter/Tin, Mercury, Chymical Secrets, alchemical operations, cancer cure",
            significance="This is one of the strongest content parallels between the marginalia and Digby's known works. The specific interest in Jupiter/Tin is unusual and distinctive.",
            citation_ids="cit_russell_slide32,cit_hp_alchemy",
            confidence=Confidence.MEDIUM.value,
        ),
        HypnerotomachiaFinding(
            id="hpf_mercury_master",
            title="Mercury as Master Element: Le Fevre's Influence",
            claim="The alchemical annotator writes a Latin inscription declaring the 'true intention' of the HP is a description of 'Master Mercury' — reflecting the influence of Nicholas le Fevre and Jean d'Espagnet on Digby's alchemy after 1651.",
            description="The annotator inscribes: 'verus sensus intentionis huius libri est 3um: Gen: et Totius Naturae energiae & operationum Magisteri Mercurii Descriptio elegans, ampla & ingeniossisum' ('The true intention of this book is threefold: and of the energy of all nature and the operation of Master Mercury, a description elegant, full and most ingenious'). This reflects Digby's post-1651 alchemical framework, learned from Le Fevre in Paris, which identified Mercury with the universal spirit and gold with aethereal spirit.",
            evidence_excerpt="Marginalia: 'Magisteri Mercurii Descriptio elegans' — Digby's 1660 Royal Society lecture: 'Gold is of the same Nature as the aethereal Spirit'",
            related_concepts="Mercury, Universal Spirit, Le Fevre, d'Espagnet, gold, aethereal spirit",
            significance="This inscription dates the marginalia to after 1651 (when Digby studied with Le Fevre) and connects them to Digby's mature alchemical philosophy as presented to the Royal Society.",
            citation_ids="cit_russell_slide37,cit_dobbs_1973",
            confidence=Confidence.MEDIUM.value,
        ),
        HypnerotomachiaFinding(
            id="hpf_three_hands",
            title="Three Annotating Hands in BL C.60.o.12",
            claim="Russell and O'Neill identify three distinct annotating hands in the British Library copy of the 1545 HP: Ben Jonson's hand (in brown ink and pencil), the alchemical hand (attributed to Digby, in black ink and pencil), and Thomas Bourne's hand (dated 1641).",
            description="The copy (BL C.60.o.12) bears Jonson's signature ('sum Ben: Ionsonii') and motto ('tanquam explorator'). Jonson's annotations focus on syntax, sentence structure, and circling specific words. The alchemical hand overwrites both Jonson's and Bourne's annotations, reads the HP as alchemical allegory, uses idiosyncratic alchemical abbreviations not found in standard lists, and annotates both images and margins. Bourne's hand is dated 1641.",
            evidence_excerpt="Three hands: Jonson (signature, syntax focus), Alchemical (overwrites others, allegorical reading), Bourne (1641 date)",
            related_concepts="BL C.60.o.12, 1545 Aldine edition, paleography, marginal annotation",
            significance="Establishing three distinct hands is the foundation of the attribution argument. That the alchemical hand overwrites the others establishes chronological sequence.",
            citation_ids="cit_russell_slide21,cit_hp_russell",
            confidence=Confidence.HIGH.value,
        ),
        HypnerotomachiaFinding(
            id="hpf_attribution_args",
            title="Three Arguments for Attributing the Alchemical Hand to Digby",
            claim="Russell and O'Neill present three main arguments for the Digby attribution: (1) Digby's proximity to Jonson as his friend and literary executor, (2) handwriting comparison with known Digby manuscripts, and (3) parallels between the marginalia's alchemical concepts and Digby's Chymical Secrets (1682).",
            description="First, Digby and Jonson were close from 1629 onward; Digby was Jonson's literary executor and received his unpublished papers. Second, handwriting comparison shows similarities between the alchemical annotations and Digby's known hand (including matching numerals). Third, the alchemical content — particularly Jupiter/Tin operations and Mercury as master element — closely parallels Digby's documented experiments and theories. Additionally, one annotation in English ('Frogg Green') suggests an English annotator, and the purchase price inscription matches Digby's hand rather than Bourne's.",
            evidence_excerpt="Proximity to Jonson; handwriting comparison; Chymical Secrets parallels; English inscription 'Frogg Green'",
            related_concepts="literary executor, paleography, Chymical Secrets, friendship with Jonson",
            significance="The convergence of provenance, paleography, and content analysis provides a cumulative case for the attribution, though each strand individually is suggestive rather than conclusive.",
            citation_ids="cit_russell_slide25,cit_russell_slide28,cit_russell_slide32",
            confidence=Confidence.MEDIUM.value,
        ),
        HypnerotomachiaFinding(
            id="hpf_book_provenance",
            title="Book Provenance: Jonson to Bourne to Digby",
            claim="The book's provenance chain runs from Jonson through the bookseller Thomas Bourne (a recusant recorded joining the Stationer's Company in 1623) to Digby, likely purchased around 1641. The purchase price inscription matches Digby's hand.",
            description="Thomas Bourne, a recusant bookseller, annotated the book in 1641. Both Digby and Jonson were (sometime) Catholics, and Bourne was a recusant — a shared confessional network. There is no 'ex dono' from Jonson to Digby (unlike other books they exchanged). The purchase price numerals match Digby's handwriting. If Digby bought the book in 1641, he likely had it during his imprisonment at Winchester House in 1642, when he was conducting alchemical experiments. The book later entered Hans Sloane's collections and thence the British Museum/Library.",
            evidence_excerpt="Bourne dated 1641; purchase price matches Digby's hand; recusant book trade network; no ex dono inscription",
            related_concepts="Thomas Bourne, Stationer's Company, recusant networks, Winchester House, Hans Sloane",
            significance="Establishes a plausible transmission path and dates Digby's acquisition to around 1641, with alchemical annotation likely post-1651 based on content.",
            citation_ids="cit_russell_slide42",
            confidence=Confidence.MEDIUM.value,
        ),
    ]

    # New HP Evidence
    new_evidence = [
        HypnerotomachiaEvidence(
            id="hpe_chymical_jupiter",
            finding_id="hpf_jupiter_tin",
            excerpt="Chymical Secrets: 'An Operation upon Jupiter — Distill a Menstruum out of Vitriol and sal ammoniac, with which make Sulphur naturae Iovis.' The alchemical annotator similarly transcribes Jupiter's titles from the HP into the flyleaf in a hierarchical scheme.",
            source="Russell/O'Neill PPTX, Slides 32-36; Chymical Secrets (1682), p. 106",
            page_or_location="PPTX Slide 35",
            notes="Both the marginalia and Chymical Secrets show specific interest in Jupiter/Tin — an unusual focus that supports the attribution.",
        ),
        HypnerotomachiaEvidence(
            id="hpe_mercury_inscription",
            finding_id="hpf_mercury_master",
            excerpt="Marginalia inscription: 'verus sensus intentionis huius libri est...Magisteri Mercurii Descriptio elegans, ampla & ingeniossisum.' Digby's 1660 Royal Society lecture: 'Gold is of the same Nature as the aethereal Spirit; or rather, it is nothing but it, first corporify'd in a pure place.'",
            source="Russell/O'Neill PPTX, Slides 37-40; Dobbs (1973), p. 157",
            page_or_location="PPTX Slide 39",
            notes="The Mercury-as-master-element concept links the marginalia to Digby's post-1651 alchemy via Le Fevre and d'Espagnet.",
        ),
        HypnerotomachiaEvidence(
            id="hpe_panton_tokadi",
            finding_id="hpf_mercury_master",
            excerpt="The annotator renders 'Panton Tokadi' as 'rerum omnium vas' ('The vessel of all things') rather than Jonson's 'The mother of all things.' Adjacent notes read 'calor naturae' and 'nam in Humore.' This reflects d'Espagnet's concept of the universal spirit associated with the water cycle.",
            source="Russell/O'Neill PPTX, Slide 41",
            page_or_location="PPTX Slide 41",
            notes="The shift from 'mother' to 'vessel' reflects an alchemical reading focused on containment and transformation.",
        ),
        HypnerotomachiaEvidence(
            id="hpe_handwriting_match",
            finding_id="hpf_attribution_args",
            excerpt="Handwriting analysis shows the purchase price inscription numerals (specifically the '5' and '6') match Digby's hand rather than Bourne's. One inscription in English ('Frogg Green') labels a heptagonal fountain, suggesting an English annotator.",
            source="Russell/O'Neill PPTX, Slides 28-31, 43",
            page_or_location="PPTX Slides 28-31",
            notes="Paleographic evidence is suggestive but not conclusive on its own; strongest when combined with content parallels.",
        ),
        HypnerotomachiaEvidence(
            id="hpe_significance",
            finding_id="hpf_attribution_args",
            excerpt="Russell/O'Neill identify five areas of significance: (1) adds a major body of text to Digby's corpus, (2) illuminates the Jonson-Digby relationship, (3) informs about post-1651 alchemical work in Paris, (4) validates alchemical readings proposed in the 1600 edition and Carl Jung's Psychology and Alchemy, (5) provides a basis for comparison with other alchemically annotated HP copies.",
            source="Russell/O'Neill PPTX, Slide 44",
            page_or_location="PPTX Slide 44",
            notes="The attribution, if accepted, significantly expands our understanding of Digby's intellectual practices.",
        ),
    ]

    added_findings = 0
    for f in new_findings:
        if f.id not in existing:
            validate_record(f)
            insert_record("hypnerotomachia_findings", f.to_dict())
            added_findings += 1
    print(f"Added {added_findings} new HP findings.")

    added_ev = 0
    for e in new_evidence:
        if e.id not in existing_ev:
            validate_record(e)
            insert_record("hypnerotomachia_evidence", e.to_dict())
            added_ev += 1
    print(f"Added {added_ev} new HP evidence records.")

    # Summary
    conn = get_connection()
    for t in ["hypnerotomachia_findings", "hypnerotomachia_evidence", "citations"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {count} records")
    conn.close()


if __name__ == "__main__":
    expand_hp()
