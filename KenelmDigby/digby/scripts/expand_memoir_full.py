"""
Expand memoir episodes from the full Private Memoirs analysis.
Adds episodes not yet in the database, sourced from the 1827 text.
"""

import os, sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.db import init_db, insert_record, get_connection
from src.models import MemoirEpisode, Citation, Confidence
from src.validate import validate_record


def expand():
    init_db()
    conn = get_connection()
    existing = {r["id"] for r in conn.execute("SELECT id FROM memoir_episodes").fetchall()}
    existing_cits = {r["id"] for r in conn.execute("SELECT id FROM citations").fetchall()}
    conn.close()

    # Citations for memoir-specific content
    new_cits = [
        Citation(id="cit_memoirs_early", source_document_id="sdoc_memoirs",
                 page_or_location="pp. 1-100",
                 context="Childhood, Stelliana, Ursatius abduction"),
        Citation(id="cit_memoirs_mid", source_document_id="sdoc_memoirs",
                 page_or_location="pp. 100-200",
                 context="Grand Tour, Brahmin, Spain"),
        Citation(id="cit_memoirs_late", source_document_id="sdoc_memoirs",
                 page_or_location="pp. 200-end",
                 context="Return, marriage, voyage, Scanderoon, Milo postscript"),
    ]
    added_c = 0
    for c in new_cits:
        if c.id not in existing_cits:
            c.created_at = datetime.now().isoformat()
            validate_record(c)
            insert_record("citations", c.to_dict())
            added_c += 1

    # Episodes from the Private Memoirs not yet in database
    new_episodes = [
        MemoirEpisode(
            id="mem_childhood_love",
            title="Childhood Love: Theagenes and Stelliana",
            episode_number=0,
            date_display="c. 1607-1613",
            year=1607,
            summary="Stelliana (Venetia), orphaned of her mother as an infant, is raised near the home of Arete (Lady Digby). The children Theagenes and Stelliana develop a precocious mutual attachment, but are separated when Stelliana's father reclaims her.",
            key_events="First meetings as children, early attachment, separation by Nearchus/Sir Edward Stanley",
            people="Theagenes/Kenelm, Stelliana/Venetia, Nearchus/Sir Edward Stanley, Arete/Lady Digby",
            places="Country houses near Gayhurst",
            themes="memoir,biography",
            citation_ids="cit_memoirs_early",
        ),
        MemoirEpisode(
            id="mem_ursatius_abduction",
            title="The Abduction by Ursatius",
            episode_number=3,
            date_display="c. 1613-1614",
            year=1613,
            summary="Faustina, bribed by the powerful nobleman Ursatius, lures Stelliana into a coach that carries her to his country lodge. He professes love; she resists. She escapes by lowering herself from a window using sheets, is attacked by a wolf in the woods, and rescued by the young nobleman Mardontius.",
            key_events="Faustina's betrayal, abduction, captivity, escape through window, wolf attack, rescue by Mardontius",
            people="Stelliana/Venetia, Ursatius, Faustina, Mardontius",
            places="Country lodge, woods",
            themes="memoir,biography",
            citation_ids="cit_memoirs_early",
        ),
        MemoirEpisode(
            id="mem_secret_meeting_hunt",
            title="Secret Meeting During the Stag Hunt",
            episode_number=4,
            date_display="c. 1615-1618",
            year=1615,
            summary="At Artesia's house, the lovers manage a secret meeting during a hunt. Theagenes slips a note into Stelliana's glove. They exchange tokens — a diamond ring and a lock of hair — and vow constancy before his departure abroad.",
            key_events="Note in glove, secret rendezvous during hunt, exchange of ring and hair, vows of constancy",
            people="Theagenes/Kenelm, Stelliana/Venetia, Artesia, Arete/Lady Digby",
            places="Artesia's house, the forest",
            themes="memoir,biography",
            citation_ids="cit_memoirs_early",
        ),
        MemoirEpisode(
            id="mem_brahmin_spirit",
            title="The Brahmin and the Spirit of Stelliana",
            episode_number=9,
            date_display="c. 1622",
            year=1622,
            summary="Traveling to Spain, Theagenes encounters a Brahmin who engages him in philosophical dialogue about astrology and free will. The Brahmin conjures a spirit in Stelliana's form, which reveals her honor is intact and prophesies that Theagenes will kill two men in a fight and that the lovers are fated to unite.",
            key_events="Meeting the Brahmin, philosophical debate, spirit conjuration, prophecy of combat, revelation of Stelliana's innocence",
            people="Theagenes/Kenelm, the Brahmin, spirit of Stelliana",
            places="On the road to Spain",
            themes="memoir,alchemist_natural_philosopher",
            citation_ids="cit_memoirs_mid",
        ),
        MemoirEpisode(
            id="mem_madrid_ambush",
            title="The Night Ambush in Madrid",
            episode_number=10,
            date_display="c. 1623",
            year=1623,
            summary="In Madrid, Theagenes and Leodivius are ambushed by fifteen armed men lying in wait over a jealous quarrel. Theagenes fights them single-handedly, killing two including the leader, fulfilling the spirit's prophecy. Prince Charles and Buckingham arrive incognito the next day.",
            key_events="Night ambush, single combat against fifteen, killing of two men, fulfillment of prophecy, arrival of Prince Charles",
            people="Theagenes/Kenelm, Leodivius, Aristobulus/Earl of Bristol, Prince Charles, Hephaestion/Buckingham",
            places="Alexandria/Madrid",
            themes="memoir,pirate,courtier_legal_thinker",
            citation_ids="cit_memoirs_mid",
        ),
        MemoirEpisode(
            id="mem_stelliana_jewels",
            title="Stelliana Pawns Her Jewels",
            episode_number=14,
            date_display="c. 1624-1625",
            year=1624,
            summary="When Theagenes faces financial difficulty for an embassy appointment, Stelliana pawns her jewels and plate to fund his expenses. This act of selfless generosity finally tips the balance: Theagenes resolves to marry her, overcoming all his remaining doubts.",
            key_events="Financial crisis, Stelliana pawns jewels, Theagenes resolves to marry, Clericius's rejected suit",
            people="Theagenes/Kenelm, Stelliana/Venetia, Clericius",
            places="Corinth/London",
            themes="memoir,biography",
            citation_ids="cit_memoirs_late",
        ),
        MemoirEpisode(
            id="mem_mardontius_portrait",
            title="The Challenge to Mardontius and the Portrait",
            episode_number=15,
            date_display="c. January 1625",
            year=1625,
            summary="Stelliana refuses to marry while Mardontius possesses her portrait, given under a promise. Theagenes challenges Mardontius to a duel; Mardontius declines and surrenders the portrait with a written declaration of Stelliana's honor. The obstacle removed, they marry secretly.",
            key_events="Portrait as obstacle, duel challenge, Mardontius surrenders, secret marriage ceremony",
            people="Theagenes/Kenelm, Stelliana/Venetia, Mardontius",
            places="Corinth/London",
            themes="memoir,biography",
            citation_ids="cit_memoirs_late",
        ),
        MemoirEpisode(
            id="mem_milo_postscript",
            title="The Postscript at Milos: Writing the Memoir",
            episode_number=18,
            date_display="August 1628",
            year=1628,
            summary="Stranded on Milos after a storm separated his fleet, Digby explains he wrote the memoir to occupy himself while refusing the company of local women offered by his host. He pretended to write dispatches but instead set down his 'loose fantasies' as a private record, requesting that the manuscript be burned if found.",
            key_events="Storm separates fleet, stranded on Milos, temptation refused, composition of memoir, plea for destruction",
            people="Kenelm Digby",
            places="Island of Milos, Greece",
            themes="memoir,biography",
            citation_ids="cit_memoirs_late",
        ),
    ]

    added = 0
    for ep in new_episodes:
        if ep.id not in existing:
            validate_record(ep)
            insert_record("memoir_episodes", ep.to_dict())
            added += 1

    print(f"Added {added_c} citations, {added} memoir episodes.")

    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM memoir_episodes").fetchone()[0]
    total = sum(conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                for t in ["source_documents", "source_excerpts", "citations",
                          "life_events", "work_records", "memoir_episodes",
                          "digby_theme_records", "hypnerotomachia_findings",
                          "hypnerotomachia_evidence"])
    print(f"Memoir episodes: {count}")
    print(f"Total records: {total}")
    conn.close()


if __name__ == "__main__":
    expand()
