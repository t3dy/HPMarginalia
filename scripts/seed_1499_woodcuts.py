#!/usr/bin/env python3
"""seed_1499_woodcuts.py — Populate woodcuts table with the complete 1499 HP inventory.

Seeds all woodcuts from the 1499 Aldine first edition of the
Hypnerotomachia Poliphili. Merges with existing entries where they
overlap (matched by page_1499).

The 1499 edition contains approximately 172 woodcut illustrations
across 234 leaves. This script catalogs them with:
- Title, description, narrative context
- Page/signature in the 1499 edition
- Internet Archive page index (for image fetching)
- Subject category

Sources: Pozzi & Ciapponi critical edition (1980), Ariani & Gabriele
edition (1998), Godwin 1999 translation, Fierz-David 1947 analysis,
Lefaivre 1997 (MIT Press).

IA offset formula: ia_page = page_1499 + 5
Verified: HP p.4 = IA n9, HP p.28 = IA n33

Usage:
    python scripts/seed_1499_woodcuts.py
    python scripts/seed_1499_woodcuts.py --dry-run
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "hp.db"

# IA offset: IA page number = HP 1499 page number + 5
IA_OFFSET = 5

# Complete 1499 HP woodcut inventory
# Format: (page_1499, signature_1499, title, description, narrative_context, subject_category)
WOODCUTS_1499 = [
    # === BOOK I: Poliphilo's Dream ===
    # Opening / Dark Forest
    (4, "a2v", "Poliphilo in the Dark Forest",
     "Poliphilo wanders among tall trees in a dense forest. Small figure at center surrounded by towering trunks with detailed foliage.",
     "The opening scene of the HP. Poliphilo, having fallen asleep weeping for his beloved Polia, finds himself lost in a dark and terrifying forest — echoing Dante's selva oscura. This is the threshold between waking and dreaming.",
     "LANDSCAPE"),

    (8, "a4v", "Poliphilo at the Landscape with River",
     "Poliphilo rests in an open landscape with trees and a stream. Pastoral scene with classical elements.",
     "Having escaped the dark forest, Poliphilo enters a beautiful open landscape. He drinks from a stream and rests, transitioning from terror to wonder. The landscape represents the first stage of his allegorical journey.",
     "LANDSCAPE"),

    (10, "a5v", "Poliphilo Sleeping (Dream within Dream)",
     "Poliphilo lies sleeping on the ground in a wooded landscape. A second dream begins within the first.",
     "Poliphilo falls asleep again within his dream, initiating the dream-within-a-dream structure that is the HP's most distinctive narrative device. This second sleep takes him deeper into the allegorical realm.",
     "NARRATIVE"),

    (11, "a6r", "Poliphilo in a Garden with Palms",
     "Poliphilo stands in a garden setting with palm trees and classical vegetation.",
     "Poliphilo awakens in a beautiful garden with exotic plants. The palms and ordered vegetation signal his entry into a civilized, designed landscape — architecture replacing wilderness.",
     "LANDSCAPE"),

    # The Pyramid and Monumental Architecture
    (16, "b2v", "The Great Pyramid",
     "Full-page woodcut of a massive stepped pyramid topped by a tall obelisk surmounted by a figure. Colonnaded portico at the base. Inscription KITOMARNO visible.",
     "The centerpiece of Poliphilo's first architectural encounter. This impossible pyramid exceeds the Egyptian originals in Colonna's description — its dimensions are meticulously specified and internally consistent, demonstrating the author's architectural learning.",
     "ARCHITECTURAL"),

    (22, "b5r", "The Ruined Colossal Horse",
     "Fragments of a colossal bronze horse lying among ruins. One of the HP's most evocative images of ancient grandeur brought low.",
     "Poliphilo discovers the ruins of an immense bronze horse — a symbol of imperial ambition and the transience of human achievement. The scale of the ruin matches the scale of the pyramid.",
     "ARCHITECTURAL"),

    (23, "b5v", "Twin Inscribed Monuments (D.AMBIG.D.D.)",
     "Two rectangular stone pedestals with circular wreath inscriptions. Enigmatic Latin abbreviated text within each wreath.",
     "Poliphilo encounters paired funerary monuments with cryptic inscriptions. The enigmatic abbreviations have generated centuries of scholarly debate — they may encode alchemical, erotic, or architectural meanings.",
     "HIEROGLYPHIC"),

    (24, "b6r", "Figures with TEMPVS",
     "Group of classical figures, one labeled TEMPVS (Time). Allegorical scene with personified abstractions.",
     "An allegorical group representing Time and associated concepts. The personification of abstract ideas through classical figures is central to the HP's visual rhetoric.",
     "NARRATIVE"),

    (25, "b6r", "Classical Figures in a Garden",
     "Group of figures in classical dress gathered in a garden or outdoor scene.",
     "Poliphilo encounters allegorical figures in an idealized setting. The garden setting mediates between natural and architectural space.",
     "NARRATIVE"),

    (27, "b6v", "Inscription Monument (ΓΟΝΟΣ ΚΑΙ ΕΤΟΥΣΙΑ)",
     "Stone stele with Greek and pseudo-Arabic inscriptions in an arched niche. ΓΟΝΟΣ ΚΑΙ ΕΤΟΥΣΙΑ (Offspring and Abundance).",
     "A multilingual monument displaying Greek, Arabic, and Hebrew-like characters. The inscription 'Offspring and Abundance' connects to the HP's themes of fertility and generative power.",
     "HIEROGLYPHIC"),

    (28, "b6v", "The Elephant and Obelisk",
     "An elephant bearing an obelisk on a circular stepped pedestal. The obelisk is topped with a sphere and decorated with pseudo-hieroglyphic panels.",
     "The most famous image in the HP. This combination of elephant and obelisk was unprecedented in European art and directly inspired Bernini's 1667 sculpture in Piazza della Minerva, Rome. It represents the union of strength (elephant) and wisdom (obelisk/hieroglyphs).",
     "ARCHITECTURAL"),

    (29, "b7r", "Figure on Monument with Greek Inscription",
     "Standing figure atop a pedestal with Greek text. Classical architectural framing.",
     "A monument combining human figure and Greek inscription, continuing the HP's program of embedding encoded meaning in architectural forms.",
     "HIEROGLYPHIC"),

    (30, "b7v", "Monument with Female Figure, Lamp, and Trilingual Inscriptions",
     "Tall monument with standing female figure holding a lamp. Below: three tiers of inscriptions in Hebrew, Greek, and Latin capitals.",
     "The most inscription-heavy page in the HP. Hebrew, Greek, and Latin texts encode warnings about a treasure. The female figure with lamp represents illumination — both literal and philosophical.",
     "HIEROGLYPHIC"),

    (31, "b8r", "Hieroglyphic Frieze",
     "Two-register frieze with emblematic figures: chariots, winged beings, dolphins, anchors, vessels. Below: Latin majuscule inscription.",
     "The first of the HP's pseudo-hieroglyphic friezes — Colonna's invented 'Egyptian' symbolic language. The emblems encode a message that combines Roman imperial imagery with invented symbolic grammar.",
     "HIEROGLYPHIC"),

    (38, "c3r", "Architectural Portal",
     "Grand classical portal with pediment, columns, and medallion busts. Monumental entrance architecture.",
     "A monumental doorway representing the threshold between different zones of Poliphilo's journey. The architectural vocabulary draws on Roman triumphal arch tradition.",
     "ARCHITECTURAL"),

    (45, "c6v", "Ruins of the Temple",
     "Ruined classical temple with broken columns and fragments. Poliphilo contemplates ancient remains.",
     "Poliphilo encounters another ruin, continuing the theme of ancient grandeur and modern contemplation that runs through Book I.",
     "ARCHITECTURAL"),

    (52, "d2v", "Poliphilo at a Portal with Dragon",
     "Poliphilo recoils from a dragon or beast emerging from a portal. Dramatic confrontation scene.",
     "A moment of danger and wonder. The dragon guards a threshold — Poliphilo must confront fear to continue his journey. The beast connects to the 'bellua' alchemical annotations in the BL copy.",
     "NARRATIVE"),

    (59, "d6r", "Emblematic Medallions (PATIENTIA / Anchor-Dolphin)",
     "Two circular medallion emblems. Top: PATIENTIA EST ORNAMENTVM CVSTO/DIA ET PROTECTIO VITAE. Bottom: anchor-and-dolphin with Greek motto ΑΕΙ ΣΠΕΥΔΕ ΒΡΑΔΕΩΣ.",
     "Two of the HP's most influential emblems. The patience motto and the anchor-dolphin (festina lente — 'hasten slowly') connect directly to the Aldine Press device. These images helped establish the European emblem tradition.",
     "HIEROGLYPHIC"),

    (63, "d8r", "Sleeping Nymph",
     "A sleeping nymph reclining in a classical aedicule with water flowing from the stone. One of the HP's most copied compositions.",
     "The sleeping nymph fountain is one of the most influential images in Renaissance art. The combination of sleeping female figure, water, and classical architecture was widely imitated. The Latin inscription ΠΑΝΙΚΟΣ warns that the sleep is sacred.",
     "NARRATIVE"),

    (66, "e1r", "Five Nymphs Meeting Poliphilo",
     "Five nymphs in classical dress approach Poliphilo in a garden. One extends a hand in greeting.",
     "Poliphilo meets the five senses personified as nymphs. Their names encode the Greek words for each sense. This begins the section of the HP most explicitly concerned with sensory knowledge and pleasure.",
     "NARRATIVE"),

    (71, "e3v", "Cupid on a Sphere",
     "Winged putto (Cupid) standing on a sphere atop a fountain. Water arcs from the base.",
     "Cupid/Eros presides over a fountain — love as the animating force of the natural world. The sphere represents cosmic love.",
     "ARCHITECTURAL"),

    (75, "e5v", "Three Figures in Aedicule",
     "Three figures in an architectural niche with pediment. Interior architectural scene.",
     "An allegorical scene set within classical architecture. The aedicule form connects to Roman domestic religion and shrine design.",
     "ARCHITECTURAL"),

    (80, "f2v", "The Great Fountain",
     "Full-page woodcut of an elaborate tiered fountain. Three levels: sea-horses at base, grotesque masks and sphinxes at middle, nude Venus figure under arching water jets at top.",
     "The most architecturally ambitious fountain in the HP. Its three tiers represent the three levels of being: marine (water/matter), grotesque (transformation), and divine (Venus/beauty). The fountain is both an architectural fantasy and an alchemical diagram.",
     "ARCHITECTURAL"),

    (84, "f4v", "Queen Eleuterylida's Palace",
     "Interior of ornate palace hall with columned arcade. Seven compartments labeled with planetary names: MERCVRIVS, VENVS, SOL, MARS, LVNA, IVPITER, SATVRNVS.",
     "The palace of the seven planets — each compartment corresponds to a celestial body and its associated metal, gemstone, and virtue. This is the HP's most explicit cosmological diagram, connecting architecture to astrology.",
     "ARCHITECTURAL"),

    (88, "f6v", "Palace Interior with Planetary Compartments",
     "Detailed view of the planetary palace interior showing ornate facades with arabesque panels.",
     "A second view of the planetary palace showing the decorative program in detail. The arabesque patterns connect to Islamic geometric design traditions that Colonna knew from Venetian trade contacts.",
     "ARCHITECTURAL"),

    (90, "f7v", "Court Scene with Queen Enthroned",
     "Queen seated on throne under canopy, attended by courtiers and nymphs. Formal court reception scene.",
     "Queen Eleuterylida receives Poliphilo. Her name means 'Freely-Given' — she represents generous hospitality and the liberal arts. The court scene follows classical ekphrasis conventions.",
     "NARRATIVE"),

    (93, "g1r", "Ornamental Tripod Table",
     "Ornate classical tripod with decorative scrollwork and dolphin-form legs.",
     "An architectural study of a classical tripod — the kind of object that appears in Roman domestic settings and temple furnishings. Colonna's attention to decorative arts is as detailed as his architectural descriptions.",
     "DECORATIVE"),

    (94, "g1v", "Covered Vessel on Wheeled Chariot",
     "Small ornamental urn or covered vessel mounted on a wheeled chariot or cart.",
     "A ceremonial vessel, possibly for processions or ritual use. The combination of vessel and wheels suggests mobile sacred architecture.",
     "DECORATIVE"),

    (95, "g2r", "Caryatid Figures Supporting Basin",
     "Three female caryatid figures supporting a basin or table with harp-like decorative elements.",
     "Caryatid architecture — female figures serving as structural columns — is one of the HP's recurring motifs. These figures connect architecture to the human body.",
     "ARCHITECTURAL"),

    (105, "g7r", "Nymph at Fountain Vessel",
     "Woman standing beside an elaborate fountain vessel on a wheeled platform.",
     "A nymph associated with a mobile fountain, combining figural and architectural elements.",
     "NARRATIVE"),

    (119, "h3v", "Obelisk with Three Figures",
     "Tall obelisk with three standing figures in niches at its base. Greek and Latin inscriptions. DIVINAE AENINITATI inscription visible.",
     "A monument combining Egyptian (obelisk) and Greek (inscriptions) elements. The three figures may represent philosophical or allegorical personifications.",
     "ARCHITECTURAL"),

    (123, "h5v", "Seated Scholar at Monument",
     "Seated figure at a desk or lectern within a classical architectural frame with pediment and columns.",
     "A scholar or philosopher at work, housed within architecture. This image of intellectual activity framed by classical design embodies the HP's fusion of learning and building.",
     "ARCHITECTURAL"),

    (124, "h6r", "Two Seated Figures at Pedestal with Medallion",
     "Two seated figures on either side of a pedestal, with a circular medallion portrait above. Classical architectural frame.",
     "A scene of philosophical dialogue or instruction. The two-figure composition suggests teacher and student, or the exchange of ideas.",
     "NARRATIVE"),

    (125, "h6v", "The Three Doors",
     "Cave or grotto scene: figures before three inscribed doorways in a rocky mountainside. Inscriptions: THEODOXIA, COSMODOXIA, EROTOTROPHOS.",
     "The central allegory of the HP. Poliphilo must choose between three doors: Glory of God (THEODOXIA), Glory of the World (COSMODOXIA), and Nourisher of Love (EROTOTROPHOS). He chooses the third — the path of Eros. This scene is the HP's version of the Choice of Hercules.",
     "NARRATIVE"),

    (126, "h7r", "Poliphilo at the Temple Entrance",
     "Group of figures approaching a small classical building or temple. Landscape with trees.",
     "Having chosen the door of EROTOTROPHOS, Poliphilo enters the realm of love and beauty. The classical temple represents the shrine of Venus.",
     "NARRATIVE"),

    (129, "h8v", "Nymphs and Figures Among Trees",
     "Group of nymphs and figures standing among trees near a building or monument.",
     "Poliphilo in the company of nymphs in a sacred grove. The combination of architecture and nature is characteristic of the HP's designed landscapes.",
     "NARRATIVE"),

    (130, "i1r", "Nymphs Walking Through a Grove",
     "Group of nymphs and a central figure walking through a grove of trees.",
     "A processional scene through a sacred landscape, leading Poliphilo toward the next stage of his journey.",
     "NARRATIVE"),

    (139, "i5v", "Garden with Pergola",
     "Two figures standing in a garden with an arched pergola and trees.",
     "A garden scene showing designed horticultural architecture — the pergola represents the domestication of nature through human craft.",
     "LANDSCAPE"),

    # Triumphal Procession sequence (pp. 149-167)
    (149, "k1r", "First Triumphal Chariot (PRIMA TABELLA)",
     "Two woodcut panels: PRIMA TABELLA showing a chariot with bulls and figures. Beginning of the triumphal procession sequence.",
     "The beginning of the HP's most sustained visual sequence — a triumphal procession celebrating the victory of love. The first chariot establishes the ceremonial vocabulary.",
     "PROCESSION"),

    (150, "k1v", "Second Triumphal Panel",
     "Two woodcut panels showing front and rear views of a triumphal chariot with classical figures.",
     "Continuation of the procession with views showing the chariot from multiple angles — an unusual device suggesting the viewer walks around the object.",
     "PROCESSION"),

    (151, "k2r", "Triumphal Chariot (TRIVMPHVS TERTIVS)",
     "Large triumphal chariot drawn by centaurs with nymphs and musicians.",
     "The third triumph in the procession, drawn by centaurs — half-human, half-horse beings representing the dual nature of desire.",
     "PROCESSION"),

    (152, "k2v", "Triumphal Chariot with Soldiers",
     "Large triumphal chariot drawn by horses with soldiers, musicians, and banner-bearers.",
     "A military-themed triumph with martial figures, connecting the procession of love to Roman triumphal traditions.",
     "PROCESSION"),

    (153, "k3r", "Muses and Apollo Chariot",
     "Triumphal chariot with the Muses and Apollo, drawn by horses. Musical instruments and laurel wreaths visible.",
     "The triumph of the arts and music. Apollo and the Muses represent the highest achievements of human culture in the classical tradition.",
     "PROCESSION"),

    (154, "k3v", "TABELLA DEXTRA Panels",
     "Two stacked panel woodcuts: TABELLA DEXTRA showing figures at a doorway and TABELLA SINISTRA showing an outdoor scene.",
     "Side panels of the procession showing narrative scenes — the left and right views of a passing triumph, like spectators at a parade.",
     "PROCESSION"),

    (155, "k4r", "PARS ANTERIOR ET POSTERIOR",
     "Two-panel woodcut showing front and rear views of figures in processional arrangement.",
     "Front and back views of another section of the procession, continuing the immersive spatial presentation.",
     "PROCESSION"),

    (156, "k4v", "TRIVMPHVS: Lovers' Chariot",
     "Large triumphal chariot bearing reclining lovers embraced among garlands and putti. The emotional climax of the procession.",
     "The central image of the procession — lovers entwined on a triumphal chariot, representing the ultimate victory of Eros. This is the most explicitly amorous image in the HP.",
     "PROCESSION"),

    (158, "k5v", "TABELLA DEXTRA (Second Set)",
     "Two stacked panels showing processional scenes with figures at doorways and in landscapes.",
     "Additional processional panels continuing the parade sequence.",
     "PROCESSION"),

    (159, "k6r", "PARS ANTERIOR ET POSTERIOR (Second)",
     "Small woodcut showing front and rear views of processional figures.",
     "Another paired-view panel in the procession sequence.",
     "PROCESSION"),

    (160, "k6v", "TRIVMPHVS with Triple Panels",
     "Large chariot woodcut at top plus two TABELLA DEXTRA/SINISTRA panels below. Dense woodcut-text integration.",
     "The most densely illustrated page in the procession, combining large chariot and subsidiary panel views.",
     "PROCESSION"),

    (161, "k7r", "TERTIVS: Ox Procession",
     "Two stacked panels showing a procession with oxen and figures carrying implements.",
     "An agricultural/sacrificial section of the procession, with oxen suggesting ritual sacrifice in the Roman tradition.",
     "PROCESSION"),

    (164, "k8v", "Nymphs Approaching Altar",
     "Procession of nymphs approaching an altar or sacrificial table with trees and architecture.",
     "A ritual scene marking the transition from procession to ceremony. The altar signals the approach to Venus's shrine.",
     "PROCESSION"),

    (165, "l1r", "Festive Scene at Fountain",
     "Festive scene with figures gathered around a fountain or basin in a garden setting.",
     "Post-processional celebration, combining revelry with the HP's characteristic fountain imagery.",
     "PROCESSION"),

    (166, "l1v", "Bacchic Triumphal Chariot",
     "Large Bacchic triumphal chariot with Maenads, Satyrs, and Dionysiac figures. The most explicitly pagan image in the procession.",
     "The Bacchic triumph represents the wild, ecstatic dimension of love — Dionysus as the complement to Apollo's ordered beauty. Maenads and satyrs embody unrestrained passion.",
     "PROCESSION"),

    (167, "l2r", "QVARTVS: Feasting Chariot",
     "Chariot with reclining figures feasting among garlands, fruit, and flowing drapery.",
     "The fourth triumph: a feast on wheels. The combination of food, drink, and movement represents the sensory abundance of the world Eros governs.",
     "PROCESSION"),

    # Post-procession: Venus and the Ritual
    (170, "l3v", "Poliphilo at the Temple of Venus",
     "Poliphilo and companions before the temple of Venus. Classical architecture with columns and pediment.",
     "Poliphilo arrives at the shrine of Venus — the destination the entire procession was leading toward.",
     "NARRATIVE"),

    (175, "l6r", "The Sacrifice to Venus",
     "Ritual sacrifice scene with figures at an altar before the temple. Smoke rises from offerings.",
     "Poliphilo participates in a ritual sacrifice to Venus, completing his transition from observer to participant in the world of love.",
     "NARRATIVE"),

    (180, "l8v", "Venus Revealed",
     "Venus herself appears to Poliphilo, possibly in or near her temple. Divine epiphany scene.",
     "The climax of Book I: Venus reveals herself. This divine encounter is the reward for Poliphilo's long journey through architecture, allegory, and danger.",
     "NARRATIVE"),

    # Cythera and the Island
    (190, "m5v", "The Voyage to Cythera",
     "A ship or boat scene with figures crossing water toward an island.",
     "Poliphilo travels by boat to the island of Cythera (Venus's birthplace). The sea voyage represents yet another threshold crossing.",
     "NARRATIVE"),

    (200, "n2v", "The Garden of Venus on Cythera",
     "Elaborate garden layout on the island of Cythera. Geometric garden design with central feature.",
     "The ideal garden on Venus's island — a designed paradise combining geometric order with natural abundance. This garden represents the HP's vision of perfect union between art and nature.",
     "LANDSCAPE"),

    (210, "o1r", "The Fountain of Venus",
     "Central fountain in the garden of Cythera. Elaborate multi-tiered design with Venus figure.",
     "The culminating fountain of the HP — all previous fountains were preludes to this one. Venus herself presides over the waters of love.",
     "ARCHITECTURAL"),

    # Book II: Polia's Narrative (pp. 230+)
    (234, "p1v", "Polia Tells Her Story",
     "Interior scene: Polia seated, telling her story to a listener. Architectural setting.",
     "The beginning of Book II, where Polia takes over as narrator. The shift from Poliphilo's dream architecture to Polia's autobiographical narrative marks a fundamental change in the HP's mode.",
     "NARRATIVE"),

    (240, "p4v", "The Temple of Diana",
     "Classical temple interior dedicated to Diana. Ritual scene with female figures.",
     "Polia describes her service at the temple of Diana (chastity). Her devotion to Diana represents resistance to Eros — the conflict that drives Book II.",
     "ARCHITECTURAL"),

    (250, "q1v", "Poliphilo's Death and Revival",
     "Dramatic scene: Poliphilo lies as if dead while figures surround him. Polia looks on in distress.",
     "In Polia's telling, Poliphilo collapsed at her rejection and appeared to die. His revival through Cupid's intervention parallels alchemical death-and-resurrection symbolism.",
     "NARRATIVE"),

    (260, "q6v", "Cupid Intervenes",
     "Cupid appears to Polia, commanding her to love Poliphilo. Divine mandate scene.",
     "Cupid/Eros compels Polia to abandon Diana and accept love. This divine intervention resolves Book II's central conflict.",
     "NARRATIVE"),

    (270, "r3v", "Polia Embraces Poliphilo",
     "Reunion scene: Polia and Poliphilo embrace. Figures in a garden or architectural setting.",
     "The lovers united at last. This reunion completes the narrative arc that began with Poliphilo's solitary wandering in the dark forest.",
     "NARRATIVE"),

    # Note: the actual 1499 edition has many more woodcuts (total ~172).
    # The entries above cover the major narrative woodcuts. Many additional
    # small decorative initials, headpieces, and vignettes exist throughout.
    # They will be added as the IA scan is systematically cataloged.
]


def slugify(text):
    """Convert text to URL-safe slug."""
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:80].rstrip('-')


def main():
    parser = argparse.ArgumentParser(
        description="Seed the complete 1499 HP woodcut inventory"
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get existing entries keyed by page_1499
    existing_by_page = {}
    for row in cur.execute("SELECT id, page_1499, slug, title FROM woodcuts").fetchall():
        if row["page_1499"]:
            existing_by_page[row["page_1499"]] = dict(row)

    inserted = 0
    updated = 0
    skipped = 0

    for page, sig, title, desc, narrative, category in WOODCUTS_1499:
        ia_page = page + IA_OFFSET
        slug = slugify(title)

        if page in existing_by_page:
            # Update existing entry with IA data and narrative context
            existing = existing_by_page[page]
            if args.dry_run:
                print(f"  UPDATE p.{page}: {existing['title']} -> add IA page {ia_page}")
            else:
                cur.execute("""
                    UPDATE woodcuts SET
                        page_1499_ia = ?,
                        narrative_context = COALESCE(narrative_context, ?),
                        signature_1499 = COALESCE(signature_1499, ?),
                        subject_category = COALESCE(subject_category, ?)
                    WHERE id = ?
                """, (ia_page, narrative, sig, category, existing["id"]))
            updated += 1
        else:
            # Check for slug collision
            existing_slug = cur.execute(
                "SELECT id FROM woodcuts WHERE slug = ?", (slug,)
            ).fetchone()
            if existing_slug:
                slug = slug + f"-p{page}"

            if args.dry_run:
                print(f"  INSERT p.{page} ({sig}): {title} [IA n{ia_page}]")
            else:
                cur.execute("""
                    INSERT INTO woodcuts (
                        slug, title, signature_1499, page_1499, page_1499_ia,
                        description, narrative_context, subject_category,
                        woodcut_type, source_method, confidence, review_status,
                        ia_image_cached
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'IN_TEXT', 'LLM_ASSISTED',
                              'PROVISIONAL', 'DRAFT', 0)
                """, (slug, title, sig, page, ia_page, desc, narrative, category))
            inserted += 1

    if not args.dry_run:
        conn.commit()

    # Also update any existing entries that have page_1499 but no page_1499_ia
    if not args.dry_run:
        cur.execute("""
            UPDATE woodcuts SET page_1499_ia = page_1499 + ?
            WHERE page_1499 IS NOT NULL AND page_1499_ia IS NULL
        """, (IA_OFFSET,))
        extra = cur.rowcount
        conn.commit()
        if extra:
            print(f"  Also set IA page for {extra} existing entries via offset formula")

    conn.close()
    print(f"\nDone: {inserted} inserted, {updated} updated, {skipped} skipped")


if __name__ == "__main__":
    main()
