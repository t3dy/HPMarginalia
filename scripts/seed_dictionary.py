"""Seed the dictionary_terms table with 35+ core HP terminology entries."""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

# Category constants
BOOK = "Book History & Bibliography"
TEXT = "Textual & Visual Motifs"
ANNOT = "Annotation Studies"
ALCHEM = "Alchemical Interpretation"
ARCH = "Architecture & Gardens"
DEBATE = "Scholarly Debates"

TERMS = [
    # === Book History & Bibliography ===
    {
        "slug": "signature",
        "label": "Signature",
        "category": BOOK,
        "definition_short": "A letter-number code printed at the foot of certain pages to guide the binder in assembling the book.",
        "definition_long": "In early printed books, signatures are marks (usually a lowercase letter followed by a numeral) placed at the bottom of the first recto of each leaf in a gathering. The 1499 HP uses signatures a-z (omitting j, u, w) then A-G, each gathering consisting of eight leaves. Russell's thesis references folios by signature (e.g., b6v) rather than by page number, since no page numbers were printed in the original.",
        "source_basis": "Standard bibliographic terminology; Russell 2014 passim",
    },
    {
        "slug": "quire",
        "label": "Quire",
        "category": BOOK,
        "definition_short": "A section of a book made from sheets folded together, also called a gathering.",
        "definition_long": "A quire (or gathering) is the basic structural unit of a bound book. In the HP, each quire consists of a single large sheet folded to produce eight leaves (sixteen pages). The quire is identified by its signature letter: quire 'a' contains leaves a1-a8, quire 'b' contains b1-b8, and so on. The collation formula of the 1499 HP describes this structure systematically.",
        "source_basis": "Standard bibliographic terminology",
    },
    {
        "slug": "folio",
        "label": "Folio",
        "category": BOOK,
        "definition_short": "A single leaf of a book, having two sides: recto (front) and verso (back).",
        "definition_long": "In bibliographic usage, 'folio' refers to a leaf rather than a page. Each folio has two sides. In the HP, folio references combine a signature with a side designation: 'b6v' means the verso (back) of the sixth leaf in quire b. The Siena digital facsimile photographs are labeled by folio number with recto/verso suffixes (e.g., O.III.38_0014r.jpg).",
        "source_basis": "Standard bibliographic terminology",
    },
    {
        "slug": "recto",
        "label": "Recto",
        "category": BOOK,
        "definition_short": "The front side of a leaf, conventionally the right-hand page when the book lies open.",
        "definition_long": "Abbreviated 'r' in signature references (e.g., a1r). In the HP's original layout, most woodcuts appear on the recto. The recto is the side that would have been printed first in the press.",
        "source_basis": "Standard bibliographic terminology",
    },
    {
        "slug": "verso",
        "label": "Verso",
        "category": BOOK,
        "definition_short": "The back side of a leaf, conventionally the left-hand page when the book lies open.",
        "definition_long": "Abbreviated 'v' in signature references (e.g., b6v). Some of the most important marginal annotations in the BL copy appear on versos facing significant woodcuts on the following recto.",
        "source_basis": "Standard bibliographic terminology",
    },
    {
        "slug": "gathering",
        "label": "Gathering",
        "category": BOOK,
        "definition_short": "A group of leaves folded together to form a section of a book; synonym for quire.",
        "definition_long": "The HP's gatherings are quaternions (four sheets folded to make eight leaves). The 1499 edition consists of approximately 29 gatherings (a-z then A-G, with some irregular final gatherings). The regularity of this structure is what makes the signature map a reliable concordance tool.",
        "source_basis": "Standard bibliographic terminology; build_signature_map.py",
    },
    {
        "slug": "collation",
        "label": "Collation",
        "category": BOOK,
        "definition_short": "A formula describing the physical structure of a printed book: how many gatherings, how many leaves per gathering.",
        "definition_long": "The collation formula for the 1499 HP is: a-z8 A-F8 G6 (with j, u, w omitted from the lowercase alphabet). This means 26 gatherings of 8 leaves each, plus 7 uppercase gatherings. The formula allows bibliographers to detect missing or inserted leaves. Harris (2002) used collation analysis to identify typographical anomalies in the HP's woodcuts.",
        "source_basis": "Harris 2002; standard bibliographic terminology",
    },
    {
        "slug": "incunabulum",
        "label": "Incunabulum",
        "category": BOOK,
        "definition_short": "A book printed before 1501, during the infancy of European printing.",
        "definition_long": "The 1499 HP is an incunabulum (plural: incunabula), produced in the last year of the fifteenth century. It is catalogued in the Incunabula Short Title Catalogue (ISTC) maintained by the British Library. Russell's world census was conducted primarily through ISTC records. The HP is widely regarded as the most elaborately illustrated incunabulum ever produced.",
        "source_basis": "Russell 2014, p. 16; Painter 1963",
    },
    {
        "slug": "woodcut",
        "label": "Woodcut",
        "category": TEXT,
        "definition_short": "An illustration printed from a carved wooden block, integral to the HP's text-image program.",
        "definition_long": "The 1499 HP contains 172 woodcut illustrations, attributed to an unidentified artist sometimes called the 'Master of the Poliphilo.' The woodcuts are integrated into the text in a manner unprecedented for the period, with images appearing mid-page within the flow of prose. The 1545 edition recast the woodcuts using new blocks. Huelsen (1910) provided the first systematic study of their architectural sources. Priki (2012) analyzed how the text-image relationship shifts across editions.",
        "source_basis": "Huelsen 1910; Priki 2012; Painter 1963",
    },

    # === Annotation Studies ===
    {
        "slug": "marginalia",
        "label": "Marginalia",
        "category": ANNOT,
        "definition_short": "Handwritten notes in the margins of a printed book, recording a reader's responses to the text.",
        "definition_long": "Russell's thesis documents marginalia in six copies of the HP, showing that the book was actively read and annotated by diverse readers including humanists, playwrights, a pope, and alchemists. The marginalia range from simple underlines and source identifications to elaborate alchemical decipherments and cross-references to other works. Russell frames the annotated HP as a 'humanistic activity book' in which readers cultivated their ingegno through playful engagement.",
        "source_basis": "Russell 2014 passim; Sherman 2007",
    },
    {
        "slug": "annotator-hand",
        "label": "Annotator Hand",
        "category": ANNOT,
        "definition_short": "A distinct handwriting identified in a manuscript or printed book, attributed to a specific reader.",
        "definition_long": "Russell identified 11 distinct annotator hands across 6 copies of the HP. Distinguishing hands involves analyzing ink color, language, ductus (letter formation), content focus, and stratigraphic relationships (which hand overwrites which). The BL copy bears two hands: Ben Jonson (Hand A) and an anonymous alchemist (Hand B). The Buffalo copy has five interleaved hands (A-E).",
        "source_basis": "Russell 2014, Ch. 6-9",
    },
    {
        "slug": "acrostic",
        "label": "Acrostic",
        "category": TEXT,
        "definition_short": "A text in which the initial letters of each section spell out a hidden message.",
        "definition_long": "The HP's chapter initials spell POLIAM FRATER FRANCISCVS COLVMNA PERAMAVIT ('Brother Francesco Colonna loved Polia greatly'). This acrostic is the primary evidence for attributing authorship to a Dominican friar named Francesco Colonna. However, the acrostic has been contested: Lefaivre (1997) argued it could have been inserted by someone other than the author, and proposed Leon Battista Alberti as the true author. The acrostic does not resolve which Francesco Colonna is meant, leading to the long-running authorship debate.",
        "source_basis": "Casella & Pozzi 1959; Lefaivre 1997; Russell 2014, p. 8",
    },
    {
        "slug": "hieroglyph",
        "label": "Hieroglyph",
        "category": TEXT,
        "definition_short": "A picture-writing system; in the HP, pseudo-Egyptian symbolic inscriptions that Poliphilo encounters and interprets.",
        "definition_long": "The HP contains numerous pseudo-hieroglyphic inscriptions that Poliphilo deciphers during his journey. These are not authentic Egyptian hieroglyphs but Renaissance inventions inspired by the rediscovery of Horapollo's Hieroglyphica. Curran (1998) situates them within fifteenth-century humanist Egyptology. Priki analyzes their narrative function, arguing they serve as structural devices within the dream journey rather than mere antiquarian decoration. The hieroglyphs influenced the later emblem tradition.",
        "source_basis": "Curran 1998; Priki (undated); Gombrich 1972",
    },
    {
        "slug": "emblem",
        "label": "Emblem",
        "category": TEXT,
        "definition_short": "A combination of image, motto, and explanatory text; a genre that the HP helped to inaugurate.",
        "definition_long": "The emblem tradition, formalized by Andrea Alciato in 1531, combined a motto (inscriptio), an image (pictura), and an explanatory verse (subscriptio). The HP's hieroglyphic woodcuts, which pair symbolic images with interpretive text, are widely considered proto-emblematic. The book's influence on Alciato and subsequent emblem books has been documented by Gombrich and others.",
        "source_basis": "Gombrich 1972; Caruso 2004",
    },
    {
        "slug": "ekphrasis",
        "label": "Ekphrasis",
        "category": TEXT,
        "definition_short": "A vivid verbal description of a visual work of art, used extensively throughout the HP.",
        "definition_long": "Much of the HP consists of elaborate ekphrastic descriptions: Poliphilo encounters buildings, sculptures, fountains, gardens, and processions, each described in painstaking visual detail. These descriptions serve multiple functions: they display the author's antiquarian learning, provide material for the woodcut illustrations, and create the immersive dream-atmosphere. Trippe (2002) argues these ekphrases adapt Petrarchan conventions of lyric poetry into a visual register.",
        "source_basis": "Trippe 2002; Stewering 2000",
    },

    # === Alchemical Interpretation ===
    {
        "slug": "alchemical-allegory",
        "label": "Alchemical Allegory",
        "category": ALCHEM,
        "definition_short": "The interpretation of the HP as encoding alchemical processes beneath its love narrative.",
        "definition_long": "Two annotators in Russell's study -- Hand B in the BL copy and Hand E in the Buffalo copy -- independently read the HP as concealing alchemical formulae. This interpretive tradition dates to Beroalde de Verville's 1600 French edition, which included a 'tableau steganographique' listing alchemical equivalents for the narrative's symbols. The two alchemists followed different schools: the BL annotator applied d'Espagnet's mercury-centered framework, while the Buffalo annotator followed pseudo-Geber's sulphur/Sol-Luna emphasis.",
        "source_basis": "Russell 2014, Ch. 6-7; Perifano 2004",
    },
    {
        "slug": "master-mercury",
        "label": "Master Mercury",
        "category": ALCHEM,
        "definition_short": "The central alchemical principle identified by the BL copy's anonymous annotator (Hand B).",
        "definition_long": "The BL alchemist wrote on the flyleaf verso: 'verus sensus intentionis huius libri est 3um: Geni et Totius Naturae energiae & operationum Magisteri Mercurii Descriptio elegans, ampla' -- the HP's true sense is the 'full and elegant description of the energy and spirit of the whole nature, and of the operations of Master Mercury.' This reading positions mercury (quicksilver) as the catalytic principle uniting all elements, consistent with d'Espagnet's Enchiridion Physicae Restitutae and with Isaac Newton's corpuscularian alchemy.",
        "source_basis": "Russell 2014, pp. 159-160",
    },
    {
        "slug": "sol-luna",
        "label": "Sol and Luna",
        "category": ALCHEM,
        "definition_short": "The Sun (gold, masculine) and Moon (silver, feminine) as alchemical principles of opposition and unity.",
        "definition_long": "In the pseudo-Geberian tradition followed by the Buffalo annotator (Hand E), Sol and Luna represent the masculine and feminine principles whose union produces the philosopher's stone. Hand E identified the king and queen statues in the HP as Sol and Luna, and read the chess match on h1r as an allegory of silver/gold transmutation. The chemical wedding -- the union of Sol and Luna -- maps onto Poliphilo and Polia's love story.",
        "source_basis": "Russell 2014, pp. 187-190; Newman 1991",
    },
    {
        "slug": "chemical-wedding",
        "label": "Chemical Wedding",
        "category": ALCHEM,
        "definition_short": "The alchemical union of two opposing substances, symbolized as a marriage producing a hermaphrodite.",
        "definition_long": "The alchemical concept of the chemical wedding (chymische Hochzeit) posits that the refinement of base matter requires the union of opposing principles. In the HP, the love between Poliphilo and Polia was read by alchemically-inclined readers as encoding this process. The offspring of the chemical wedding is the hermaphrodite, harmonizing male and female elements. Russell documents how the Buffalo annotator identified such hermaphroditic imagery on h1r.",
        "source_basis": "Russell 2014, pp. 189-190",
    },
    {
        "slug": "prisca-sapientia",
        "label": "Prisca Sapientia",
        "category": ALCHEM,
        "definition_short": "The concept of an 'ancient wisdom' transmitted from Hermes Trismegistus through successive sages, which alchemists sought to recover.",
        "definition_long": "Prisca sapientia held that original knowledge was progressively hidden under layers of allegory and obscurity. The more incomprehensible a text, the more ancient wisdom it was thought to contain. The HP's deliberately obscure language and its prefatory claim that only the most learned could penetrate its meaning made it an ideal vehicle for alchemical interpretation. Newton, Boyle, and d'Espagnet all worked within this paradigm.",
        "source_basis": "Russell 2014, pp. 153-156; Muslow & Hamalainen 2004",
    },

    # === Architecture & Gardens ===
    {
        "slug": "architectural-body",
        "label": "Architectural Body",
        "category": ARCH,
        "definition_short": "Lefaivre's concept that the HP treats architecture as an extension of embodied cognition and corporeal experience.",
        "definition_long": "In her 1997 attribution study, Liane Lefaivre argued that the HP presents architecture not as abstract geometrical form but as an expression of the body's engagement with space. This 'architectural body' concept connects the HP to Alberti's theories of design as dreamwork and to phenomenological approaches in architectural theory. Hunt (1998) extended this by arguing that the HP foregrounds the process of experiencing gardens over the description of finished architectural objects.",
        "source_basis": "Lefaivre 1997; Hunt 1998",
    },
    {
        "slug": "dream-narrative",
        "label": "Dream Narrative",
        "category": DEBATE,
        "definition_short": "A literary work framed as a dream, a genre to which the HP belongs alongside the Roman de la Rose.",
        "definition_long": "The HP is structured as a dream within a dream: Poliphilo falls asleep and enters a vision, within which he falls asleep again and enters a deeper dream (the dream-within-a-dream beginning at a6v). Priki (2016) places the HP in a comparative tradition with the Roman de la Rose and the Byzantine Tale of Livistros and Rodamne, arguing that the dream frame enables pedagogical encounters that prepare the lover for union with the beloved. Gollnick (1999) provides a theoretical framework for dream-narrative hermeneutics through his study of Apuleius.",
        "source_basis": "Priki 2016; Gollnick 1999; Agamben 1984",
    },
    {
        "slug": "inventio",
        "label": "Inventio",
        "category": ANNOT,
        "definition_short": "The rhetorical process of finding or discovering material for creative production; the act of gathering ideas.",
        "definition_long": "In classical rhetoric, inventio is the first of five canons: the discovery of arguments and material. Russell argues that early modern readers used the HP as a source for inventio -- gathering visual, architectural, linguistic, and philosophical material for their own creative projects. Ben Jonson mined it for stage design ideas. Benedetto Giovio extracted botanical and natural-historical content. The alchemists sought hidden formulae. All were practicing inventio through annotation.",
        "source_basis": "Russell 2014, pp. 38-42; Sloane 1989",
    },
    {
        "slug": "ingegno",
        "label": "Ingegno",
        "category": ANNOT,
        "definition_short": "Wit, mental agility, and improvisational intelligence -- a faculty that HP readers cultivated through annotation.",
        "definition_long": "Ingegno (or ingenium) in Renaissance usage encompassed wit, invention, and the ability to perceive unexpected connections. Russell proposes that the act of annotating the HP was itself a form of ingegno cultivation: readers sharpened their perceptiveness by decoding the text's obscurities, tracing its sources, and making creative associations. The BL alchemist twice praised the HP as 'ingeniosissimo,' recognizing it as exemplifying this virtue.",
        "source_basis": "Russell 2014, pp. 40-41, 160",
    },
    {
        "slug": "antiquarianism",
        "label": "Antiquarianism",
        "category": DEBATE,
        "definition_short": "The systematic study and collection of artifacts from the ancient past, a practice central to the HP's intellectual world.",
        "definition_long": "Griggs (1998) argues that the HP should be understood as the culmination of fifteenth-century Italian antiquarianism rather than as Romantic escapism. The book's verbal and visual strategies derive from Cyriacus of Ancona's commentaria and mid-century antiquarian syllogae (topographically organized manuscript collections of inscriptions and monuments). Poliphilo's journey through architectural ruins enacts the antiquarian mode of knowledge-making.",
        "source_basis": "Griggs 1998; Curran 1998",
    },
    {
        "slug": "vernacular-poetics",
        "label": "Vernacular Poetics",
        "category": DEBATE,
        "definition_short": "The HP as a work of Italian vernacular literature, adapting Petrarchan conventions into a prose-image hybrid.",
        "definition_long": "Trippe (2002) argues that the HP has been understudied as literature, with scholars treating it primarily as architectural or philosophical. Through close analysis of woodcuts and their accompanying text, she demonstrates how the author adapted Petrarchan tropes -- the beloved's beauty, the lover's suffering -- into an interplay of word and image. The HP's invented language operates within recognizable Italian vernacular poetic frameworks rather than being merely eccentric.",
        "source_basis": "Trippe 2002",
    },
    {
        "slug": "reception-history",
        "label": "Reception History",
        "category": DEBATE,
        "definition_short": "The study of how the HP was read, interpreted, and repurposed across five centuries and multiple cultures.",
        "definition_long": "The HP's reception spans Venetian humanism, French court culture, Elizabethan theatre, Enlightenment bibliography, Romantic aestheticism, Jungian psychology, and contemporary digital humanities. Priki (2009) surveys two peak periods of engagement: early modern (through c.1657) and the twentieth-century scholarly revival. Blunt (1937) documented French seventeenth-century reception. Praz (1947) traced influence on Swinburne and Beardsley. Semler (2006) reframed the 1592 English translation as deliberate cultural appropriation rather than failed translation.",
        "source_basis": "Priki 2009; Blunt 1937; Praz 1947; Semler 2006",
    },
    {
        "slug": "apparatus",
        "label": "Apparatus",
        "category": BOOK,
        "definition_short": "The scholarly infrastructure surrounding a critical edition: introduction, notes, bibliography, indexes.",
        "definition_long": "The HP has been the subject of two major critical editions: Pozzi & Ciapponi (1964) and Ariani & Gabriele (1998, Adelphi). Godwin's 1999 English translation (Thames & Hudson) provides the most accessible modern apparatus. The term 'apparatus criticus' refers specifically to the textual notes recording variant readings across copies and editions.",
        "source_basis": "Pozzi & Ciapponi 1964; Ariani & Gabriele 1998; Godwin 1999",
    },
    {
        "slug": "commentary",
        "label": "Commentary",
        "category": ANNOT,
        "definition_short": "A systematic explanation of a text, either printed alongside it or written in its margins.",
        "definition_long": "The HP lacks a printed commentary in either of its Aldine editions (1499, 1545). Instead, the commentary tradition is supplied by readers' marginalia. Russell shows that annotations by Giovio, Jonson, the alchemists, and Alexander VII collectively constitute an informal commentary tradition. Beroalde de Verville's 1600 edition adds the first published interpretive apparatus, though framed as an alchemical key rather than a philological commentary.",
        "source_basis": "Russell 2014 passim",
    },
    {
        "slug": "activity-book",
        "label": "Activity Book",
        "category": ANNOT,
        "definition_short": "Russell's concept of the HP as a text designed to provoke active, playful reader engagement.",
        "definition_long": "Drawing on analogy with modern educational media, Russell reframes the HP as a 'humanistic activity book' in which readers cultivated ingegno through creative engagement with the text and its woodcuts. The HP's puzzles, obscure language, embedded inscriptions, and visual-textual interplay invited readers to decode, annotate, cross-reference, and extend the text in their own marginalia. This concept shifts attention from the author's intent to the reader's creative practice.",
        "source_basis": "Russell 2014, pp. 34-42",
    },
    {
        "slug": "elephant-obelisk",
        "label": "Elephant and Obelisk",
        "category": ARCH,
        "definition_short": "A monumental image in the HP showing an elephant bearing an obelisk, later realized by Bernini in Rome.",
        "definition_long": "The woodcut of the elephant bearing an obelisk (b6v-b7r) is one of the HP's most influential images. Heckscher (1947) documented how Bernini drew upon it for his 1667 sculpture in the Piazza della Minerva, commissioned by Alexander VII (who annotated his own copy of the HP). The BL alchemist (Hand B) covered this image with alchemical ideograms, reading it as encoding alchemical processes. The Buffalo annotator (Hand E) identified the surrounding statues with Geberian Sol/Luna symbolism.",
        "source_basis": "Heckscher 1947; Russell 2014, pp. 157, 187",
    },
    {
        "slug": "cythera",
        "label": "Cythera",
        "category": ARCH,
        "definition_short": "The island of Venus, described in the HP with elaborate concentric garden designs.",
        "definition_long": "In the HP, Poliphilo travels to the island of Cythera, sacred to Venus, where he encounters an elaborate circular garden with concentric rings of planting. Segre (1998) provides the first critical analysis of Cythera's garden design, tracing its mythological associations and arguing it anticipates sixteenth-century botanical garden layouts. Fabiani Giannetto (2015) connects Cythera to the Sacro Bosco at Bomarzo through the lens of meraviglia (wonderment).",
        "source_basis": "Segre 1998; Fabiani Giannetto 2015",
    },
    {
        "slug": "aldus-manutius",
        "label": "Aldus Manutius",
        "category": BOOK,
        "definition_short": "The Venetian printer who published the HP in 1499, renowned for Greek scholarship and italic type.",
        "definition_long": "Aldus Manutius (c.1449-1515) published the HP as one of his most ambitious productions, at a time when his press was primarily known for Greek texts. The HP stands apart from his other publications in its elaborate illustration program and vernacular language. Farrington (2015) contextualizes the HP within Aldus's career and his partnership with Andrea Torresani. Davies (1999) provides the standard biography of Aldus as printer and publisher.",
        "source_basis": "Farrington 2015; Davies 1999",
    },
    {
        "slug": "authorship-debate",
        "label": "Authorship Debate",
        "category": DEBATE,
        "definition_short": "The centuries-long dispute over who wrote the HP, with candidates including two Francesco Colonnas, Alberti, and Feliciano.",
        "definition_long": "The acrostic points to 'Frater Franciscus Colonna,' but which one? Casella & Pozzi (1959) established the Venetian Dominican Francesco Colonna (d.1527) as the canonical attribution. Calvesi (1996) argued for a Roman nobleman of the same name. Lefaivre (1997) proposed Leon Battista Alberti. Khomentovskaia (1935) suggested Felice Feliciano. O'Neill (2021) surveys all candidates and proposes that future research should use narratological analysis rather than archival evidence alone.",
        "source_basis": "Casella & Pozzi 1959; Calvesi 1996; Lefaivre 1997; O'Neill 2021",
    },
    {
        "slug": "ideogram",
        "label": "Ideogram (Alchemical)",
        "category": ALCHEM,
        "definition_short": "A symbolic sign representing an alchemical element or process, used by annotators to label HP passages.",
        "definition_long": "The BL alchemist (Hand B) used an extensive vocabulary of alchemical ideograms -- compact symbols for gold, silver, mercury, Venus, Jupiter, and other elements -- within the syntax of Latin annotations. These signs often had Latin inflections appended (e.g., the sun symbol + '-ra' for 'aurata'). Russell notes that B's ideographic vocabulary shows consistency with Newton's Keynes MSS, suggesting a possible connection to the Royal Society or Cambridge circle.",
        "source_basis": "Russell 2014, pp. 156-158; Taylor 1951",
    },
    {
        "slug": "acutezze",
        "label": "Acutezze",
        "category": ANNOT,
        "definition_short": "Examples of verbal wit or sharp conceits; the primary interest of Pope Alexander VII's annotations.",
        "definition_long": "Fabio Chigi (Pope Alexander VII) annotated his copy of the HP with particular attention to acutezze -- instances of verbal cleverness, wordplay, and rhetorical ingenuity. This practice reflects the seventeenth-century Italian tradition of collecting examples of wit, codified in works like Tesauro's Il cannocchiale aristotelico (1663) and Pellegrini's Delle Acutezze (1639). Chigi's reading of the HP was aesthetic rather than alchemical or encyclopedic.",
        "source_basis": "Russell 2014, Ch. 8; Pellegrini 1639; Tesauro 1663",
    },
    {
        "slug": "allegory",
        "label": "Allegory",
        "category": TEXT,
        "definition_short": "A narrative in which characters and events represent abstract ideas or principles beneath the surface meaning.",
        "definition_long": "The HP has been read allegorically in multiple registers: as an allegory of love (the surface narrative), of alchemical transformation (Beroalde, the BL and Buffalo annotators), of humanist self-cultivation (Lefaivre), and of architectural and political dreams (Temple 1998). The multiplicity of allegorical readings reflects the HP's deliberate obscurity. Priki (2009) shows how each historical audience imposed its own allegorical framework based on cultural context.",
        "source_basis": "Priki 2009; Russell 2014 passim",
    },
]

