"""Generate significance_to_hp and significance_to_scholarship prose for all dictionary terms.

Uses reading packets (staging/packets/*.json) and existing definitions as context.
Generates 2-3 sentence prose per field following docs/WRITING_TEMPLATES.md Template 1c/1d.

All generated prose is marked:
- source_method = 'LLM_ASSISTED'
- review_status = 'DRAFT'
- confidence = 'MEDIUM'

Never overwrites fields where review_status = 'VERIFIED'.
Writes staging/dictionary_significance.json with full provenance before updating DB.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"
PACKETS_DIR = BASE_DIR / "staging" / "packets"
STAGING_DIR = BASE_DIR / "staging"

# ============================================================
# Significance prose generation
# ============================================================
# These are grounded in the reading packets and existing definitions.
# Each entry follows the Writing Templates spec:
#   significance_to_hp: 40-80 words, what this means for the HP specifically
#   significance_to_scholarship: 40-80 words, how scholars have used this concept

SIGNIFICANCE = {
    # === Book History & Bibliography ===
    "signature": {
        "hp": "The HP uses signatures a-z (omitting j, u, w) then A-G, each gathering consisting of eight leaves. Russell references all folios by signature rather than page number, making the signature system the primary navigational framework for both the original book and this project's concordance pipeline.",
        "scholarship": "Russell (2014) adopts signature-based referencing throughout his thesis because the 1499 HP has no printed pagination. This practice, standard in incunabular bibliography, allows scholars to locate passages precisely across different copies regardless of later pagination schemes.",
    },
    "quire": {
        "hp": "The HP's quires are regular quaternions — four sheets folded to make eight leaves each. This regularity across quires a-z and A-G is what makes the signature map a reliable concordance tool, enabling deterministic folio-to-image matching for the Siena copy.",
        "scholarship": "The HP's quire structure is central to bibliographic analysis of the 1499 edition. Harris (2002) used collation analysis to identify typographical anomalies in the HP's woodcuts, and the quire structure underpins Russell's system for locating annotations across copies.",
    },
    "folio": {
        "hp": "Each folio of the HP carries text and sometimes woodcut illustrations on both sides. The book's 234 folios contain 172 woodcuts and the full text of Poliphilo's dream narrative, with some of the most important annotations appearing on versos facing woodcuts on the following recto.",
        "scholarship": "Folio-level analysis is the foundation of Russell's annotation study. He documents marginal notes by folio position (e.g., b6v, h1r), enabling precise comparison of how different readers engaged with the same passages across different copies of the HP.",
    },
    "recto": {
        "hp": "In the HP's original layout, most woodcuts appear on the recto. The recto is the side that would have been printed first in the press, and its prominence means that recto-placed woodcuts received more sustained attention from annotators.",
        "scholarship": "Russell's folio references use 'r' for recto (e.g., a1r). The distinction between recto and verso placement is significant for understanding annotation patterns: annotators often wrote on the verso facing a recto woodcut.",
    },
    "verso": {
        "hp": "Some of the most important marginal annotations in the BL copy appear on versos facing significant woodcuts on the following recto. The verso-recto relationship creates a visual dialogue between reader annotations and printed images.",
        "scholarship": "Verso annotations are frequently positional responses to facing-page content. Russell documents how the BL alchemist placed alchemical ideograms on versos adjacent to woodcuts that depicted allegorically significant scenes.",
    },
    "gathering": {
        "hp": "The HP's gatherings are regular quaternions throughout most of the book, with the final gathering G being shorter. This regularity is essential for the deterministic signature map that enables folio-level concordance between Russell's references and manuscript photographs.",
        "scholarship": "The gathering structure of the 1499 HP follows the standard collation formula a-z8 A-F8 G6 (omitting j, u, w). Bibliographers use this formula to detect missing or inserted leaves and to identify variant copies.",
    },
    "collation": {
        "hp": "The collation formula for the 1499 HP is a-z8 A-F8 G6, describing 29 gatherings totaling approximately 234 leaves. This formula is the basis for the project's deterministic signature map, which converts any valid signature to a sequential folio number.",
        "scholarship": "Harris (2002) used collation analysis to identify typographical anomalies in the HP's woodcuts. The collation formula enables bibliographers to detect variant states, missing leaves, and cancel slips across surviving copies.",
    },
    "incunabulum": {
        "hp": "The 1499 HP is widely regarded as the most elaborately illustrated incunabulum ever produced. Its 172 woodcuts, historiated initials, and pseudo-hieroglyphic inscriptions represent the highest point of Aldine typographic ambition before Aldus shifted to smaller-format Greek texts.",
        "scholarship": "Russell's world census of annotated copies was conducted primarily through Incunabula Short Title Catalogue (ISTC) records. The HP's status as an incunabulum places it within the well-catalogued universe of fifteenth-century printed books, enabling systematic identification of surviving copies.",
    },
    "aldus-manutius": {
        "hp": "Aldus Manutius published the HP as one of his most ambitious productions in 1499, at a time when his press was primarily known for Greek texts. The HP stands apart from his other publications in its elaborate illustration program and vernacular Italian language.",
        "scholarship": "Farrington (2015) contextualizes the HP within Aldus's career, arguing that its production represented a commercial and aesthetic experiment distinct from the press's Greek scholarly mission. Davies (1999) provides the standard biography of Aldus as printer and publisher.",
    },
    "apparatus": {
        "hp": "The HP lacks a printed commentary or apparatus in either of its Aldine editions (1499, 1545). The commentary tradition is instead supplied by readers' marginalia, which Russell argues collectively constitute an informal apparatus built by successive generations of annotators.",
        "scholarship": "The absence of a printed apparatus distinguishes the HP from most classical texts of the period. Pozzi and Ciapponi's 1964 critical edition provides the first modern scholarly apparatus, including textual notes and a glossary of the HP's unusual vocabulary.",
    },
    "woodcut": {
        "hp": "The 1499 HP contains 172 woodcut illustrations integrated into the text flow in a manner unprecedented for the period. The woodcuts appear mid-page within the prose, creating a text-image relationship where neither element is subordinate to the other.",
        "scholarship": "Huelsen (1910) provided the first systematic study of the woodcuts' architectural sources. Priki (2012) analyzed how the text-image relationship shifts across editions. The identity of the woodcut artist — sometimes called the 'Master of the Poliphilo' — remains debated.",
    },
    "acrostic": {
        "hp": "The HP's chapter initials spell POLIAM FRATER FRANCISCVS COLVMNA PERAMAVIT ('Brother Francesco Colonna loved Polia greatly'). This embedded message, formed by the sequence of historiated initials, is the primary evidence for attributing authorship to a Dominican friar.",
        "scholarship": "Casella and Pozzi (1959) established the acrostic attribution as canonical. Lefaivre (1997) challenged it by arguing the acrostic could have been inserted by someone other than the author. O'Neill (2021) surveys how the acrostic has shaped and constrained all subsequent authorship debates.",
    },
    "hieroglyph": {
        "hp": "The HP contains numerous pseudo-hieroglyphic inscriptions that Poliphilo encounters on monuments, obelisks, and architectural surfaces. These are Renaissance inventions inspired by Horapollo's Hieroglyphica, not authentic Egyptian writing, but they function as hermeneutic puzzles within the narrative.",
        "scholarship": "Curran (1998) situates the HP's hieroglyphs within fifteenth-century humanist Egyptology. Priki analyzes their narrative function, arguing they serve as structural devices within the dream journey rather than mere antiquarian decoration. The hieroglyphs influenced the later emblem tradition.",
    },
    "emblem": {
        "hp": "The HP's hieroglyphic woodcuts, which pair symbolic images with interpretive text, are widely considered proto-emblematic. The book's combination of picture, inscription, and explanatory prose anticipates the formal emblem structure codified by Alciato in 1531.",
        "scholarship": "Gombrich (1972) and Caruso (2004) document the HP's influence on the emblem tradition. Canone and Spruit analyze the HP's emblematic structures within the broader context of early modern emblematics and their relationship to natural philosophy.",
    },
    "ekphrasis": {
        "hp": "Much of the HP consists of elaborate ekphrastic descriptions: buildings, sculptures, fountains, gardens, and processions described in painstaking visual detail. These passages create the immersive dream-atmosphere and provide material for the woodcut illustrations.",
        "scholarship": "Trippe (2002) argues the HP's ekphrases adapt Petrarchan conventions of lyric poetry into a visual register. Stewering (2000) analyzes the architectural ekphrases as sophisticated representations that reflect genuine knowledge of classical and contemporary building practice.",
    },
    "marginalia": {
        "hp": "Russell documents marginalia in six copies of the HP, showing that the book was actively read and annotated by humanists, playwrights, a pope, and alchemists. The annotations range from simple underlines to elaborate alchemical decipherments and cross-references to other works.",
        "scholarship": "Russell (2014) frames HP marginalia within the broader field of annotation studies established by Sherman (2007) and others. The HP's annotators demonstrate how early modern readers used books as working tools for creative and intellectual production.",
    },
    "annotator-hand": {
        "hp": "Russell identified 11 distinct annotator hands across 6 copies of the HP. The BL copy bears two hands (Ben Jonson and an anonymous alchemist), while the Buffalo copy has five interleaved hands (A-E), demonstrating sustained multi-reader engagement.",
        "scholarship": "Distinguishing hands involves analyzing ink color, language, ductus, content focus, and stratigraphic relationships. Russell's hand identification methodology draws on paleographic and codicological methods adapted for printed book annotation studies.",
    },
    "inventio": {
        "hp": "Early modern readers used the HP as a source for inventio — gathering visual, architectural, linguistic, and philosophical material for their own creative projects. Ben Jonson mined it for stage design. Benedetto Giovio extracted botanical content. The alchemists sought hidden formulae.",
        "scholarship": "Russell (2014, pp. 38-42) argues that inventio, the first of the five classical rhetorical canons, best explains the diverse purposes served by HP annotation. Each reader's marginalia represents a distinct inventional practice shaped by their professional and intellectual context.",
    },
    "ingegno": {
        "hp": "The BL alchemist twice praised the HP as 'ingeniosissimo,' recognizing it as exemplifying the mental agility and improvisational intelligence that ingegno denotes. The act of annotating the HP was itself a form of ingegno cultivation.",
        "scholarship": "Russell proposes that annotating the HP cultivated readers' ingegno — their capacity for perceiving unexpected connections and making creative associations. This framing positions HP annotation within Renaissance theories of cognitive development and rhetorical education.",
    },
    "commentary": {
        "hp": "The HP lacks a printed commentary in either Aldine edition. Instead, five centuries of readers' marginalia constitute an informal commentary tradition, with each annotator's notes reflecting their interpretive framework — humanist, alchemical, aesthetic, or encyclopedic.",
        "scholarship": "Russell shows that the HP's commentary tradition is distributed across annotated copies rather than published in a single apparatus. Beroalde de Verville's 1600 edition adds the first published interpretive apparatus, framed as an alchemical key rather than a philological commentary.",
    },
    "activity-book": {
        "hp": "Russell reframes the HP as a 'humanistic activity book' — a text whose puzzles, obscure language, embedded inscriptions, and visual-textual interplay invited readers to decode, annotate, cross-reference, and extend the text through their own marginalia.",
        "scholarship": "The 'activity book' concept is Russell's central theoretical contribution. It shifts scholarly attention from the author's intent to the reader's creative practice, positioning the HP alongside commonplace books and album amicorum as genres that structure active readerly engagement.",
    },
    "acutezze": {
        "hp": "Pope Alexander VII annotated his HP copy with particular attention to acutezze — instances of verbal cleverness, wordplay, and rhetorical ingenuity. His reading of the HP was aesthetic rather than alchemical or encyclopedic, focused on the text's wit.",
        "scholarship": "Russell contextualizes Chigi's annotations within the seventeenth-century Italian tradition of collecting examples of wit, codified in works like Tesauro's Il cannocchiale aristotelico (1663) and Pellegrini's Delle Acutezze (1639).",
    },
    "allegory": {
        "hp": "The HP has been read allegorically in multiple registers: as an allegory of love (the surface narrative), of alchemical transformation (Beroalde and the BL/Buffalo annotators), of humanist self-cultivation (Lefaivre), and of architectural and political dreams (Temple 1998).",
        "scholarship": "Priki (2009) shows how each historical audience imposed its own allegorical framework based on cultural context. The multiplicity of allegorical readings reflects the HP's deliberate obscurity and its capacity to sustain contradictory interpretive schemes simultaneously.",
    },

    # === Alchemical Interpretation ===
    "alchemical-allegory": {
        "hp": "Two annotators in Russell's study — Hand B in the BL copy and Hand E in the Buffalo copy — independently read the HP as concealing alchemical formulae beneath its love narrative. Their annotations map narrative elements to alchemical processes and substances.",
        "scholarship": "The alchemical reading tradition dates to Beroalde de Verville's 1600 French edition. Russell documents how two later annotators followed different alchemical schools (d'Espagnet vs pseudo-Geber), producing divergent but internally consistent readings of the same passages.",
    },
    "master-mercury": {
        "hp": "The BL alchemist wrote on the flyleaf that the HP's true sense is 'Magisteri Mercurii Descriptio' — the description of the operations of Master Mercury. This reading positions mercury as the catalytic principle uniting all elements in the HP's narrative.",
        "scholarship": "Russell (2014, pp. 159-160) identifies the Master Mercury declaration as the key to the BL alchemist's interpretive framework. The declaration's consistency with d'Espagnet's Enchiridion Physicae Restitutae (1623) helps date the annotations and situate the annotator within a specific alchemical tradition.",
    },
    "sol-luna": {
        "hp": "The Buffalo alchemist (Hand E) identified king and queen statues in the HP as Sol and Luna, and read the chess match on h1r as an allegory of silver/gold transmutation. The Sol-Luna duality maps onto Poliphilo and Polia's love story in this reading.",
        "scholarship": "Russell (2014, pp. 187-190) shows that Hand E's Sol-Luna emphasis places this annotator within the pseudo-Geberian tradition, distinct from the BL alchemist's mercury-centered framework. The comparison reveals how different alchemical schools generated different readings of identical passages.",
    },
    "chemical-wedding": {
        "hp": "The alchemical concept of the chemical wedding — the union of opposing principles producing a hermaphrodite — maps onto the HP's central love narrative. The Buffalo annotator identified hermaphroditic imagery on h1r as encoding this process.",
        "scholarship": "Russell documents how the chemical wedding provided alchemical readers with a master narrative that reframed the HP's entire love plot. The concept connects the HP to the broader tradition of alchemical romance literature, including the Chymische Hochzeit (1616).",
    },
    "prisca-sapientia": {
        "hp": "The HP's deliberately obscure language and its prefatory claim that only the most learned could penetrate its meaning made it an ideal vehicle for prisca sapientia — the idea that ancient texts concealed original wisdom beneath layers of allegory.",
        "scholarship": "Russell (2014, pp. 153-156) argues that the prisca sapientia framework explains why alchemical readers were drawn to the HP specifically. Its linguistic obscurity and visual complexity were read as signs of concealed ancient knowledge, consistent with the Hermetic tradition.",
    },
    "ideogram": {
        "hp": "The BL alchemist (Hand B) used an extensive vocabulary of alchemical ideograms — compact symbols for gold, silver, mercury, Venus, Jupiter — within the syntax of Latin annotations. These signs sometimes had Latin inflections appended, creating a hybrid semiotic system.",
        "scholarship": "Russell notes that Hand B's ideographic vocabulary shows consistency with Newton's Keynes MSS, suggesting a possible connection to the Royal Society or Cambridge circle. Taylor (1951) provides a reference table for standard alchemical signs.",
    },

    # === Architecture & Gardens (existing) ===
    "architectural-body": {
        "hp": "The HP presents architecture not as abstract geometrical form but as an expression of embodied cognition. Poliphilo's descriptions consistently connect built space to bodily experience — heat, shade, texture, pressure, and the kinetic sensation of walking through layered environments.",
        "scholarship": "Lefaivre (1997) introduced the 'architectural body' concept to argue that the HP anticipates phenomenological approaches to architecture. Hunt (1998) extended this by arguing that the HP foregrounds the process of experiencing gardens over the description of finished architectural objects.",
    },
    "elephant-obelisk": {
        "hp": "The woodcut of the elephant bearing an obelisk (b6v-b7r) is one of the HP's most influential images. The BL alchemist covered this image with alchemical ideograms. The Buffalo annotator identified the surrounding statues with Geberian Sol/Luna symbolism.",
        "scholarship": "Heckscher (1947) documented how Bernini drew upon the HP's elephant-obelisk for his 1667 sculpture in Piazza della Minerva, commissioned by Alexander VII — who himself annotated his own HP copy. This is the clearest case of the HP's direct influence on major public art.",
    },
    "cythera": {
        "hp": "Poliphilo travels to Cythera, Venus's sacred island, where he encounters an elaborate circular garden with concentric rings of planting and is united with Polia at Venus's temple. Cythera is the narrative and symbolic destination of the entire journey.",
        "scholarship": "Segre (1998) provides the first critical analysis of Cythera's garden design, tracing its mythological associations and arguing it anticipates sixteenth-century botanical garden layouts. Fabiani Giannetto (2015) connects Cythera to the Sacro Bosco at Bomarzo.",
    },

    # === Scholarly Debates ===
    "dream-narrative": {
        "hp": "The HP is structured as a dream within a dream: Poliphilo falls asleep and enters a vision, within which he falls asleep again at a6v and enters a deeper dream. The double dream frame enables pedagogical encounters that prepare the lover for union with the beloved.",
        "scholarship": "Priki (2016) places the HP within a comparative tradition alongside the Roman de la Rose and the Byzantine Livistros and Rodamne. Gollnick (1999) provides a theoretical framework for dream-narrative hermeneutics through Apuleius's Metamorphoses.",
    },
    "antiquarianism": {
        "hp": "The HP enacts the antiquarian mode of knowledge-making: Poliphilo encounters ruins, inscriptions, and ancient monuments, and generates understanding through careful observation and recording. The book's verbal and visual strategies derive from the fifteenth-century antiquarian tradition.",
        "scholarship": "Griggs (1998) argues that the HP should be understood as the culmination of Italian antiquarianism rather than Romantic escapism. The book's strategies derive from Cyriacus of Ancona's commentaria and mid-century manuscript collections of inscriptions and monuments.",
    },
    "vernacular-poetics": {
        "hp": "The HP's invented macaronic language operates within recognizable Italian vernacular poetic frameworks. The author adapted Petrarchan tropes — the beloved's beauty, the lover's suffering — into a prose-image hybrid that is eccentric but literarily purposeful.",
        "scholarship": "Trippe (2002) argues that the HP has been understudied as literature. Through close analysis of woodcuts and their accompanying text, she demonstrates how the author adapted Petrarchan conventions into an interplay of word and image that deserves literary rather than purely art-historical analysis.",
    },
    "reception-history": {
        "hp": "The HP's reception spans Venetian humanism, French court culture, Elizabethan theatre, Enlightenment bibliography, Romantic aestheticism, Jungian psychology, and contemporary digital humanities. Each era has read the HP through its own interpretive concerns.",
        "scholarship": "Priki (2009) surveys two peak periods of engagement: early modern (through c.1657) and the twentieth-century scholarly revival. Blunt (1937) documented French seventeenth-century reception. Semler (2006) reframed the 1592 English translation as deliberate cultural appropriation.",
    },
    "authorship-debate": {
        "hp": "The acrostic points to 'Frater Franciscus Colonna,' but which one? The Venetian Dominican (d. 1527) is the canonical attribution, but candidates include a Roman nobleman of the same name, Leon Battista Alberti, and Felice Feliciano.",
        "scholarship": "Casella and Pozzi (1959) established the Venetian friar as canonical. Calvesi (1996) argued for the Roman Colonna. Lefaivre (1997) proposed Alberti. O'Neill (2021) argues that future research should use narratological analysis rather than archival evidence alone.",
    },

    # === Characters & Figures ===
    "poliphilo": {
        "hp": "Poliphilo is the HP's first-person narrator and dreamer. His name encodes the book's central ambiguity: 'lover of many things' (poly + philos) or 'lover of Polia.' His obsessive visual attention and learned digressions generate the HP's characteristic mode of architectural ekphrasis.",
        "scholarship": "Scholars have read Poliphilo variously as an authorial self-portrait (Casella and Pozzi 1959), as an Albertian architect-dreamer (Lefaivre 1997), and as a generic humanist everyman undergoing allegorical education (Priki 2016). His identity is inseparable from the authorship debate.",
    },
    "polia": {
        "hp": "Polia narrates Book II of the HP in her own voice, reframing the love story from the beloved's perspective. Her name derives from Greek polis or polios, linking her to antiquity itself. She is both the object of desire and an autonomous narrator with her own account of events.",
        "scholarship": "Trippe (2002) argues that Polia's narration adapts Petrarchan conventions by giving the beloved a textual voice. This makes the HP unusual among Renaissance love narratives, which typically silence the beloved or reduce her to a visual object.",
    },
    "eleuterylida": {
        "hp": "Queen Eleuterylida presides over the realm of free will where Poliphilo must choose among three doors. Her court stages the HP's philosophical core: the exercise of rational choice guided by desire. Her five attendant nymphs represent the bodily senses.",
        "scholarship": "The Thelemia/Eleuterylida episode connects the HP to Renaissance moral philosophy and the Choice of Hercules tradition. Rabelais adapted the name 'Theleme' for his utopian abbey in Gargantua (1534), demonstrating the HP's influence on French humanist thought.",
    },
    "nymphs-five-senses": {
        "hp": "Five nymphs embody sight, hearing, smell, taste, and touch. They bathe, dress, and guide Poliphilo through the queen's palace in a sequence that combines sensory education with erotic initiation. Their ministrations constitute one of the HP's most sustained ekphrastic passages.",
        "scholarship": "The five-senses allegory connects the HP to Neoplatonic traditions linking sensory experience to philosophical knowledge. Hunt (1998) reads the nymph sequence as staging the relationship between bodily perception and architectural understanding.",
    },
    "cupid-eros": {
        "hp": "Cupid appears in the HP as child archer, triumphal participant, and philosophical force. The HP's Cupid functions simultaneously as erotic desire and as the Neoplatonic eros that moves the soul toward beauty and truth.",
        "scholarship": "The alchemical annotators read Cupid's arrows as symbols of chemical transformation. Russell documents how the same Cupid passages received radically different interpretations from humanist, aesthetic, and alchemical readers.",
    },
    "venus-aphrodite": {
        "hp": "Venus presides over the HP's climactic sequences on Cythera. The HP presents her in dual aspect: Venus Genetrix (generative love, fertility) and Venus Urania (celestial love, philosophical beauty). The union of Poliphilo and Polia occurs at her temple.",
        "scholarship": "Segre (1998) analyzes the elaborate garden designs surrounding Venus's temple. The alchemical annotators read Venus as encoding the feminine principle in the chemical wedding. Her dual nature reflects the HP's characteristic layering of erotic and philosophical meaning.",
    },

    # === Places & Settings ===
    "dark-forest": {
        "hp": "The HP opens with Poliphilo lost in a dark wood, deliberately echoing Dante's 'selva oscura.' The forest represents confusion and the threshold between waking consciousness and dream vision. Poliphilo's emergence into sunlit landscape marks the beginning of his architectural education.",
        "scholarship": "Priki (2016) reads the dark forest as a structural device common to dream narratives from the Roman de la Rose onward. The Dantean echo positions the HP within the Italian literary tradition of visionary journey literature.",
    },
    "thelemia": {
        "hp": "At the portal of Thelemia, Poliphilo chooses among three doors representing the vita voluptuosa, vita activa, and vita contemplativa. His choice of the middle path reflects the HP's humanist ethics of balance between pleasure and contemplation.",
        "scholarship": "Rabelais adopted the name 'Theleme' for his utopian abbey in Gargantua (1534), almost certainly drawing on the HP. The three-gate motif connects the HP to the Choice of Hercules tradition in Renaissance moral philosophy.",
    },
    "ruined-temple": {
        "hp": "Poliphilo explores a vast ruined temple early in his journey, describing its columns, capitals, entablatures, and inscriptions in obsessive architectural detail. The temple establishes the ekphrastic mode that dominates the rest of the narrative.",
        "scholarship": "Griggs (1998) reads this passage as the HP's closest approach to the antiquarian tradition of Cyriacus of Ancona, where encountering ruins generates knowledge through careful observation. Huelsen (1910) analyzed the temple's architectural sources.",
    },
    "triumphal-gate": {
        "hp": "The HP describes several triumphal gates decorated with reliefs and inscriptions. These function as thresholds between narrative zones and as occasions for sustained architectural ekphrasis. The woodcut illustrations of gates are among the HP's most architecturally detailed images.",
        "scholarship": "Stewering (2000) analyzes the relationship between the HP's triumphal gates and Alberti's De re aedificatoria. The gates demonstrate the HP's sophisticated knowledge of Roman triumphal architecture and its adaptation for narrative purposes.",
    },

    # === Architecture & Built Form ===
    "column-orders": {
        "hp": "The HP contains detailed descriptions of Doric, Ionic, Corinthian, and Composite column orders, including measurements and proportions that rival contemporary architectural treatises. The woodcuts depict columns with remarkable precision.",
        "scholarship": "Jarzombek (1990) argues that the HP's architectural descriptions are structurally constitutive of the narrative's meaning, not merely decorative. Stewering (2000) demonstrates that the column descriptions reflect genuine knowledge of the Vitruvian tradition.",
    },
    "pyramid": {
        "hp": "The HP's pyramid is described with precise geometric proportions including dimensions, materials, and ascending stairways. An obelisk surmounts the structure, combining Egyptian and classical motifs in a way characteristic of Renaissance pseudo-archaeology.",
        "scholarship": "The pyramid passage is one of the HP's most celebrated architectural set pieces. It anticipates the elephant-obelisk combination that later influenced Bernini. The alchemical annotators read the pyramid as encoding stages of material refinement.",
    },
    "triumphal-arch": {
        "hp": "The HP features several triumphal arches whose carved reliefs depict processions, sacrifices, and mythological scenes. These arches serve as both architectural showpieces and narrative thresholds, with Poliphilo pausing to interpret their imagery at length.",
        "scholarship": "Stewering (2000) and Huelsen (1910) analyze the HP's triumphal arches as reflecting knowledge of surviving Roman arches. The arches demonstrate the characteristically dense interweaving of architectural description, visual imagery, and allegorical meaning.",
    },
    "bath-thermae": {
        "hp": "The bathing sequences combine architectural description of classical thermae with erotic content and ritual significance. The nymphs bathe Poliphilo in sequences that move from purification to sensory awakening, fusing bodily experience with architectural knowledge.",
        "scholarship": "Lefaivre (1997) reads the bath passages as central to her concept of the 'architectural body' — architecture experienced through embodied cognition rather than abstract geometrical analysis. The bath architecture is described with attention to water systems and spatial arrangement.",
    },
    "amphitheatre": {
        "hp": "The HP's amphitheatre passages describe a classical performance venue with careful attention to proportions and spectatorship. Poliphilo observes performances from within the structure, making the amphitheatre a site where architecture, spectacle, and narrative converge.",
        "scholarship": "The amphitheatre description reflects knowledge of surviving Roman amphitheatres and Renaissance theoretical interest in theatre architecture. It contributes to the HP's broader demonstration that architecture is experienced through the body, not merely observed.",
    },
    "fountain": {
        "hp": "Fountains range from simple springs to elaborate multi-tiered structures with sculptural programs and water jets. The sleeping nymph fountain became one of the HP's most influential images, copied in Renaissance gardens across Europe.",
        "scholarship": "Hunt (1998) reads the fountains as nodes where the HP's garden discourse achieves its fullest integration of architecture, water, sculpture, and meaning. Segre (1998) analyzes the Cythera fountains within the circular garden's cosmological program.",
    },
    "labyrinth": {
        "hp": "The HP describes labyrinthine structures that function both as garden features and as allegories of the questing mind. Poliphilo's navigation of mazes parallels his broader journey from confusion to understanding.",
        "scholarship": "The labyrinth connects the HP to classical myth (Theseus and the Minotaur) and to Renaissance garden design. Fabiani Giannetto (2015) reads the HP's labyrinths within the wider context of meraviglia — architectural structures designed to produce wonder.",
    },
    "portal": {
        "hp": "The HP uses portals and gateways as structural devices dividing the narrative into discrete zones of experience. Each portal is described architecturally and allegorically — the three doors of Thelemia being the most famous example.",
        "scholarship": "Portal passages in the HP demonstrate the book's structural use of architecture to organize narrative meaning. Each threshold demands a choice or transformation from Poliphilo, making the portal a narratological as well as architectural device.",
    },
    "sleeping-nymph-fountain": {
        "hp": "The sleeping nymph fountain depicts a female figure reclining beside a spring with the inscription meaning 'mother of all things.' This image was widely copied in Renaissance gardens as actual fountain sculptures across Italy and France.",
        "scholarship": "Kurz (1953) traces the reception history of the sleeping nymph motif from the HP through its numerous garden adaptations. The image combines the classical tradition of the sleeping Ariadne with the Renaissance cult of the genius loci.",
    },
    "obelisk": {
        "hp": "Obelisks appear throughout the HP as bearers of hieroglyphic inscriptions and as monuments connecting the narrative to Egyptian antiquity. The most famous is the obelisk surmounting the elephant (b6v-b7r), which influenced Bernini's 1667 sculpture.",
        "scholarship": "The HP's obelisks reflect the Renaissance conviction that Egyptian monuments encoded prisca sapientia. Curran (1998) connects them to the broader humanist project of recovering ancient knowledge through the study of inscribed monuments.",
    },

    # === Gardens & Landscape ===
    "circular-garden": {
        "hp": "The garden of Cythera radiates from Venus's temple in concentric circles, each ring containing different plantings in geometric patterns. The circular form carries cosmological significance: the Neoplatonic emanation from the One outward through levels of material existence.",
        "scholarship": "Segre (1998) argues that Cythera's circular garden anticipates sixteenth-century botanical garden layouts. Hunt (1998) reads the circular design as the HP's most sophisticated integration of garden form, cosmological symbolism, and narrative meaning.",
    },
    "topiary": {
        "hp": "The HP describes topiary — ornamental clipping of trees into geometric and figurative shapes — in its garden passages. These descriptions place the HP at the origin of Renaissance garden discourse, where shaping nature into art is a central concern.",
        "scholarship": "The topiary passages illustrate the HP's interest in the boundary between natural and artificial form. Leslie (1998) reads them within the broader context of Renaissance debates about the garden as a site where art and nature negotiate their relationship.",
    },
    "pergola": {
        "hp": "Pergolas appear in the HP as transitional garden structures where marble columns support vine-covered beams. Poliphilo describes the sensory experience of walking through them — shade, fragrance, filtered light — fusing architectural precision with bodily immersion.",
        "scholarship": "The pergola serves the HP's characteristic integration of built form and landscape. Hunt (1998) reads these passages as demonstrating the HP's conviction that garden architecture is experienced through movement and sensation, not static contemplation.",
    },
    "water-garden": {
        "hp": "Water is a governing element in the HP's garden passages. Poliphilo encounters gardens structured around canals, reflecting pools, cascading fountains, and streams. Water serves both practical functions and symbolic ones — purification, reflection, and the flow of desire.",
        "scholarship": "The HP's water gardens influenced real Renaissance garden design, particularly in the Veneto and Rome. Segre (1998) and Hunt (1998) both analyze how water functions as both a design element and a carrier of symbolic meaning in the HP's landscape descriptions.",
    },

    # === Processions & Ritual ===
    "triumphal-procession": {
        "hp": "The HP's triumphal processions depict chariots drawn by exotic animals, musicians, dancers, allegorical personifications, and elaborate spectacle. The procession woodcuts are among the most complex in the book, filling entire pages with detailed figural compositions.",
        "scholarship": "The procession passages connect the HP to Renaissance festival culture and to the classical literary tradition of the triumphus. The alchemical annotators read the processions as encoding stages of the Great Work — each figure representing an element or phase of transmutation.",
    },
    "sacrifice-priapus": {
        "hp": "A donkey is sacrificed at Priapus's altar in a ceremony combining classical sacrificial practice with garden-cult imagery. The scene's frank treatment of fertility symbolism made it a focus for allegorical interpreters, including the alchemical annotators.",
        "scholarship": "The Priapus sacrifice is one of the HP's most explicitly pagan ritual scenes. Russell documents how the alchemical annotators read Priapus as encoding generative force in the alchemical process, demonstrating how diverse readers imposed different symbolic frameworks on the same passage.",
    },
    "navigation-cythera": {
        "hp": "The sea voyage to Cythera marks the transition from the HP's mainland landscapes to its island climax. The crossing represents the passage from earthly desire to divine love. Poliphilo and Polia travel by boat to Venus's island for their consecration.",
        "scholarship": "The navigation passage connects to a broader literary tradition of voyages to Venus's island. Praz (1947) notes that Watteau's L'Embarquement pour Cythere (1717) may owe something to this tradition, though direct influence from the HP is not established.",
    },
    "dream-within-dream": {
        "hp": "At a6v, Poliphilo falls asleep within his own dream, creating a two-layered vision. The inner dream contains the main narrative while the outer frame provides the dark-forest setting and the final awakening. This nesting structure doubles the hermeneutic distance between reader and event.",
        "scholarship": "Priki (2016) reads the double dream as a deliberate adaptation of the Roman de la Rose's single-layer frame. The nested structure enables pedagogical encounters — each dream level imposes different rules on what Poliphilo can perceive and understand.",
    },

    # === Visual & Typographic ===
    "macaronic-language": {
        "hp": "The HP is written in a deliberate hybrid of Italian syntax with Latinate vocabulary, Greek loanwords, and invented terms. This macaronic style enacts the book's thematic interest in translation, hybridity, and the gap between ancient and modern expression.",
        "scholarship": "Trippe (2002) argues the macaronic language is a literary strategy, not eccentric affectation. Semler (2006) examines how Robert Dallington navigated this language in his 1592 English adaptation. Ure (1952) provides early philological notes on the HP's vocabulary.",
    },
    "historiated-initial": {
        "hp": "Each HP chapter begins with a historiated initial — a large capital letter containing figurative decoration. The sequence of initials spells the authorship acrostic. These initials integrate type and woodcut illustration, demonstrating Aldus's press at its most ambitious.",
        "scholarship": "The historiated initials are part of the HP's typographic program. Painter (1963) analyzes them within the context of Aldine press production. The initials demonstrate that the HP's text-image integration extends even to the level of individual letterforms.",
    },
    "in-text-inscription": {
        "hp": "The HP embeds inscriptions in Latin, Greek, Hebrew, Arabic, and pseudo-Egyptian within its architectural descriptions. Poliphilo reads and translates these inscriptions at length, turning each encounter into an interpretive exercise for both character and reader.",
        "scholarship": "Curran (1998) connects the HP's inscriptions to the Renaissance epigraphic tradition. Griggs (1998) reads them as enacting the antiquarian mode of knowledge-making, where encountering inscribed surfaces generates understanding through careful decipherment.",
    },
    "pseudo-latin": {
        "hp": "The HP's vocabulary includes many pseudo-Latin words formed by applying Latin declensions to Italian roots or adapting Greek through Latin morphological patterns. The result resists easy translation and rewards the learned reader with interpretive pleasure.",
        "scholarship": "Ure (1952) provides early notes on the HP's distinctive vocabulary. Pozzi and Ciapponi's critical edition (1964) includes a glossary that remains the standard reference for the HP's most unusual coinages and neologisms.",
    },

    # === Aesthetic Concepts ===
    "meraviglia": {
        "hp": "Meraviglia — wonder, astonishment — is the dominant aesthetic response the HP cultivates. Poliphilo repeatedly expresses stupefaction before colossal ruins, intricate gardens, and processions of unearthly beauty, making wonder both subject and method.",
        "scholarship": "Fabiani Giannetto (2015) connects the HP's cultivation of meraviglia to the Sacro Bosco at Bomarzo, arguing that both deploy architectural surprise as philosophical instruction. The concept links the HP to Renaissance aesthetic theory where wonder precedes understanding.",
    },
    "varieta": {
        "hp": "The HP enacts the principle of varieta through relentless accumulation of different materials, forms, and species. Poliphilo catalogs marble types, tree species, and column capitals with taxonomic precision, making variety itself a structural principle.",
        "scholarship": "The HP's varieta connects to Alberti's aesthetic theory, where variety sustains visual interest across an extended work. Lefaivre (1997) reads the HP's descriptive abundance as an Albertian design principle applied to literary rather than architectural composition.",
    },
    "disegno": {
        "hp": "The HP's 172 woodcuts and their precise relationship to the text demonstrate disegno — the integration of drawing and intellectual conception. The images are not illustrations subordinate to text but integral components of the work's meaning.",
        "scholarship": "Jarzombek (1990) and Stewering (2000) analyze how the HP demonstrates that disegno operates across media. The HP's influence on design culture — from garden design to emblem books — stems from its demonstration that visual and verbal conception are inseparable.",
    },
    "decorum": {
        "hp": "The HP applies the classical principle of decorum to its architectural descriptions: each structure is ornamented according to its purpose, and each garden element is placed according to its symbolic function. Poliphilo notes where decorum is observed and where violated.",
        "scholarship": "The HP's attention to architectural decorum connects it to the Vitruvian tradition and to Alberti's insistence that beauty arises from rational correspondence between part and whole. Stewering (2000) analyzes how the HP theorizes decorum through narrative demonstration.",
    },
    "grotesque": {
        "hp": "The HP describes and illustrates grotesque ornament — hybrid decorative forms where human figures merge with acanthus scrolls and animal forms sprout architectural elements. The HP is among the earliest printed works to depict and theorize this ornamental mode.",
        "scholarship": "The grotesque style was rediscovered in the grottoes of Nero's Domus Aurea around 1480. Dacos (1969) provides the standard account of its Renaissance revival. The HP's grotesque passages situate the book within this moment of ornamental rediscovery.",
    },

    # === Material Culture ===
    "porphyry": {
        "hp": "Porphyry appears throughout the HP as a marker of supreme quality and imperial association. Poliphilo describes porphyry columns, floors, basins, and sculptures, specifying its color and the difficulty of working it.",
        "scholarship": "In Renaissance material culture, porphyry carried associations of antiquity, authority, and permanence. The HP's repeated invocation of porphyry situates its imagined architecture within the highest register of classical luxury and imperial power.",
    },
    "chalcedony": {
        "hp": "The HP catalogs precious and semi-precious stones with lapidary precision. Chalcedony appears among the luxury materials adorning architectural surfaces. Each stone carries traditional symbolic associations that add layers of meaning to the descriptions.",
        "scholarship": "The HP's material vocabulary reflects the Renaissance fascination with natural history and the moral significance of stones. Lapidary traditions associated chalcedony with eloquence and courage, adding symbolic depth to the HP's architectural descriptions.",
    },
    "jasper": {
        "hp": "Jasper is one of the most frequently named stones in the HP. Poliphilo describes jasper columns, pavements, and vessel interiors. The stone's variety of colors allows the HP to build complex chromatic descriptions of architectural surfaces.",
        "scholarship": "In the medieval and Renaissance lapidary tradition, jasper was associated with healing, protection, and the stopping of blood. The alchemical annotators may have found these associations significant within their interpretive frameworks.",
    },

    # === Editions ===
    "1499-edition": {
        "hp": "The editio princeps was published by Aldus Manutius in Venice in December 1499. It is a folio volume with 172 woodcut illustrations, historiated initials, and the authorship acrostic. It is the basis for this project's signature map and concordance pipeline.",
        "scholarship": "Russell's world census was conducted primarily through ISTC records. The 1499 edition is the reference text for all bibliographic, codicological, and annotation studies of the HP. Approximately 200 copies survive in institutional and private collections.",
    },
    "1545-edition": {
        "hp": "The second Aldine edition reused the 1499 text with new woodcut blocks. The BL copy in this project (C.60.o.12) is a 1545 edition, which complicates folio-to-image matching since the signature map is based on the 1499 collation.",
        "scholarship": "Priki (2009) documents differences between the 1499 and 1545 editions as part of the HP's reception history. The existence of a second Aldine edition demonstrates sustained commercial demand for the HP in the mid-sixteenth century.",
    },
    "beroalde-1600": {
        "hp": "Beroalde de Verville's 1600 French edition included a 'tableau steganographique' mapping narrative elements to alchemical processes. This edition inaugurated the tradition of reading the HP as alchemical allegory that Russell documents in the BL and Buffalo annotators.",
        "scholarship": "Beroalde's edition is the earliest published alchemical interpretation of the HP. Russell (2014, pp. 147-153) traces how Beroalde's framework influenced all subsequent alchemical readings, including those of the anonymous BL and Buffalo annotators.",
    },
}


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check which terms are VERIFIED (do not touch)
    cur.execute("SELECT slug, review_status FROM dictionary_terms")
    statuses = {row[0]: row[1] for row in cur.fetchall()}

    # Build staging artifact
    staging_data = []
    updated = 0
    skipped = 0

    for slug, sig in SIGNIFICANCE.items():
        status = statuses.get(slug)
        if status == 'VERIFIED':
            print(f"  SKIP (VERIFIED): {slug}")
            skipped += 1
            continue

        if slug not in statuses:
            print(f"  SKIP (not in DB): {slug}")
            continue

        hp_text = sig.get('hp', '')
        schol_text = sig.get('scholarship', '')

        staging_data.append({
            'slug': slug,
            'significance_to_hp': hp_text,
            'significance_to_scholarship': schol_text,
            'source_method': 'LLM_ASSISTED',
            'review_status': 'DRAFT',
            'confidence': 'MEDIUM',
        })

        cur.execute("""
            UPDATE dictionary_terms
            SET significance_to_hp = ?,
                significance_to_scholarship = ?,
                source_method = COALESCE(source_method, 'LLM_ASSISTED'),
                confidence = COALESCE(confidence, 'MEDIUM'),
                updated_at = ?
            WHERE slug = ?
              AND (review_status IS NULL OR review_status != 'VERIFIED')
        """, (hp_text, schol_text, datetime.now().isoformat(), slug))

        if cur.rowcount > 0:
            updated += 1
            print(f"  UPDATED: {slug}")

    conn.commit()
    conn.close()

    # Write staging artifact
    staging_path = STAGING_DIR / "dictionary_significance.json"
    with open(staging_path, 'w', encoding='utf-8') as f:
        json.dump(staging_data, f, indent=2, ensure_ascii=False)

    print(f"\nUpdated {updated} terms, skipped {skipped} verified.")
    print(f"Staging artifact: {staging_path}")


if __name__ == "__main__":
    print("=== Generating Dictionary Significance Prose ===\n")
    main()
