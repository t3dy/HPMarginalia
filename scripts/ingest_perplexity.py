"""Ingest new bibliography entries from HPPERPLEXITY.txt research into the database.

Adds entries that are genuinely new scholarship not already in our bibliography,
with proper source_method tagging.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

# New entries from HPPERPLEXITY.txt that are NOT already in our bibliography
NEW_ENTRIES = [
    # Scholarly articles discovered via Perplexity
    {
        "author": "Unknown (botanical study)",
        "title": "On the Botanical Content of Hypnerotomachia Poliphili",
        "year": "2016",
        "pub_type": "article",
        "journal": "Landscape Ecology / Taylor & Francis (Botanical Journal of the Linnean Society?)",
        "hp_relevance": "DIRECT",
        "topic_cluster": "architecture_gardens",
        "url": "https://www.tandfonline.com/doi/full/10.1080/23818107.2016.1166070",
        "notes": "Catalogues 285 plant entities referenced in the HP text. Via HPPERPLEXITY.txt.",
        "source_method": "WEB_SEARCH",
        "needs_verification": True,
    },
    {
        "author": "Unknown (musicological study)",
        "title": "Music and Its Powers in the Hypnerotomachia Poliphili (1499)",
        "year": "2020",
        "pub_type": "article",
        "journal": "Cahiers de recherches medievales et humanistes 39",
        "hp_relevance": "DIRECT",
        "topic_cluster": "text_image",
        "url": "https://classiques-garnier.com/cahiers-de-recherches-medievales-et-humanistes-journal-of-medieval-and-humanistic-studies-2020-1-n-39-music-and-its-powers-in-the-hypnerotomachia-poliphili-1499.html",
        "notes": "Musicological reading of musical scenes, instruments, and Ficinian spiritus. Via HPPERPLEXITY.txt.",
        "source_method": "WEB_SEARCH",
        "needs_verification": True,
    },
    {
        "author": "Unknown (UPenn repository)",
        "title": "Architectures of the Text: An Inquiry Into the Hypnerotomachia Poliphili",
        "year": None,
        "pub_type": "article",
        "journal": "University of Pennsylvania Repository",
        "hp_relevance": "DIRECT",
        "topic_cluster": "architecture_gardens",
        "url": "https://repository.upenn.edu/items/37a3b059-be9a-4b2a-aad4-9fc2feb5b7f1",
        "notes": "Architecture, design, and Aldine printing. Via HPPERPLEXITY.txt.",
        "source_method": "WEB_SEARCH",
        "needs_verification": True,
    },
    {
        "author": "Unknown (Polish publisher)",
        "title": "Hypnerotomachia Poliphili: Thoughts on the Earliest Reception",
        "year": None,
        "pub_type": "article",
        "journal": "Akademicka.pl (Polish academic press)",
        "hp_relevance": "DIRECT",
        "topic_cluster": "reception",
        "url": "https://books.akademicka.pl/publishing/catalog/download/145/488/469?inline=1",
        "notes": "Examines annotated copies and earliest readers. Via HPPERPLEXITY.txt.",
        "source_method": "WEB_SEARCH",
        "needs_verification": True,
    },

    # Digital editions and resources (not scholarship per se, but important references)
    {
        "author": "MIT Press",
        "title": "The Electronic Hypnerotomachia",
        "year": "1999",
        "pub_type": "book",
        "journal": "MIT Press (digital edition)",
        "hp_relevance": "PRIMARY",
        "topic_cluster": "text_image",
        "url": "https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/4196/HP.zip/hyptext1.htm",
        "notes": "Electronic text with typographic information. Companion to Lefaivre 1997.",
        "source_method": "WEB_SEARCH",
        "needs_verification": False,
    },

    # Routledge volume
    {
        "author": "Various (ed. unknown)",
        "title": "Francesco Colonna's Hypnerotomachia Poliphili and Its European Context",
        "year": "2023",
        "pub_type": "book",
        "journal": "Routledge (Anglo-Italian Renaissance Studies)",
        "hp_relevance": "DIRECT",
        "topic_cluster": "reception",
        "url": "https://api.pageplace.de/preview/DT0400.9781000911848_A46453224/preview-9781000911848_A46453224.pdf",
        "notes": "Chapters on narrative, architecture, travel, love, self-transformation. Via HPPERPLEXITY.txt.",
        "source_method": "WEB_SEARCH",
        "needs_verification": True,
    },

    # Music / creative works inspired by HP
    {
        "author": "Alexander Moosbrugger",
        "title": "Wind (opera based on Hypnerotomachia Poliphili)",
        "year": "2021",
        "pub_type": "book",
        "journal": "Contemporary opera",
        "hp_relevance": "INDIRECT",
        "topic_cluster": "reception",
        "notes": "Libretto drawn from German and English HP translations. Via HPPERPLEXITY.txt.",
        "source_method": "WEB_SEARCH",
        "needs_verification": True,
    },
    {
        "author": "Sagenhaft",
        "title": "Hypnerotomachia (dungeon synth EP)",
        "year": "2021",
        "pub_type": "book",
        "journal": "Moonlit Castle Records",
        "hp_relevance": "INDIRECT",
        "topic_cluster": "reception",
        "notes": "4-track EP inspired by the HP. Dungeon synth genre. Via HPPERPLEXITY.txt.",
        "source_method": "WEB_SEARCH",
        "needs_verification": True,
    },

    # The Codex 99 essay - important web resource
    {
        "author": "Codex 99",
        "title": "The Hypnerotomachia Poliphili (typographic essay)",
        "year": None,
        "pub_type": "article",
        "journal": "Codex 99 (web)",
        "hp_relevance": "INDIRECT",
        "topic_cluster": "material_bibliographic",
        "url": "http://www.codex99.com/typography/82.html",
        "notes": "Substantial web essay on printing, typography, and images with links to digitized copies.",
        "source_method": "WEB_SEARCH",
        "needs_verification": False,
    },
]

# Timeline events from Perplexity findings
NEW_TIMELINE = [
    (2021, None, 'OTHER', "Moosbrugger's opera Wind premieres",
     "German composer Alexander Moosbrugger uses HP translations as libretto for opera Wind.",
     'reception'),
    (2016, None, 'PUBLICATION', 'Botanical content study published',
     'Study cataloguing 285 plant entities referenced in the HP text.',
     'architecture_gardens'),
    (2020, None, 'PUBLICATION', 'Music and its powers study published',
     'Musicological analysis of musical episodes and Ficinian spiritus in the HP.',
     'text_image'),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Ingesting HPPERPLEXITY.txt entries...\n")

    inserted = 0
    skipped = 0
    for e in NEW_ENTRIES:
        # Check if already exists
        cur.execute(
            "SELECT id FROM bibliography WHERE title = ?",
            (e["title"],)
        )
        if cur.fetchone():
            skipped += 1
            continue

        cur.execute("""
            INSERT INTO bibliography
                (author, title, year, pub_type, journal_or_publisher,
                 hp_relevance, topic_cluster, notes,
                 in_collection, review_status, needs_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 'UNREVIEWED', 1)
        """, (e["author"], e["title"], e.get("year"),
              e["pub_type"], e.get("journal", ""),
              e["hp_relevance"], e.get("topic_cluster", ""),
              e.get("notes", "")))
        inserted += 1

    conn.commit()
    print(f"  Inserted {inserted} new bibliography entries (skipped {skipped} duplicates)")

    # Timeline events
    print("\nInserting timeline events...")
    tl_inserted = 0
    for year, year_end, evt_type, title, desc, topic in NEW_TIMELINE:
        cur.execute(
            "SELECT id FROM timeline_events WHERE title = ?", (title,)
        )
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO timeline_events
                    (year, year_end, event_type, title, description, needs_review, source_method)
                VALUES (?, ?, ?, ?, ?, 1, 'WEB_SEARCH')
            """, (year, year_end, evt_type, title, desc))
            tl_inserted += 1
    conn.commit()
    print(f"  Inserted {tl_inserted} timeline events")

    # Summary
    cur.execute("SELECT COUNT(*) FROM bibliography")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bibliography WHERE in_collection = 1")
    have = cur.fetchone()[0]
    print(f"\nBibliography total: {total} entries ({have} in collection)")

    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
