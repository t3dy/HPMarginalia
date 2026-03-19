"""Seed dictionary_terms with HP entities: characters, places, architecture,
gardens, processions, visual/typographic features, aesthetic concepts,
and material culture from the Hypnerotomachia Poliphili itself.

Extends the existing 37 scholarly-apparatus terms with ~65 new terms
drawn from the book's narrative, imagery, and intellectual world.

Idempotent: uses INSERT OR IGNORE.
All new terms are seeded as review_status='DRAFT', source_method='LLM_ASSISTED'.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

# Category constants (existing)
BOOK = "Book History & Bibliography"
TEXT = "Textual & Visual Motifs"
ANNOT = "Annotation Studies"
ALCHEM = "Alchemical Interpretation"
ARCH = "Architecture & Gardens"
DEBATE = "Scholarly Debates"

# New categories
CHARS = "Characters & Figures"
PLACES = "Places & Settings"
BUILT = "Architecture & Built Form"
GARDEN = "Gardens & Landscape"
PROC = "Processions & Ritual"
VISUAL = "Visual & Typographic"
AESTH = "Aesthetic Concepts"
MATERIAL = "Material Culture"

TERMS = [
    # === Characters & Figures ===
    {
        "slug": "poliphilo",
        "label": "Poliphilo",
        "category": CHARS,
        "definition_short": "The protagonist and dreamer of the HP, whose name means 'lover of many things' or 'lover of Polia.'",
        "definition_long": "Poliphilo is the first-person narrator of the HP's outer dream frame. He falls asleep, enters a dark forest, and journeys through architectural ruins, gardens, and allegorical landscapes toward union with his beloved Polia. His name encodes the book's central ambiguity: 'poliphilo' can mean either 'lover of many things' (from Greek poly + philos) or 'lover of Polia.' This double meaning reflects the HP's oscillation between encyclopedic desire and erotic narrative. Poliphilo's voice is learned, digressive, and obsessively attentive to visual and material detail.",
        "source_basis": "HP passim; Godwin 1999, introduction; Lefaivre 1997",
    },
    {
        "slug": "polia",
        "label": "Polia",
        "category": CHARS,
        "definition_short": "Poliphilo's beloved and the object of his dream quest, who narrates the second part of the HP in her own voice.",
        "definition_long": "Polia appears first as the goal of Poliphilo's journey and then, in Book II, as narrator of her own backstory. Her account reframes the love story from the beloved's perspective, including her initial rejection of Poliphilo and her eventual conversion by Venus. Polia's name derives from the Greek polis (city) or polios (gray/ancient), linking her to antiquity itself. Trippe (2002) argues that Polia's narration adapts Petrarchan conventions by giving the beloved a textual voice rather than reducing her to a silent image.",
        "source_basis": "HP Book II; Trippe 2002; Godwin 1999",
    },
    {
        "slug": "eleuterylida",
        "label": "Queen Eleuterylida",
        "category": CHARS,
        "definition_short": "The queen of the realm of free will whom Poliphilo encounters early in his journey, presiding over a court of allegorical figures.",
        "definition_long": "Eleuterylida (from Greek eleutheria, 'freedom') rules a palace where Poliphilo must choose among three doors or gates representing different life paths. Her realm stages the HP's philosophical core: the exercise of rational choice guided by desire. The queen's court introduces the five senses as personified nymphs who attend Poliphilo and guide him toward deeper understanding. Her name and function connect the HP to the broader Renaissance discourse on free will, virtue, and the vita activa.",
        "source_basis": "HP a4r-b2v; Godwin 1999, pp. 31-52",
    },
    {
        "slug": "nymphs-five-senses",
        "label": "Nymphs of the Five Senses",
        "category": CHARS,
        "definition_short": "Five allegorical nymphs who guide Poliphilo through Queen Eleuterylida's realm, each representing a bodily sense.",
        "definition_long": "The five nymphs who attend Poliphilo embody sight, hearing, smell, taste, and touch. They bathe him, dress him, and lead him through the queen's palace in a sequence that combines sensory education with erotic initiation. The nymphs' names and attributes are drawn from classical and Neoplatonic traditions linking sensory experience to philosophical knowledge. Their ministrations constitute one of the HP's most sustained ekphrastic sequences, described in lavish material detail.",
        "source_basis": "HP b2v-c4r; Hunt 1998; Godwin 1999",
    },
    {
        "slug": "cupid-eros",
        "label": "Cupid / Eros",
        "category": CHARS,
        "definition_short": "The god of love who appears throughout the HP as guide, tormentor, and agent of transformation.",
        "definition_long": "Cupid appears in multiple forms in the HP: as a child archer, as a participant in the triumphal procession, and as an allegorical force driving Poliphilo's journey. The HP's Cupid draws on both Ovidian and Neoplatonic traditions, functioning simultaneously as erotic desire and as the philosophical eros that moves the soul toward beauty and truth. The alchemical annotators read Cupid's arrows as symbols of chemical transformation.",
        "source_basis": "HP passim; Russell 2014, Ch. 6-7; Gollnick 1999",
    },
    {
        "slug": "venus-aphrodite",
        "label": "Venus / Aphrodite",
        "category": CHARS,
        "definition_short": "The goddess of love and beauty whose island (Cythera) is the destination of Poliphilo's journey and the site of his union with Polia.",
        "definition_long": "Venus presides over the HP's climactic sequences on the island of Cythera, where Poliphilo and Polia are united at her temple. The HP presents Venus in her dual aspect: Venus Genetrix (generative love, fertility) and Venus Urania (celestial love, philosophical beauty). The alchemical annotators read Venus as encoding the feminine principle in the chemical wedding. Segre (1998) analyzes the elaborate garden designs surrounding Venus's temple as the HP's most sophisticated landscape composition.",
        "source_basis": "HP Book I, final sections; Segre 1998; Russell 2014",
    },

    # === Places & Settings ===
    {
        "slug": "dark-forest",
        "label": "Dark Forest (Selva Oscura)",
        "category": PLACES,
        "definition_short": "The dense, terrifying forest where Poliphilo's dream begins, echoing Dante's opening of the Commedia.",
        "definition_long": "The HP opens with Poliphilo lost in a dark wood, a deliberate echo of Dante's 'selva oscura' from Inferno I. The forest represents confusion, sensory deprivation, and the threshold between waking consciousness and dream vision. Poliphilo's emergence from the forest into a sunlit landscape marks the beginning of his architectural and erotic education. Priki (2016) reads the dark forest as a structural device common to dream narratives from the Roman de la Rose onward.",
        "source_basis": "HP a1r-a3v; Priki 2016; Godwin 1999, pp. 17-23",
    },
    {
        "slug": "thelemia",
        "label": "Thelemia (Gate of Free Will)",
        "category": PLACES,
        "definition_short": "The gate or portal of free will where Poliphilo chooses among three paths, representing different modes of life.",
        "definition_long": "At the portal of Thelemia (from Greek thelema, 'will'), Poliphilo confronts three doors leading to the vita voluptuosa (life of pleasure), the vita activa (active life), and the vita contemplativa (contemplative life). His choice of the middle path reflects the HP's humanist ethics. Rabelais later adopted the name 'Theleme' for his utopian abbey in Gargantua (1534), almost certainly drawing on the HP. The three-gate motif connects the HP to the Choice of Hercules tradition in Renaissance moral philosophy.",
        "source_basis": "HP b5r-b6r; Godwin 1999; Lefaivre 1997",
    },
    {
        "slug": "ruined-temple",
        "label": "Ruined Temple",
        "category": PLACES,
        "definition_short": "The great ruined classical temple Poliphilo explores early in his journey, establishing the HP's antiquarian and architectural program.",
        "definition_long": "Poliphilo encounters a vast ruined temple shortly after escaping the dark forest. He describes its columns, capitals, entablatures, and inscriptions in obsessive architectural detail, establishing the ekphrastic mode that dominates the rest of the narrative. The temple's ruins embody the Renaissance topos of antiquity's grandeur and loss. Griggs (1998) reads this passage as the HP's closest approach to the antiquarian tradition of Cyriacus of Ancona, where encountering ruins generates knowledge through careful observation.",
        "source_basis": "HP a4r-a8v; Griggs 1998; Huelsen 1910",
    },
    {
        "slug": "triumphal-gate",
        "label": "Triumphal Gate",
        "category": PLACES,
        "definition_short": "A monumental arch decorated with reliefs and inscriptions that Poliphilo passes through, modeled on Roman triumphal architecture.",
        "definition_long": "The HP describes several triumphal gates and arches, each decorated with carved reliefs, pseudo-classical inscriptions, and allegorical imagery. These gates function as thresholds between narrative zones and as occasions for sustained architectural ekphrasis. The woodcut illustrations of the gates are among the HP's most architecturally detailed images, and they influenced subsequent Renaissance architectural treatises. Stewering (2000) analyzes their relationship to Alberti's De re aedificatoria.",
        "source_basis": "HP passim; Stewering 2000; Huelsen 1910",
    },

    # === Architecture & Built Form ===
    {
        "slug": "column-orders",
        "label": "Column Orders",
        "category": BUILT,
        "definition_short": "The classical orders of architecture (Doric, Ionic, Corinthian, Composite) described and illustrated throughout the HP.",
        "definition_long": "The HP contains detailed descriptions of column orders, including measurements, proportions, and ornamental details that rival contemporary architectural treatises. Poliphilo's accounts of columns and their capitals reflect the Vitruvian tradition as filtered through fifteenth-century Italian humanism. The woodcuts depict columns with remarkable architectural precision. Jarzombek (1990) argues that the HP's architectural descriptions are not merely decorative but structurally constitutive of the narrative's meaning.",
        "source_basis": "HP passim; Jarzombek 1990; Stewering 2000",
    },
    {
        "slug": "pyramid",
        "label": "Pyramid",
        "category": BUILT,
        "definition_short": "A massive pyramidal structure Poliphilo encounters, surmounted by an obelisk and described with precise geometric proportions.",
        "definition_long": "The HP's pyramid is one of its most celebrated architectural set pieces, described in minute detail including dimensions, materials, and the stairways ascending its faces. The structure combines Egyptian and classical motifs in a way characteristic of Renaissance pseudo-archaeology. An obelisk surmounts the pyramid, anticipating the elephant-obelisk combination that later influenced Bernini. The alchemical annotators read the pyramid as encoding stages of material refinement.",
        "source_basis": "HP a6r-a8r; Godwin 1999; Russell 2014",
    },
    {
        "slug": "triumphal-arch",
        "label": "Triumphal Arch",
        "category": BUILT,
        "definition_short": "Monumental arched structures in the HP modeled on Roman victory arches, decorated with relief sculptures and inscriptions.",
        "definition_long": "The HP features several triumphal arches that serve as both architectural showpieces and narrative thresholds. Their carved reliefs depict processions, sacrifices, and mythological scenes that Poliphilo interprets at length. The arches demonstrate the HP's characteristically dense interweaving of architectural description, visual imagery, and allegorical meaning. They are among the most architecturally accurate structures in the HP, reflecting knowledge of surviving Roman arches.",
        "source_basis": "HP passim; Stewering 2000; Huelsen 1910",
    },
    {
        "slug": "bath-thermae",
        "label": "Bath / Thermae",
        "category": BUILT,
        "definition_short": "Elaborate bathing scenes in the HP where Poliphilo is ritually cleansed by nymphs in architecturally detailed bath complexes.",
        "definition_long": "The bathing sequences in the HP combine architectural description of classical thermae with erotic content and ritual significance. The nymphs bathe Poliphilo in sequences that move from purification to sensory awakening. The bath architecture is described with attention to water systems, marble surfaces, and spatial arrangement. These passages illustrate the HP's fusion of bodily experience with architectural knowledge, central to Lefaivre's (1997) concept of the 'architectural body.'",
        "source_basis": "HP c1r-c4r; Lefaivre 1997; Godwin 1999",
    },
    {
        "slug": "amphitheatre",
        "label": "Amphitheatre",
        "category": BUILT,
        "definition_short": "A classical amphitheatre Poliphilo encounters, described with attention to seating, proportions, and performance spaces.",
        "definition_long": "The HP's amphitheatre passages describe a classical performance venue with careful attention to architectural proportions and the experience of spectatorship. Poliphilo observes performances and processions from within the structure, making the amphitheatre a site where architecture, spectacle, and narrative converge. The description reflects knowledge of surviving Roman amphitheatres and Renaissance theoretical interest in theatre architecture.",
        "source_basis": "HP; Godwin 1999; Stewering 2000",
    },
    {
        "slug": "fountain",
        "label": "Fountain",
        "category": BUILT,
        "definition_short": "Elaborate fountains described throughout the HP, combining hydraulic engineering with allegorical sculpture and symbolic water imagery.",
        "definition_long": "Fountains are among the HP's most frequently described architectural features. They range from simple springs to elaborate multi-tiered structures with sculptural programs, water jets, and inscribed basins. The sleeping nymph fountain, in particular, became one of the HP's most influential images, copied in Renaissance gardens across Europe. Hunt (1998) reads the fountains as nodes where the HP's garden discourse achieves its fullest integration of architecture, water, sculpture, and meaning.",
        "source_basis": "HP passim; Hunt 1998; Segre 1998",
    },
    {
        "slug": "labyrinth",
        "label": "Labyrinth",
        "category": BUILT,
        "definition_short": "Maze structures in the HP that Poliphilo navigates, combining garden design with allegorical significance.",
        "definition_long": "The HP describes labyrinthine structures that function both as garden features and as allegories of the questing mind. Poliphilo's navigation of these mazes parallels his broader journey from confusion to understanding. The labyrinth connects the HP to classical myth (Theseus and the Minotaur) and to Renaissance garden design, where hedge mazes served as sites of aristocratic recreation and philosophical contemplation.",
        "source_basis": "HP; Godwin 1999; Fabiani Giannetto 2015",
    },
    {
        "slug": "portal",
        "label": "Portal",
        "category": BUILT,
        "definition_short": "Doorways and thresholds in the HP that mark transitions between narrative zones and allegorical states.",
        "definition_long": "The HP uses portals, doors, and gateways as structural devices that divide the narrative into discrete zones of experience. Each portal is described architecturally (material, proportion, decoration) and allegorically (what it represents, what choice it demands). The three doors of Thelemia are the most famous example, but portals appear throughout the narrative as sites where Poliphilo must choose, pause, or transform before proceeding.",
        "source_basis": "HP passim; Godwin 1999",
    },

    # === Gardens & Landscape ===
    {
        "slug": "circular-garden",
        "label": "Circular Garden",
        "category": GARDEN,
        "definition_short": "The elaborate concentric garden on the island of Cythera, with circular rings of planting surrounding Venus's temple.",
        "definition_long": "The garden of Cythera is designed as a series of concentric circles radiating from Venus's temple at the center. Each ring contains different plantings arranged in geometric patterns. Segre (1998) provides the first critical analysis of this garden, arguing it anticipates sixteenth-century botanical garden layouts. The circular form carries cosmological significance: it maps the Neoplatonic emanation from the One (Venus at the center) outward through successive levels of material existence.",
        "source_basis": "HP Book I, final sections; Segre 1998; Hunt 1998",
    },
    {
        "slug": "topiary",
        "label": "Topiary",
        "category": GARDEN,
        "definition_short": "Ornamental clipping of trees and shrubs into geometric or figurative shapes, described in the HP's garden passages.",
        "definition_long": "The HP describes topiary in its garden passages with attention to the shapes formed (spheres, cones, animal figures) and the relationship between clipped vegetation and architectural structure. These descriptions place the HP at the origin of Renaissance garden discourse, where the shaping of nature into art is a central concern. The topiary passages illustrate the HP's broader interest in the boundary between natural and artificial form.",
        "source_basis": "HP; Hunt 1998; Leslie 1998",
    },
    {
        "slug": "pergola",
        "label": "Pergola",
        "category": GARDEN,
        "definition_short": "Garden structures of columns or posts supporting climbing plants, creating shaded walkways described in the HP.",
        "definition_long": "Pergolas appear in the HP as transitional garden structures that mediate between built architecture and living vegetation. Poliphilo describes their materials (marble columns, vine-covered beams) and the sensory experience of walking through them (shade, fragrance, filtered light). The pergola serves the HP's characteristic fusion of architectural precision with bodily immersion in landscape.",
        "source_basis": "HP; Hunt 1998; Godwin 1999",
    },
    {
        "slug": "water-garden",
        "label": "Water Garden",
        "category": GARDEN,
        "definition_short": "Gardens organized around water features — canals, fountains, pools — that figure prominently in the HP's landscape descriptions.",
        "definition_long": "Water is a governing element in the HP's garden passages. Poliphilo encounters gardens structured around canals, reflecting pools, cascading fountains, and streams. Water serves both practical functions (irrigation, cooling) and symbolic ones (purification, reflection, the flow of time and desire). The HP's water gardens influenced real Renaissance garden design, particularly in the great villa gardens of the Veneto and Rome.",
        "source_basis": "HP passim; Hunt 1998; Segre 1998",
    },

    # === Processions & Ritual ===
    {
        "slug": "triumphal-procession",
        "label": "Triumphal Procession",
        "category": PROC,
        "definition_short": "Elaborate processions described in the HP, modeled on Roman triumphs, featuring chariots, musicians, allegorical figures, and captives.",
        "definition_long": "The HP's triumphal processions are among its most visually spectacular passages. They depict chariots drawn by exotic animals, musicians, dancers, allegorical personifications, and crowds of participants, all described in exhaustive detail. The procession woodcuts are among the most complex in the book. These passages connect the HP to Renaissance festival culture and to the classical literary tradition of the triumphus. The alchemical annotators read the processions as encoding stages of the Great Work.",
        "source_basis": "HP d1r-e4v; Russell 2014; Godwin 1999",
    },
    {
        "slug": "sacrifice-priapus",
        "label": "Sacrifice to Priapus",
        "category": PROC,
        "definition_short": "A ritual sacrifice scene in the HP where a donkey is offered to Priapus, the garden god of fertility.",
        "definition_long": "The sacrifice to Priapus is one of the HP's most explicitly pagan ritual scenes. A donkey is sacrificed at Priapus's altar in a ceremony that combines classical sacrificial practice with garden-cult imagery. The scene's frank treatment of fertility symbolism made it a focus for later allegorical interpreters, including the alchemical annotators who read Priapus as encoding generative force in the alchemical process.",
        "source_basis": "HP; Godwin 1999; Russell 2014",
    },
    {
        "slug": "navigation-cythera",
        "label": "Navigation to Cythera",
        "category": PROC,
        "definition_short": "The sea voyage carrying Poliphilo and Polia to the island of Cythera, Venus's sacred island.",
        "definition_long": "The voyage to Cythera marks the transition from the HP's mainland landscapes to its island climax. Poliphilo and Polia travel by boat to Venus's island, where their union will be consecrated. The navigation passage combines maritime description with allegorical significance: the sea crossing represents the passage from earthly desire to divine love. Watteau's later painting L'Embarquement pour Cythere (1717) may owe something to this literary tradition.",
        "source_basis": "HP Book I; Godwin 1999; Praz 1947",
    },
    {
        "slug": "dream-within-dream",
        "label": "Dream within a Dream",
        "category": PROC,
        "definition_short": "The nested dream structure of the HP: Poliphilo falls asleep within his dream, entering a deeper level of vision.",
        "definition_long": "At a6v, Poliphilo falls asleep within his own dream, creating a two-layered dream structure. The inner dream contains the main narrative (the journey, the ruins, the gardens, the union with Polia), while the outer frame provides the initial dark-forest setting and the final awakening. Priki (2016) reads this structure as a deliberate adaptation of the Roman de la Rose's single-layer dream frame, arguing that the double dream enables pedagogical encounters that prepare the lover for union.",
        "source_basis": "HP a6v; Priki 2016; Gollnick 1999",
    },

    # === Visual & Typographic ===
    {
        "slug": "macaronic-language",
        "label": "Macaronic Language",
        "category": VISUAL,
        "definition_short": "The HP's distinctive hybrid language mixing Italian, Latin, and Greek vocabulary with invented words and pseudo-classical formations.",
        "definition_long": "The HP is written in a language that is neither standard Italian nor Latin but a deliberate hybrid. Poliphilo's prose mixes Italian syntax with Latinate vocabulary, Greek loanwords, and invented terms. This macaronic style was long dismissed as eccentric affectation, but Trippe (2002) argues it is a literary strategy that enacts the HP's thematic interest in translation, hybridity, and the gap between ancient and modern expression. Semler (2006) examines how Robert Dallington navigated this language in his 1592 English adaptation.",
        "source_basis": "HP passim; Trippe 2002; Semler 2006; Ure 1952",
    },
    {
        "slug": "historiated-initial",
        "label": "Historiated Initial",
        "category": VISUAL,
        "definition_short": "Decorated capital letters at the start of HP chapters that contain figurative imagery and spell out the acrostic.",
        "definition_long": "Each chapter of the HP begins with a large historiated initial — a capital letter containing or surrounded by figurative decoration. The sequence of these initials spells out the acrostic POLIAM FRATER FRANCISCVS COLVMNA PERAMAVIT. The initials are part of the book's typographic program, designed to be read both as text (the letter itself) and as image (the figurative decoration). They demonstrate Aldus Manutius's press at its most ambitious, integrating type and woodcut illustration.",
        "source_basis": "HP passim; Painter 1963; Godwin 1999",
    },
    {
        "slug": "in-text-inscription",
        "label": "In-Text Inscription",
        "category": VISUAL,
        "definition_short": "Pseudo-classical inscriptions embedded within the HP's text and woodcuts, which Poliphilo reads and interprets.",
        "definition_long": "The HP contains numerous inscriptions set into its architectural descriptions and woodcut illustrations. These inscriptions are presented as carved into monuments, buildings, and tombs that Poliphilo encounters. He reads and translates them, often at length. The inscriptions are in Latin, Greek, Hebrew, Arabic, and pseudo-Egyptian, and they function as textual puzzles that reward the learned reader. Curran (1998) connects them to the Renaissance epigraphic tradition of collecting and interpreting ancient inscriptions.",
        "source_basis": "HP passim; Curran 1998; Griggs 1998",
    },
    {
        "slug": "pseudo-latin",
        "label": "Pseudo-Latin",
        "category": VISUAL,
        "definition_short": "Invented Latin-like vocabulary in the HP, formed by applying Latin morphology to Italian or Greek roots.",
        "definition_long": "The HP's characteristic vocabulary includes many pseudo-Latin words: terms that look and sound Latin but do not appear in classical texts. These are formed by applying Latin declensions and conjugations to Italian roots, or by adapting Greek words through Latin morphological patterns. The result is a learned-sounding language that resists easy translation. Ure (1952) provides early notes on this vocabulary, and Pozzi and Ciapponi's critical edition (1964) includes a glossary of the HP's most distinctive coinages.",
        "source_basis": "HP passim; Ure 1952; Pozzi & Ciapponi 1964",
    },

    # === Aesthetic Concepts ===
    {
        "slug": "meraviglia",
        "label": "Meraviglia (Wonder)",
        "category": AESTH,
        "definition_short": "The aesthetic experience of wonder that the HP cultivates through its descriptions of extraordinary architecture, gardens, and spectacles.",
        "definition_long": "Meraviglia — wonder, marvel, astonishment — is the dominant aesthetic response the HP seeks to produce. Poliphilo repeatedly expresses stupefaction before the sights he encounters: colossal ruins, intricate gardens, bejeweled fountains, and processions of unearthly beauty. Fabiani Giannetto (2015) connects the HP's cultivation of meraviglia to the Sacro Bosco at Bomarzo, arguing that both deploy architectural surprise as a mode of philosophical instruction.",
        "source_basis": "HP passim; Fabiani Giannetto 2015; Hunt 1998",
    },
    {
        "slug": "varieta",
        "label": "Varieta (Variety)",
        "category": AESTH,
        "definition_short": "The aesthetic principle of variety — in materials, forms, and experiences — that governs the HP's descriptive abundance.",
        "definition_long": "The HP enacts the Renaissance principle of varieta through its relentless accumulation of different materials, architectural forms, plant species, animal figures, and human types. Poliphilo's descriptions catalog variety with taxonomic precision: types of marble, species of tree, kinds of column capital. This principle connects the HP to Alberti's aesthetic theory, where varieta is the quality that sustains visual interest and pleasure across an extended work.",
        "source_basis": "HP passim; Lefaivre 1997; Alberti, De re aedificatoria",
    },
    {
        "slug": "disegno",
        "label": "Disegno",
        "category": AESTH,
        "definition_short": "The concept of design as both drawing and intellectual conception, central to the HP's integration of text and image.",
        "definition_long": "Disegno in Renaissance usage encompasses both the physical act of drawing and the intellectual faculty of design or conception. The HP's 172 woodcuts and their precise relationship to the text demonstrate disegno in action: the images are not merely illustrations but integral components of the work's meaning. The HP's influence on subsequent design culture — from garden design to emblem books to architectural treatises — stems from its demonstration that disegno operates across media.",
        "source_basis": "HP passim; Jarzombek 1990; Stewering 2000",
    },
    {
        "slug": "decorum",
        "label": "Decorum",
        "category": AESTH,
        "definition_short": "The classical principle of fitness or appropriateness — matching style to subject, ornament to function — applied throughout the HP.",
        "definition_long": "The HP applies the classical principle of decorum to its architectural and garden descriptions: each structure is ornamented according to its purpose, and each garden element is placed according to its symbolic function. Poliphilo notes where decorum is observed and where it is violated. This attention to fitness connects the HP to the Vitruvian tradition and to Alberti's insistence that beauty arises from the rational correspondence between part and whole.",
        "source_basis": "HP passim; Stewering 2000; Vitruvius, De architectura",
    },
    {
        "slug": "grotesque",
        "label": "Grotesque",
        "category": AESTH,
        "definition_short": "Ornamental style combining human, animal, and vegetable forms in fantastical hybrids, described and depicted in the HP.",
        "definition_long": "The HP describes and illustrates grotesque ornament — the hybrid decorative style rediscovered in the grottoes (grotte) of Nero's Domus Aurea in Rome around 1480. Poliphilo encounters carved surfaces where human figures merge with acanthus scrolls, animal forms sprout architectural elements, and natural and artificial forms intertwine. The HP is among the earliest printed works to depict and theorize this ornamental mode, which became one of the defining visual vocabularies of Renaissance decoration.",
        "source_basis": "HP passim; Dacos 1969; Godwin 1999",
    },

    # === Material Culture ===
    {
        "slug": "porphyry",
        "label": "Porphyry",
        "category": MATERIAL,
        "definition_short": "A hard purple-red stone associated with imperial authority, frequently named in the HP's material descriptions.",
        "definition_long": "Porphyry appears throughout the HP as a marker of supreme quality and imperial association. Poliphilo describes columns, floors, basins, and sculptures made of porphyry, often specifying its color and the difficulty of working it. In Renaissance material culture, porphyry carried associations of antiquity, authority, and permanence. The HP's repeated invocation of porphyry situates its imagined architecture within the highest register of classical luxury.",
        "source_basis": "HP passim; Godwin 1999",
    },
    {
        "slug": "chalcedony",
        "label": "Chalcedony",
        "category": MATERIAL,
        "definition_short": "A translucent microcrystalline quartz named among the precious stones in the HP's descriptions of luxury surfaces.",
        "definition_long": "The HP catalogs precious and semi-precious stones with lapidary precision: chalcedony, jasper, agate, sardonyx, and others. These material descriptions serve both aesthetic and symbolic functions. Each stone carries traditional associations (chalcedony with eloquence and courage, jasper with healing) that add layers of meaning to the architectural surfaces Poliphilo describes. The HP's material vocabulary reflects the Renaissance fascination with natural history and the moral significance of stones.",
        "source_basis": "HP passim; Godwin 1999",
    },
    {
        "slug": "jasper",
        "label": "Jasper",
        "category": MATERIAL,
        "definition_short": "An opaque quartz used for columns and pavements in the HP, associated with healing and protection in lapidary tradition.",
        "definition_long": "Jasper (diaspro) is one of the most frequently named stones in the HP. Poliphilo describes jasper columns, jasper pavements, and jasper vessel interiors. The stone's variety of colors (red, green, yellow) allows the HP to build complex chromatic descriptions of architectural surfaces. In the medieval and Renaissance lapidary tradition, jasper was associated with healing, protection from poison, and the stopping of blood — associations that the alchemical annotators may have found significant.",
        "source_basis": "HP passim; Russell 2014; Godwin 1999",
    },

    # === Additional Architecture & Gardens (expanding existing category) ===
    {
        "slug": "sleeping-nymph-fountain",
        "label": "Sleeping Nymph Fountain",
        "category": BUILT,
        "definition_short": "A famous HP image of a reclining nymph beside a spring, which became one of the book's most widely copied motifs.",
        "definition_long": "The sleeping nymph fountain depicts a female figure reclining beside a natural spring with the inscription PANTΩΝ TOKAΔI ('mother of all things'). This image was widely copied in Renaissance gardens, appearing as actual fountain sculptures across Italy and France. It combines the classical tradition of the sleeping Ariadne with the Renaissance cult of the genius loci (spirit of place). The nymph fountain is one of the clearest examples of the HP's direct influence on material culture.",
        "source_basis": "HP; Godwin 1999; Kurz 1953",
    },
    {
        "slug": "obelisk",
        "label": "Obelisk",
        "category": BUILT,
        "definition_short": "Tall, tapering stone monuments in the HP, associated with Egyptian wisdom and the encoding of hidden knowledge.",
        "definition_long": "Obelisks appear throughout the HP as bearers of hieroglyphic inscriptions and as monuments connecting the narrative to Egyptian antiquity. The most famous is the obelisk surmounting the elephant (b6v-b7r), which Bernini later adapted for his 1667 sculpture in Piazza della Minerva. The HP's obelisks reflect the Renaissance conviction that Egyptian monuments encoded prisca sapientia — ancient wisdom accessible only to initiated readers. The alchemical annotators treated the obelisk passages as particularly dense with hidden meaning.",
        "source_basis": "HP b6v-b7r passim; Heckscher 1947; Curran 1998",
    },

    # === Additional Scholarly/Textual ===
    {
        "slug": "1545-edition",
        "label": "1545 Edition",
        "category": BOOK,
        "definition_short": "The second Aldine edition of the HP, published in 1545, which reused the 1499 text but with new woodcut blocks.",
        "definition_long": "The 1545 edition was published by the Aldine press (then under Paolo Manuzio, Aldus's son) with new woodcut blocks that generally followed the 1499 designs but with some variations. The BL copy in this project (C.60.o.12) is a 1545 edition, which complicates folio-to-image matching since the signature map is based on the 1499 collation. Priki (2009) documents the differences between editions as part of the HP's reception history.",
        "source_basis": "Priki 2009; Russell 2014; Painter 1963",
    },
    {
        "slug": "1499-edition",
        "label": "1499 Edition",
        "category": BOOK,
        "definition_short": "The first edition of the HP, printed by Aldus Manutius in Venice in December 1499, with 172 woodcut illustrations.",
        "definition_long": "The editio princeps of the HP was published by Aldus Manutius's press in Venice, dated December 1499. It is a folio volume with 172 woodcut illustrations, historiated initials, and the author-attribution acrostic. The 1499 edition is the basis for Russell's world census of annotated copies and for this project's signature map. It is widely regarded as the most elaborately illustrated incunabulum ever produced. The Incunabula Short Title Catalogue (ISTC) records approximately 200 surviving copies.",
        "source_basis": "Russell 2014, p. 16; Painter 1963; ISTC",
    },
    {
        "slug": "beroalde-1600",
        "label": "Beroalde de Verville's 1600 Edition",
        "category": BOOK,
        "definition_short": "The French alchemical edition of the HP published by Beroalde de Verville in 1600, with a 'tableau steganographique' of alchemical keys.",
        "definition_long": "Beroalde de Verville published a French adaptation of the HP in 1600 that included a 'tableau steganographique' — a systematic table mapping narrative elements to alchemical processes and substances. This edition inaugurated the tradition of reading the HP as alchemical allegory that Russell documents in the BL and Buffalo annotators. Beroalde's edition is the earliest published alchemical interpretation of the HP and influenced all subsequent alchemical readings.",
        "source_basis": "Russell 2014, pp. 147-153; Perifano 2004",
    },
]

# Cross-links between new terms and between new and existing terms
LINKS = [
    # Characters
    ("poliphilo", "polia", "RELATED"),
    ("poliphilo", "dream-narrative", "RELATED"),
    ("poliphilo", "dark-forest", "RELATED"),
    ("polia", "venus-aphrodite", "RELATED"),
    ("eleuterylida", "thelemia", "RELATED"),
    ("eleuterylida", "nymphs-five-senses", "RELATED"),
    ("nymphs-five-senses", "bath-thermae", "RELATED"),
    ("cupid-eros", "venus-aphrodite", "RELATED"),
    ("cupid-eros", "triumphal-procession", "RELATED"),
    ("venus-aphrodite", "cythera", "RELATED"),
    ("venus-aphrodite", "circular-garden", "RELATED"),
    ("venus-aphrodite", "chemical-wedding", "SEE_ALSO"),

    # Places
    ("dark-forest", "dream-narrative", "RELATED"),
    ("dark-forest", "dream-within-dream", "RELATED"),
    ("thelemia", "portal", "RELATED"),
    ("ruined-temple", "antiquarianism", "RELATED"),
    ("ruined-temple", "column-orders", "RELATED"),
    ("triumphal-gate", "triumphal-arch", "RELATED"),

    # Architecture
    ("column-orders", "ekphrasis", "RELATED"),
    ("pyramid", "obelisk", "RELATED"),
    ("pyramid", "hieroglyph", "RELATED"),
    ("triumphal-arch", "triumphal-procession", "RELATED"),
    ("bath-thermae", "architectural-body", "RELATED"),
    ("fountain", "sleeping-nymph-fountain", "RELATED"),
    ("fountain", "water-garden", "RELATED"),
    ("labyrinth", "circular-garden", "RELATED"),
    ("sleeping-nymph-fountain", "meraviglia", "RELATED"),
    ("obelisk", "elephant-obelisk", "RELATED"),
    ("obelisk", "hieroglyph", "RELATED"),

    # Gardens
    ("circular-garden", "cythera", "RELATED"),
    ("topiary", "circular-garden", "RELATED"),
    ("pergola", "circular-garden", "RELATED"),
    ("water-garden", "fountain", "RELATED"),

    # Processions & Ritual
    ("triumphal-procession", "woodcut", "RELATED"),
    ("sacrifice-priapus", "alchemical-allegory", "SEE_ALSO"),
    ("navigation-cythera", "cythera", "RELATED"),
    ("dream-within-dream", "dream-narrative", "PARENT"),

    # Visual & Typographic
    ("macaronic-language", "vernacular-poetics", "RELATED"),
    ("macaronic-language", "pseudo-latin", "RELATED"),
    ("historiated-initial", "acrostic", "RELATED"),
    ("historiated-initial", "woodcut", "RELATED"),
    ("in-text-inscription", "hieroglyph", "RELATED"),
    ("in-text-inscription", "antiquarianism", "RELATED"),
    ("pseudo-latin", "macaronic-language", "RELATED"),

    # Aesthetic
    ("meraviglia", "ekphrasis", "RELATED"),
    ("varieta", "ekphrasis", "RELATED"),
    ("disegno", "woodcut", "RELATED"),
    ("decorum", "column-orders", "RELATED"),
    ("grotesque", "woodcut", "RELATED"),

    # Material
    ("porphyry", "jasper", "RELATED"),
    ("porphyry", "chalcedony", "RELATED"),
    ("jasper", "chalcedony", "RELATED"),

    # Editions
    ("1499-edition", "aldus-manutius", "RELATED"),
    ("1499-edition", "incunabulum", "RELATED"),
    ("1499-edition", "1545-edition", "RELATED"),
    ("1545-edition", "1499-edition", "RELATED"),
    ("beroalde-1600", "alchemical-allegory", "RELATED"),
    ("beroalde-1600", "reception-history", "RELATED"),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Seeding HP entity dictionary terms (v2)...")
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

    # Summary
    print("\nDictionary by category:")
    cur.execute("""
        SELECT category, COUNT(*) FROM dictionary_terms
        GROUP BY category ORDER BY COUNT(*) DESC
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]}")

    cur.execute("SELECT COUNT(*) FROM dictionary_terms")
    total = cur.fetchone()[0]
    print(f"\nTotal terms: {total}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
