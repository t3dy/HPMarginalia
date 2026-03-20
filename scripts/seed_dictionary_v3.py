"""Seed additional HP entity terms — third expansion wave.

Adds terms for: narrative structures, specific woodcuts, editions/translations,
scholarly methodology, and concepts that fill gaps in existing categories.

Idempotent: uses INSERT OR IGNORE.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

# Categories
CHARS = "Characters & Figures"
PLACES = "Places & Settings"
BUILT = "Architecture & Built Form"
GARDEN = "Gardens & Landscape"
PROC = "Processions & Ritual"
VISUAL = "Visual & Typographic"
AESTH = "Aesthetic Concepts"
MATERIAL = "Material Culture"
BOOK = "Book History & Bibliography"
TEXT = "Textual & Visual Motifs"
ANNOT = "Annotation Studies"
ALCHEM = "Alchemical Interpretation"
DEBATE = "Scholarly Debates"
NARR = "Narrative & Literary Form"

TERMS = [
    # === Narrative & Literary Form (new category) ===
    {
        "slug": "dream-vision",
        "label": "Dream Vision",
        "category": NARR,
        "definition_short": "A literary genre in which the narrator falls asleep and experiences a visionary journey, to which the HP belongs.",
        "definition_long": "The dream vision is a medieval and early modern literary genre in which the narrator falls asleep and undergoes a guided journey through an allegorical landscape. The HP belongs to this tradition alongside the Roman de la Rose, Dante's Commedia, and Chaucer's Book of the Duchess. The genre provides a license for mixing registers (erotic, philosophical, architectural) and for encounters with allegorical figures that would be implausible in a realistic narrative frame. Priki (2016) places the HP's double dream within this comparative tradition.",
        "source_basis": "Priki 2016; Gollnick 1999; Agamben 1984",
    },
    {
        "slug": "petrarchism",
        "label": "Petrarchism",
        "category": NARR,
        "definition_short": "The literary tradition of imitating Petrarch's love poetry, whose conventions the HP adapts into a prose-image hybrid.",
        "definition_long": "Petrarchism — the tradition of imitating Petrarch's Canzoniere — provides the HP with its central love vocabulary: the distant beloved, the suffering lover, the transformative power of beauty, and the interplay of desire and frustration. Trippe (2002) argues that the HP adapts these Petrarchan conventions from lyric poetry into a visual register, translating the beloved's beauty from metaphor into woodcut illustration. The HP's treatment of Polia draws heavily on Petrarchan tropes while exceeding them through narrative and architectural elaboration.",
        "source_basis": "Trippe 2002; Godwin 1999",
    },
    {
        "slug": "roman-de-la-rose",
        "label": "Roman de la Rose",
        "category": NARR,
        "definition_short": "The thirteenth-century French allegorical poem that is the HP's most important literary predecessor in the dream-vision genre.",
        "definition_long": "The Roman de la Rose (c. 1230-1275), by Guillaume de Lorris and Jean de Meun, is the foundational European dream-vision allegory. Like the HP, it combines a love quest with encyclopedic digressions and allegorical encounters in a garden setting. Priki (2016) places the HP within a lineage running from the Roman de la Rose through the HP to later dream narratives, arguing that both texts use the dream frame to enable pedagogical encounters that prepare the dreamer for union with the beloved.",
        "source_basis": "Priki 2016; Godwin 1999",
    },
    {
        "slug": "neoplatonism",
        "label": "Neoplatonism",
        "category": NARR,
        "definition_short": "The philosophical tradition of Plotinus and Ficino that informs the HP's treatment of beauty, love, and ascent from sensory experience to intellectual vision.",
        "definition_long": "Neoplatonic philosophy pervades the HP's structure and imagery. Poliphilo's journey from the dark forest through sensory initiation to union with Polia on Cythera enacts a Neoplatonic ascent from material confusion to intellectual clarity. The five nymphs represent the senses as stages in this ascent. The circular garden of Cythera embodies the Neoplatonic emanation from the One. The HP's combination of erotic desire and philosophical aspiration reflects Ficino's reading of Platonic eros as the soul's drive toward beauty and truth.",
        "source_basis": "Lefaivre 1997; Godwin 1999; Gollnick 1999",
    },

    # === More Characters ===
    {
        "slug": "logistica-thelemia",
        "label": "Logistica and Thelemia",
        "category": CHARS,
        "definition_short": "Two allegorical figures representing reason (Logistica) and desire/will (Thelemia) who guide Poliphilo at a critical juncture.",
        "definition_long": "At a key narrative moment, Poliphilo encounters two female figures: Logistica (reason, calculation) and Thelemia (will, desire). They represent the competing claims of rational judgment and passionate aspiration. Poliphilo must navigate between them, and his choice reflects the HP's humanist conviction that neither pure reason nor pure desire suffices — both must be integrated. The pairing echoes the three gates of Thelemia (vita contemplativa, vita activa, vita voluptuosa) and the broader Renaissance discourse on free will.",
        "source_basis": "HP; Godwin 1999; Lefaivre 1997",
    },

    # === More Architecture ===
    {
        "slug": "colossus",
        "label": "Colossus",
        "category": BUILT,
        "definition_short": "A gigantic figure or statue encountered by Poliphilo, described with measurements evoking the Colossus of Rhodes.",
        "definition_long": "Poliphilo encounters colossal statues and figures that evoke the ancient Wonders of the World, particularly the Colossus of Rhodes. These passages demonstrate the HP's interest in extreme scale as a vehicle for meraviglia (wonder). The colossal figures are described with precise measurements, combining the awe of gigantism with the rationality of architectural proportion. They represent the HP's characteristic fusion of the marvelous and the measurable.",
        "source_basis": "HP; Godwin 1999",
    },
    {
        "slug": "mosaic",
        "label": "Mosaic",
        "category": BUILT,
        "definition_short": "Intricate floor and wall mosaics described in the HP, depicting mythological scenes in tessellated stone and glass.",
        "definition_long": "The HP describes elaborate mosaic work on floors, walls, and ceilings of the buildings Poliphilo explores. These mosaics depict mythological scenes, geometric patterns, and symbolic imagery. Poliphilo reads them as visual texts, interpreting their iconography alongside their material composition. The mosaic passages contribute to the HP's broader interest in surfaces that carry meaning — inscribed, painted, carved, or tessellated.",
        "source_basis": "HP; Godwin 1999; Stewering 2000",
    },

    # === More Visual/Typographic ===
    {
        "slug": "colophon",
        "label": "Colophon",
        "category": BOOK,
        "definition_short": "The printed statement at the end of the 1499 HP identifying the printer (Aldus), place (Venice), and date (December 1499).",
        "definition_long": "The 1499 HP ends with a colophon identifying the book as printed in Venice by Aldus Manutius in December 1499. The colophon is one of the few paratextual elements that provides external evidence about the book's production. It confirms the date and printer but does not name the author, leaving the authorship question dependent on internal evidence like the acrostic and stylistic analysis.",
        "source_basis": "HP colophon; Painter 1963; Farrington 2015",
    },
    {
        "slug": "world-census",
        "label": "World Census of Annotated Copies",
        "category": ANNOT,
        "definition_short": "Russell's systematic survey identifying all known annotated copies of the HP, conducted through ISTC records and institutional catalogs.",
        "definition_long": "Russell's world census of annotated HP copies involved searching the Incunabula Short Title Catalogue (ISTC) and contacting holding institutions worldwide to identify copies bearing manuscript annotations. From this census he selected six copies for detailed study, encompassing eleven distinct annotator hands. The census methodology — systematic, institutionally grounded, and reproducible — established the evidentiary foundation for his annotation studies.",
        "source_basis": "Russell 2014, Ch. 1-2",
    },

    # === Aesthetic/Intellectual ===
    {
        "slug": "ut-pictura-poesis",
        "label": "Ut Pictura Poesis",
        "category": AESTH,
        "definition_short": "The classical principle 'as painting, so poetry' — the interchangeability of verbal and visual art — which the HP embodies.",
        "definition_long": "The Horatian principle ut pictura poesis ('as painting, so poetry') asserts a fundamental analogy between visual and verbal art. The HP takes this principle further than perhaps any other Renaissance text: its 172 woodcuts are not subordinate illustrations but integral components of the work, and its verbal descriptions aspire to the vividness of painting. Trippe (2002) and Priki analyze how the HP negotiates the text-image boundary, making ut pictura poesis a structural rather than merely theoretical commitment.",
        "source_basis": "Trippe 2002; Priki; Horace, Ars Poetica",
    },
    {
        "slug": "horror-vacui",
        "label": "Horror Vacui",
        "category": AESTH,
        "definition_short": "The aesthetic tendency to fill every available surface with ornament, characteristic of the HP's descriptive and visual density.",
        "definition_long": "The HP exhibits a pronounced horror vacui — an aversion to empty space — in both its verbal descriptions and its woodcut illustrations. Every surface Poliphilo encounters is carved, inscribed, painted, or planted. Every page of text is dense with description, digression, and learned vocabulary. This aesthetic density is not accidental but structural: the HP's meaning emerges from accumulation, overlay, and the refusal to leave any surface unworked.",
        "source_basis": "HP passim; Jarzombek 1990",
    },

    # === More Alchemical ===
    {
        "slug": "great-work",
        "label": "Great Work (Magnum Opus)",
        "category": ALCHEM,
        "definition_short": "The alchemical process of transmuting base matter into gold or the philosopher's stone, which both HP alchemist annotators read into the narrative.",
        "definition_long": "The Great Work (magnum opus) is the central goal of alchemy: the transformation of base matter into gold, the philosopher's stone, or the elixir of life. Both the BL and Buffalo alchemist annotators read the HP as encoding stages of the Great Work beneath its love narrative. The BL alchemist followed d'Espagnet's mercury-centered framework; the Buffalo alchemist followed pseudo-Geber's sulphur and Sol/Luna emphasis. In both readings, Poliphilo's journey maps onto the stages of refinement, and his union with Polia represents the successful completion of the Work.",
        "source_basis": "Russell 2014, Ch. 6-7; Perifano 2004",
    },

    # === Material Culture additions ===
    {
        "slug": "gold-leaf",
        "label": "Gold Leaf",
        "category": MATERIAL,
        "definition_short": "Thin sheets of hammered gold used for gilding surfaces, frequently described adorning the HP's architectural interiors.",
        "definition_long": "Gold leaf and gilding appear throughout the HP as markers of supreme luxury and divine association. Poliphilo describes ceilings, columns, and sculptural details covered in gold, specifying the quality of the application and the visual effect of light on gilded surfaces. The alchemical annotators took particular interest in gold references, reading them as encoding the final stage of transmutation.",
        "source_basis": "HP passim; Russell 2014",
    },
    {
        "slug": "silk",
        "label": "Silk",
        "category": MATERIAL,
        "definition_short": "Fine textile featured prominently in the HP's descriptions of clothing, drapery, and ceremonial hangings.",
        "definition_long": "Silk and other fine textiles receive detailed attention in the HP. Poliphilo describes the garments of nymphs, queens, and processional figures with attention to weave, color, drape, and embroidery. These textile descriptions contribute to the HP's tactile and sensory richness, reinforcing the book's investment in material culture as a vehicle for meaning.",
        "source_basis": "HP passim; Godwin 1999",
    },
]

LINKS = [
    # Narrative form
    ("dream-vision", "dream-narrative", "RELATED"),
    ("dream-vision", "dream-within-dream", "RELATED"),
    ("dream-vision", "roman-de-la-rose", "RELATED"),
    ("petrarchism", "vernacular-poetics", "RELATED"),
    ("petrarchism", "polia", "RELATED"),
    ("petrarchism", "ekphrasis", "RELATED"),
    ("roman-de-la-rose", "dream-narrative", "RELATED"),
    ("roman-de-la-rose", "allegory", "RELATED"),
    ("neoplatonism", "venus-aphrodite", "RELATED"),
    ("neoplatonism", "circular-garden", "RELATED"),
    ("neoplatonism", "prisca-sapientia", "RELATED"),

    # Characters
    ("logistica-thelemia", "thelemia", "RELATED"),
    ("logistica-thelemia", "eleuterylida", "RELATED"),

    # Architecture
    ("colossus", "meraviglia", "RELATED"),
    ("colossus", "pyramid", "RELATED"),
    ("mosaic", "grotesque", "RELATED"),
    ("mosaic", "ekphrasis", "RELATED"),

    # Book
    ("colophon", "aldus-manutius", "RELATED"),
    ("colophon", "1499-edition", "RELATED"),
    ("world-census", "annotator-hand", "RELATED"),
    ("world-census", "incunabulum", "RELATED"),

    # Aesthetic
    ("ut-pictura-poesis", "woodcut", "RELATED"),
    ("ut-pictura-poesis", "ekphrasis", "RELATED"),
    ("horror-vacui", "varieta", "RELATED"),
    ("horror-vacui", "grotesque", "RELATED"),

    # Alchemy
    ("great-work", "alchemical-allegory", "RELATED"),
    ("great-work", "master-mercury", "RELATED"),
    ("great-work", "chemical-wedding", "RELATED"),

    # Material
    ("gold-leaf", "porphyry", "RELATED"),
    ("silk", "nymphs-five-senses", "RELATED"),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Seeding HP entity dictionary terms (v3)...")
    inserted = 0
    for t in TERMS:
        cur.execute("""
            INSERT OR IGNORE INTO dictionary_terms
                (slug, label, category, definition_short, definition_long,
                 source_basis, review_status, needs_review, source_method)
            VALUES (?, ?, ?, ?, ?, ?, 'DRAFT', 1, 'LLM_ASSISTED')
        """, (t["slug"], t["label"], t["category"],
              t["definition_short"], t["definition_long"],
              t.get("source_basis", "")))
        inserted += cur.rowcount
    conn.commit()
    print(f"  Inserted {inserted} new terms ({len(TERMS)} defined)")

    print("Creating term links...")
    linked = 0
    for slug_a, slug_b, link_type in LINKS:
        cur.execute("SELECT id FROM dictionary_terms WHERE slug=?", (slug_a,))
        a = cur.fetchone()
        cur.execute("SELECT id FROM dictionary_terms WHERE slug=?", (slug_b,))
        b = cur.fetchone()
        if a and b:
            cur.execute("""
                INSERT OR IGNORE INTO dictionary_term_links
                    (term_id, linked_term_id, link_type)
                VALUES (?, ?, ?)
            """, (a[0], b[0], link_type))
            linked += cur.rowcount
            if link_type == "RELATED":
                cur.execute("""
                    INSERT OR IGNORE INTO dictionary_term_links
                        (term_id, linked_term_id, link_type)
                    VALUES (?, ?, ?)
                """, (b[0], a[0], link_type))
                linked += cur.rowcount
    conn.commit()
    print(f"  Created {linked} links")

    cur.execute("SELECT COUNT(*) FROM dictionary_terms")
    print(f"\nTotal terms: {cur.fetchone()[0]}")
    cur.execute("SELECT category, COUNT(*) FROM dictionary_terms GROUP BY category ORDER BY COUNT(*) DESC")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
