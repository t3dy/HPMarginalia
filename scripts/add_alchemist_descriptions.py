"""Add scholarly descriptions to alchemist-annotated folios.

Sources: Russell 2014, Ch. 6 (BL Hand B / d'Espagnet) and Ch. 7 (Buffalo Hand E / pseudo-Geber).
These descriptions are derived from close reading of Russell's thesis and are tagged
with source_method='LLM_ASSISTED' since the extraction and synthesis was done by Claude
reading Russell's prose, not by Russell himself writing these summaries.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

# Schema addition
SCHEMA = """
CREATE TABLE IF NOT EXISTS folio_descriptions (
    id INTEGER PRIMARY KEY,
    signature_ref TEXT NOT NULL,
    manuscript_shelfmark TEXT,
    hand_label TEXT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    alchemical_element TEXT,
    alchemical_process TEXT,
    alchemical_framework TEXT,
    russell_page_ref TEXT,
    source_method TEXT DEFAULT 'LLM_ASSISTED',
    needs_review BOOLEAN DEFAULT 1,
    UNIQUE(signature_ref, manuscript_shelfmark, hand_label)
);
"""

# BL C.60.o.12 - Hand B (d'Espagnet school)
BL_DESCRIPTIONS = [
    {
        "sig": "flyleaf",
        "hand": "B",
        "ms": "C.60.o.12",
        "title": "The Alchemist's Manifesto: 'Master Mercury'",
        "description": (
            "On the flyleaf verso, the anonymous alchemist lays out his entire interpretive "
            "framework in a programmatic summary: 'verus sensus intentionis huius libri est "
            "3um: Geni et Totius Naturae energiae & operationum Magisteri Mercurii Descriptio "
            "elegans, ampla' -- the HP's true sense is threefold: the full and elegant "
            "description of the generation of all nature, its energies, and the operations of "
            "'Master Mercury.' This Rosetta Stone for all subsequent annotations identifies "
            "quicksilver as the supreme operative principle, reflecting Jean d'Espagnet's "
            "Enchiridion Physicae Restitutae, where mercury is the vehicle of the world spirit "
            "continuously emanating from the Sun."
        ),
        "element": "Mercury (Master Mercury / Magisteri Mercurii)",
        "process": "Universal generation and spirit-matter mediation",
        "framework": "d'Espagnet: mercury as vehicle of spiritus mundi",
        "page": "pp. 159-160",
    },
    {
        "sig": "a1r",
        "hand": "B",
        "ms": "C.60.o.12",
        "title": "Dawn as Albedo: The Sun's First Emanation",
        "description": (
            "At the opening of Poliphilo's narrative, Hand B annotates the dawn scene "
            "with careful precision: 'Tempus ergo matutinum erat, sine diluculo, uel "
            "crepusculum' (It was the early morning, before dawn, or later in the evening). "
            "This is not mere translation. The annotator identifies the exact solar position -- "
            "the moment before the sun crests the horizon -- because in d'Espagnet's framework, "
            "the sun is the origin of the world spirit whose emanations are most potent at dawn. "
            "The passage heading is labeled 'AURORAE DESCRIPTIO' (Description of the Dawn). "
            "Hand B also notes the etymology of Leucothea: 'Leucos albus, candidus' -- white, "
            "bright -- connecting the dawn goddess to the alchemical stage of Albedo (whitening)."
        ),
        "element": "Sol (Sun) and Albedo (whitening stage)",
        "process": "Solar emanation at dawn; beginning of the Work",
        "framework": "d'Espagnet: sun as source of world spirit",
        "page": "pp. 165-166",
    },
    {
        "sig": "a3r",
        "hand": "B",
        "ms": "C.60.o.12",
        "title": "The HP as Alchemical Treatise",
        "description": (
            "Hand B recognized that the HP's own dedicatory letter mirrors the conventions "
            "of alchemical texts. The letter claims the book is written so that 'none but the "
            "most learned should be able to penetrate the inner sanctum of his teaching' -- "
            "language directly paralleling the alchemical tradition of deliberate obscurantism, "
            "where knowledge is veiled 'so that it might not come to the attention of the "
            "greedy and the insane.' For a reader steeped in the prisca sapientia (ancient "
            "wisdom), the HP's extreme linguistic difficulty was not a flaw but a guarantee "
            "of hidden knowledge. The more incomprehensible the text, the more ancient wisdom "
            "it was understood to contain."
        ),
        "element": "Prisca sapientia (ancient wisdom)",
        "process": "Horizon of expectation; alchemical hermeneutics",
        "framework": "d'Espagnet: obscurantism as marker of authenticity",
        "page": "pp. 155-156",
    },
    {
        "sig": "a4r",
        "hand": "B",
        "ms": "C.60.o.12",
        "title": "Jupiter's Titles: Planetary Hierarchy",
        "description": (
            "Hand B extracts Poliphilo's invocation to Jupiter, transcribing the god's "
            "divine titles into a hierarchical list on the flyleaf: 'O Diespiter, Maximo, "
            "Optimo, & Omnipotente & Opitulo...' Jupiter rules the higher, middle, and "
            "lower realms. In alchemical metals, Jupiter corresponds to tin. The annotator's "
            "interest in Jupiter's cosmic hierarchy maps onto the Hermetic principle 'as above, "
            "so below' -- the resonance between celestial order and material transformation "
            "that underpins all alchemical practice."
        ),
        "element": "Jupiter / Tin",
        "process": "Planetary-metal correspondence; cosmic hierarchy",
        "framework": "d'Espagnet: Hermetic resonance between realms",
        "page": "p. 167",
    },
    {
        "sig": "b6v",
        "hand": "B",
        "ms": "C.60.o.12",
        "title": "Elephant and Obelisk: Ideograms in Syntax",
        "description": (
            "The famous woodcut of the elephant bearing an obelisk -- later realized by "
            "Bernini in the Piazza della Minerva for Pope Alexander VII -- is densely annotated "
            "by Hand B with alchemical ideograms embedded directly in the syntax of Latin "
            "sentences. The sun symbol with the suffix '-ra' reads 'scintillata aurata' "
            "(shimmering gold). These are not marginal glosses but a complete symbolic language: "
            "compact symbols for gold, silver, mercury, Venus, and Jupiter carry Latin case "
            "endings, allowing them to function as nouns and adjectives within grammatical "
            "sentences. Russell notes the consistency with Newton's Keynes MSS vocabulary, "
            "suggesting a possible connection to the Royal Society or Cambridge alchemical circle."
        ),
        "element": "Multiple metals: Gold, Silver, Mercury, Venus, Jupiter",
        "process": "Ideographic decipherment of the printed text",
        "framework": "d'Espagnet: standardized ideographic vocabulary",
        "page": "pp. 156-158",
    },
    {
        "sig": "d8v",
        "hand": "B",
        "ms": "C.60.o.12",
        "title": "Panta Tokadi: Mercury as Universal Vessel",
        "description": (
            "Facing the Panta Tokadi woodcut, Hand B translates the phrase as 'rerum omnium "
            "vas' -- vessel of all things -- rather than 'mother of all,' as Godwin translates "
            "it. This deliberate shift from biological generation to instrumental containment "
            "equates the Panta Tokadi figure directly with Mercury: not a passive mother but "
            "an active vessel through which the world spirit is channeled into matter. "
            "The annotation reflects d'Espagnet's concept of the 'magnetick principle' -- "
            "the force by which mercury draws the animating spirit of the sun into the "
            "vessels of physical matter."
        ),
        "element": "Mercury as universal vessel (vas)",
        "process": "Spirit-matter mediation via mercury",
        "framework": "d'Espagnet: magnetick principle; mercury as conduit",
        "page": "pp. 164-165",
    },
    {
        "sig": "e1r",
        "hand": "B",
        "ms": "C.60.o.12",
        "title": "Panta Tokadi: Cinnabar, Digestion, and the World Spirit",
        "description": (
            "The Panto Tokadi woodcut -- a satyr revealing a mother figure flanked by two fauns "
            "bearing vessels -- receives Hand B's most elaborate alchemical annotation. The mercury "
            "symbol appears on the top frieze and above the right faun's vessel. The left faun "
            "bears the cinnabar symbol (mercury sulphide). Below the caption, B writes: 'duae "
            "columbae in uno vase bibentes sunt minium & digestione' -- the two doves drinking "
            "in one vase represent cinnabar and digestion. The streams of milk from the mother's "
            "nipples signify the generation of all things through mercury's magnetick principle. "
            "This is the key annotation revealing Hand B's d'Espagnet-based schema at full power."
        ),
        "element": "Mercury, Cinnabar (mercury sulphide), Digestion",
        "process": "Emanation of world spirit; generation through mercury",
        "framework": "d'Espagnet: sun's outpouring of animating energy via mercury",
        "page": "pp. 163-165",
    },
    {
        "sig": "E8v",
        "hand": "B",
        "ms": "C.60.o.12",
        "title": "Venus Persists: The Alchemist's Stamina",
        "description": (
            "Deep into Book II -- where most annotators' energy has long since flagged -- "
            "Hand B is still at work, replacing the goddess Venus's name with her alchemical "
            "symbol: the text reads 'Veneris' but the annotation substitutes the Venus/copper "
            "ideogram with the Latin case ending '-eris' appended. Russell observes that this "
            "demonstrates the alchemist's remarkable persistence: 'notes decline in frequency "
            "and alchemical significance in Book II' but the symbolic vocabulary is maintained "
            "to the end. Venus (copper) is the feminine planetary metal in the d'Espagnet system."
        ),
        "element": "Venus / Copper (feminine planetary metal)",
        "process": "Persistent symbolic substitution through Book II",
        "framework": "d'Espagnet: planetary-metal associations maintained throughout",
        "page": "p. 157",
    },
    {
        "sig": "y7r",
        "hand": "B",
        "ms": "C.60.o.12",
        "title": "Fons Heptagonis: The Seven Metals",
        "description": (
            "The illustration of the heptagonal fountain -- seven-sided, with seven angles -- "
            "is labeled by Hand B with the alchemical sign of a different element at each angle. "
            "The seven metals correspond to the seven classical planets: gold/Sun, silver/Moon, "
            "mercury/Mercury, copper/Venus, iron/Mars, tin/Jupiter, lead/Saturn. This systematic "
            "labeling transforms the decorative fountain into a diagram of the complete "
            "alchemical cosmos, with each planetary metal occupying its proper position. "
            "The annotator labels the fountain 'frogg green' (in English, confirming his "
            "nationality), apparently describing the color of the ink or the patina."
        ),
        "element": "All seven planetary metals",
        "process": "Complete cosmological mapping of the alchemical system",
        "framework": "d'Espagnet: planetary-metal correspondence system",
        "page": "p. 136",
    },
]

# Buffalo - Hand E (pseudo-Geber school)
BUFFALO_DESCRIPTIONS = [
    {
        "sig": "b7r",
        "hand": "E",
        "ms": "Buffalo RBR",
        "title": "Geber's Ingenium: Opening the Alchemical Reading",
        "description": (
            "At the episode of the elephant and obelisk, with its statues of a crowned king "
            "and queen, Hand E establishes the interpretive framework for everything that "
            "follows. Under the motto 'Gonos et Euphyia' (Labor and Industry), the annotator "
            "praises Geber's 'ingenium subtile' (subtle ingenuity) -- declaring that the HP "
            "will be read within a Geberian framework. Labor and industry are the essential "
            "virtues of the alchemist, whose work might involve distilling the same substance "
            "hundreds of times. The king and queen statues 'easily commend themselves to "
            "reading along the lines of Geber,' where the masculine principle (Sol/Gold) and "
            "the feminine principle (Luna/Silver) are interconnected inverses."
        ),
        "element": "Sol/Luna (Gold/Silver) as gendered principles",
        "process": "Initiation of Geberian reading; framework declaration",
        "framework": "pseudo-Geber: Summa Perfectionis methodology",
        "page": "pp. 187-188",
    },
    {
        "sig": "c6v",
        "hand": "E",
        "ms": "Buffalo RBR",
        "title": "Bacchus and Demeter: The Chemical Wedding Encoded",
        "description": (
            "Poliphilo views a Greek epigram: 'to the blessed Mother, the Goddess Venus, "
            "and to her Son, Amor, Bacchus and Demeter have given of their own substances.' "
            "Hand E cuts directly to the alchemical meaning: 'Bacchus et Ceres [Demeter] "
            "id est sol et luna' -- Bacchus and Demeter ARE Sol and Luna. Hand D elaborates "
            "that 'Bacchus was believed by the ancients to be that hidden virtue which helps "
            "plants to produce mature fruits.' But for the alchemist, the mythological pairing "
            "encodes the chemical wedding -- the union of masculine (Sol/gold) and feminine "
            "(Luna/silver) principles that produces the philosopher's stone."
        ),
        "element": "Sol/Luna identified as Bacchus/Demeter",
        "process": "Chemical wedding; union of masculine and feminine metals",
        "framework": "pseudo-Geber: mythological coding of the Great Work",
        "page": "pp. 187-188",
    },
    {
        "sig": "h1r",
        "hand": "E",
        "ms": "Buffalo RBR",
        "title": "The Chess Match: Three Rounds of Distillation",
        "description": (
            "The HP's elaborate chess match between 32 maidens (16 silver, 16 gold) becomes, "
            "in Hand E's reading, an allegory of iterative alchemical refinement. In Round 1, "
            "silver wins: the annotator writes 'Argentum' with a crescent moon sketch and "
            "'Rex ex argento factus victor remanet' (The king made of silver remains victor). "
            "Round 2: silver wins again. Round 3: gold finally triumphs -- but E's annotation "
            "undergoes a telling correction. He first writes 'Rex ex auro' (king of gold), "
            "then revises to 'Regina' (queen) and 'aura' and 'victrix' (feminine victor), "
            "with the sun symbol. The final word is 'Auru(m)' -- Gold, the perfected metal. "
            "The correction reveals E recognizing the hermaphroditic outcome: the triumphant "
            "figure combines king and queen, masculine and feminine, Sol and Luna."
        ),
        "element": "Silver (Luna) yielding to Gold (Sol); Hermaphrodite",
        "process": "Iterative distillation (three rounds); coincidentia oppositorum",
        "framework": "pseudo-Geber: transmutation through repeated refinement",
        "page": "pp. 189-190",
    },
    {
        "sig": "b5r",
        "hand": "E",
        "ms": "Buffalo RBR",
        "title": "The Ambiguous Gods: Alchemical Hermaphrodites",
        "description": (
            "An epigram reading 'D.AMBIG.DD' -- 'dedicated to the ambiguous gods' -- "
            "triggers Hand E's most explicit statement of Geberian theory. The annotation "
            "reads: 'diis ambiguis id est metallis hermafroditis guarda enim metalla sunt "
            "mas et foemina... aura-argentu enim in sua altitudine mas est in sua profunda "
            "foeminina argentum vero in sua altitudine est foemininum in suo profundo mas.' "
            "The 'ambiguous gods' are metals that possess both genders: gold is masculine "
            "'in its height' but feminine 'in its depth'; silver is feminine in its height "
            "but masculine in its depth. This paradoxical gender-inversion is the fundamental "
            "principle of pseudo-Geber's system -- the engine that makes transmutation possible."
        ),
        "element": "Hermaphroditic metals (Gold-Silver gender inversion)",
        "process": "Coincidentia oppositorum; gender-inversion as transmutation principle",
        "framework": "pseudo-Geber: metals as masculine-feminine inverses",
        "page": "p. 190",
    },
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Creating folio_descriptions table...")
    cur.executescript(SCHEMA)
    conn.commit()

    print("Inserting BL alchemist descriptions (Hand B, d'Espagnet)...")
    bl_count = 0
    for d in BL_DESCRIPTIONS:
        cur.execute("""
            INSERT OR REPLACE INTO folio_descriptions
                (signature_ref, manuscript_shelfmark, hand_label, title,
                 description, alchemical_element, alchemical_process,
                 alchemical_framework, russell_page_ref, source_method, needs_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'LLM_ASSISTED', 1)
        """, (d["sig"], d["ms"], d["hand"], d["title"], d["description"],
              d["element"], d["process"], d["framework"], d["page"]))
        bl_count += 1
    conn.commit()
    print(f"  {bl_count} BL descriptions inserted")

    print("Inserting Buffalo alchemist descriptions (Hand E, pseudo-Geber)...")
    buf_count = 0
    for d in BUFFALO_DESCRIPTIONS:
        cur.execute("""
            INSERT OR REPLACE INTO folio_descriptions
                (signature_ref, manuscript_shelfmark, hand_label, title,
                 description, alchemical_element, alchemical_process,
                 alchemical_framework, russell_page_ref, source_method, needs_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'LLM_ASSISTED', 1)
        """, (d["sig"], d["ms"], d["hand"], d["title"], d["description"],
              d["element"], d["process"], d["framework"], d["page"]))
        buf_count += 1
    conn.commit()
    print(f"  {buf_count} Buffalo descriptions inserted")

    print(f"\nTotal: {bl_count + buf_count} alchemist folio descriptions")
    conn.close()


if __name__ == "__main__":
    main()
