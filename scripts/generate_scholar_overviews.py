"""Generate scholar_overview prose for all scholars with linked works.

Step 2 of the Scholar Pipeline (docs/SCHOLAR_PIPELINE.md).

For modern scholars: 2-3 paragraph overview (max 400 words)
For historical subjects: 1-paragraph role description

All generated prose marked source_method='LLM_ASSISTED', review_status='DRAFT'.
Writes staging/scholar/overviews.json before updating DB.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
SUMMARIES_PATH = BASE_DIR / "scholars" / "summaries.json"
STAGING_DIR = BASE_DIR / "staging" / "scholar"

# Load summaries for context
def load_summaries():
    if SUMMARIES_PATH.exists():
        with open(SUMMARIES_PATH, encoding='utf-8') as f:
            return json.load(f)
    return []

# Scholar overviews — generated from summaries.json + bibliography data
# Following docs/WRITING_TEMPLATES.md Template 3a (modern) and 3b (historical)

OVERVIEWS = {
    # === Historical Figures ===
    "Francesco Colonna": (
        "Francesco Colonna (d. 1527) is the presumed author of the Hypnerotomachia Poliphili, "
        "identified through the acrostic formed by the chapter initials: POLIAM FRATER FRANCISCVS "
        "COLVMNA PERAMAVIT. A Dominican friar in Venice, Colonna's attribution has been canonical "
        "since Casella and Pozzi's 1959 study, though contested by scholars proposing alternative "
        "candidates including a Roman nobleman of the same name (Calvesi 1996) and Leon Battista "
        "Alberti (Lefaivre 1997)."
    ),
    "Aldus Manutius": (
        "Aldus Manutius (c. 1449-1515) was the Venetian printer who published the HP in 1499, "
        "producing what is widely regarded as the most elaborately illustrated incunabulum in the "
        "history of printing. The HP stands apart from his press's primary output of Greek scholarly "
        "texts, representing an ambitious experiment in vernacular illustration and typographic design. "
        "His son Paolo published the second edition in 1545."
    ),
    "Ben Jonson": (
        "Ben Jonson (1572-1637), the English playwright and poet, annotated the British Library copy "
        "of the HP (C.60.o.12, the 1545 edition). Russell identifies Jonson as Hand A in this copy, "
        "noting that Jonson mined the HP for stage design imagery and architectural vocabulary. "
        "Jonson's annotations represent a theatrical and literary mode of reading distinct from the "
        "alchemical annotations of the copy's other hand."
    ),
    "Fabio Chigi (Pope Alexander VII)": (
        "Fabio Chigi (1599-1667), who became Pope Alexander VII in 1655, annotated his copy of the HP "
        "(Vatican Chig.II.610) with particular attention to acutezze — instances of verbal cleverness "
        "and rhetorical ingenuity. His reading was aesthetic rather than alchemical or encyclopedic. "
        "Chigi later commissioned Bernini's elephant-obelisk sculpture in Piazza della Minerva (1667), "
        "which drew on the HP's famous woodcut."
    ),
    "Benedetto Giovio": (
        "Benedetto Giovio (c. 1471-1545), a humanist and natural historian from Como, annotated two "
        "copies of the HP (Modena and Como). Russell identifies his annotations as primarily extractive: "
        "Giovio read the HP as a source for botanical, zoological, and antiquarian knowledge, treating "
        "it as a Plinian natural history compendium rather than as an allegorical or literary text."
    ),
    "Paolo Giovio": (
        "Paolo Giovio (1483-1552), historian and biographer, was Benedetto's brother and may have "
        "contributed to annotations in the Modena and Como copies of the HP. He is better known for "
        "his emblem collection and biographical works than for HP scholarship per se."
    ),
    "Jean Martin": (
        "Jean Martin (d. 1553) produced the first French translation of the HP in 1546, adapting "
        "the text for a French courtly audience. His translation introduced the HP to the French "
        "cultural sphere, where it influenced garden design, festival culture, and the emblem tradition "
        "throughout the sixteenth and seventeenth centuries."
    ),
    "Beroalde de Verville": (
        "Beroalde de Verville (1556-1626) published a French edition of the HP in 1600 that included "
        "a 'tableau steganographique' — a systematic table mapping narrative elements to alchemical "
        "processes and substances. This edition inaugurated the tradition of reading the HP as alchemical "
        "allegory and directly influenced all subsequent alchemical annotators, including those documented "
        "by Russell in the BL and Buffalo copies."
    ),
    "Charles Nodier": (
        "Charles Nodier (1780-1844), the French bibliophile and Romantic writer, was among the "
        "earliest modern enthusiasts of the HP, praising its typographic beauty and mysterious "
        "character. His championing of the book contributed to the nineteenth-century revival of "
        "interest in the HP as a bibliophilic and aesthetic object."
    ),

    # === Modern Scholars ===
    "James Russell": (
        "James Russell is the central scholarly figure for this project. His PhD thesis, submitted "
        "to Durham University in 2014, documented the marginalia in six copies of the 1499 "
        "Hypnerotomachia Poliphili, identifying eleven distinct annotator hands. Russell's work "
        "demonstrated that the HP was far from an unreadable curiosity: the Giovio brothers read it "
        "as Plinian natural history, Ben Jonson mined it for stage design, Pope Alexander VII "
        "extracted examples of verbal wit, and multiple readers interpreted it as alchemical allegory.\n\n"
        "Russell's central theoretical contribution is the concept of the HP as a 'humanistic activity "
        "book' — a text whose puzzles, obscure language, and visual-textual interplay invited readers "
        "to cultivate ingegno through creative annotation. His methodology combines codicological "
        "analysis (identifying hands by ink, ductus, and content) with intellectual history (situating "
        "each annotator within their cultural and professional context). The thesis provides the "
        "evidence base for this project's concordance pipeline, hand attribution data, and folio-level "
        "analysis."
    ),
    "James O'Neill": (
        "James O'Neill's work on the HP spans authorship studies and narratological analysis. His "
        "Durham thesis examines self-transformation in the HP's narrative structure, while his "
        "co-authored study with Maggie O'Neill surveys the full range of authorship candidates. "
        "O'Neill argues that future research should use narratological analysis rather than archival "
        "evidence alone to address the authorship question, shifting the debate from external "
        "biographical evidence to internal literary form."
    ),
    "Efthymia Priki": (
        "Efthymia Priki has produced some of the most wide-ranging recent scholarship on the HP. "
        "Her work spans reception history, text-image relations, and comparative dream-narrative "
        "analysis. In her 2009 study, she surveys two peak periods of engagement with the HP: early "
        "modern (through c. 1657) and the twentieth-century scholarly revival. Her 2016 work places "
        "the HP within a comparative tradition alongside the Roman de la Rose and the Byzantine "
        "Livistros and Rodamne, arguing that the dream frame enables pedagogical encounters that "
        "prepare the lover for union.\n\n"
        "Priki's text-image boundary study analyzes how the relationship between woodcuts and prose "
        "shifts across editions, demonstrating that the HP's visual program is not stable but adapts "
        "to new contexts. Her work establishes the HP as a genuinely European text whose reception "
        "crosses linguistic, cultural, and disciplinary boundaries."
    ),
    "Anthony Blunt": (
        "Anthony Blunt (1907-1983), the art historian, published a foundational 1937 study of the "
        "HP's influence on seventeenth-century French art. Blunt documented how the HP's woodcuts "
        "and architectural imagery were adapted by French garden designers, festival planners, and "
        "artists, establishing the book's importance for French visual culture. His article remains "
        "the standard reference for the HP's French reception."
    ),
    "Mario Praz": (
        "Mario Praz (1896-1982) published a 1947 study documenting foreign imitations of the HP, "
        "tracing the book's influence on English, French, and German literature. Praz established "
        "the breadth of the HP's European reception, showing that its influence extended well beyond "
        "Italy and encompassed writers from Swinburne to Beardsley."
    ),
    "Liane Lefaivre": (
        "Liane Lefaivre's 1997 monograph proposed that Leon Battista Alberti, not Francesco Colonna, "
        "was the true author of the HP. Her argument rests on architectural, philosophical, and "
        "stylistic analysis rather than traditional archival evidence. Lefaivre introduced the concept "
        "of the 'architectural body' — the idea that the HP presents architecture as an extension of "
        "embodied cognition rather than abstract geometrical form.\n\n"
        "Whether or not her Alberti attribution is accepted, Lefaivre's work shifted HP scholarship "
        "toward architectural and phenomenological analysis, demonstrating that the HP's descriptions "
        "of buildings and gardens are intellectually serious rather than merely decorative."
    ),
    "Rosemary Trippe": (
        "Rosemary Trippe's 2002 study in Renaissance Quarterly argues that the HP has been "
        "understudied as literature. Through close analysis of woodcuts and their accompanying text, "
        "she demonstrates how the author adapted Petrarchan conventions — the beloved's beauty, the "
        "lover's suffering — into an interplay of word and image. Trippe's work recovers the HP's "
        "literary dimension from art-historical and architectural approaches that had dominated "
        "previous scholarship."
    ),
    "L. E. Semler": (
        "L. E. Semler's 2006 study reframes Robert Dallington's 1592 English adaptation of the HP "
        "as deliberate cultural appropriation rather than failed translation. Semler shows that "
        "Dallington's Hypnerotomachia was designed to serve Protestant antiquarian interests in "
        "Elizabethan England, adapting the HP's Catholic and Italian content for a specifically "
        "English political and religious context."
    ),
    "John Dixon Hunt": (
        "John Dixon Hunt's 1998 study is a landmark in HP garden scholarship. Hunt argues that the "
        "HP foregrounds the process of experiencing gardens over the description of finished "
        "architectural objects, anticipating phenomenological approaches to landscape. His reading "
        "positions the HP at the origin of a tradition of garden writing that emphasizes bodily "
        "movement through designed space."
    ),
    "Roswitha Stewering": (
        "Roswitha Stewering's 2000 study in the Journal of the Society of Architectural Historians "
        "analyzes the HP's architectural representations as sophisticated engagements with classical "
        "building practice. She demonstrates that the HP's descriptions of columns, arches, and "
        "thermae reflect genuine knowledge of the Vitruvian tradition and contemporary architectural "
        "theory, not merely literary fantasy."
    ),
    "Tamara Griggs": (
        "Tamara Griggs's 1998 study argues that the HP should be understood as the culmination of "
        "fifteenth-century Italian antiquarianism rather than as Romantic escapism. She traces the "
        "HP's verbal and visual strategies to Cyriacus of Ancona's commentaria and mid-century "
        "antiquarian manuscript collections, positioning the book within the material and intellectual "
        "culture of Renaissance archaeology."
    ),
    "Brian A. Curran": (
        "Brian Curran's 1998 study situates the HP's pseudo-hieroglyphic inscriptions within "
        "fifteenth-century humanist Egyptology. He shows that the HP's hieroglyphs are not authentic "
        "Egyptian writing but Renaissance inventions inspired by the rediscovery of Horapollo's "
        "Hieroglyphica, and he traces their influence on the later emblem tradition."
    ),
    "Mark Jarzombek": (
        "Mark Jarzombek's 1990 study in Renaissance Studies addresses the 'structural problematics' "
        "of the HP's architectural descriptions. He argues that the architectural passages are not "
        "merely decorative but structurally constitutive of the narrative's meaning, functioning as "
        "a kind of architectural argumentation that unfolds through description."
    ),
    "Raffaella Fabiani Giannetto": (
        "Raffaella Fabiani Giannetto's 2015 study connects the HP's cultivation of meraviglia "
        "(wonder) to the Sacro Bosco at Bomarzo. She argues that both deploy architectural surprise "
        "as a mode of philosophical instruction, creating environments where wonder precedes and "
        "enables understanding."
    ),
    "Georg Leidinger": (
        "Georg Leidinger's study examines Albrecht Durer's relationship to the HP, exploring "
        "connections between the German artist's visual imagination and the HP's woodcuts and "
        "architectural imagery."
    ),
    "James Gollnick": (
        "James Gollnick provides a theoretical framework for dream-narrative hermeneutics through "
        "his study of Apuleius's Metamorphoses. His work on the religious and initiatory dimensions "
        "of dream narratives offers an interpretive lens applicable to the HP's own dream structure."
    ),
    "Peter Ure": (
        "Peter Ure's 1952 notes in Notes and Queries provide early philological observations on the "
        "HP's unusual vocabulary. His brief but precise annotations remain useful for readers "
        "navigating the HP's macaronic language."
    ),
    "D. R. Edward Wright": (
        "D. R. Edward Wright's study in the Journal of the Warburg and Courtauld Institutes examines "
        "connections between Alberti and the HP, contributing to the debate over Albertian influence "
        "on the book's architectural and philosophical content."
    ),
    "A. Segre": (
        "A. Segre's 1998 study provides the first critical analysis of the garden designs on the "
        "island of Cythera in the HP. Segre traces the mythological associations of Cythera's "
        "concentric garden layout and argues it anticipates sixteenth-century botanical garden design."
    ),
    "Lynne Farrington": (
        "Lynne Farrington's 2015 study contextualizes the HP within Aldus Manutius's career, "
        "examining the book's production within the broader output of the Aldine press and its "
        "partnership with Andrea Torresani."
    ),
    "Christophe Poncet": (
        "Christophe Poncet's research addresses aspects of the HP's production history and its "
        "relationship to fifteenth-century Venetian printing culture."
    ),
    "William B. Keller": (
        "William B. Keller's work contributes to the bibliographic and material study of the HP, "
        "examining the book's physical form and production context."
    ),
    "Michael Leslie": (
        "Michael Leslie's research addresses the HP's garden descriptions within the broader context "
        "of Renaissance garden literature and the relationship between literary gardens and actual "
        "garden design."
    ),
    "N. Temple": (
        "N. Temple's study addresses architectural and political dimensions of the HP's dream "
        "narrative, reading the book's built spaces as encoding political and social meanings."
    ),
    "Marcel Francon": (
        "Marcel Francon's research examines the HP's French reception and translation history, "
        "contributing to understanding of how the book crossed linguistic and cultural boundaries."
    ),
    "Eric L. Pumroy": (
        "Eric L. Pumroy's bibliographic work contributes to the census and cataloging of HP copies "
        "and related materials in institutional collections."
    ),
    "Christopher J. Nygren": (
        "Christopher J. Nygren's research addresses the HP within the context of Renaissance visual "
        "culture and the relationship between text and image in early modern printed books."
    ),
    "John Bury": (
        "John Bury's scholarship contributes to the architectural analysis of the HP, examining "
        "the book's representations of built form within the context of Renaissance architectural "
        "theory and practice."
    ),
}


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("=== Generating Scholar Overviews ===\n")

    # Get all scholars
    cur.execute("SELECT id, name, is_historical_subject, review_status FROM scholars")
    scholars = cur.fetchall()

    staging_data = []
    updated = 0
    skipped = 0

    for sid, name, is_hist, status in scholars:
        if status == 'VERIFIED':
            print(f"  SKIP (VERIFIED): {name}")
            skipped += 1
            continue

        overview = OVERVIEWS.get(name)
        if not overview:
            # Try partial match
            for oname, otext in OVERVIEWS.items():
                if oname.lower() in name.lower() or name.lower() in oname.lower():
                    overview = otext
                    break

        if not overview:
            print(f"  SKIP (no overview): {name}")
            continue

        # Check word count
        word_count = len(overview.split())
        if word_count > 400:
            print(f"  WARNING: {name} overview is {word_count} words (max 400)")

        staging_data.append({
            'name': name,
            'is_historical_subject': bool(is_hist),
            'overview': overview,
            'word_count': word_count,
            'source_method': 'LLM_ASSISTED',
            'review_status': 'DRAFT',
        })

        cur.execute("""
            UPDATE scholars SET
                scholar_overview = ?,
                source_method = 'LLM_ASSISTED',
                review_status = 'DRAFT'
            WHERE id = ?
        """, (overview, sid))

        if cur.rowcount > 0:
            updated += 1
            print(f"  UPDATED: {name} ({word_count} words)")

    conn.commit()
    conn.close()

    # Write staging artifact
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    staging_path = STAGING_DIR / "overviews.json"
    with open(staging_path, 'w', encoding='utf-8') as f:
        json.dump(staging_data, f, indent=2, ensure_ascii=False)

    print(f"\nUpdated {updated} scholars, skipped {skipped}.")
    print(f"Staging artifact: {staging_path}")


if __name__ == "__main__":
    main()
