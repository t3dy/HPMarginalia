"""Generate overviews for scholars that don't have them yet."""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

OVERVIEWS = {
    "Jean d'Espagnet": (
        "Jean d'Espagnet (1564-1637) was a French magistrate and natural philosopher whose "
        "Enchiridion Physicae Restitutae (1623) provided the alchemical framework applied by "
        "the BL copy's anonymous annotator (Hand B). Russell identifies d'Espagnet's "
        "mercury-centered alchemy as the interpretive key to Hand B's systematic reading of "
        "the HP as encoding the operations of Master Mercury."
    ),
    "Robert Dallington": (
        "Robert Dallington (c. 1561-1637), an English diplomat and writer, produced the first "
        "English adaptation of the HP in 1592, signing it 'R.D.' Semler (2006) reframes "
        "Dallington's Hypnerotomachia not as a failed translation but as deliberate cultural "
        "appropriation, adapting the HP's Catholic and Italian content for Protestant "
        "antiquarian interests in Elizabethan England."
    ),
    "Christian Huelsen": (
        "Christian Huelsen (1858-1935), a German archaeologist and topographer of ancient Rome, "
        "published the first systematic study of the HP's woodcut illustrations in 1910. His "
        "Le illustrazioni della Hypnerotomachia Poliphili identified the classical architectural "
        "sources for the book's monuments, columns, and triumphal arches, establishing the "
        "foundation for all subsequent architectural analysis of the HP."
    ),
    "Domenico Gnoli": (
        "Domenico Gnoli (1838-1915) published Il Sogno di Polifilo in 1899, one of the earliest "
        "modern scholarly studies of the HP. Gnoli's work contributed to the identification of "
        "the author and the book's literary and cultural context, helping to inaugurate the "
        "twentieth-century revival of HP scholarship."
    ),
    "E.H. Gombrich": (
        "Ernst Gombrich (1909-2001), one of the most influential art historians of the twentieth "
        "century, published Hypnerotomachiana in 1972. This study analyzed the HP's hieroglyphic "
        "woodcuts within the broader context of Renaissance symbolic imagery and the emblem "
        "tradition. Gombrich demonstrated the HP's role in transmitting pseudo-Egyptian visual "
        "culture from antiquity through the Renaissance to the early modern emblem book."
    ),
    "Giovanni Pozzi": (
        "Giovanni Pozzi (1923-2002), a Swiss-Italian philologist, produced the standard critical "
        "edition of the HP with Lucia Ciapponi in 1964. His Francesco Colonna. Biografia e opere "
        "(1959, with Maria Teresa Casella) established the canonical attribution to the Venetian "
        "Dominican friar. Pozzi's philological work remains the foundation for all textual "
        "scholarship on the HP, and his glossary of the book's unusual vocabulary is still the "
        "primary reference."
    ),
    "Maria Teresa Casella": (
        "Maria Teresa Casella, working with Giovanni Pozzi, published Francesco Colonna. Biografia "
        "e opere in 1959, establishing the canonical attribution of the HP to the Venetian Dominican "
        "friar Francesco Colonna (d. 1527). Their biographical and philological research remains "
        "the starting point for all subsequent authorship studies."
    ),
    "Maurizio Calvesi": (
        "Maurizio Calvesi proposed in his 1996 study La pugna d'amore in sogno that the HP was "
        "written not by the Venetian Dominican but by a Roman nobleman also named Francesco Colonna. "
        "His attribution, based on art-historical and biographical evidence, represents the most "
        "sustained challenge to the Casella-Pozzi consensus and has generated significant scholarly "
        "debate about the HP's authorial identity and cultural milieu."
    ),
    "Emilio Menegazzo": (
        "Emilio Menegazzo, a philologist specializing in Paduan literary culture, published three "
        "studies on Francesco Colonna's biography between 1962 and 1966. His archival research "
        "on Colonna's connections to the University of Padua and to Venice contributed to the "
        "biographical understanding of the canonical author."
    ),
    "Myriam Billanovich": (
        "Myriam Billanovich, a philologist, published three studies between 1966 and 1976 examining "
        "Francesco Colonna's biography and his connections to the Lelli family. Her archival "
        "research, conducted in parallel with Menegazzo's work, contributed biographical evidence "
        "for the Venetian attribution of the HP."
    ),
    "Fritz Saxl": (
        "Fritz Saxl (1890-1948), the Austrian-British art historian and director of the Warburg "
        "Institute, published a 1937 study identifying an HP scene in a painting by the Ferrarese "
        "artist Garofalo. This discovery demonstrated the HP's direct influence on Italian "
        "Renaissance painting and visual culture."
    ),
    "Dorothea Stichel": (
        "Dorothea Stichel published the first study of the Modena copy's marginalia in 1994. "
        "Her work on reading the HP in the cinquecento helped establish the field of HP annotation "
        "studies that Russell would later expand in his comprehensive survey of six annotated copies."
    ),
    "Linda Fierz-David": (
        "Linda Fierz-David (1891-1955), a Jungian analyst, published The Dream of Poliphilo "
        "(1950, English translation 1987), the most sustained Jungian reading of the HP. She "
        "interpreted Poliphilo's journey as a process of individuation, reading the dream's "
        "architectural and erotic imagery as symbols of psychological transformation. Her work "
        "established a psychoanalytic strand of HP interpretation distinct from art-historical "
        "and philological approaches."
    ),
    "Marco Arnaudo": (
        "Marco Arnaudo's 2008 study examines the metaphor of the labyrinth in the HP, analyzing "
        "how maze structures function both as architectural features within Poliphilo's journey "
        "and as allegories of interpretive complexity. His work connects the HP's labyrinthine "
        "spaces to the book's broader thematic interest in difficulty, desire, and discovery."
    ),
    "Karl Giehlow": (
        "Karl Giehlow's study of Horapollo's hieroglyphics and their importance for Renaissance "
        "symbolism provides essential context for the HP's pseudo-Egyptian inscriptions. His "
        "research documents how the rediscovery of Horapollo's text shaped the visual and "
        "symbolic vocabulary that the HP's author drew upon."
    ),
    "Mino Gabriele": (
        "Mino Gabriele prepared the introduction and commentary for the 2004 Adelphi critical "
        "edition of the HP (edited with Marco Ariani). This edition provides the most recent "
        "Italian scholarly apparatus for the HP, complementing the earlier Pozzi-Ciapponi edition "
        "with updated commentary and critical notes."
    ),
    "Alexander Nagel": (
        "Alexander Nagel's Medieval Modern: Art Out of Time (2012) engages with the HP as part "
        "of a broader argument about anachronism and temporal complexity in art. His work positions "
        "the HP within a framework that challenges linear periodization, reading the book's "
        "mixture of ancient and contemporary references as deliberate temporal play."
    ),
    "Sophia Rhizopoulou": (
        "Sophia Rhizopoulou has published three studies on the botanical content of the HP, "
        "identifying and classifying the plant species described in Poliphilo's garden and "
        "landscape passages. Her botanical analysis brings scientific expertise to a text usually "
        "studied from literary or art-historical perspectives, demonstrating that the HP's plant "
        "descriptions are botanically specific rather than merely decorative."
    ),
    "Paul Summers Young": (
        "Paul Summers Young produced a new English translation of the HP published in 2024. "
        "This translation provides contemporary readers with an updated rendering of the HP's "
        "notoriously difficult macaronic language, supplementing Godwin's 1999 Thames and Hudson "
        "translation."
    ),
    "Guo Quanzhao": (
        "Guo Quanzhao's 2021 study examines the HP and its afterlife, contributing to the "
        "growing body of reception studies that trace the book's influence across cultures and "
        "centuries."
    ),
    "Thodoris Koutsogiannis": (
        "Thodoris Koutsogiannis's 2024 study examines images of Greek antiquity in the HP, "
        "analyzing how the book's woodcuts and descriptions represent and adapt classical Greek "
        "architectural and sculptural forms."
    ),
}


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    updated = 0
    for name, overview in OVERVIEWS.items():
        cur.execute("""
            UPDATE scholars SET scholar_overview = ?, source_method = 'LLM_ASSISTED',
                   review_status = 'DRAFT'
            WHERE name = ? AND (scholar_overview IS NULL OR scholar_overview = '')
        """, (overview, name))
        if cur.rowcount > 0:
            updated += 1
            print(f"  UPDATED: {name} ({len(overview.split())} words)")

    conn.commit()
    conn.close()
    print(f"\nUpdated {updated} scholars")


if __name__ == "__main__":
    print("=== Generating Remaining Scholar Overviews ===\n")
    main()
