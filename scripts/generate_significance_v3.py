"""Generate significance prose for v3 dictionary terms."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "hp.db"

SIGS = {
    "dream-vision": {
        "hp": "The HP belongs to the dream-vision genre, using its double dream frame to license encyclopedic digressions, allegorical encounters, and the mixing of erotic and philosophical registers that would be implausible in a realistic narrative.",
        "scholarship": "Priki (2016) places the HP within a comparative dream-vision tradition running from the Roman de la Rose through Dante to the HP. Gollnick (1999) provides the theoretical framework for reading dream narratives as vehicles for initiatory transformation.",
    },
    "petrarchism": {
        "hp": "The HP adapts Petrarchan love conventions into a prose-image hybrid: the distant beloved, the suffering lover, and the transformative power of beauty are rendered not only in language but in woodcut illustration. Polia is both a Petrarchan beloved and an autonomous narrator.",
        "scholarship": "Trippe (2002) demonstrates that the HP translates Petrarchan lyric conventions into a visual-verbal register, recovering the HP as a work of vernacular literature rather than merely an architectural curiosity.",
    },
    "roman-de-la-rose": {
        "hp": "The Roman de la Rose provides the HP with its primary structural model: a dream-frame love quest through an allegorical landscape with pedagogical encounters. The HP extends this model through architectural elaboration and the addition of a second narrative voice (Polia).",
        "scholarship": "Priki (2016) argues that the HP consciously adapts and exceeds the Roman de la Rose model, particularly through its double dream structure and its unprecedented integration of text and image.",
    },
    "neoplatonism": {
        "hp": "Neoplatonic philosophy structures the HP at every level: the ascent from dark forest to Cythera enacts the soul's journey from confusion to clarity, the five nymphs represent sensory stages of philosophical ascent, and the circular garden embodies emanation from the One.",
        "scholarship": "Lefaivre (1997) reads the HP through an Albertian-Neoplatonic lens, arguing that its architecture embodies a theory of beauty derived from Ficino and Plotinus. The Neoplatonic framework has become one of the standard interpretive approaches to the HP.",
    },
    "logistica-thelemia": {
        "hp": "Logistica (reason) and Thelemia (will/desire) appear as allegorical guides at a critical juncture in Poliphilo's journey. Their pairing stages the HP's humanist conviction that rational judgment and passionate aspiration must be integrated rather than opposed.",
        "scholarship": "The Logistica-Thelemia episode connects the HP to Renaissance debates on free will and rational choice. The pairing echoes the three gates of Thelemia and the broader vita activa/contemplativa/voluptuosa framework central to humanist moral philosophy.",
    },
    "colossus": {
        "hp": "Poliphilo encounters colossal statues that evoke the ancient Wonders of the World. These passages combine the awe of gigantism with precise architectural measurement, demonstrating the HP's characteristic fusion of the marvelous and the rational.",
        "scholarship": "The colossal figures contribute to the HP's cultivation of meraviglia (wonder) as an aesthetic and philosophical response. The precise measurements given for colossal structures demonstrate the HP's investment in architectural rationality even at extreme scales.",
    },
    "mosaic": {
        "hp": "The HP describes elaborate mosaics depicting mythological scenes in tessellated stone and glass. Poliphilo reads them as visual texts, interpreting their iconography alongside their material composition, treating surfaces as carriers of hermeneutic content.",
        "scholarship": "The mosaic passages contribute to the HP's broader interest in surfaces that carry meaning. Stewering (2000) analyzes how the HP treats architectural ornament as a form of visual argument rather than mere decoration.",
    },
    "colophon": {
        "hp": "The 1499 HP colophon identifies the printer (Aldus Manutius), place (Venice), and date (December 1499) but does not name the author. This omission leaves the authorship question dependent on internal evidence like the acrostic.",
        "scholarship": "The colophon is one of the few paratextual elements providing external evidence about the HP's production. Painter (1963) and Farrington (2015) use the colophon to situate the HP within the production history of the Aldine press.",
    },
    "world-census": {
        "hp": "Russell's world census identified all known annotated copies of the HP through ISTC records and institutional catalogs. From this systematic survey he selected six copies bearing eleven distinct hands for detailed study.",
        "scholarship": "The census methodology exemplifies the disciplined bibliographic approach that distinguishes Russell's work from earlier impressionistic treatments of HP annotations. It establishes the evidentiary foundation for his annotation typology.",
    },
    "ut-pictura-poesis": {
        "hp": "The HP takes the principle ut pictura poesis further than perhaps any other Renaissance text. Its 172 woodcuts are not subordinate illustrations but integral components of meaning, and its verbal descriptions aspire to the vividness of visual art.",
        "scholarship": "Trippe (2002) and Priki analyze how the HP negotiates the text-image boundary, making ut pictura poesis a structural commitment rather than a theoretical ornament. The HP demonstrates what it means for poetry and painting to be genuinely interchangeable.",
    },
    "horror-vacui": {
        "hp": "The HP exhibits pronounced horror vacui in both prose and woodcuts: every surface is carved, inscribed, or planted; every page is dense with description and vocabulary. This aesthetic density is structural, not accidental — the HP's meaning emerges from accumulation.",
        "scholarship": "Jarzombek (1990) reads the HP's descriptive density as architecturally constitutive: the HP does not merely describe full surfaces but demonstrates through its own verbal fullness how ornamental density produces meaning.",
    },
    "great-work": {
        "hp": "Both HP alchemist annotators read Poliphilo's journey as encoding the Great Work of transmutation. The BL alchemist followed d'Espagnet's mercury framework; the Buffalo alchemist followed pseudo-Geber's sulphur and Sol/Luna emphasis. In both, union with Polia represents completion.",
        "scholarship": "Russell (2014, Ch. 6-7) demonstrates how the Great Work provided alchemical readers with a master narrative that reframed the entire love plot. The divergent readings show how the same text could support fundamentally different alchemical interpretations.",
    },
    "gold-leaf": {
        "hp": "Gold leaf and gilding appear throughout the HP as markers of luxury and divine association. Poliphilo specifies the quality of gilding and the visual effect of light on gold surfaces. The alchemical annotators took particular interest in gold references.",
        "scholarship": "The HP's gold references function at multiple levels: as architectural ornament, as markers of imperial and divine association, and as potential alchemical signifiers. The frequency of gold in the HP's material vocabulary underscores the book's investment in luxury as a mode of meaning.",
    },
    "silk": {
        "hp": "Silk and fine textiles receive detailed attention in the HP. Poliphilo describes garments of nymphs, queens, and processional figures with attention to weave, color, drape, and embroidery, contributing to the book's tactile and sensory richness.",
        "scholarship": "The textile descriptions reinforce the HP's investment in material culture as a vehicle for meaning. The specificity of fabric descriptions places the HP within the material knowledge culture of late fifteenth-century Venice, a center of the silk trade.",
    },
}


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    updated = 0
    for slug, texts in SIGS.items():
        cur.execute("""
            UPDATE dictionary_terms SET significance_to_hp = ?, significance_to_scholarship = ?,
                   source_method = COALESCE(source_method, 'LLM_ASSISTED'), updated_at = ?
            WHERE slug = ? AND (review_status IS NULL OR review_status != 'VERIFIED')
        """, (texts["hp"], texts["scholarship"], datetime.now().isoformat(), slug))
        if cur.rowcount > 0:
            updated += 1
            print(f"  UPDATED: {slug}")

    conn.commit()
    conn.close()
    print(f"\nUpdated {updated} terms with significance prose")


if __name__ == "__main__":
    print("=== Generating Significance Prose (v3 terms) ===\n")
    main()