# Related term links (slug pairs + type)
LINKS = [
    ("signature", "quire", "RELATED"),
    ("signature", "folio", "RELATED"),
    ("signature", "collation", "RELATED"),
    ("folio", "recto", "RELATED"),
    ("folio", "verso", "RELATED"),
    ("recto", "verso", "RELATED"),
    ("quire", "gathering", "RELATED"),
    ("gathering", "collation", "RELATED"),
    ("incunabulum", "aldus-manutius", "RELATED"),
    ("incunabulum", "woodcut", "RELATED"),
    ("woodcut", "ekphrasis", "RELATED"),
    ("woodcut", "emblem", "RELATED"),
    ("hieroglyph", "emblem", "RELATED"),
    ("hieroglyph", "ideogram", "SEE_ALSO"),
    ("marginalia", "annotator-hand", "RELATED"),
    ("marginalia", "commentary", "RELATED"),
    ("marginalia", "activity-book", "RELATED"),
    ("annotator-hand", "inventio", "RELATED"),
    ("annotator-hand", "ingegno", "RELATED"),
    ("acrostic", "authorship-debate", "RELATED"),
    ("alchemical-allegory", "master-mercury", "RELATED"),
    ("alchemical-allegory", "sol-luna", "RELATED"),
    ("alchemical-allegory", "chemical-wedding", "RELATED"),
    ("alchemical-allegory", "prisca-sapientia", "RELATED"),
    ("master-mercury", "ideogram", "RELATED"),
    ("sol-luna", "chemical-wedding", "RELATED"),
    ("prisca-sapientia", "alchemical-allegory", "RELATED"),
    ("architectural-body", "dream-narrative", "RELATED"),
    ("architectural-body", "ekphrasis", "SEE_ALSO"),
    ("dream-narrative", "allegory", "RELATED"),
    ("inventio", "ingegno", "RELATED"),
    ("inventio", "activity-book", "RELATED"),
    ("antiquarianism", "hieroglyph", "RELATED"),
    ("vernacular-poetics", "ekphrasis", "RELATED"),
    ("reception-history", "authorship-debate", "RELATED"),
    ("elephant-obelisk", "alchemical-allegory", "RELATED"),
    ("elephant-obelisk", "aldus-manutius", "SEE_ALSO"),
    ("cythera", "architectural-body", "RELATED"),
    ("acutezze", "ingegno", "RELATED"),
    ("allegory", "alchemical-allegory", "PARENT"),
    ("apparatus", "commentary", "RELATED"),
    ("aldus-manutius", "incunabulum", "RELATED"),
    ("authorship-debate", "acrostic", "RELATED"),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Seeding dictionary terms...")
    inserted = 0
    for t in TERMS:
        cur.execute("""
            INSERT OR IGNORE INTO dictionary_terms
                (slug, label, category, definition_short, definition_long,
                 source_basis, review_status, needs_review)
            VALUES (?, ?, ?, ?, ?, ?, 'DRAFT', 1)
        """, (t["slug"], t["label"], t["category"],
              t["definition_short"], t["definition_long"],
              t.get("source_basis", "")))
        inserted += cur.rowcount
    conn.commit()
    print(f"  Inserted {inserted} terms ({len(TERMS)} total defined)")

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
            # Bidirectional for RELATED
            if link_type == "RELATED":
                cur.execute("""
                    INSERT OR IGNORE INTO dictionary_term_links
                        (term_id, linked_term_id, link_type)
                    VALUES (?, ?, ?)
                """, (b[0], a[0], link_type))
                linked += cur.rowcount
    conn.commit()
    print(f"  Created {linked} links")

    # Summary
    print("\nDictionary by category:")
    cur.execute("""
        SELECT category, COUNT(*) FROM dictionary_terms
        GROUP BY category ORDER BY COUNT(*) DESC
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
