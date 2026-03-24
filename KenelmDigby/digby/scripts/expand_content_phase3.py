"""
Phase 3 Content Expansion: HP & Digby page and Life & Works page.

Expands the Hypnerotomachia page (~3,200 -> ~10,000 words) and the
Life & Works page (~5,200 -> ~12,000 words) by adding PageSections
for narrative prose and updating existing findings/events with longer
descriptions.

All claims grounded in source materials:
- Russell/O'Neill PPTX (sdoc_russell_pptx)
- Moshenska biography (sdoc_moshenska)
- Dobbs alchemy articles (sdoc_dobbs_ii)
- Georgescu philosophy (sdoc_georgescu)
- Miles overview (sdoc_miles)
- Mellick biographical summary (sdoc_mellick)
"""

import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.db import init_db, insert_record, get_connection
from src.models import (
    HypnerotomachiaFinding, HypnerotomachiaEvidence, LifeEvent,
    WorkRecord, PageSection, Citation, Confidence, SourceMethod, ReviewStatus
)
from src.validate import validate_record


def expand_phase3():
    init_db()

    # Check existing records
    conn = get_connection()
    existing_sections = {r["id"] for r in conn.execute("SELECT id FROM page_sections").fetchall()}
    existing_cits = {r["id"] for r in conn.execute("SELECT id FROM citations").fetchall()}
    existing_findings = {r["id"] for r in conn.execute("SELECT id FROM hypnerotomachia_findings").fetchall()}
    existing_events = {r["id"] for r in conn.execute("SELECT id FROM life_events").fetchall()}
    conn.close()

    # =========================================================================
    # CITATIONS
    # =========================================================================
    new_citations = [
        Citation(
            id="cit_hp_intro_russell",
            source_document_id="sdoc_russell_pptx",
            page_or_location="Slides 1-10",
            context="Introduction to the HP, the BL copy, Jonson's ownership, three hands",
        ),
        Citation(
            id="cit_hp_methodology_russell",
            source_document_id="sdoc_russell_pptx",
            page_or_location="Slides 11-24",
            context="Methodology for distinguishing three annotating hands",
        ),
        Citation(
            id="cit_hp_implications_russell",
            source_document_id="sdoc_russell_pptx",
            page_or_location="Slide 44",
            context="Significance of the Digby attribution for scholarship",
        ),
        Citation(
            id="cit_life_intro_moshenska",
            source_document_id="sdoc_moshenska",
            page_or_location="passim",
            context="Biographical overview framing Digby's life",
        ),
        Citation(
            id="cit_life_intro_miles",
            source_document_id="sdoc_miles",
            page_or_location="passim",
            context="Overview of Digby's career and accomplishments",
        ),
        Citation(
            id="cit_life_phase_youth_moshenska",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapter 1",
            context="Youth phase: Gayhurst, father's execution, Venetia, Napier",
        ),
        Citation(
            id="cit_life_phase_tour_moshenska",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapter 2",
            context="Grand Tour phase: Florence, Siena, Madrid",
        ),
        Citation(
            id="cit_life_phase_voyage_moshenska",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapters 4-8",
            context="Voyage phase: Mediterranean expedition 1628-1629",
        ),
        Citation(
            id="cit_life_phase_exile_miles",
            source_document_id="sdoc_miles",
            page_or_location="passim",
            context="Exile phase: Paris, Civil War, alchemy, Royal Society",
        ),
        Citation(
            id="cit_life_works_intro",
            source_document_id="sdoc_georgescu",
            page_or_location="passim",
            context="Overview of Digby's major published works",
        ),
    ]

    added_cits = 0
    for c in new_citations:
        if c.id not in existing_cits:
            c.created_at = datetime.now().isoformat()
            validate_record(c)
            insert_record("citations", c.to_dict())
            added_cits += 1
    print(f"Added {added_cits} new citations.")

    # =========================================================================
    # HP & DIGBY PAGE — PAGE SECTIONS
    # =========================================================================

    hp_sections = [
        PageSection(
            id="sec_hp_intro",
            page="hypnerotomachia",
            section_key="intro",
            title="The Hypnerotomachia Poliphili and the Alchemical Reader",
            position=0,
            body=(
                "The Hypnerotomachia Poliphili, first published in Venice in 1499 by Aldus Manutius, "
                "is one of the most enigmatic and visually stunning books of the Renaissance. Written "
                "in an extraordinary hybrid language blending Italian, Latin, Greek, Hebrew, and Arabic, "
                "the text follows its protagonist Poliphilo through a dreamscape of classical ruins, "
                "elaborate gardens, mysterious processions, and alchemical transformations. The woodcuts "
                "that accompany the narrative — depicting triumphal arches, hieroglyphic inscriptions, "
                "architectural fantasies, and mythological scenes — have captivated readers for over "
                "five centuries. The authorship of the work is traditionally attributed to the Dominican "
                "friar Francesco Colonna, though this attribution remains contested. What is beyond "
                "dispute is the book's extraordinary influence on architecture, garden design, typography, "
                "and esoteric thought across early modern Europe.\n\n"
                "Among the surviving copies of the Hypnerotomachia, one stands apart for the density "
                "and significance of its marginal annotations. British Library shelfmark C.60.o.12 is a "
                "copy of the 1545 Aldine reprint that bears the ownership inscription of Ben Jonson — "
                "England's foremost dramatist and poet laureate — in his characteristic hand: 'sum Ben: "
                "Ionsonii', accompanied by his personal motto 'tanquam explorator' ('as an explorer'). "
                "Jonson was a voracious reader and prolific annotator whose marginalia survive in dozens "
                "of books, providing invaluable evidence of his reading practices and intellectual "
                "preoccupations. But the Jonson copy of the Hypnerotomachia contains far more than "
                "Jonson's own notes. Research by Dr James Russell and Dr James O'Neill has identified "
                "three distinct annotating hands in the volume, each representing a different reader "
                "and a different mode of engagement with Colonna's text.\n\n"
                "The first hand is Jonson's own, recognizable from his signature, his characteristic "
                "brown ink, and his focus on syntax, sentence structure, and circling individual words "
                "for later reference. The second hand belongs to Thomas Bourne, a recusant bookseller "
                "recorded as joining the Stationers' Company in 1623, whose annotations include a date "
                "of 1641. The third hand — the most extensive and intellectually ambitious of the three "
                "— reads the entire Hypnerotomachia as alchemical allegory. This 'alchemical hand' "
                "writes in black ink and pencil, uses idiosyncratic alchemical abbreviations not found "
                "in standard reference works, annotates both text and images, and crucially overwrites "
                "both Jonson's and Bourne's annotations, establishing that this reader came last in the "
                "chronological sequence.\n\n"
                "Russell and O'Neill's research program argues that this alchemical annotator was Sir "
                "Kenelm Digby (1603-1665) — philosopher, naval commander, alchemist, and close friend "
                "of Ben Jonson. The attribution rests on three converging lines of evidence: Digby's "
                "proximity to Jonson as his friend and literary executor; handwriting comparison between "
                "the annotations and Digby's known manuscripts; and striking conceptual parallels between "
                "the marginalia's alchemical framework and Digby's documented experiments and theories, "
                "particularly as recorded in his posthumous Chymical Secrets (1682). If the attribution "
                "is correct, these annotations represent an extraordinary window into Digby's alchemical "
                "reading practices and his engagement with one of the Renaissance's most mysterious texts."
            ),
            citation_ids="cit_hp_intro_russell,cit_hp_russell",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_hp_methodology",
            page="hypnerotomachia",
            section_key="methodology",
            title="Distinguishing the Three Hands",
            position=1,
            body=(
                "The foundation of Russell and O'Neill's attribution argument is the careful "
                "paleographic and intellectual distinction of three separate annotating hands in "
                "BL C.60.o.12. Each hand exhibits distinctive characteristics in ink color, writing "
                "instruments, annotation style, and intellectual focus.\n\n"
                "Ben Jonson's hand is the most readily identifiable. His annotations appear in brown "
                "ink and pencil, consistent with the materials found in his other annotated books. "
                "Jonson approaches the Hypnerotomachia primarily as a literary text: he circles "
                "individual words, marks syntactical constructions, underlines passages of interest, "
                "and occasionally provides brief marginal glosses. His focus is on language and "
                "structure rather than symbolic or allegorical content. This is characteristic of "
                "Jonson's broader reading practice, well documented across his surviving library, "
                "in which he treated books as working tools for his own literary production.\n\n"
                "Thomas Bourne's hand is dated 1641, providing a firm chronological anchor. Bourne "
                "was a recusant — a Catholic who refused to attend Church of England services — and "
                "a member of the Stationers' Company from 1623. His annotations are relatively sparse "
                "compared to the other two hands, and his primary significance lies in establishing "
                "the book's presence in the recusant book trade network through which it likely passed "
                "from Jonson's library to Digby's possession.\n\n"
                "The alchemical hand is by far the most extensive and intellectually ambitious of the "
                "three. This annotator reads the Hypnerotomachia systematically as alchemical allegory, "
                "interpreting Colonna's imagery of gardens, fountains, architectural forms, and "
                "mythological processions as encoded descriptions of alchemical processes and "
                "substances. The hand uses black ink and pencil, and employs a system of alchemical "
                "abbreviations and symbols that Russell and O'Neill have been unable to locate in any "
                "standard early modern reference work — suggesting an annotator working from a highly "
                "personal and idiosyncratic alchemical vocabulary. Crucially, the alchemical hand "
                "overwrites annotations by both Jonson and Bourne, demonstrating that this reader "
                "engaged with the book after both earlier annotators. The alchemical annotator also "
                "reads and responds to the woodcut illustrations, treating them as visual keys to the "
                "alchemical meaning of the text — an approach consistent with the broader early modern "
                "tradition of reading the Hypnerotomachia's images as hieroglyphic or symbolic systems. "
                "One annotation in English — the label 'Frogg Green' applied to a heptagonal fountain "
                "woodcut — further suggests an English-speaking annotator."
            ),
            citation_ids="cit_hp_methodology_russell,cit_russell_slide21,cit_russell_slide28",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_hp_implications",
            page="hypnerotomachia",
            section_key="implications",
            title="Significance of the Attribution",
            position=2,
            body=(
                "Russell and O'Neill identify five areas of significance should the attribution of "
                "the alchemical hand to Digby be accepted. First, it adds a substantial body of "
                "previously unknown text to Digby's intellectual corpus — hundreds of marginal notes "
                "and inscriptions that reveal his alchemical reading practices in unprecedented detail. "
                "Unlike his published philosophical works, which present polished arguments, these "
                "annotations capture Digby in the act of thinking through a text, testing alchemical "
                "interpretations against Colonna's imagery in real time.\n\n"
                "Second, the attribution illuminates the friendship between Digby and Ben Jonson. "
                "Digby became Jonson's literary executor after the poet's death in 1637 and received "
                "his unpublished papers. The Hypnerotomachia annotations show a different facet of "
                "this relationship: Digby reading and responding to a book that Jonson had previously "
                "annotated, creating a layered dialogue between two of the seventeenth century's most "
                "formidable intellects. The absence of an 'ex dono' inscription — unlike other books "
                "the pair exchanged — suggests Digby may have acquired this copy through the book "
                "trade rather than as a direct gift.\n\n"
                "Third, the content of the annotations informs our understanding of Digby's alchemical "
                "work during his Paris exile after 1651. The Mercury-as-master-element framework "
                "visible in the marginalia reflects the influence of Nicholas le Fevre and Jean "
                "d'Espagnet, with whom Digby studied alchemy in Paris. This dates the annotations "
                "to Digby's mature intellectual period and connects them to the alchemical philosophy "
                "he later presented to the Royal Society. Fourth, the annotations validate alchemical "
                "readings of the Hypnerotomachia that have been proposed since the 1600 edition and "
                "developed by scholars including Carl Jung in Psychology and Alchemy — demonstrating "
                "that at least one seventeenth-century reader with deep alchemical knowledge read the "
                "text in precisely this way. Fifth, the annotated copy provides a comparison basis "
                "for other alchemically annotated copies of the Hypnerotomachia, opening new avenues "
                "for research into early modern esoteric reading communities."
            ),
            citation_ids="cit_hp_implications_russell,cit_russell_slide44",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
    ]

    added_sections = 0
    for s in hp_sections:
        if s.id not in existing_sections:
            validate_record(s)
            insert_record("page_sections", s.to_dict())
            added_sections += 1
    print(f"Added {added_sections} HP page sections.")

    # =========================================================================
    # HP FINDINGS — UPDATE (expand descriptions to 250-400 words)
    # =========================================================================

    hp_finding_updates = {
        "hpf_alchemical_hand": {
            "description": (
                "The annotated copy of the Hypnerotomachia Poliphili (BL C.60.o.12) contains "
                "marginalia from several distinct hands. One hand is characterized by alchemical "
                "symbolic markings, Latin notes interpreting both images and text as alchemical "
                "allegory, and sustained attention to themes of transformation, transmutation, and "
                "the relationship between visible forms and hidden truths. Russell and O'Neill argue "
                "that this hand can be attributed to Sir Kenelm Digby based on three converging "
                "lines of evidence.\n\n"
                "First, Digby's historical proximity to Ben Jonson makes him one of a very small "
                "number of plausible candidates. From 1629 onward, Digby and Jonson were close "
                "friends. Digby served as Jonson's literary executor after the poet's death in 1637 "
                "and received his unpublished papers. Digby was also a renowned bibliophile whose "
                "library — later bequeathed to the Bodleian — was one of the finest private "
                "collections in England. He had both motive and opportunity to acquire Jonson's "
                "annotated copy of the Hypnerotomachia.\n\n"
                "Second, handwriting comparison reveals similarities between the alchemical "
                "annotations and Digby's known hand, particularly in the formation of numerals. "
                "The purchase price inscription on the copy matches Digby's handwriting rather than "
                "Bourne's, suggesting Digby was the purchaser. One annotation in English, the label "
                "'Frogg Green' applied to a heptagonal fountain woodcut, further indicates an "
                "English-speaking annotator with alchemical knowledge.\n\n"
                "Third, the alchemical content of the annotations closely parallels Digby's "
                "documented experiments and theories. The annotator's interest in Jupiter/Tin "
                "symbolism, the identification of Mercury as the master element, and the framework "
                "of universal spirit animating matter all correspond to positions documented in "
                "Digby's Chymical Secrets (1682), his Royal Society lectures, and the alchemical "
                "philosophy he developed under the influence of Nicholas le Fevre in Paris after "
                "1651. The cumulative weight of provenance, paleography, and content analysis "
                "provides a persuasive, if not conclusive, case for the attribution."
            ),
        },
        "hpf_intellectual_context": {
            "description": (
                "Digby's known works demonstrate a consistent and lifelong interest in how material "
                "substances interact across distances (the Powder of Sympathy), how spirit animates "
                "and transforms matter (Two Treatises of 1644), and how visible forms encode hidden "
                "philosophical truths. The alchemical annotations in the Hypnerotomachia show the "
                "same interpretive framework applied to Francesco Colonna's text and woodcuts — "
                "reading images of gardens, architectural fantasies, fountains, and mythological "
                "processions as encoded descriptions of alchemical processes.\n\n"
                "This mode of reading was not unique to Digby. The Hypnerotomachia had attracted "
                "alchemical interpretations since at least the 1600 edition, and the tradition "
                "continued through the twentieth century in Carl Jung's Psychology and Alchemy. "
                "What distinguishes the annotations in BL C.60.o.12 is their specificity and "
                "sophistication. The annotator does not simply label passages as 'alchemical' but "
                "provides detailed interpretations keyed to particular operations, substances, and "
                "theoretical frameworks. The Latin inscription identifying the 'true intention' of "
                "the book as a description of 'Master Mercury' reflects a mature and systematic "
                "alchemical philosophy, not casual marginalia.\n\n"
                "If attributable to Digby, these annotations reveal his philosophical practice in "
                "its most intimate form — not the polished arguments of published treatises but "
                "the working notes of a thinker testing ideas against a complex text. They "
                "demonstrate that Digby's natural philosophy was not compartmentalized from his "
                "literary and visual culture but was instead a unified interpretive practice. His "
                "reading of Spenser's Faerie Queene through an alchemical lens — documented in his "
                "Observations on the 22nd Stanza (1643) — provides a direct parallel: in both "
                "cases, Digby read literary texts as vehicles for alchemical and philosophical "
                "truth, finding in poetic imagery the same principles he pursued in the laboratory."
            ),
        },
        "hpf_jupiter_tin": {
            "description": (
                "Early in the Hypnerotomachia, Poliphilo invokes Jupiter under multiple classical "
                "titles. The alchemical annotator transcribes these titles into the flyleaf of the "
                "book as a hierarchical list organized with brackets: 'Maximum, optimum, "
                "omnipotentem and opitulatorem' and 'sumum patrem, supererum, medioximorum & "
                "inferum.' This careful transcription and hierarchical organization indicates an "
                "annotator who saw Jupiter not merely as a mythological figure but as an alchemical "
                "principle — the planet and metal Jupiter/Tin occupying a specific position in the "
                "hierarchy of celestial and material correspondences.\n\n"
                "Digby's posthumous Chymical Secrets (1682) contains multiple operations "
                "specifically involving Jupiter/Tin, including 'An Operation upon Jupiter' that "
                "details the distillation of a menstruum from vitriol and sal ammoniac to extract "
                "the sulphur of tin. Most striking is a recipe for a cancer cure using an amalgam "
                "of Jupiter/Tin and Mercury — a therapeutic application that connects planetary "
                "metals to medical practice in precisely the way the marginalia's hierarchical "
                "scheme implies.\n\n"
                "The specificity of this parallel is significant. Jupiter/Tin was not a major focus "
                "of most early modern alchemical writers; the dominant concerns were typically gold, "
                "silver, and mercury. An annotator who singles out Jupiter's titles for special "
                "attention and organizes them hierarchically shares an unusual preoccupation with "
                "the author of the Chymical Secrets. Russell argues this is one of the strongest "
                "content parallels between the marginalia and Digby's known works, because the "
                "interest is both specific and distinctive — not a generic alchemical concern but "
                "a particular theoretical emphasis that narrows the field of possible annotators."
            ),
        },
        "hpf_mercury_master": {
            "description": (
                "The alchemical annotator inscribes on the book a Latin declaration of the "
                "Hypnerotomachia's 'true intention': 'verus sensus intentionis huius libri est "
                "3um: Gen: et Totius Naturae energiae & operationum Magisteri Mercurii Descriptio "
                "elegans, ampla & ingeniossisum' — translated as 'The true intention of this book "
                "is threefold: and of the energy of all nature and the operation of Master Mercury, "
                "a description elegant, full and most ingenious.' This inscription represents a "
                "comprehensive hermeneutic claim: the entire Hypnerotomachia, in the annotator's "
                "reading, is fundamentally about Mercury as the master element animating all of "
                "nature.\n\n"
                "This framework reflects the specific alchemical philosophy that Digby developed "
                "after 1651 under the influence of Nicholas le Fevre, the royal chemist in Paris, "
                "and the writings of Jean d'Espagnet. Le Fevre taught that Mercury was identical "
                "with the universal spirit — the animating principle that pervades all matter — "
                "and that gold represented aethereal spirit in its most concentrated corporeal form. "
                "Digby adopted and refined this framework, presenting it to the Royal Society in "
                "January 1661 in his lecture on the vegetation of plants, where he argued that 'Gold "
                "is of the same Nature as the aethereal Spirit; or rather, it is nothing but it, "
                "first corporify'd in a pure place.'\n\n"
                "The Mercury inscription in the Hypnerotomachia thus serves a double function in "
                "the attribution argument. It provides a conceptual parallel with Digby's documented "
                "alchemical philosophy, and it establishes a terminus post quem for the annotations: "
                "since the Mercury-as-universal-spirit framework derives from le Fevre's teaching "
                "after 1651, the annotations must date from Digby's mature intellectual period, "
                "consistent with his Paris exile and the years following his return to England. "
                "The annotator also renders the Greek phrase 'Panton Tokadi' as 'rerum omnium vas' "
                "('the vessel of all things') rather than Jonson's earlier translation 'the mother "
                "of all things' — a shift toward alchemical vocabulary of containment and "
                "transformation that is characteristic of d'Espagnet's influence."
            ),
        },
        "hpf_three_hands": {
            "description": (
                "The copy of the 1545 Aldine reprint of the Hypnerotomachia Poliphili held at the "
                "British Library under shelfmark C.60.o.12 bears the ownership inscription 'sum "
                "Ben: Ionsonii' ('I belong to Ben Jonson') accompanied by Jonson's personal motto "
                "'tanquam explorator' ('as an explorer'). This signature establishes Jonson's "
                "ownership and provides a starting point for the paleographic analysis of the "
                "volume's multiple annotating hands.\n\n"
                "Russell and O'Neill's examination distinguishes three hands operating with "
                "different materials and intellectual purposes. Jonson's hand appears in brown ink "
                "and pencil, focusing on syntactical analysis, word-circling, and structural "
                "observations consistent with his documented reading practices across his surviving "
                "library. His approach to the Hypnerotomachia is literary and linguistic rather "
                "than symbolic or allegorical.\n\n"
                "The second hand belongs to Thomas Bourne, whose annotations include a date of "
                "1641. Bourne was a recusant bookseller — a member of the Catholic community who "
                "refused to attend Church of England services — and had joined the Stationers' "
                "Company in 1623. His presence in the book connects it to the recusant book trade "
                "networks through which Catholic intellectuals like Digby and Jonson (who converted "
                "to Catholicism at various points) exchanged and acquired books.\n\n"
                "The third hand — designated the 'alchemical hand' — is the most extensive and "
                "intellectually ambitious. It reads the Hypnerotomachia systematically as alchemical "
                "allegory, using black ink and pencil. This annotator employs idiosyncratic "
                "alchemical abbreviations not found in standard early modern reference compilations, "
                "annotates both text and woodcut illustrations, and crucially overwrites annotations "
                "by both Jonson and Bourne. This overwriting establishes the chronological sequence "
                "definitively: Jonson first, then Bourne in 1641, then the alchemical reader. The "
                "temporal layering of three distinct readers across a single copy of the "
                "Hypnerotomachia makes BL C.60.o.12 a uniquely rich document for studying early "
                "modern reading practices."
            ),
        },
        "hpf_attribution_args": {
            "description": (
                "Russell and O'Neill present three main arguments for attributing the alchemical "
                "hand to Digby, each drawing on different evidential methods that converge toward "
                "the same conclusion.\n\n"
                "The first argument concerns proximity and opportunity. Digby and Jonson were close "
                "friends from 1629 until Jonson's death in 1637. Digby served as Jonson's literary "
                "executor and received his unpublished papers, including the manuscript of Jonson's "
                "English Grammar. Digby was also a renowned collector whose library, later bequeathed "
                "to the Bodleian, was among the finest in England. He had both the means and the "
                "motive to acquire Jonson's annotated Hypnerotomachia, whether directly from Jonson's "
                "estate or through the recusant book trade represented by Thomas Bourne.\n\n"
                "The second argument is paleographic. Handwriting comparison reveals similarities "
                "between the alchemical annotations and Digby's known hand, particularly in the "
                "distinctive formation of certain numerals (specifically the '5' and '6'). The "
                "purchase price inscription on the volume matches Digby's handwriting rather than "
                "Bourne's, suggesting that Digby was the book's purchaser rather than merely a "
                "subsequent owner. One annotation in English, 'Frogg Green,' labeling a heptagonal "
                "fountain illustration, confirms that the annotator was an English speaker — further "
                "narrowing the field of candidates.\n\n"
                "The third argument is conceptual. The alchemical content of the marginalia closely "
                "parallels Digby's documented alchemical writings and lectures. The Jupiter/Tin "
                "operations described in the Chymical Secrets, the Mercury-as-master-element "
                "framework derived from le Fevre and d'Espagnet, and the universal spirit theory "
                "presented to the Royal Society all find direct correspondences in the annotations. "
                "While each individual strand of evidence is suggestive rather than conclusive, "
                "their convergence — provenance, paleography, and content — creates a cumulative "
                "case that significantly narrows the pool of possible annotators."
            ),
        },
        "hpf_book_provenance": {
            "description": (
                "The provenance chain of BL C.60.o.12 begins with Ben Jonson, whose ownership "
                "inscription and motto establish his possession of the volume. The book then passed "
                "through the hands of Thomas Bourne, a recusant bookseller who annotated it in "
                "1641. Bourne had joined the Stationers' Company in 1623 and operated within the "
                "network of Catholic book traders that served the recusant community in London. "
                "Both Digby and Jonson were at various times practicing Catholics, and Bourne's "
                "confessional identity places all three figures within a shared social and "
                "commercial network.\n\n"
                "Notably, there is no 'ex dono' inscription from Jonson to Digby, unlike other "
                "books that the pair exchanged as gifts. This suggests that Digby did not receive "
                "the Hypnerotomachia directly from Jonson but rather purchased it through the book "
                "trade — most likely from Bourne himself around 1641. The purchase price numerals "
                "inscribed in the volume match Digby's handwriting rather than Bourne's, supporting "
                "the identification of Digby as the buyer.\n\n"
                "If Digby acquired the book around 1641, he likely had it in his possession during "
                "his imprisonment at Winchester House in Southwark in 1642, where he was held for "
                "his Catholic loyalties during the outbreak of the Civil War. Contemporary accounts "
                "record that Digby conducted alchemical experiments during his confinement, and the "
                "Hypnerotomachia may have been among the books he studied during this period. "
                "However, the content of the alchemical annotations — particularly the Mercury-as-"
                "master-element framework — suggests the actual annotation occurred later, after "
                "1651, when Digby studied with le Fevre in Paris. The book eventually entered the "
                "collection of Sir Hans Sloane, whose vast library and curiosity cabinet formed the "
                "founding collection of the British Museum in 1753, and thence passed to the "
                "British Library where it remains today."
            ),
        },
    }

    updated_findings = 0
    conn = get_connection()
    for finding_id, updates in hp_finding_updates.items():
        if finding_id in existing_findings:
            conn.execute(
                "UPDATE hypnerotomachia_findings SET description = ? WHERE id = ?",
                (updates["description"], finding_id)
            )
            updated_findings += 1
    conn.commit()
    conn.close()
    print(f"Updated {updated_findings} HP finding descriptions.")

    # =========================================================================
    # LIFE & WORKS PAGE — PAGE SECTIONS
    # =========================================================================

    life_sections = [
        PageSection(
            id="sec_life_intro",
            page="life_works",
            section_key="intro",
            title="The Life of Sir Kenelm Digby",
            position=0,
            body=(
                "Sir Kenelm Digby (1603-1665) was one of the most remarkable and contradictory "
                "figures of seventeenth-century England. Born into a Catholic family disgraced by "
                "his father's role in the Gunpowder Plot of 1605, Digby spent his entire life "
                "seeking to redeem his family name while navigating the treacherous intersections "
                "of religion, politics, and intellectual ambition in a confessionally divided Europe. "
                "He was, as his contemporaries marveled, a man who seemed to contain multitudes: a "
                "naval commander who fought pitched battles in the Mediterranean, and a philosopher "
                "who lectured the Royal Society on the vegetation of plants; a devoted husband who "
                "wrote one of the century's most intimate autobiographical romances, and a courtier "
                "who served as chancellor to the exiled Queen Henrietta Maria; an alchemist who "
                "pursued the transmutation of metals in his Paris laboratory, and a cookbook author "
                "whose recipes for metheglin and marinated beef remain in print to this day.\n\n"
                "The Earl of Clarendon, one of the most perceptive political observers of the age, "
                "captured something of this multiplicity in his famous character sketch, describing "
                "Digby as a man of 'very extraordinary person and presence' who 'had a very fair "
                "reputation.' John Aubrey, that tireless collector of biographical curiosities, "
                "recorded Digby's physical magnificence — his immense height, his broad shoulders, "
                "his penetrating gaze — alongside the intellectual restlessness that drove him from "
                "one field of inquiry to the next. Modern biographers, building on the work of "
                "Vittorio Gabrieli, Joe Moshenska, and others, have begun to recover the full scope "
                "of a career that touched nearly every sphere of early modern life.\n\n"
                "The chronology that follows traces Digby's path from his Buckinghamshire childhood "
                "through his European Grand Tour, his celebrated Mediterranean voyage, his years of "
                "grief and exile, and his final decades as a founding member of the Royal Society. "
                "It draws primarily on Moshenska's narrative of the voyage years and on the broader "
                "biographical accounts provided by Wyndham Miles, Mellick, and the primary sources "
                "they synthesize. Each event is grounded in documented evidence, though the density "
                "of documentation varies considerably across the different phases of Digby's life."
            ),
            citation_ids="cit_life_intro_moshenska,cit_life_intro_miles",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_life_phase_youth",
            page="life_works",
            section_key="phase_youth",
            title="Youth: 1603-1620",
            position=1,
            body=(
                "The first seventeen years of Digby's life were shaped by two defining forces: the "
                "shadow of his father's treason, and the Catholic intellectual culture in which his "
                "mother Mary raised him. Born at Gayhurst in Buckinghamshire on 11 July 1603, "
                "Kenelm was barely two years old when Sir Everard Digby was hanged, drawn, and "
                "quartered for his role in the Gunpowder Plot. The trauma of his father's execution "
                "— and the annual nationwide celebrations of its anniversary on 5 November — left a "
                "permanent mark. Yet Gayhurst also provided a rich intellectual environment. Mary "
                "Digby engaged Jesuit tutors, including the polemicist John Percy (known as Fisher), "
                "and ensured her sons learned French, Italian, and the social accomplishments "
                "expected of Catholic gentry. The young Digby's encounter with Richard Napier, the "
                "physician-priest at nearby Great Linford who practiced astrology, alchemy, and "
                "herbal medicine alongside conventional healing, planted the seeds of his lifelong "
                "fascination with the occult sciences. It was also during these Buckinghamshire "
                "years that Digby first met Venetia Stanley, three years his senior, who would "
                "become the great love of his life."
            ),
            citation_ids="cit_life_phase_youth_moshenska,cit_ch1_youth",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_life_phase_grand_tour",
            page="life_works",
            section_key="phase_grand_tour",
            title="Grand Tour: 1620-1623",
            position=2,
            body=(
                "Digby's three years of European travel transformed him from a provincial Catholic "
                "youth into a cosmopolitan intellectual at ease in multiple languages and cultures. "
                "In France he encountered Marie de Medici; in Florence he immersed himself in the "
                "city's artistic and scientific culture, studying Galileo's works, attending the "
                "Accademia dei Filomati in Siena where he delivered four learned orations in fluent "
                "Italian, and acquiring rare manuscripts on geomancy and alchemical medicine. In "
                "Florence he also obtained the secret recipe for the Powder of Sympathy from a "
                "Carmelite friar returned from Persia. His time in Madrid with Prince Charles and "
                "the Duke of Buckingham during the failed Spanish Match introduced him to the world "
                "of high politics and courtly diplomacy. He returned to England in 1623 with "
                "enhanced languages, a broadened intellectual horizon, and the beginnings of an "
                "international reputation."
            ),
            citation_ids="cit_life_phase_tour_moshenska,cit_ch2_europe",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_life_phase_voyage",
            page="life_works",
            section_key="phase_voyage",
            title="The Mediterranean Voyage: 1628-1629",
            position=3,
            body=(
                "Digby's thirteen-month Mediterranean voyage of 1628-1629 was the defining episode "
                "of his early career — the event through which he sought to redeem his family name "
                "and establish himself as a figure of national significance. Sailing with a small "
                "fleet under royal commission, he overcame plague among his crew, negotiated the "
                "release of English captives in Algiers, won a celebrated naval victory over "
                "Venetian galleasses at Scanderoon (Iskenderun), collected ancient marble statues "
                "from the ruins of Apollo's temple on Delos, and composed both his autobiographical "
                "romance Loose Fantasies and his alchemical reading of Spenser's Faerie Queene "
                "while at sea. The voyage combined privateering, diplomacy, antiquarianism, and "
                "philosophical reflection in a manner that was uniquely characteristic of Digby's "
                "multifaceted ambitions."
            ),
            citation_ids="cit_life_phase_voyage_moshenska,cit_ch4_voyage_start",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_life_phase_exile",
            page="life_works",
            section_key="phase_exile",
            title="Exile, Alchemy, and the Royal Society: 1633-1665",
            position=4,
            body=(
                "The sudden death of Venetia Stanley on 1 May 1633 devastated Digby and marked a "
                "turning point in his life. He retreated into intense grief and scholarly seclusion, "
                "commissioned Van Dyck to paint Venetia on her deathbed, and increasingly devoted "
                "himself to philosophical and alchemical pursuits. The outbreak of the English Civil "
                "War forced Digby into exile in Paris, where he served as chancellor to Queen "
                "Henrietta Maria, published his major philosophical work Two Treatises (1644), and "
                "built an active alchemical laboratory. It was during these Paris years, particularly "
                "after 1651, that Digby studied with the royal chemist Nicholas le Fevre and "
                "developed the mature alchemical philosophy centered on Mercury as universal spirit "
                "that Russell identifies in the Hypnerotomachia annotations. After the Restoration "
                "in 1660, Digby returned to England and became a founding member of the Royal "
                "Society, delivering his influential lecture on the vegetation of plants at Gresham "
                "College in January 1661. He died on his sixty-second birthday, 11 June 1665, and "
                "his library — one of the finest private collections in England — was bequeathed to "
                "the Bodleian Library at Oxford."
            ),
            citation_ids="cit_life_phase_exile_miles,cit_miles_overview,cit_mellick_bio",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_life_works_intro",
            page="life_works",
            section_key="works_intro",
            title="Digby's Major Works",
            position=10,
            body=(
                "Digby's published output spans philosophy, theology, literary criticism, cookery, "
                "and natural history — a range that reflects the extraordinary breadth of his "
                "intellectual interests and the refusal to compartmentalize that characterized his "
                "entire career. His most ambitious philosophical work, Two Treatises: Of Bodies and "
                "Of Man's Soul (Paris, 1644), attempted to reconcile Catholic theology with the "
                "emerging corpuscular philosophy, arguing for the immortality of the soul on natural "
                "philosophical grounds. His Observations on the 22nd Stanza of the 9th Canto of "
                "Spenser's Faerie Queene (1643), first drafted aboard ship during his Mediterranean "
                "voyage, reads a single stanza through the combined lenses of alchemy, astrology, "
                "and Christian angelology — demonstrating the same interpretive method visible in "
                "the Hypnerotomachia marginalia, should the attribution hold.\n\n"
                "His Discourse Concerning the Vegetation of Plants (1661), delivered to the Royal "
                "Society, represents his mature alchemical philosophy in its most accessible form, "
                "arguing for the universal spirit as the animating principle of all growth. The "
                "posthumously published Chymical Secrets (1682) preserves his laboratory recipes "
                "and alchemical operations, including the Jupiter/Tin procedures that parallel the "
                "Hypnerotomachia annotations. His Closet Opened (1669), a cookbook compiled from "
                "his lifelong culinary experiments, remains in print as a vivid record of "
                "seventeenth-century English and Continental cooking. The autobiographical Loose "
                "Fantasies, composed during the Mediterranean voyage and published posthumously, "
                "and his Journal of the voyage itself complete a body of work that ranges from the "
                "most abstract metaphysics to the most practical kitchen craft."
            ),
            citation_ids="cit_life_works_intro,cit_miles_overview",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
    ]

    added_life_sections = 0
    for s in life_sections:
        if s.id not in existing_sections:
            validate_record(s)
            insert_record("page_sections", s.to_dict())
            added_life_sections += 1
    print(f"Added {added_life_sections} Life & Works page sections.")

    # =========================================================================
    # LIFE EVENTS — UPDATE (expand descriptions to 100-200 words)
    # =========================================================================

    life_event_updates = {
        "evt_birth": (
            "Kenelm Digby was born at Gayhurst in Buckinghamshire on 11 July 1603, the elder "
            "son of Sir Everard Digby and Mary Mulshaw. He entered the world during the final "
            "months of Elizabeth I's long reign — she had died in March — and his birth coincided "
            "with the accession of James I, under whose rule the religious tensions that would "
            "shape Digby's entire life intensified dramatically. The Digby family was Catholic "
            "gentry, prosperous enough to maintain the elegant three-storey house at Gayhurst that "
            "Everard had completed with characteristic gusto. Within two and a half years, the "
            "Gunpowder Plot would shatter this comfortable existence and cast a shadow over "
            "Kenelm's childhood and career. He grew to resemble his father strikingly in both "
            "physique and temperament — a resemblance that was at once a source of pride and an "
            "inescapable reminder of the family's disgrace."
        ),
        "evt_father_executed": (
            "Sir Everard Digby was hanged, drawn, and quartered at St Paul's churchyard on "
            "20 January 1606 for his role in the Gunpowder Plot. He was dragged through streets "
            "lined with hostile crowds to the gallows, where he maintained a composure that "
            "astonished even his judges. At his trial he had impressed the court with his bearing, "
            "arriving in black satin and a taffeta gown, and delivering an impassioned plea that "
            "his wife and infant sons not be punished for his crime. At the scaffold he greeted "
            "onlookers as if departing for the country. The executioner cut open his chest while "
            "he was still conscious and ripped out his heart, proclaiming it a traitor's heart. "
            "According to family lore, the infant Kenelm — barely two years old and miles away at "
            "Gayhurst — leapt from his nurse's knee and cried out at the exact moment of his "
            "father's death. The annual 5 November celebrations commemorating the foiling of the "
            "Plot ensured that the trauma of Everard's treason was renewed every year of Kenelm's life."
        ),
        "evt_meets_venetia": (
            "The young Kenelm met Venetia Stanley through the visits between their Catholic "
            "families in Buckinghamshire. Venetia, three years his senior, had been sent to live "
            "with her relatives Francis and Grace Fortescue after her mother's death. Both families "
            "were recusant Catholics, and the pious Grace Fortescue and Mary Digby visited each "
            "other frequently, allowing the two young people to meet. Kenelm was captivated by "
            "Venetia's beauty — her dark hair and pale skin with a small mole on her cheek — but "
            "came to admire her intelligence, composure, and sharp judgment of character even more "
            "deeply. Their first kiss occurred secretly during a hunting expedition near Gayhurst, "
            "sheltered beneath a tree during a rainstorm. Kenelm's mother opposed the match because "
            "Venetia, despite her noble Percy and Stanley bloodlines, was extremely poor — her "
            "father had squandered the family fortune. Kenelm never relinquished his attachment, "
            "and the relationship that began in these Buckinghamshire fields would define the rest of his life."
        ),
        "evt_grand_tour": (
            "Digby's three-year Grand Tour through France, Italy, and Spain transformed him from "
            "a provincial English Catholic into a cosmopolitan intellectual. In France he had "
            "already survived a dramatic episode at Angers (rumors of his death circulated), and "
            "he encountered Marie de Medici at the French court. Arriving in Florence around late "
            "1620, he immersed himself in the city's artistic and intellectual life, studying "
            "Galileo's astronomical works, purchasing rare manuscripts including a geomancy treatise "
            "and an illuminated Petrarch, and experimenting with Italian cuisine. At Siena he was "
            "admitted to the Accademia dei Filomati under the name 'Il Fiorito' and delivered four "
            "orations in Italian on subjects ranging from the mysteries of language to the soul's "
            "habitation of the body. A Florentine Carmelite friar confided to him the secret of the "
            "Powder of Sympathy. In Madrid he joined Prince Charles and the Duke of Buckingham "
            "during the failed Spanish Match, entering the world of high politics. He returned to "
            "England in late 1623 with perfected languages, a network of European contacts, and "
            "intellectual ambitions that would occupy the rest of his career."
        ),
        "evt_marriage_venetia": (
            "Digby secretly married Venetia Stanley in January 1625, just months before the death "
            "of King James. The marriage was kept private for pressing practical reasons: Kenelm's "
            "mother Mary still opposed the match because of Venetia's poverty, while Venetia's "
            "father Sir Edward Stanley was attempting to settle an inheritance on her that he might "
            "withhold if he knew she was already married. The secret became increasingly difficult "
            "to maintain when Venetia fell pregnant almost immediately. Plans for a discreet lying-in "
            "were disrupted when she fell from her horse the day before her planned departure, "
            "spraining her leg and triggering premature labor. Kenelm stayed with her throughout "
            "the delivery — unusual for an English husband at the time, though common on the "
            "Continent — and their first son, also named Kenelm, was born on 6 October 1625. "
            "The marriage remained a secret from the broader public, though close associates like "
            "the Earl of Bristol eventually guessed the truth."
        ),
        "evt_voyage_depart": (
            "Digby departed England from the port of Deal aboard his flagship the Eagle on "
            "7 January 1628, accompanied by the Elizabeth and George and approximately 250 crewmen. "
            "He sailed under a royal commission authorizing him to attack French and Spanish "
            "shipping in the Mediterranean. The preparations had been fraught: the Duke of "
            "Buckingham, who bore a deep personal animus against anyone named Digby, had actively "
            "sought to obstruct the expedition. Digby had spent months negotiating ship purchases, "
            "recruiting sailors scarred by the recent disastrous expeditions to Cadiz and the Ile "
            "de Re, and stockpiling provisions. His determination to set sail was driven by multiple "
            "motives: the desire to redeem his family name through martial glory, the hope of "
            "enriching himself through prizes, and the urge to escape the damaging rumors about "
            "himself and Venetia that circulated in London. The voyage would keep him at sea for "
            "thirteen months and take him across the entire Mediterranean."
        ),
        "evt_scanderoon": (
            "On 11 June 1628 — Digby's twenty-fifth birthday — his fleet engaged Venetian "
            "galleasses and merchant ships in the Bay of Scanderoon (modern Iskenderun, Turkey). "
            "The battle was the decisive military event of his voyage. Digby's smaller but more "
            "maneuverable English ships used their superior gunnery to defeat the larger Venetian "
            "vessels, winning a victory that brought him immediate fame. However, the aftermath "
            "proved deeply complicated. English merchants resident in Aleppo were imprisoned by "
            "Ottoman authorities in retaliation, and the Venetians launched a coordinated propaganda "
            "campaign across their Mediterranean outposts, branding Digby as a pirate. Even English "
            "diplomats like Sir Thomas Roe, the ambassador at Constantinople, complained about the "
            "disruption to trade. The battle exemplified the ambiguity of early modern privateering: "
            "what was heroic martial achievement to one audience was piracy to another, and Digby's "
            "Catholic identity amplified Protestant suspicion of his motives."
        ),
        "evt_venetia_death": (
            "Venetia Stanley died suddenly in her sleep on 1 May 1633, devastating Kenelm and "
            "transforming the trajectory of his remaining life. The cause of death was uncertain; "
            "some contemporaries whispered that a cosmetic preparation — 'viper wine' intended to "
            "preserve her fading beauty — may have been responsible, though no evidence supports "
            "this gossip. Digby's grief was profound and performative in equal measure. He "
            "commissioned Anthony van Dyck to paint Venetia on her deathbed, producing one of the "
            "most haunting portraits of the seventeenth century. He retreated into scholarly "
            "seclusion, growing a long beard and wearing mourning clothes for years. The woman he "
            "had loved since adolescence, defended against a decade of cruel gossip, and celebrated "
            "in his autobiographical romance was gone. Her death channeled Digby's energies "
            "decisively away from the active life of court and combat and toward the philosophical "
            "and alchemical pursuits that would occupy his remaining decades. It was the pivotal "
            "event between the swashbuckling young adventurer of the Mediterranean voyage and the "
            "philosophical old man of the Royal Society."
        ),
        "evt_paris_exile": (
            "Digby spent much of the 1640s and 1650s in exile in Paris, driven from England by "
            "the Civil War and his Catholic loyalties. He had been imprisoned at Winchester House "
            "in Southwark in 1642, where he conducted alchemical experiments during his confinement. "
            "After his release he crossed to France and joined the exiled royalist court, becoming "
            "chancellor to Queen Henrietta Maria. Paris provided Digby with an intellectual milieu "
            "that suited his temperament perfectly. He published his major philosophical work, Two "
            "Treatises (1644), engaged with the leading natural philosophers of the Continent, and "
            "built an active alchemical laboratory. Most significantly for the Hypnerotomachia "
            "research, it was during the Paris years — particularly after 1651 — that Digby studied "
            "with Nicholas le Fevre, the royal chemist, and absorbed the alchemical framework "
            "centered on Mercury as universal spirit that Russell identifies in the HP annotations. "
            "He also read and was influenced by Jean d'Espagnet's alchemical writings. These "
            "Parisian intellectual experiences shaped the mature philosophical positions that Digby "
            "would present to the Royal Society after the Restoration."
        ),
        "evt_royal_society": (
            "After the Restoration of Charles II in 1660, Digby returned to England and became "
            "a founding member of the Royal Society, the institution that would define the new "
            "experimental philosophy for centuries. His election reflected both his genuine "
            "intellectual standing — he had been pursuing natural philosophy for four decades — and "
            "his social prominence as a Catholic aristocrat with connections to the restored court. "
            "On 23 January 1661, Digby delivered his influential Discourse Concerning the Vegetation "
            "of Plants at Gresham College, in which he argued that a universal spirit permeated all "
            "matter and was responsible for the growth and transformation of living things. This "
            "lecture articulated the alchemical philosophy he had developed under le Fevre's "
            "influence in Paris, presenting it in a form compatible with the Society's commitment "
            "to experimental method. His claim that 'Gold is of the same Nature as the aethereal "
            "Spirit' connected his alchemical theories to the broader project of understanding "
            "material transformation that the early Royal Society pursued."
        ),
        "evt_death": (
            "Sir Kenelm Digby died in London on 11 June 1665, his sixty-second birthday — the "
            "same date on which he had fought the Battle of Scanderoon thirty-seven years earlier. "
            "He was buried at Christ Church, Newgate Street. In his will he bequeathed his library "
            "to the Bodleian Library at Oxford, where it remains one of the most significant "
            "named collections. The Bibliotheca Digbeiana, a catalogue of his books published "
            "posthumously in 1680, documents the extraordinary range of his reading: theology, "
            "natural philosophy, alchemy, medicine, history, poetry, and cookery. His death came "
            "just as the Great Plague was beginning to devastate London — a final instance of the "
            "dramatic historical coincidences that seemed to punctuate his life. Among the works "
            "published posthumously were his Chymical Secrets (1682), whose Jupiter/Tin operations "
            "provide key evidence for the attribution of the Hypnerotomachia annotations, and The "
            "Closet Opened (1669), the cookbook that has kept his name familiar to a readership far "
            "beyond the world of seventeenth-century intellectual history."
        ),
    }

    updated_events = 0
    conn = get_connection()
    for event_id, new_desc in life_event_updates.items():
        if event_id in existing_events:
            conn.execute(
                "UPDATE life_events SET description = ? WHERE id = ?",
                (new_desc, event_id)
            )
            updated_events += 1
    conn.commit()
    conn.close()
    print(f"Updated {updated_events} life event descriptions.")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    conn = get_connection()
    print("\n--- Phase 3 Content Expansion Summary ---")
    for t in ["page_sections", "hypnerotomachia_findings", "hypnerotomachia_evidence",
              "life_events", "work_records", "citations"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {count} records")

    # Word count estimates
    print("\n--- Word Count Estimates ---")
    hp_sections_words = 0
    for row in conn.execute("SELECT body FROM page_sections WHERE page = 'hypnerotomachia'").fetchall():
        hp_sections_words += len(row["body"].split())
    hp_findings_words = 0
    for row in conn.execute("SELECT description, claim, significance FROM hypnerotomachia_findings").fetchall():
        for field in ["description", "claim", "significance"]:
            if row[field]:
                hp_findings_words += len(row[field].split())
    print(f"  HP page sections: ~{hp_sections_words} words")
    print(f"  HP findings (desc+claim+sig): ~{hp_findings_words} words")
    print(f"  HP page total estimate: ~{hp_sections_words + hp_findings_words} words")

    life_sections_words = 0
    for row in conn.execute("SELECT body FROM page_sections WHERE page = 'life_works'").fetchall():
        life_sections_words += len(row["body"].split())
    life_events_words = 0
    for row in conn.execute("SELECT description FROM life_events").fetchall():
        if row["description"]:
            life_events_words += len(row["description"].split())
    works_words = 0
    for row in conn.execute("SELECT description, significance FROM work_records").fetchall():
        for field in ["description", "significance"]:
            if row[field]:
                works_words += len(row[field].split())
    print(f"  Life sections: ~{life_sections_words} words")
    print(f"  Life events (descriptions): ~{life_events_words} words")
    print(f"  Works (desc+sig): ~{works_words} words")
    print(f"  Life & Works page total estimate: ~{life_sections_words + life_events_words + works_words} words")

    conn.close()


if __name__ == "__main__":
    expand_phase3()
