"""
Add remaining life events discovered by the research agent
from Moshenska's biography (Chapters 1-3, 8, Epilogue).
"""

import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.db import init_db, insert_record, get_connection
from src.models import LifeEvent, MemoirEpisode, Citation, Confidence
from src.validate import validate_record


def expand():
    init_db()
    conn = get_connection()
    existing = {r["id"] for r in conn.execute("SELECT id FROM life_events").fetchall()}
    existing_cits = {r["id"] for r in conn.execute("SELECT id FROM citations").fetchall()}
    existing_eps = {r["id"] for r in conn.execute("SELECT id FROM memoir_episodes").fetchall()}
    conn.close()

    # Additional citations
    new_cits = [
        Citation(id="cit_ch1_spain", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 1, Section II",
                 context="First journey to Spain with John Digby, 1617"),
        Citation(id="cit_ch1_oxford", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 1, Section II",
                 context="Oxford studies with Thomas Allen"),
        Citation(id="cit_ch2_france", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 2, Section I",
                 context="Grand Tour France, Maria de Medici"),
        Citation(id="cit_ch2_madrid", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 2, Section II",
                 context="Madrid, Spanish Match, knighthood"),
        Citation(id="cit_ch3_powder", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 3",
                 context="Powder of Sympathy demonstration, marriage"),
        Citation(id="cit_epilogue", source_document_id="sdoc_moshenska",
                 page_or_location="Epilogue",
                 context="Civil War, exile, Cromwell, death"),
        Citation(id="cit_ch9_venetia_death", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 9",
                 context="Death of Venetia, Gresham College retreat"),
    ]

    added = 0
    for c in new_cits:
        if c.id not in existing_cits:
            c.created_at = datetime.now().isoformat()
            validate_record(c)
            insert_record("citations", c.to_dict())
            added += 1
    print(f"Added {added} new citations.")

    # Events not yet in the database
    new_events = [
        LifeEvent(
            id="evt_spain_first",
            title="First Journey to Spain with John Digby",
            date_display="July 1617 - early 1618",
            year=1617,
            description="Aged fourteen, Kenelm joined his relative John Digby's ambassadorial retinue to Spain. His first foreign travel and first experience of a Catholic country openly practiced. He visited Valladolid and Madrid over eight months.",
            life_phase="youth",
            location="Spain (Valladolid, Madrid)",
            people_involved="John Digby (Earl of Bristol)",
            citation_ids="cit_ch1_spain",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_oxford",
            title="Studies at Oxford with Thomas Allen",
            date_display="Autumn 1618 - 1619",
            year=1618,
            description="Kenelm enrolled at Gloucester Hall, Oxford, a safe haven for Catholics, studying under the renowned mathematician and alchemist Thomas Allen. Allen called him 'the Mirandula of his age.' Kenelm did not formally matriculate to avoid the Protestant oath.",
            life_phase="education",
            location="Oxford (Gloucester Hall)",
            people_involved="Thomas Allen",
            citation_ids="cit_ch1_oxford",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_madrid_spanish_match",
            title="The Spanish Match and Knighthood",
            date_display="February - October 1623",
            year=1623,
            description="In Madrid, Kenelm joined the Earl of Bristol's embassy and befriended Prince Charles during the failed Spanish Match. He killed a man in self-defense during a street fight. On 28 October 1623, King James knighted him at Whitehall on Charles's recommendation.",
            life_phase="grand_tour",
            location="Madrid; London (Whitehall)",
            people_involved="Prince Charles, Duke of Buckingham, John Digby, King James I",
            citation_ids="cit_ch2_madrid",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_powder_demo_1624",
            title="Demonstration of the Powder of Sympathy at Court",
            date_display="1624",
            year=1624,
            description="Digby demonstrated the Powder of Sympathy at court by healing James Howell's wounded hand at a distance, impressing King James and Francis Bacon. This was his first public demonstration of the sympathetic cure that would make him famous.",
            life_phase="early_career",
            location="London",
            people_involved="James Howell, King James I, Francis Bacon, Theodore de Mayerne",
            citation_ids="cit_ch3_powder",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_son_birth",
            title="Birth of First Son, Kenelm Jr.",
            date_display="6 October 1625",
            year=1625,
            description="Venetia fell from her horse near the end of pregnancy, triggering premature labor. Kenelm was present for the birth — unusual for English husbands at the time. The baby was named Kenelm and baptized quickly due to the fraught delivery.",
            life_phase="marriage",
            location="London",
            people_involved="Venetia Digby, Kenelm Digby Jr.",
            citation_ids="cit_ch3_london",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_return_voyage",
            title="Arrival at Woolwich and Royal Audience",
            date_display="2 February 1629",
            year=1629,
            description="Digby's fleet arrived at Woolwich after over a year at sea. He brought ancient marbles from Delos, Arabic manuscripts, natural specimens, and the manuscript of Loose Fantasies. He was summoned to Whitehall where he presented the Delos antiquities to a changed King Charles, now grieving Buckingham.",
            life_phase="return",
            location="Woolwich, Whitehall Palace, London",
            people_involved="King Charles I, Queen Henrietta Maria, Alvise Contarini, Earl of Bristol",
            citation_ids="cit_ch8_return",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_jonson_friendship",
            title="Friendship with Ben Jonson and Literary Circle",
            date_display="Spring 1629 onwards",
            year=1629,
            description="Through James Howell, Kenelm was introduced to the poet Ben Jonson and became one of the 'Sons of Ben' at the Mermaid Tavern. He befriended Thomas Hobbes and John Selden. Jonson wrote poetry celebrating Digby, and Kenelm later became Jonson's literary executor.",
            life_phase="intellectual_life",
            location="London (Westminster, Mermaid Tavern)",
            people_involved="Ben Jonson, Thomas Hobbes, John Selden, James Howell",
            citation_ids="cit_ch8_return",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_protestant_conversion",
            title="Conversion to Protestantism and Naval Appointment",
            date_display="October - December 1630",
            year=1630,
            description="Charles named Kenelm a Principal Officer of the navy. To accept, he took Protestant oaths and received the sacrament at Whitehall in December 1630, abandoning the faith for which his father died. The Venetian ambassador wrote he was 'moved by ambition.'",
            life_phase="career",
            location="London (Whitehall, Deptford)",
            people_involved="King Charles I, Sir John Coke",
            citation_ids="cit_epilogue",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_gresham_alchemy",
            title="Retreat to Gresham College and Alchemical Laboratory",
            date_display="1633",
            year=1633,
            description="After Venetia's death, Kenelm sent his sons to his mother, resigned from the navy, and took rooms at Gresham College. He fitted out four rooms as an alchemical laboratory with multiple furnaces and employed the Hungarian alchemist Johannes Banfi Hunyades as assistant.",
            life_phase="mourning",
            location="Gresham College, London",
            people_involved="Johannes Banfi Hunyades",
            citation_ids="cit_ch9_venetia_death",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_catholic_return",
            title="Return to Catholicism",
            date_display="c. 1635",
            year=1635,
            description="Within two years of Venetia's death, Kenelm returned to Catholicism, prompted by her pious memory. He relocated to Paris, where he was sometimes seen wandering the streets in a long gray coat with a large mastiff.",
            life_phase="exile",
            location="Paris",
            people_involved="Thomas White",
            citation_ids="cit_epilogue",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_civil_war_imprisonment",
            title="Imprisonment at Winchester Palace",
            date_display="1640-1643",
            year=1640,
            description="Charged with collecting Catholic funds for the Royalist cause, Kenelm was detained by the Long Parliament, denounced as a ringleader of the 'Popish faction,' and imprisoned at Winchester Palace. There he practiced chemistry (making artificial precious stones) and wrote his Two Treatises.",
            life_phase="civil_war",
            location="Winchester Palace, London",
            people_involved="Queen Henrietta Maria",
            citation_ids="cit_epilogue",
            confidence=Confidence.HIGH.value,
        ),
    ]

    added_events = 0
    for evt in new_events:
        if evt.id not in existing:
            validate_record(evt)
            insert_record("life_events", evt.to_dict())
            added_events += 1
    print(f"Added {added_events} new life events.")

    # Additional memoir episode
    new_episodes = [
        MemoirEpisode(
            id="mem_maria_medici",
            title="The Maria de' Medici Affair in Angers",
            episode_number=4.5,
            date_display="1620",
            year=1620,
            summary="During his Grand Tour, plague forced Digby from Paris to Angers, where the exiled Queen Regent Maria de' Medici attempted to seduce him. He resisted out of fidelity to Venetia. During a military assault on the city, he faked his own death and fled France. His letters home were intercepted by his mother, leading Venetia to believe him dead.",
            key_events="Maria de Medici's seduction attempt, faked death, flight from Angers, intercepted letters",
            people="Kenelm Digby, Maria de Medici, Venetia Stanley, Mary Digby",
            places="Paris, Angers, France",
            themes="memoir,biography,courtier_legal_thinker",
            citation_ids="cit_ch2_france",
        ),
    ]

    added_eps = 0
    for ep in new_episodes:
        if ep.id not in existing_eps:
            validate_record(ep)
            insert_record("memoir_episodes", ep.to_dict())
            added_eps += 1
    print(f"Added {added_eps} new memoir episodes.")

    # Summary
    conn = get_connection()
    print("\n--- Final Database Summary ---")
    total = 0
    for t in ["source_documents", "source_excerpts", "citations", "life_events",
              "work_records", "memoir_episodes", "digby_theme_records",
              "hypnerotomachia_findings", "hypnerotomachia_evidence"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {count}")
        total += count
    print(f"\n  TOTAL: {total} records")
    conn.close()


if __name__ == "__main__":
    expand()
