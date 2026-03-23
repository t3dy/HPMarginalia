"""
Vertical Slice: Seed the database with real structured records
extracted from the Kenelm Digby corpus.

Creates at minimum:
- 1 LifeEvent
- 1 MemoirEpisode
- 1 DigbyThemeRecord (Pirate)
- 1 DigbyThemeRecord (Alchemist/Natural Philosopher)
- 1 DigbyThemeRecord (Courtier/Legal Thinker)
- 2 HypnerotomachiaFindings
- Citations for each

All claims are grounded in the source corpus.
"""

import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.db import init_db, insert_record, get_connection
from src.models import (
    SourceDocument, Citation, LifeEvent, WorkRecord,
    MemoirEpisode, DigbyThemeRecord, HypnerotomachiaFinding,
    HypnerotomachiaEvidence, make_id, SourceMethod, ReviewStatus, Confidence
)
from src.validate import validate_record


def seed():
    """Seed the database with the vertical slice data."""
    init_db()

    # --- Register key source documents ---
    sources = [
        SourceDocument(
            id="sdoc_moshenska",
            filename="The Remarkable Voyage of Sir Kenelm Digby.md",
            filepath="KenelmDigby/The Remarkable Voyage of Sir Kenelm Digby.md",
            title="A Stain in the Blood: The Remarkable Voyage of Sir Kenelm Digby",
            file_type="md",
            author="Joe Moshenska",
            year=2016,
        ),
        SourceDocument(
            id="sdoc_miles",
            filename="[Chymia 1949] Sir Kenelm Digby, Alchemist, Scholar, Courtier",
            filepath="KenelmDigby/[Chymia 1949-jan vol. 2] Sir Kenelm Digby, Alchemist, Scholar, Courtier, and Man of Adventure{Wyndham Miles}(1949 January)[10.2307_27757138]{55884445} libgen.li.pdf",
            title="Sir Kenelm Digby, Alchemist, Scholar, Courtier, and Man of Adventure",
            file_type="pdf",
            author="Wyndham Miles",
            year=1949,
            journal="Chymia",
            doi="10.2307/27757138",
        ),
        SourceDocument(
            id="sdoc_dobbs_ii",
            filename="[Ambix 1973] Studies in Natural Philosophy Part II: Digby and Alchemy",
            filepath="KenelmDigby/[Ambix 1973-nov vol. 20 iss. 3] Studies in the Natural Philosophy of Sir Kenelm Digby Part II. Digby and Alchemy{Dobbs, Betty Jo}(1973 November)[10.1179_amb.1973.20.3.143]{35783430} libgen.li.pdf",
            title="Studies in the Natural Philosophy of Sir Kenelm Digby Part II: Digby and Alchemy",
            file_type="pdf",
            author="Betty Jo Dobbs",
            year=1973,
            journal="Ambix",
            doi="10.1179/amb.1973.20.3.143",
        ),
        SourceDocument(
            id="sdoc_dobbs_iii",
            filename="[Ambix 1974] Studies in Natural Philosophy Part III: Experimental Alchemy",
            filepath="KenelmDigby/[Ambix 1974-mar vol. 21 iss. 1] Studies in the Natural Philosophy of Sir Kenelm Digby Part III. Digby's Experimental Alchemy",
            title="Studies in the Natural Philosophy of Sir Kenelm Digby Part III: Digby's Experimental Alchemy",
            file_type="pdf",
            author="Betty Jo Dobbs",
            year=1974,
            journal="Ambix",
            doi="10.1179/amb.1974.21.1.1",
        ),
        SourceDocument(
            id="sdoc_principe",
            filename="[Ambix 2013] Sir Kenelm Digby and His Alchemical Circle in 1650s Paris",
            filepath="KenelmDigby/[Ambix 2013-feb vol. 60 iss. 1] Sir Kenelm Digby and His Alchemical Circle in 1650s Paris_ Newly Discovered Manuscripts{Principe, Lawrence M.}(2013 February)[10.1179_0002698012z.00000000019]{42786279} libgen.li.pdf",
            title="Sir Kenelm Digby and His Alchemical Circle in 1650s Paris",
            file_type="pdf",
            author="Lawrence M. Principe",
            year=2013,
            journal="Ambix",
            doi="10.1179/0002698012z.00000000019",
        ),
        SourceDocument(
            id="sdoc_moshenska_piracy",
            filename="Sir Kenelm Digby's Interruptions: Piracy and Lived Romance in the 1620s",
            filepath="KenelmDigby/Sir Kenelm Digby&_039_s Interruptions_ Piracy and Lived Romance in the 1620s{Moshenska, Joe (author)}(2016){109643212} libgen.li.pdf",
            title="Sir Kenelm Digby's Interruptions: Piracy and Lived Romance in the 1620s",
            file_type="pdf",
            author="Joe Moshenska",
            year=2016,
        ),
        SourceDocument(
            id="sdoc_mellick",
            filename="[ANZ 2011] Sir Kenelm Digby (1603-1665): diplomat, entrepreneur, privateer",
            filepath="KenelmDigby/[ANZ Journal of Surgery 2011-apr 04 vol. 81 iss. 12] Sir Kenelm Digby (1603-1665)",
            title="Sir Kenelm Digby (1603-1665): diplomat, entrepreneur, privateer, duellist, scientist and philosopher",
            file_type="pdf",
            author="Sam A. Mellick",
            year=2011,
            journal="ANZ Journal of Surgery",
        ),
        SourceDocument(
            id="sdoc_russell_pptx",
            filename="The HP of Ben Jonson and Kenelm Digby.pptx",
            filepath="KenelmDigby/The HP of Ben Jonson and Kenelm Digby.pptx",
            title="The Hypnerotomachia Poliphili, Ben Jonson, and Kenelm Digby",
            file_type="pptx",
            author="James Russell",
        ),
        SourceDocument(
            id="sdoc_hedrick",
            filename="[BJHS 2008] Romancing the Salve: Sir Kenelm Digby and the Powder of Sympathy",
            filepath="KenelmDigby/[The British Journal for the History of Science 2008-jun vol. 41 iss. 2] Romancing the Salve",
            title="Romancing the Salve: Sir Kenelm Digby and the Powder of Sympathy",
            file_type="pdf",
            author="Elizabeth Hedrick",
            year=2008,
            journal="The British Journal for the History of Science",
        ),
        SourceDocument(
            id="sdoc_lobis",
            filename="[HLQ 2011] Sir Kenelm Digby and the Power of Sympathy",
            filepath="KenelmDigby/[Huntington Library Quarterly 2011-jun vol. 74 iss. 2] Sir Kenelm Digby and the Power of Sympathy",
            title="Sir Kenelm Digby and the Power of Sympathy",
            file_type="pdf",
            author="Seth Lobis",
            year=2011,
            journal="Huntington Library Quarterly",
        ),
        SourceDocument(
            id="sdoc_georgescu",
            filename="The Philosophy of Kenelm Digby (1603-1665)",
            filepath="KenelmDigby/Laura Georgescu_ Han Thomas Adriaenssen - The Philosophy of Kenelm Digby (1603-1665) (2022, Springer) - libgen.li.pdf",
            title="The Philosophy of Kenelm Digby (1603-1665)",
            file_type="pdf",
            author="Laura Georgescu, Han Thomas Adriaenssen",
            year=2022,
        ),
        SourceDocument(
            id="sdoc_memoirs",
            filename="Private Memoirs of Sir Kenelm Digby (1827)",
            filepath="KenelmDigby/Kenelm Digby - Private Memoirs of Sir Kenelm Digby, Gentleman of the Bedchamber to King Charles the First (1827, Saunders and Otley) - libgen.li.pdf",
            title="Private Memoirs of Sir Kenelm Digby, Gentleman of the Bedchamber to King Charles the First",
            file_type="pdf",
            author="Kenelm Digby",
            year=1827,
        ),
    ]

    for s in sources:
        validate_record(s)
        insert_record("source_documents", s.to_dict())
    print(f"Registered {len(sources)} source documents.")

    # --- Citations ---
    # Each substantive record needs at least one citation
    citations = {
        "cit_birth": Citation(
            id="cit_birth",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapter 1",
            quote_fragment="born 11 July 1603 at Gayhurst",
            context="Digby's birth date and location",
        ),
        "cit_voyage_departure": Citation(
            id="cit_voyage_departure",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapter 4",
            quote_fragment="on 7 January 1628 Kenelm watched from the deck of the Eagle",
            context="Departure of Digby's Mediterranean voyage",
        ),
        "cit_scanderoon": Citation(
            id="cit_scanderoon",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapter 7",
            quote_fragment="fired his cannons at Scanderoon",
            context="Battle of Scanderoon, June 1628",
        ),
        "cit_piracy_moshenska": Citation(
            id="cit_piracy_moshenska",
            source_document_id="sdoc_moshenska_piracy",
            page_or_location="passim",
            quote_fragment="Piracy and Lived Romance in the 1620s",
            context="Digby's piracy as self-fashioning",
        ),
        "cit_alchemy_dobbs": Citation(
            id="cit_alchemy_dobbs",
            source_document_id="sdoc_dobbs_ii",
            page_or_location="passim",
            quote_fragment="Digby and Alchemy",
            context="Digby's alchemical interests and theories",
        ),
        "cit_alchemy_principe": Citation(
            id="cit_alchemy_principe",
            source_document_id="sdoc_principe",
            page_or_location="passim",
            quote_fragment="Alchemical Circle in 1650s Paris",
            context="Digby's Parisian alchemical network",
        ),
        "cit_powder_hedrick": Citation(
            id="cit_powder_hedrick",
            source_document_id="sdoc_hedrick",
            page_or_location="passim",
            quote_fragment="Powder of Sympathy",
            context="Digby's famous sympathetic cure",
        ),
        "cit_courtier_miles": Citation(
            id="cit_courtier_miles",
            source_document_id="sdoc_miles",
            page_or_location="passim",
            quote_fragment="Alchemist, Scholar, Courtier, and Man of Adventure",
            context="Digby's court career and scholarly identity",
        ),
        "cit_petition_moshenska": Citation(
            id="cit_petition_moshenska",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapter 7",
            quote_fragment="Petition of Right",
            context="Digby's voyage during the Petition of Right crisis",
        ),
        "cit_memoir_source": Citation(
            id="cit_memoir_source",
            source_document_id="sdoc_memoirs",
            page_or_location="pp. 1-50",
            quote_fragment="Private Memoirs",
            context="Digby's own memoir, published posthumously 1827",
        ),
        "cit_hp_russell": Citation(
            id="cit_hp_russell",
            source_document_id="sdoc_russell_pptx",
            page_or_location="slides",
            quote_fragment="alchemical annotator",
            context="Russell's research on Digby as HP annotator",
        ),
        "cit_hp_alchemy": Citation(
            id="cit_hp_alchemy",
            source_document_id="sdoc_dobbs_ii",
            page_or_location="passim",
            quote_fragment="universal spirit, Jupiter, Mercury",
            context="Alchemical concepts in Digby's work paralleling HP marginalia",
        ),
        "cit_two_treatises": Citation(
            id="cit_two_treatises",
            source_document_id="sdoc_georgescu",
            page_or_location="passim",
            quote_fragment="Two Treatises",
            context="Digby's major philosophical work",
        ),
    }

    for c in citations.values():
        validate_record(c)
        insert_record("citations", c.to_dict())
    print(f"Created {len(citations)} citations.")

    # --- Life Events ---
    life_events = [
        LifeEvent(
            id="evt_birth",
            title="Birth of Kenelm Digby",
            date_display="11 July 1603",
            year=1603,
            description="Kenelm Digby was born at Gayhurst, Buckinghamshire, into a prominent Catholic family. His father was Sir Everard Digby, who would be executed for his role in the Gunpowder Plot just two years later.",
            life_phase="youth",
            location="Gayhurst, Buckinghamshire",
            people_involved="Everard Digby, Mary Mulshaw",
            citation_ids="cit_birth",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_voyage_depart",
            title="Departure of Mediterranean Voyage",
            date_display="7 January 1628",
            year=1628,
            description="Digby departed England from the port of Deal aboard the Eagle with a fleet of two ships and approximately 250 crewmen, setting sail for the Mediterranean on a privateering expedition against French and Spanish shipping.",
            life_phase="voyage",
            location="Deal, England",
            people_involved="Edward Stradling, Mr Milborne",
            citation_ids="cit_voyage_departure",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_scanderoon",
            title="Battle of Scanderoon",
            date_display="11 June 1628",
            year=1628,
            description="Digby's fleet engaged Venetian galleasses in the Bay of Scanderoon (Iskenderun), winning a notable victory. The battle brought him fame but also controversy, as it disrupted English merchant trade in the region and led to the imprisonment of English merchants in Aleppo.",
            life_phase="voyage",
            location="Bay of Scanderoon (Iskenderun), Ottoman Empire",
            people_involved="Antonio Capello, Edward Stradling",
            citation_ids="cit_scanderoon",
            confidence=Confidence.HIGH.value,
        ),
    ]

    for evt in life_events:
        validate_record(evt)
        insert_record("life_events", evt.to_dict())
    print(f"Created {len(life_events)} life events.")

    # --- Work Records ---
    works = [
        WorkRecord(
            id="wrk_two_treatises",
            title="Two Treatises: Of Bodies and Of Man's Soul",
            year=1644,
            work_type="treatise",
            subject="Natural philosophy and metaphysics",
            description="Digby's major philosophical work, published in Paris. The first treatise examines the nature of bodies and physical matter; the second addresses the immortality of the soul. It engages with contemporary debates about atomism, Aristotelianism, and the mechanical philosophy.",
            significance="Digby's most important philosophical contribution, attempting to reconcile Catholic theology with the new natural philosophy.",
            citation_ids="cit_two_treatises",
        ),
        WorkRecord(
            id="wrk_powder_sympathy",
            title="A Late Discourse on the Powder of Sympathy",
            year=1658,
            work_type="treatise",
            subject="Sympathetic medicine and natural philosophy",
            description="Digby's famous account of the Powder of Sympathy, a substance claimed to heal wounds at a distance by being applied to the weapon that caused the wound. First delivered as a lecture at Montpellier, it became one of his most widely read works.",
            significance="Made Digby internationally famous and exemplified the intersection of empirical observation and magical thinking in early modern natural philosophy.",
            citation_ids="cit_powder_hedrick",
        ),
        WorkRecord(
            id="wrk_closet",
            title="The Closet of Sir Kenelm Digby Knight Opened",
            year=1669,
            work_type="recipe_book",
            subject="Cookery and household receipts",
            description="Published posthumously, this collection of recipes and household receipts reveals Digby's wide-ranging culinary interests, from mead and metheglin to elaborate dishes gathered during his travels across Europe.",
            significance="One of the earliest and most important English cookbooks, reflecting Digby's cosmopolitan tastes and social networks.",
            citation_ids="cit_courtier_miles",
        ),
        WorkRecord(
            id="wrk_memoirs",
            title="Private Memoirs of Sir Kenelm Digby",
            year=1827,
            work_type="memoir",
            subject="Autobiography and romance",
            description="Digby's romanticized autobiography, written in the third person under the names Theagenes (himself) and Stelliana (Venetia Stanley). Published posthumously in 1827, it recounts his youth, education, travels, and love for Venetia in a highly literary style modelled on Heliodorus.",
            significance="A unique early modern autobiography blending romance, self-fashioning, and real events, essential for understanding Digby's self-image.",
            citation_ids="cit_memoir_source",
        ),
    ]

    for w in works:
        validate_record(w)
        insert_record("work_records", w.to_dict())
    print(f"Created {len(works)} work records.")

    # --- Memoir Episodes ---
    memoir_episodes = [
        MemoirEpisode(
            id="mem_plague_at_sea",
            title="Plague at Sea: The Crew's Pestilential Disease",
            episode_number=1,
            date_display="Late January 1628",
            year=1628,
            summary="Shortly after entering the Mediterranean, a violent pestilential disease erupted among Digby's crew aboard the Eagle. Within days, sixty of 150 men were stricken. The sick suffered fevers, vomiting, and delirium, with their 'depraved fantasy' causing them to believe the sea was a green meadow. The dead lay unattended in their hammocks. Despite his officers' urging to return home, Digby refused, arguing that England was now the farthest point they could reach, and resolved to press on to Algiers for help.",
            key_events="Outbreak of plague, crew decimation, officers urge return, Digby refuses",
            people="Kenelm Digby, Edward Stradling, Captain Michael",
            places="Mediterranean Sea, Bay of Biscay, Barbary Coast, Algiers",
            themes="memoir,pirate,biography",
            citation_ids="cit_voyage_departure",
        ),
        MemoirEpisode(
            id="mem_departure",
            title="Departure from England and the Organized Fleet",
            episode_number=0,
            date_display="7 January 1628",
            year=1628,
            summary="Digby departed from Deal with two ships (the Eagle and the Elizabeth and George) and approximately 250 crewmen. He meticulously organized his fleet, distributing men and provisions, appointing officers, and drafting detailed instructions for communication, rendezvous points, and prize distribution. He studied John Smith's Sea Grammar to master naval terminology and command.",
            key_events="Fleet organization, departure from Deal, detailed sailing instructions drafted",
            people="Kenelm Digby, Edward Stradling, Henry Stradling, Mr Milborne",
            places="Deal, English Channel",
            themes="memoir,pirate",
            citation_ids="cit_voyage_departure",
        ),
    ]

    for ep in memoir_episodes:
        validate_record(ep)
        insert_record("memoir_episodes", ep.to_dict())
    print(f"Created {len(memoir_episodes)} memoir episodes.")

    # --- Digby Theme Records ---
    theme_records = [
        # PIRATE
        DigbyThemeRecord(
            id="thm_scanderoon_battle",
            theme="pirate",
            title="The Battle of Scanderoon (Iskenderun), June 1628",
            summary="Digby's most famous naval exploit. On 11 June 1628, his small fleet engaged Venetian galleasses in the Bay of Scanderoon, winning a decisive victory that demonstrated his naval skill and audacity. The Venetians subsequently branded him 'a pirate, who had sold all his property for the sake of robbing.' The battle disrupted English trade in the region and led to diplomatic repercussions.",
            key_details="Two English ships defeated larger Venetian force; English merchants imprisoned in Aleppo as consequence; Digby lingered in the area for weeks afterward",
            people="Kenelm Digby, Antonio Capello, Edward Stradling, Thomas Roe",
            places="Bay of Scanderoon (Iskenderun), Aleppo, Ottoman Empire",
            date_display="June 1628",
            year=1628,
            significance="Established Digby's military reputation but also revealed the tension between privateering glory and diplomatic consequences. The Venetians' labeling of Digby as 'pirate' became part of his public identity.",
            citation_ids="cit_scanderoon,cit_piracy_moshenska",
            confidence=Confidence.HIGH.value,
        ),
        # ALCHEMIST / NATURAL PHILOSOPHER
        DigbyThemeRecord(
            id="thm_powder_sympathy",
            theme="alchemist_natural_philosopher",
            title="The Powder of Sympathy: Digby's Most Famous Natural Philosophical Claim",
            summary="Digby's Powder of Sympathy was a substance claimed to heal wounds at a distance by being applied to the weapon or bloodied bandage rather than the wound itself. First presented as a lecture at Montpellier, it became internationally famous. Digby explained its action through a theory of material 'atoms' or 'small bodies' that carried healing properties through the air, connecting the wound to the treated object via invisible sympathetic forces.",
            key_details="Lecture at Montpellier; published 1658; theory of atoms and sympathetic action; intersection of empirical observation and occult philosophy",
            people="Kenelm Digby, James Howell",
            places="Montpellier, Paris, London",
            significance="Exemplifies the boundary between natural philosophy and magic in the early modern period. Made Digby an international celebrity and remains one of the most discussed episodes in the history of science.",
            citation_ids="cit_powder_hedrick,cit_alchemy_dobbs",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_paris_circle",
            theme="alchemist_natural_philosopher",
            title="Digby's Alchemical Circle in 1650s Paris",
            summary="During his exile in Paris in the 1650s, Digby was at the center of an active alchemical circle. Newly discovered manuscripts by Lawrence Principe reveal that Digby conducted and documented alchemical experiments, corresponded with other practitioners, and engaged seriously with the transmutation of metals. This circle included both English exiles and French savants.",
            key_details="1650s Paris exile; experimental alchemy; newly discovered manuscripts; transmutation interests",
            people="Kenelm Digby",
            places="Paris",
            date_display="1650s",
            significance="Demonstrates that Digby's alchemy was not merely theoretical but actively experimental, and that he was embedded in a serious network of alchemical practitioners.",
            citation_ids="cit_alchemy_principe",
            confidence=Confidence.HIGH.value,
        ),
        # COURTIER / LEGAL THINKER
        DigbyThemeRecord(
            id="thm_petition_of_right",
            theme="courtier_legal_thinker",
            title="Digby's Voyage and the Petition of Right (1628)",
            summary="Digby's Mediterranean voyage coincided exactly with one of the most significant constitutional crises of early modern England. On 7 June 1628, just four days before Digby fought at Scanderoon, the House of Commons presented Charles I with the Petition of Right. This landmark document demanded protection of subjects' liberties against forced loans, arbitrary imprisonment, martial law, and forced billeting. Digby was at sea as the political world he inhabited was being transformed.",
            key_details="Petition of Right presented 2 June 1628, approved 7 June; Digby fought at Scanderoon 11 June; Edward Coke and John Selden led the parliamentary effort",
            people="Charles I, Duke of Buckingham, Edward Coke, John Selden",
            places="London, Parliament, Bay of Scanderoon",
            date_display="June 1628",
            year=1628,
            significance="Illustrates how Digby's personal adventure was embedded in larger constitutional and political transformations. His Catholic identity and ties to the Crown made him vulnerable to the same political forces driving the Petition.",
            citation_ids="cit_petition_moshenska,cit_courtier_miles",
            confidence=Confidence.HIGH.value,
        ),
    ]

    for tr in theme_records:
        validate_record(tr)
        insert_record("digby_theme_records", tr.to_dict())
    print(f"Created {len(theme_records)} theme records.")

    # --- Hypnerotomachia Findings ---
    hp_findings = [
        HypnerotomachiaFinding(
            id="hpf_alchemical_hand",
            title="Identification of Digby as the Alchemical Annotator",
            claim="James Russell's research argues that Kenelm Digby is the most likely candidate for the 'alchemical hand' identified among the multiple annotating hands in a copy of the Hypnerotomachia Poliphili.",
            description="The annotated copy of the Hypnerotomachia Poliphili contains marginalia from several distinct hands. One hand is characterized by alchemical symbolic markings, Latin notes interpreting images and text as alchemical allegory, and attention to themes of transformation and transmutation. Russell argues that this hand can be attributed to Digby based on handwriting similarities, conceptual parallels with Digby's known alchemical writings, and historical plausibility given Digby's bibliophilic habits and access to rare books.",
            evidence_excerpt="The alchemical annotations show attention to Jupiter/Tin symbolism, universal spirit concepts, and Mercury — all central to Digby's documented alchemical theories",
            related_concepts="Jupiter/Tin, Mercury, universal spirit, alchemical allegory, transmutation",
            significance="If correct, this attribution expands Digby's known corpus to include his reading practices and alchemical interpretation of Renaissance texts, connecting his natural philosophy to a broader tradition of esoteric reading.",
            citation_ids="cit_hp_russell,cit_hp_alchemy",
            confidence=Confidence.MEDIUM.value,
        ),
        HypnerotomachiaFinding(
            id="hpf_intellectual_context",
            title="Digby's Alchemical Reading as Intellectual Practice",
            claim="The alchemical marginalia in the Hypnerotomachia, if attributable to Digby, represent a form of active alchemical reading that connects his philosophical theories to his engagement with Renaissance visual and textual culture.",
            description="Digby's known works demonstrate a consistent interest in how material substances interact across distances (the Powder of Sympathy), how spirit animates matter (Two Treatises), and how visible forms encode hidden truths. The alchemical annotations in the Hypnerotomachia show the same interpretive framework applied to Colonna's text and woodcuts — reading images of gardens, architecture, and mythological scenes as encoded alchemical processes.",
            evidence_excerpt="Parallels between marginalia's interpretation of HP imagery and Digby's theories of sympathy and atomic transmission in Two Treatises",
            related_concepts="sympathetic action, atoms, spirit-matter relationship, allegorical reading",
            significance="Situates Digby within early modern alchemical reading practices and demonstrates that his natural philosophy was not separate from his literary and visual culture.",
            citation_ids="cit_hp_russell,cit_two_treatises",
            confidence=Confidence.MEDIUM.value,
        ),
    ]

    for f in hp_findings:
        validate_record(f)
        insert_record("hypnerotomachia_findings", f.to_dict())
    print(f"Created {len(hp_findings)} Hypnerotomachia findings.")

    # --- HP Evidence ---
    hp_evidence = [
        HypnerotomachiaEvidence(
            id="hpe_jupiter_tin",
            finding_id="hpf_alchemical_hand",
            excerpt="The alchemical annotator consistently marks passages relating to Jupiter/Tin symbolism — a connection central to Digby's alchemical theory as documented by Dobbs.",
            source="Russell PPTX + Dobbs, Ambix 1973",
            page_or_location="Multiple slides; Dobbs passim",
            notes="Conceptual parallel, not direct handwriting proof. Confidence: MEDIUM.",
        ),
        HypnerotomachiaEvidence(
            id="hpe_universal_spirit",
            finding_id="hpf_intellectual_context",
            excerpt="Digby's Two Treatises articulates a theory of universal spirit that animates matter — the same framework visible in the marginalia's interpretation of HP imagery as alchemical process.",
            source="Georgescu & Adriaenssen, The Philosophy of Kenelm Digby (2022); Russell PPTX",
            page_or_location="Georgescu passim",
            notes="Parallel between published philosophy and annotation practice.",
        ),
    ]

    for e in hp_evidence:
        validate_record(e)
        insert_record("hypnerotomachia_evidence", e.to_dict())
    print(f"Created {len(hp_evidence)} HP evidence records.")

    # --- Summary ---
    conn = get_connection()
    tables = [
        "source_documents", "citations", "life_events", "work_records",
        "memoir_episodes", "digby_theme_records",
        "hypnerotomachia_findings", "hypnerotomachia_evidence"
    ]
    print("\n--- Vertical Slice Summary ---")
    for t in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {count} records")
    conn.close()
    print("\nVertical slice seeded successfully.")


if __name__ == "__main__":
    seed()
