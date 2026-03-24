"""
Phase 1 Content Expansion: Pirate, Alchemist, and Courtier pages.

Expands each page from ~750 words to ~7,000-9,000 words by adding:
- PageSection entries (intro, context, essay, conclusion) with long prose
- DigbyThemeRecord entries with 200-400 word summaries
- New Citations grounding all claims in the source corpus

All content grounded in:
- Moshenska, 'A Stain in the Blood' / 'The Remarkable Voyage' (biography)
- Moshenska, 'Piracy and Lived Romance' (Studies in Philology, 2016)
- Dobbs, 'Digby and Alchemy' (Ambix, 1973)
- Dobbs, 'Experimental Alchemy - The Book of Secrets' (Ambix, 1974)
- Principe, 'Alchemical Circle in 1650s Paris' (Ambix, 2013)
- Miles, 'Sir Kenelm Digby' (Chymia, 1949)
- Mellick, 'Sir Kenelm Digby (1603-1665)' (ANZ J Surg, 2011)
- Hedrick, 'Romancing the Salve' (BJHS, 2007)
- Lobis, 'Power of Sympathy' (HLQ, 2011)
- Georgescu & Adriaenssen, 'The Philosophy of Kenelm Digby' (2022)
"""

import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.db import init_db, insert_record, get_connection
from src.models import (
    DigbyThemeRecord, PageSection, Citation,
    Confidence, SourceMethod, ReviewStatus,
)
from src.validate import validate_record


def expand_content():
    init_db()

    # Check existing records for idempotency
    conn = get_connection()
    existing_themes = {r["id"] for r in conn.execute("SELECT id FROM digby_theme_records").fetchall()}
    existing_sections = {r["id"] for r in conn.execute("SELECT id FROM page_sections").fetchall()}
    existing_cits = {r["id"] for r in conn.execute("SELECT id FROM citations").fetchall()}
    conn.close()

    # ========================================================================
    # CITATIONS — ground every claim in the corpus
    # ========================================================================
    new_citations = [
        # Pirate page citations
        Citation(
            id="cit_mosh_ch4_commission",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapter 4",
            context="Royal commission, fleet assembly, Buckingham obstruction",
        ),
        Citation(
            id="cit_mosh_ch4_plague",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapter 4, late January 1628",
            context="Plague striking the fleet in the Mediterranean",
        ),
        Citation(
            id="cit_mosh_ch5_algiers_full",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapter 5",
            context="Full account of Algiers stay, slave liberation, resupply",
        ),
        Citation(
            id="cit_mosh_ch6_prizes",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapter 6",
            context="Prize captures, economics of privateering",
        ),
        Citation(
            id="cit_mosh_ch7_scanderoon_full",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapter 7",
            context="Battle of Scanderoon, Venetian response, diplomatic crisis",
        ),
        Citation(
            id="cit_mosh_ch7_heliodorus",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapter 7, late July 1628",
            context="Becalmed off Egypt, reading Heliodorus",
        ),
        Citation(
            id="cit_mosh_ch8_aftermath",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapter 8",
            context="Return, diplomatic fallout, Venetian propaganda",
        ),
        Citation(
            id="cit_piracy_article",
            source_document_id="sdoc_32708346",
            page_or_location="pp. 424-483",
            context="Moshenska article on piracy and lived romance",
        ),
        # Alchemist page citations
        Citation(
            id="cit_dobbs_1973_gresham",
            source_document_id="sdoc_438da82c",
            page_or_location="pp. 143-148",
            context="Digby at Gresham College after Venetia's death, laboratory inventory",
        ),
        Citation(
            id="cit_dobbs_1973_winchester",
            source_document_id="sdoc_438da82c",
            page_or_location="pp. 148-150",
            context="Experiments during Winchester imprisonment 1642, glass manufacture",
        ),
        Citation(
            id="cit_dobbs_1973_paris",
            source_document_id="sdoc_438da82c",
            page_or_location="pp. 150-157",
            context="Paris exile, Evelyn visit, Le Fevre, Hartlib circle",
        ),
        Citation(
            id="cit_dobbs_1973_lefevre",
            source_document_id="sdoc_438da82c",
            page_or_location="pp. 155-160",
            context="Le Fevre's influence on Digby, Universal Spirit, mercury theory",
        ),
        Citation(
            id="cit_dobbs_1974_secrets",
            source_document_id="sdoc_c5b22c27",
            page_or_location="pp. 1-28",
            context="Chymical Secrets analysis, operational alchemy, Hartman publication",
        ),
        Citation(
            id="cit_principe_paris_circle",
            source_document_id="sdoc_3ce83ddc",
            page_or_location="pp. 3-24",
            context="Strasbourg manuscripts, Paris alchemical circle, 5000 pages",
        ),
        Citation(
            id="cit_principe_manuscripts",
            source_document_id="sdoc_3ce83ddc",
            page_or_location="pp. 6-10",
            context="Digby's textual criticism of alchemical manuscripts",
        ),
        Citation(
            id="cit_principe_dubois",
            source_document_id="sdoc_3ce83ddc",
            page_or_location="pp. 10-15",
            context="Noel Picard/Dubois transmutation accounts in Digby manuscripts",
        ),
        Citation(
            id="cit_hedrick_powder",
            source_document_id="sdoc_b03434d3",
            page_or_location="pp. 161-185",
            context="Powder of Sympathy, Montpellier lecture, priority claims",
        ),
        Citation(
            id="cit_lobis_sympathy",
            source_document_id="sdoc_4a8b454c",
            page_or_location="pp. 243-260",
            context="Power of Sympathy, moral philosophy, mechanistic explanation",
        ),
        Citation(
            id="cit_georgescu_philosophy",
            source_document_id="sdoc_dee89fe4",
            page_or_location="passim",
            context="Digby's philosophical work, Two Treatises, corpuscular theory",
        ),
        # Courtier page citations
        Citation(
            id="cit_miles_courtier_career",
            source_document_id="sdoc_4a0dcb55",
            page_or_location="pp. 119-128",
            context="Overview of Digby's courtier career, political maneuvering",
        ),
        Citation(
            id="cit_mellick_courtier",
            source_document_id="sdoc_6fc18de0",
            page_or_location="pp. 911-914",
            context="Digby's versatile career, knighthood, Privy Council, Royal Society",
        ),
        Citation(
            id="cit_mosh_ch2_grand_tour_court",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapter 2",
            context="Grand Tour, Madrid, meeting Prince Charles, court connections",
        ),
        Citation(
            id="cit_mosh_ch3_knighthood",
            source_document_id="sdoc_moshenska",
            page_or_location="Chapter 3",
            context="Knighthood, London political life, Buckingham rivalry",
        ),
        Citation(
            id="cit_dobbs_1973_civil_war",
            source_document_id="sdoc_438da82c",
            page_or_location="pp. 148-150",
            context="Civil War imprisonment at Winchester House",
        ),
        Citation(
            id="cit_mellick_duel",
            source_document_id="sdoc_6fc18de0",
            page_or_location="p. 913",
            context="Duel with Mont le Ros in Paris, 1641",
        ),
    ]

    added_cits = 0
    for c in new_citations:
        if c.id not in existing_cits:
            c.created_at = datetime.now().isoformat()
            validate_record(c)
            insert_record("citations", c.to_dict())
            added_cits += 1
    print(f"Added {added_cits} new citations.")

    # ========================================================================
    # PIRATE PAGE — Theme Records
    # ========================================================================
    pirate_themes = [
        DigbyThemeRecord(
            id="thm_pirate_royal_commission",
            theme="pirate",
            title="The Royal Commission and Its Limits",
            summary=(
                "Digby's Mediterranean voyage of 1628 operated in the murky space between "
                "legitimate privateering and outright piracy, a distinction that depended "
                "entirely on the authority under which one sailed. Digby obtained a royal "
                "commission from Charles I, but the precise terms of that commission were "
                "deliberately vague, reflecting the ambiguity of Caroline naval policy. "
                "England was nominally at war with France and Spain, which gave Digby legal "
                "cover to seize French and Spanish vessels, but the Mediterranean was "
                "controlled by the Ottoman Empire, Venice, and the Barbary regencies, none "
                "of whom were at war with England. This meant that any aggressive action "
                "against Venetian shipping, or any interference with trade at Ottoman ports "
                "like Scanderoon, could be construed as piracy under the law of nations. "
                "The commission was further complicated by the hostility of the Duke of "
                "Buckingham, who had obstructed Digby's preparations at every turn. "
                "Buckingham controlled the Admiralty and could revoke or undermine any "
                "commission he chose. Digby circumvented this through direct appeal to "
                "Charles I, but the resulting authority was fragile: dependent on royal "
                "favor that could evaporate if the voyage caused diplomatic embarrassment. "
                "The ambiguity of Digby's commission was not accidental. It gave the Crown "
                "plausible deniability if things went wrong while allowing Digby to pursue "
                "prizes aggressively if things went right. This was standard practice in "
                "the era of Caroline privateering, where the line between royal service "
                "and private enrichment was deliberately blurred."
            ),
            key_details="Royal commission from Charles I; vague terms; Buckingham obstruction; no clear authority against Venice; plausible deniability",
            people="Kenelm Digby, Charles I, Duke of Buckingham",
            places="London, Admiralty",
            date_display="Late 1627",
            year=1627,
            significance="The ambiguity of Digby's commission is central to understanding why the pirate label stuck: his authority was real but limited, and he consistently exceeded it.",
            citation_ids="cit_mosh_ch4_commission,cit_piracy_article",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_pirate_fleet_assembly",
            theme="pirate",
            title="Fleet Assembly and the Shadow of Cadiz",
            summary=(
                "Digby assembled his fleet in the autumn and winter of 1627, a process "
                "that revealed both his determination and the parlous state of English "
                "naval power. His flagship was the Eagle, a vessel of roughly 300 tons, "
                "accompanied by the smaller Elisabeth and George. He recruited sailors "
                "from the London waterfront, many of them veterans of the disastrous "
                "expeditions to Cadiz in 1625 and the Ile de Re in 1627, campaigns that "
                "had killed thousands of English sailors through disease, incompetent "
                "leadership, and inadequate supply. These men were scarred, hungry, and "
                "skeptical of grand promises. Digby had to pay and provision them from "
                "his own resources, supplemented by investments from friends and family. "
                "The total cost of outfitting the fleet ran to several thousand pounds, "
                "a substantial sum that Digby could only recoup through successful prize-"
                "taking. The fleet carried roughly 150 men on the Eagle alone, plus "
                "additional crews on the smaller vessels. Digby also needed to stockpile "
                "provisions for months at sea: biscuit, salt beef, beer, gunpowder, "
                "shot, and medical supplies. The recruitment process was complicated by "
                "Buckingham's interference: the Duke controlled naval appointments and "
                "could poach sailors and ships from any expedition he chose to obstruct. "
                "That Digby managed to assemble a seaworthy fleet and sail on schedule "
                "was itself a minor triumph of logistics and political maneuvering."
            ),
            key_details="Eagle ~300 tons; Elisabeth and George; 150+ crew; veterans of Cadiz and Ile de Re; self-funded expedition; Buckingham interference",
            people="Kenelm Digby, Duke of Buckingham, Edward Stradling",
            places="London, Thames",
            date_display="Autumn-Winter 1627",
            year=1627,
            significance="The fleet assembly demonstrates Digby's practical capabilities and the economic realities of Caroline privateering.",
            citation_ids="cit_mosh_ch4_commission,cit_piracy_article",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_pirate_plague_detail",
            theme="pirate",
            title="Plague at Sea: Crisis and Command",
            summary=(
                "Shortly after entering the Mediterranean in late January 1628, a "
                "devastating pestilential disease swept through Digby's crew. On the "
                "Eagle alone, sixty of roughly 150 men fell ill within days. The symptoms "
                "were severe: high fever, delirium, and rapid debilitation. The sick men "
                "hallucinated, believing the sea around them was a spacious and pleasant "
                "green meadow through which they tried to walk, falling overboard if not "
                "restrained. Officers urged Digby to turn back to England, arguing that "
                "the voyage was doomed before it had properly begun. The disease was "
                "almost certainly typhus, the scourge of early modern navies, spread by "
                "lice in the cramped, unsanitary conditions below decks. Digby faced his "
                "first true test of command. Rather than retreat, he pressed forward to "
                "Algiers, reasoning that the North African port offered better prospects "
                "for treating the sick and resupplying than the long voyage home through "
                "hostile waters. This decision was both brave and pragmatic. A return "
                "voyage would have taken weeks and killed many of the sick; Algiers was "
                "days away and had functioning markets for food and medicine. The crisis "
                "also revealed Digby's leadership style: he personally attended the sick, "
                "maintained discipline among the healthy crew, and made decisions quickly "
                "under pressure. His refusal to turn back set the tone for the rest of "
                "the voyage."
            ),
            key_details="60 of 150 sick on Eagle; hallucinations of green meadow; officers urged return; typhus likely; Digby pressed on to Algiers",
            people="Kenelm Digby, crew of the Eagle",
            places="Mediterranean, approaching Algiers",
            date_display="Late January 1628",
            year=1628,
            significance="The plague crisis was the defining early test of Digby's command. His decision to press forward rather than retreat shaped the entire voyage.",
            citation_ids="cit_mosh_ch4_plague,cit_piracy_article",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_pirate_algiers_liberation",
            theme="pirate",
            title="Algiers: Slave Liberation and Mediterranean Diplomacy",
            summary=(
                "Digby arrived at Algiers in February 1628 and remained for several "
                "weeks, a stay that combined medical crisis management with diplomatic "
                "initiative. The port city was the capital of one of the most powerful "
                "Barbary regencies, a corsair state that lived by raiding Christian "
                "shipping and enslaving captives. Thousands of European Christians were "
                "held as slaves in Algiers, including a significant number of English "
                "men and women captured at sea or in raids on coastal settlements. Digby "
                "negotiated with the local authorities for the release of English captives, "
                "combining persuasion with the implicit threat of his armed fleet. The "
                "exact number of slaves he freed varies between sources, but he secured "
                "the release of several dozen English subjects, an achievement that would "
                "later enhance his reputation at home. The Algiers stay also allowed Digby "
                "to resupply his ships, recruit replacement sailors, and treat the sick. "
                "The city was one of the most cosmopolitan in the Mediterranean: a hub "
                "where Turkish, Arab, Berber, European renegade, and Jewish communities "
                "intersected. Digby encountered a diverse population and a functioning "
                "urban economy that offered everything from fresh provisions to "
                "intelligence about shipping movements. His successful navigation of "
                "Algiers diplomacy demonstrated skills that went far beyond seamanship: "
                "he needed to understand Ottoman political structures, corsair customs, "
                "and the delicate balance of power in North Africa."
            ),
            key_details="Several dozen English slaves freed; resupply and medical treatment; cosmopolitan city; Ottoman political structures; diplomatic skill demonstrated",
            people="Kenelm Digby",
            places="Algiers",
            date_display="February-March 1628",
            year=1628,
            significance="The Algiers episode shows Digby as diplomat and humanitarian as well as fighter, adding moral legitimacy to a voyage that would later be contested.",
            citation_ids="cit_mosh_ch5_algiers_full,cit_piracy_article",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_pirate_prize_economics",
            theme="pirate",
            title="The Economics of Prize-Taking",
            summary=(
                "Throughout the voyage Digby captured a series of merchant vessels, the "
                "prizes that were the economic engine of any privateering expedition. "
                "The economics were straightforward in principle but complex in practice. "
                "A captured vessel and its cargo had to be adjudicated by a prize court "
                "upon return to England, which would determine whether the seizure was "
                "lawful and how the proceeds would be divided. The captain (Digby) "
                "typically received the largest share, with portions going to the crew, "
                "investors, and the Crown. Digby captured a Flemish vessel in a severe "
                "fight in March, took his fleet into the harbor at Cagliari, Sardinia, "
                "and drove defenders back from their positions. He seized French merchant "
                "ships at Scanderoon, and on his homeward voyage captured additional "
                "prizes including a Hamburg merchant ship carrying Granadan wool near "
                "Sardinia. The cumulative value of these prizes was substantial, though "
                "the exact figures are difficult to determine. Digby also had to manage "
                "prize crews to sail captured vessels, distribute food and water across "
                "an expanding fleet, and deal with captured sailors who might be hostile, "
                "ill, or simply inconvenient. The logistics of prize-taking consumed "
                "enormous energy and created ongoing tensions with local authorities at "
                "every port. The economic incentive was always in tension with the "
                "diplomatic risks: every prize taken was a potential diplomatic incident "
                "that could turn profitable privateering into prosecutable piracy."
            ),
            key_details="Flemish vessel March; Cagliari Sardinia; French ships at Scanderoon; Hamburg wool ship; prize court adjudication; crew shares system",
            people="Kenelm Digby, Edward Stradling",
            places="Mediterranean, Cagliari, Scanderoon, Sardinia",
            date_display="January-November 1628",
            year=1628,
            significance="The prize economics reveal that Digby's voyage was fundamentally a commercial enterprise as well as a quest for glory, driven by the need to recoup investment.",
            citation_ids="cit_mosh_ch6_prizes,cit_miles_courtier_career",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_pirate_heliodorus",
            theme="pirate",
            title="Reading Heliodorus Becalmed off Egypt",
            summary=(
                "In late July 1628, Digby's ships were becalmed off the Egyptian coast "
                "for five sweltering days. With nothing to do but wait for wind, Digby "
                "retreated to his cabin and read the Aethiopica of Heliodorus, a late "
                "antique Greek romance about the star-crossed lovers Theagenes and "
                "Chariclea wandering the Mediterranean. The resonance between the "
                "fictional narrative and Digby's own experience was profound: like "
                "Theagenes, Digby was a young man of noble birth traversing the "
                "Mediterranean, facing dangers, and separated from the woman he loved. "
                "The reading of Heliodorus was not merely a pastime but a formative "
                "intellectual event. It inspired Digby to write his own autobiographical "
                "romance, the Loose Fantasies, composed a few weeks later on the island "
                "of Milos. In that work Digby adopted the name Theagenes for himself "
                "and reimagined his life story through the conventions of the romance "
                "genre. As Moshenska has argued, Digby did not simply write a romance "
                "based on his life; he strove to live his life as a romance. The decision "
                "to structure his experience through a literary model was itself a form of "
                "self-fashioning, transforming a privateering voyage into a narrative of "
                "heroic adventure and personal redemption. Sweet winds blowing from the "
                "Arabian coast perfumed the air as Digby read, a detail he recorded with "
                "characteristic sensitivity to the sensory world."
            ),
            key_details="Five days becalmed off Egypt; read Heliodorus Aethiopica; adopted name Theagenes; wrote Loose Fantasies at Milos; sweet Arabian winds",
            people="Kenelm Digby, Venetia Stanley (as Stelliana)",
            places="Egyptian coast, Milos",
            date_display="Late July 1628",
            year=1628,
            significance="The Heliodorus episode reveals Digby's characteristic fusion of literary culture and lived experience, making his voyage unique among Caroline privateering expeditions.",
            citation_ids="cit_mosh_ch7_heliodorus,cit_piracy_article",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_pirate_venetian_propaganda",
            theme="pirate",
            title="The Venetian Propaganda Campaign",
            summary=(
                "After the Battle of Scanderoon on 11 June 1628, the Republic of Venice "
                "launched a systematic diplomatic campaign to brand Digby as a pirate "
                "throughout the Mediterranean and across European courts. Venetian "
                "ambassadors and consuls wrote coordinated dispatches calling Digby a "
                "thief, a pirate who had sold all his property for the sake of robbing, "
                "and an audacious criminal. These were not casual insults but deliberate "
                "diplomatic communications designed to delegitimize Digby's voyage and "
                "pressure England into disowning him. The campaign was effective: English "
                "merchants at Aleppo were imprisoned in retaliation for the battle, and "
                "English diplomats like Sir Thomas Roe, the ambassador at Constantinople, "
                "complained bitterly about the disruption to Levant trade. Roe was "
                "particularly hostile because he was Protestant and suspicious of Digby's "
                "Catholic loyalties, seeing the voyage as a reckless Catholic adventure "
                "that endangered Protestant commercial interests. The Venetian campaign "
                "also reached London, where it influenced how the voyage was received "
                "at court. Even those who admired Digby's bravery worried about the "
                "diplomatic consequences. The pirate label proved remarkably sticky: "
                "it appears in Venetian state papers, English diplomatic correspondence, "
                "and later historical accounts. Digby spent years after his return trying "
                "to rehabilitate his reputation, writing his Journal and the Loose "
                "Fantasies in part to counter the narrative that he was nothing more "
                "than an unscrupulous pirate."
            ),
            key_details="Coordinated Venetian dispatches; English merchants imprisoned at Aleppo; Thomas Roe hostile; Protestant suspicion of Catholic captain; pirate label persisted",
            people="Kenelm Digby, Thomas Roe, Alvise da Pesaro, Antonio Capello",
            places="Constantinople, Aleppo, Venice, London",
            date_display="June-December 1628",
            year=1628,
            significance="The Venetian propaganda campaign is a case study in how early modern reputations were contested across diplomatic networks, and how the pirate/privateer distinction was fundamentally political.",
            citation_ids="cit_mosh_ch7_scanderoon_full,cit_mosh_ch8_aftermath,cit_piracy_article",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_pirate_aftermath_return",
            theme="pirate",
            title="Return and Aftermath: Hero or Pirate?",
            summary=(
                "Digby returned to England in February 1629 after thirteen months at sea, "
                "arriving with captured prizes, ancient marbles from Delos, exotic plant "
                "specimens, and a greatly enhanced reputation among those who admired "
                "martial valor. He was received by King Charles I and presented his "
                "trophies at court. The Delos marbles were among the first significant "
                "collections of classical antiquities brought to England, predating the "
                "Arundel Marbles in scope if not in systematic intent. But the reception "
                "was not uniformly positive. The Venetian ambassador in London continued "
                "to press complaints, English merchants who had suffered losses demanded "
                "compensation, and the diplomatic consequences of Scanderoon lingered "
                "for years. Digby's prizes had to pass through prize courts, where their "
                "legality was contested. The assassination of Buckingham in August 1628, "
                "which Digby learned of while still at sea, removed his most powerful "
                "enemy but also eliminated the political dynamic that had partly "
                "motivated the voyage. Without Buckingham to oppose, the voyage lost "
                "some of its narrative urgency as an act of defiance. Digby was never "
                "formally charged with piracy, but the label haunted him. His response "
                "was literary as much as legal: the Journal, the Loose Fantasies, and "
                "later the published account of the Scanderoon battle were all efforts "
                "to control the narrative of his voyage and establish himself as a hero "
                "rather than a pirate."
            ),
            key_details="February 1629 return; Delos marbles; Charles I reception; Venetian complaints continued; prize court proceedings; Buckingham dead; literary self-defense",
            people="Kenelm Digby, Charles I, Venetia Stanley",
            places="London, Delos",
            date_display="February 1629 onward",
            year=1629,
            significance="The contested aftermath reveals how Digby's voyage was simultaneously a triumph and a liability, its meaning determined by competing narratives rather than fixed facts.",
            citation_ids="cit_mosh_ch8_aftermath,cit_piracy_article,cit_miles_courtier_career",
            confidence=Confidence.HIGH.value,
        ),
    ]

    # ========================================================================
    # ALCHEMIST PAGE — Theme Records
    # ========================================================================
    alchemist_themes = [
        DigbyThemeRecord(
            id="thm_alch_two_treatises",
            theme="alchemist_natural_philosopher",
            title="Two Treatises: Of Bodies and Of Man's Soul (1644)",
            summary=(
                "Digby published his major philosophical work in Paris in 1644, during "
                "the Civil War exile that had driven him from England. The Two Treatises "
                "attempted nothing less than a comprehensive account of the natural world "
                "and the human soul, reconciling Catholic theology with contemporary "
                "natural philosophy. The first treatise, Of Bodies, developed a "
                "corpuscular theory of matter that drew on both Aristotelian and "
                "atomistic traditions. Digby argued that all physical phenomena could "
                "be explained by the motions and interactions of minute particles, a "
                "position that aligned him with the emerging mechanical philosophy while "
                "retaining elements of older Aristotelian thought. The second treatise, "
                "Of Man's Soul, argued for the immortality of the rational soul on "
                "philosophical grounds, seeking to demonstrate that the soul's capacity "
                "for abstract thought proved it could not be merely material. This was "
                "a deeply Catholic argument, designed to show that natural philosophy "
                "supported rather than undermined orthodox theology. The Two Treatises "
                "were widely read and debated. Alexander Ross published a critical "
                "response, and Thomas Hobbes, who had known Digby in Paris, engaged "
                "with his arguments. The work established Digby as a serious "
                "philosophical thinker, not merely an adventurer or courtier, and it "
                "remains his most sustained intellectual achievement."
            ),
            key_details="Published Paris 1644; corpuscular theory; Aristotelian and atomistic synthesis; immortality of soul argument; Ross critique; Hobbes engagement",
            people="Kenelm Digby, Alexander Ross, Thomas Hobbes",
            places="Paris",
            date_display="1644",
            year=1644,
            significance="The Two Treatises positioned Digby at the intersection of Catholic theology and mechanical philosophy, a combination unique in seventeenth-century England.",
            citation_ids="cit_georgescu_philosophy,cit_dobbs_1973_paris",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_alch_powder_sympathy",
            theme="alchemist_natural_philosopher",
            title="The Powder of Sympathy Lectures at Montpellier",
            summary=(
                "In 1657, while travelling in southern France for treatment of his "
                "bladder stone, Digby delivered a celebrated lecture at the Academy of "
                "Sciences at Montpellier on the Powder of Sympathy, a simple compound "
                "of vitriol (iron sulphate) that purportedly healed wounds at a distance "
                "when applied to a bloodied cloth rather than the wound itself. The "
                "lecture, published in Paris and London in 1658 as A Late Discourse, "
                "went through over forty editions in French, English, Latin, Dutch, and "
                "German. Digby's account was distinctive because he offered a "
                "mechanistic explanation for the cure's operation: he argued that "
                "atoms of blood carried to the powder were combined with curative "
                "atoms of vitriol and then attracted back to the wound by sympathy, "
                "eliminating the need for astral or spiritual agencies invoked by "
                "earlier defenders of the weapon-salve like Robert Fludd. As Hedrick "
                "has shown, Digby also claimed priority for introducing the powdered "
                "form of the cure to Europe, telling the story of his cure of James "
                "Howell's wounded hand as foundational evidence. This priority claim "
                "was almost certainly false, as contemporaries recognized, but the "
                "rhetorical skill with which Digby presented it made the Late Discourse "
                "enormously influential. The practical effect of the powder was probably "
                "beneficial: by keeping the actual wound clean and free of the caustic "
                "ointments that conventional medicine applied, it allowed natural "
                "healing to proceed."
            ),
            key_details="1657 Montpellier lecture; vitriol powder; 40+ editions; mechanistic atomistic explanation; James Howell cure story; priority claim contested by Hedrick",
            people="Kenelm Digby, James Howell, Robert Fludd",
            places="Montpellier, Paris, London",
            date_display="1657-1658",
            year=1657,
            significance="The Powder of Sympathy was Digby's most famous single contribution to natural philosophy, demonstrating his ability to present occult phenomena in mechanistic terms.",
            citation_ids="cit_hedrick_powder,cit_lobis_sympathy,cit_mellick_courtier",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_alch_lefevre_paris",
            theme="alchemist_natural_philosopher",
            title="Le Fevre's Influence and the Paris Alchemical Circle",
            summary=(
                "During his extended residences in Paris in the 1650s, Digby came under "
                "the influence of Nicolas Le Fevre (Nicasius le Febvre), a distinguished "
                "chemist who served as demonstrator at the Jardin du Roi. Le Fevre's "
                "teaching systematized alchemical practice and connected it to the "
                "emerging discipline of rational chemistry. Through Le Fevre, Digby "
                "absorbed the concept of the Universal Spirit, a subtle fluid that "
                "permeated all matter and could be manipulated through chemical "
                "operations. This concept became central to Digby's mature alchemy, "
                "as expressed in his 1660 lecture on the Vegetation of Plants and in the "
                "marginalia attributed to him in the British Library Hypnerotomachia "
                "Poliphili. Le Fevre also introduced Digby to the work of Jean "
                "d'Espagnet, whose writings on the Philosophers' Stone and the universal "
                "spirit informed Digby's identification of Mercury as the master element. "
                "As Principe's discovery of the Strasbourg manuscripts has shown, Digby "
                "was part of a substantial alchemical circle in Paris during this period, "
                "trading manuscripts and information with collaborators including Samuel "
                "Cottereau Duclos and others connected to the French scientific community. "
                "This circle was not a marginal occult gathering but overlapped with "
                "the learned societies that would later become the Academie des Sciences."
            ),
            key_details="Le Fevre demonstrator Jardin du Roi; Universal Spirit concept; d'Espagnet influence; Mercury as master element; Principe Strasbourg discovery; Duclos collaboration",
            people="Kenelm Digby, Nicolas Le Fevre, Jean d'Espagnet, Samuel Cottereau Duclos",
            places="Paris, Jardin du Roi",
            date_display="1650s",
            year=1651,
            significance="Le Fevre's influence represents the crucial transition in Digby's alchemy from inherited Hermetic tradition to systematic experimental philosophy.",
            citation_ids="cit_dobbs_1973_lefevre,cit_principe_paris_circle",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_alch_chymical_secrets",
            theme="alchemist_natural_philosopher",
            title="Chymical Secrets: The Posthumous Book of Recipes",
            summary=(
                "In 1682, seventeen years after Digby's death, his servant and "
                "laboratory assistant George Hartman published A Choice Collection of "
                "Rare Chymical Secrets, compiled from Digby's manuscripts. The book "
                "provides a rich sample of mid-seventeenth-century alchemy and chemical "
                "pharmacy. Hartman, who had served Digby for several years in both "
                "France and England, translated most of the secrets from Latin, French, "
                "German, and Italian, testifying to the international scope of Digby's "
                "alchemical network. The book is divided into two sections: the first "
                "largely devoted to alchemical recipes and processes for metallic "
                "transmutation, the second to medicines and cosmetics. As Dobbs has "
                "demonstrated, the collection is remarkable for its operational clarity. "
                "Starting materials are described precisely, quantities are specified "
                "for each step, and the necessary degrees of fire are delineated. Many "
                "processes can be translated into modern chemical terminology. Digby's "
                "own favorite recipe involved the fixation of mercury using a powder "
                "that he had demonstrated before Charles I. The book also contains the "
                "recipe for engendering crayfishes through palingenesis, dating from "
                "the Gresham College period of the 1630s, and various pharmaceutical "
                "preparations collected during the Paris years. The experimental nature "
                "of the collection cannot be emphasized too strongly: these are "
                "operational instructions, not mystical allegory."
            ),
            key_details="Published 1682 by Hartman; translated from four languages; operational clarity; mercury fixation; palingenesis; medicines and cosmetics",
            people="Kenelm Digby, George Hartman, Charles I",
            places="London, Paris",
            date_display="1682 (recipes from 1630s-1660s)",
            year=1682,
            significance="The Chymical Secrets demonstrates that Digby's alchemy was empirical and operational, not merely theoretical, making it a key document in the history of experimental chemistry.",
            citation_ids="cit_dobbs_1974_secrets,cit_miles_courtier_career",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_alch_gresham_experiments",
            theme="alchemist_natural_philosopher",
            title="Experiments at Gresham College After Venetia's Death",
            summary=(
                "After the sudden death of his wife Venetia on 1 May 1633, Digby "
                "withdrew from public life and retreated to Gresham College in London, "
                "where he spent roughly two years in intense grief and scholarly "
                "seclusion. As Aubrey recorded, he wore a long mourning cloak, a high-"
                "crowned hat, and left his beard unshorn, looking like a hermit in "
                "signs of sorrow. But this period of mourning was also intensely "
                "productive. Digby established a large laboratory at Gresham under the "
                "lodgings of the Divinity Reader, with his own quarters at the end of "
                "the great gallery. A 1648 inventory of the laboratory, discovered by "
                "Wilkinson among the Hartlib Papers, reveals an impressive array of "
                "equipment: reverberating and calcining ovens, a balneum Mariae (water "
                "bath), sand and retort furnaces, an athanor (digestion furnace), "
                "twenty alembic bodies of several sizes, grinding stones, glass funnels, "
                "a screw press, and copper stills with refrigerators. Digby devoted "
                "much of his time to experiments on palingenesis, the attempt to revive "
                "or resurrect plants and animals from their calcined ashes. He "
                "successfully produced the form of calcined crayfishes and claimed to "
                "regenerate living animals from their ashes by feeding them ox-blood. "
                "The concept of palingenesis was intimately connected in Digby's mind "
                "to the Christian doctrine of the Resurrection of the Body, given "
                "particular emotional force by Venetia's death."
            ),
            key_details="1633-1635 at Gresham; elaborate laboratory inventory; palingenesis experiments; crayfish resurrection; mourning period; Hermetic and Christian synthesis",
            people="Kenelm Digby, Venetia Stanley, Hans Hunneades",
            places="Gresham College, London",
            date_display="1633-1635",
            year=1633,
            significance="The Gresham period shows how personal grief catalyzed Digby's most intense experimental work, connecting alchemy to his deepest emotional and theological concerns.",
            citation_ids="cit_dobbs_1973_gresham,cit_miles_courtier_career",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_alch_winchester_prison",
            theme="alchemist_natural_philosopher",
            title="Alchemy During Winchester Imprisonment",
            summary=(
                "In 1642, as Civil War broke out, Parliament imprisoned Digby at "
                "Winchester House, the former episcopal palace of Lancelot Andrewes in "
                "Southwark. As a Catholic Royalist, Digby was doubly suspect, but his "
                "social standing earned him privileged conditions of confinement. He "
                "established a laboratory within Winchester House and hired John Colnett, "
                "a worker from a nearby glass factory, as his operator. Together they "
                "developed an improved method for manufacturing glass bottles, a "
                "contribution to practical chemistry that only came to light in 1662 "
                "when Colnett applied for a patent and was opposed by other glass "
                "workers who knew the process to have been Digby's invention. The "
                "Attorney-General was convinced that Digby had first invented glass "
                "bottles nearly thirty years earlier and had employed Colnett to make "
                "them. Digby's work on glassware addressed a serious practical problem: "
                "available glass was of very poor quality, and defective vessels negated "
                "many experimental results or broke at crucial points. His improvements "
                "represented a very practical effort to raise the operational standards "
                "of chemical experimentation. The Winchester period also saw Digby "
                "continue his alchemical studies, likely working on processes later "
                "recorded in the Chymical Secrets."
            ),
            key_details="Winchester House 1642; privileged imprisonment; John Colnett glass operator; glass bottle improvements; 1662 patent dispute; practical chemistry",
            people="Kenelm Digby, John Colnett",
            places="Winchester House, Southwark",
            date_display="1642-1643",
            year=1642,
            significance="The Winchester imprisonment shows Digby pursuing practical chemistry even in captivity, and his glass innovations had lasting industrial significance.",
            citation_ids="cit_dobbs_1973_winchester,cit_dobbs_1973_civil_war",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_alch_vegetation_plants",
            theme="alchemist_natural_philosopher",
            title="The Vegetation of Plants: Royal Society Lecture (1661)",
            summary=(
                "On 23 January 1661, Digby delivered a notable lecture to the newly "
                "formed Royal Society at Gresham College on the vegetation of plants, "
                "published that same year as A Discourse Concerning the Vegetation of "
                "Plants. The lecture synthesized his decades of alchemical thinking into "
                "a systematic account of plant growth. Digby argued that plants drew "
                "their nourishment from a universal spirit or saltpetre distributed "
                "through the air and soil, a concept he had absorbed from Le Fevre and "
                "d'Espagnet during his Paris years. He claimed that gold was of the same "
                "nature as the aethereal spirit, or rather was nothing but that spirit "
                "first corporified in a pure place, an assertion that connected plant "
                "biology to alchemical transmutation through the concept of a universal "
                "matter. The lecture drew on his personal experience: he described his "
                "earlier laboratory at Gresham College and experiments he had conducted "
                "on plant nutrition using controlled soil conditions. The discourse was "
                "well received by the Society, whose members were eager for systematic "
                "accounts of natural processes. It represented Digby's mature natural "
                "philosophy: empirical in method, alchemical in theory, and confident "
                "that observable phenomena could be explained by the motions and "
                "transformations of a universal material spirit."
            ),
            key_details="23 January 1661; Royal Society at Gresham; universal spirit/saltpetre; gold = aethereal spirit corporified; plant nutrition experiments; Le Fevre influence",
            people="Kenelm Digby, Nicolas Le Fevre",
            places="Gresham College, London",
            date_display="23 January 1661",
            year=1661,
            significance="The Vegetation lecture was Digby's last major scientific contribution, representing the synthesis of his alchemical and philosophical thinking before the Royal Society.",
            citation_ids="cit_dobbs_1973_lefevre,cit_miles_courtier_career,cit_mellick_courtier",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_alch_strasbourg_manuscripts",
            theme="alchemist_natural_philosopher",
            title="The Strasbourg Manuscripts: 5,000 Pages of Alchemical Practice",
            summary=(
                "In 2010, Lawrence Principe discovered eleven manuscripts in the "
                "Bibliotheque Nationale et Universitaire de Strasbourg that are "
                "unambiguously identifiable as Digby's by his characteristic "
                "handwriting. These manuscripts comprise over five thousand pages of "
                "material, almost entirely relating to metallic transmutation. One "
                "volume was magnificently bound in fine leather bearing a gilt "
                "fleur-de-lis and Digby's monogram KD in gold on the spine. The "
                "manuscripts reveal Digby's method of collecting and reading alchemical "
                "texts: he strove to achieve the most accurate and complete text of "
                "materials within the manuscript tradition, employing scribes to copy "
                "works and then meticulously comparing copies against originals and "
                "other manuscripts, noting variant readings in extensive autograph "
                "marginalia. This was the method of a trained humanist applied to "
                "alchemical literature. The manuscripts also contain transcripts from "
                "the otherwise lost notebooks of Joseph Du Chesne and Samuel Cottereau "
                "Duclos, including letters from Johann Rudolf Glauber datable to late "
                "1651. They document a circle of alchemical collaborators active in "
                "Paris during the 1650s and 1660s, trading manuscripts and information "
                "and collaborating on projects ranging from the Philosophers' Stone to "
                "chemical medicines. The discovery transformed understanding of Digby's "
                "alchemy from a minor eccentricity to a major commitment."
            ),
            key_details="Principe 2010 discovery; 11 manuscripts; 5000+ pages; transmutation focus; humanist textual criticism; Glauber letters 1651; Paris circle documented",
            people="Kenelm Digby, Lawrence Principe, Samuel Cottereau Duclos, Johann Rudolf Glauber",
            places="Strasbourg, Paris",
            date_display="1650s-1660s (discovered 2010)",
            year=1652,
            significance="The Strasbourg discovery is the most important single advance in Digby studies in decades, revealing the scale and seriousness of his alchemical commitment.",
            citation_ids="cit_principe_paris_circle,cit_principe_manuscripts",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_alch_closet_recipes",
            theme="alchemist_natural_philosopher",
            title="The Closet of Sir Kenelm Digby Opened: Recipes and Domestic Chemistry",
            summary=(
                "Published posthumously in 1669, The Closet of Sir Kenelm Digby Opened "
                "is a recipe collection that sits at the intersection of alchemy, "
                "medicine, and domestic economy. The book contains recipes for meads, "
                "metheglin (spiced mead), ales, wines, cordials, conserves, and "
                "medicinal preparations, many of them collected during Digby's travels "
                "across Europe. Unlike the Chymical Secrets, which aimed at metallic "
                "transmutation, the Closet focuses on the transformation of organic "
                "materials through fermentation, distillation, and infusion. Yet the "
                "underlying principles are the same: careful observation of processes, "
                "precise specification of quantities and conditions, and confidence "
                "that natural transformations can be controlled and directed through "
                "human skill. Several recipes involve sophisticated chemical processes, "
                "including the preparation of cordials that required distillation and "
                "rectification. The Closet has been reprinted numerous times and has "
                "attracted attention from food historians as one of the earliest English "
                "cookbooks by a named male author. But it should also be understood as "
                "an extension of Digby's alchemical practice into the domestic sphere, "
                "applying the same experimental sensibility to food and drink that he "
                "brought to the laboratory."
            ),
            key_details="Published 1669 posthumously; meads, metheglin, ales, cordials; collected across Europe; fermentation and distillation; food history significance",
            people="Kenelm Digby",
            places="London, Paris, various European courts",
            date_display="1669 (recipes collected 1620s-1660s)",
            year=1669,
            significance="The Closet reveals that Digby's experimental sensibility extended beyond the laboratory into everyday life, making him a pioneer of systematic recipe literature.",
            citation_ids="cit_miles_courtier_career,cit_mellick_courtier",
            confidence=Confidence.MEDIUM.value,
        ),
    ]

    # ========================================================================
    # COURTIER PAGE — Theme Records
    # ========================================================================
    courtier_themes = [
        DigbyThemeRecord(
            id="thm_courtier_james_knighthood",
            theme="courtier_legal_thinker",
            title="Service to King James and the Knighthood of 1623",
            summary=(
                "Digby's entry into court life was remarkably swift for a young man "
                "whose father had been executed as a traitor just seventeen years "
                "earlier. After returning from his Grand Tour in September 1623, during "
                "which he had accompanied Prince Charles and Buckingham in Madrid during "
                "the failed Spanish Match, Digby was knighted by King James I on 21 "
                "October 1623, at the age of just twenty. The knighthood was a dramatic "
                "gesture of royal rehabilitation: it signaled that the Crown no longer "
                "held the sins of the father against the son. Digby had earned this "
                "favor through personal charm, intellectual brilliance, and the "
                "connections he had made in Madrid, where he impressed the Prince with "
                "his courage, learning, and courtly manner. He was tall, handsome, and "
                "extraordinarily well-read, qualities that made him a natural ornament "
                "of any court. The knighthood also reflected the Stuart monarchy's "
                "willingness to reconcile with the Catholic gentry, a policy that would "
                "cause increasing political friction as anti-Catholic sentiment grew. "
                "For Digby personally, the knighthood was redemption: the stain in his "
                "blood from the Gunpowder Plot was officially, if not entirely, "
                "expunged. He was now Sir Kenelm, a gentleman of the bedchamber to "
                "the King, with all the access and influence that position implied."
            ),
            key_details="Knighted 21 October 1623 by James I; age 20; Spanish Match connection; rehabilitation of Gunpowder Plot family; gentleman of bedchamber",
            people="Kenelm Digby, James I, Prince Charles, Duke of Buckingham",
            places="London, Madrid",
            date_display="21 October 1623",
            year=1623,
            significance="The knighthood represents the pivotal moment when Digby transformed from the son of a traitor into a courtier, the beginning of his political career.",
            citation_ids="cit_mosh_ch2_grand_tour_court,cit_mellick_courtier",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_courtier_charles_relationship",
            theme="courtier_legal_thinker",
            title="Relationship with Charles I",
            summary=(
                "Digby's relationship with Charles I was one of the most consequential "
                "of his life, providing the political foundation for his Mediterranean "
                "voyage, his courtly career, and his survival through decades of "
                "political upheaval. The friendship dated from Madrid in 1623, when "
                "the young Digby and the young Prince Charles were both guests at the "
                "Spanish court during the failed negotiations for the Spanish Match. "
                "Charles appreciated Digby's combination of physical courage, "
                "intellectual range, and courtly grace. After Charles became king in "
                "1625, Digby became part of his inner circle, with access that aroused "
                "jealousy from rivals, particularly the Duke of Buckingham. Charles "
                "granted Digby the royal commission for his Mediterranean voyage "
                "despite Buckingham's opposition, a significant demonstration of "
                "personal favor. After Digby's return, Charles received him at court "
                "and admired the Delos marbles. Digby also demonstrated his alchemical "
                "powder for fixing mercury before the King, suggesting a degree of "
                "personal intimacy unusual for a Catholic subject. The relationship "
                "survived the tensions of the late 1620s and 1630s, though Digby's "
                "Catholicism made him increasingly vulnerable as anti-Catholic "
                "sentiment intensified. When Civil War came, Digby was a committed "
                "Royalist, but his Catholicism meant he could not serve openly in "
                "the way Protestant Royalists could."
            ),
            key_details="Friendship from Madrid 1623; inner circle access; commission despite Buckingham; mercury demonstration; Royalist commitment; Catholic vulnerability",
            people="Kenelm Digby, Charles I, Duke of Buckingham",
            places="Madrid, London, Whitehall",
            date_display="1623-1649",
            year=1623,
            significance="The Charles I relationship was Digby's political lifeline, providing the royal favor that protected him from his enemies and enabled his most ambitious ventures.",
            citation_ids="cit_mosh_ch3_knighthood,cit_miles_courtier_career",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_courtier_protestant_conversion",
            theme="courtier_legal_thinker",
            title="The Protestant Conversion and Naval Appointment",
            summary=(
                "In the mid-1620s, Digby made the remarkable decision to convert to "
                "Protestantism, or at least to present himself as having done so. The "
                "conversion was almost certainly strategic: it removed the most "
                "significant obstacle to his holding official positions in a Protestant "
                "state. As a Catholic, Digby was barred from public office by the "
                "recusancy laws; as a nominal Protestant, he could receive commissions, "
                "hold monopolies, and participate fully in court life. The conversion "
                "enabled his appointment as a naval commander with official authority "
                "rather than the ambiguous status of a Catholic adventurer. It also "
                "demonstrated the pragmatic flexibility that characterized Digby's "
                "approach to confessional politics throughout his life. He was born "
                "Catholic, educated by Jesuits, and would return to Catholicism openly "
                "by the 1630s, eventually serving as chancellor to the Catholic Queen "
                "Henrietta Maria. The Protestant interlude of the late 1620s was a "
                "tactical accommodation to political reality, not a genuine change of "
                "conviction. This confessional flexibility made Digby simultaneously "
                "useful and suspect: useful because he could operate across the "
                "Catholic-Protestant divide, suspect because neither side fully "
                "trusted a man who changed his religion for advantage."
            ),
            key_details="Mid-1620s conversion; strategic motivation; enabled naval commission; recusancy laws obstacle; returned to Catholicism by 1630s; confessional flexibility",
            people="Kenelm Digby, Charles I",
            places="London",
            date_display="c. 1626-1627",
            year=1626,
            significance="The Protestant conversion episode reveals the pragmatic dimension of Digby's courtier identity: willing to bend confessional allegiance to political necessity.",
            citation_ids="cit_mosh_ch3_knighthood,cit_piracy_article",
            confidence=Confidence.MEDIUM.value,
        ),
        DigbyThemeRecord(
            id="thm_courtier_henrietta_chancellor",
            theme="courtier_legal_thinker",
            title="Chancellor to Queen Henrietta Maria in Exile",
            summary=(
                "During the Civil War exile in Paris, Digby served as chancellor to "
                "Queen Henrietta Maria, the French-born Catholic wife of Charles I. "
                "The chancellorship was one of the most senior positions in the exiled "
                "court, giving Digby responsibility for managing the Queen's affairs, "
                "correspondence, and diplomacy. It was a role that suited his talents "
                "perfectly: he was multilingual, cosmopolitan, Catholic, and intimately "
                "familiar with French court culture from his years of travel and "
                "residence. The position also gave him access to the wider network of "
                "Catholic exile politics, including negotiations with the papacy, the "
                "French crown, and sympathetic European powers. Digby used his position "
                "to pursue his own diplomatic initiatives, including a mission to Rome "
                "in 1645 to seek papal support for the Royalist cause. The "
                "chancellorship was not merely ceremonial: Henrietta Maria was an "
                "active political figure who wielded significant influence over the "
                "Royalist faction, and her chancellor was involved in substantive "
                "decisions about policy, finance, and military support. For Digby, the "
                "position represented the culmination of his courtly career: the son "
                "of a Gunpowder Plotter had become the chief officer of the Queen of "
                "England, a triumph of personal rehabilitation that would have been "
                "unimaginable at the time of his father's execution."
            ),
            key_details="Chancellor to Henrietta Maria; Paris exile; managed Queen's affairs; Rome mission 1645; Catholic exile politics; personal rehabilitation",
            people="Kenelm Digby, Henrietta Maria, Charles I",
            places="Paris, Rome",
            date_display="1640s-1650s",
            year=1643,
            significance="The chancellorship was the apex of Digby's political career, demonstrating that a Catholic intellectual could reach the highest levels of service even in exile.",
            citation_ids="cit_miles_courtier_career,cit_mellick_courtier,cit_dobbs_1973_paris",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_courtier_cromwell",
            theme="courtier_legal_thinker",
            title="The Cromwell Relationship: Catholic Royalist Meets Lord Protector",
            summary=(
                "One of the most remarkable aspects of Digby's political career was "
                "his relationship with Oliver Cromwell, the man who had overthrown and "
                "executed his king. After returning briefly to England in 1654, Digby "
                "met with Cromwell and established a working relationship that puzzled "
                "contemporaries and has puzzled historians since. Cromwell was "
                "interested in Digby's international connections, his knowledge of "
                "European courts, and possibly his alchemical expertise. Digby, for "
                "his part, needed to protect his remaining property and secure safe "
                "passage between England and the Continent. The relationship was "
                "transactional rather than ideological: neither man shared the other's "
                "political or religious convictions, but both saw advantages in "
                "cooperation. Digby reportedly discussed religious toleration with "
                "Cromwell, arguing for greater freedom for Catholics, a cause that "
                "Cromwell was more sympathetic to than many assumed. The relationship "
                "also reflected Digby's extraordinary capacity for personal connection "
                "across political divides. Marjorie Nicolson was exaggerating only "
                "slightly when she wrote that Digby knew everybody: his list of "
                "correspondents and personal contacts included Ben Jonson, Thomas "
                "Hobbes, Descartes, Mersenne, Fermat, Hartlib, John Winthrop Jr., "
                "Robert Boyle, Henrietta Maria, and now Oliver Cromwell."
            ),
            key_details="1654 meeting with Cromwell; transactional relationship; discussed religious toleration; international connections valued; property protection; political flexibility",
            people="Kenelm Digby, Oliver Cromwell",
            places="London",
            date_display="1654-1658",
            year=1654,
            significance="The Cromwell relationship demonstrates Digby's extraordinary political adaptability, maintaining connections across the most fundamental divide in English politics.",
            citation_ids="cit_miles_courtier_career,cit_piracy_article",
            confidence=Confidence.MEDIUM.value,
        ),
        DigbyThemeRecord(
            id="thm_courtier_bibliophile",
            theme="courtier_legal_thinker",
            title="The Bibliophile Identity: Books as Cultural Capital",
            summary=(
                "Digby was one of the great bibliophiles of seventeenth-century "
                "England, and his library functioned as a form of cultural capital "
                "that enhanced his standing at court and in intellectual circles. His "
                "collection began with the manuscripts inherited from his Oxford tutor "
                "Thomas Allen, who bequeathed him his burning glass and a quantity of "
                "extremely valuable manuscripts that later formed the core of Digby's "
                "donation to the Bodleian Library. Throughout his life, Digby "
                "systematically acquired books, manuscripts, and curiosities from "
                "across Europe, taking advantage of his travels and diplomatic "
                "connections to build one of the finest private collections in England. "
                "The 1680 Bibliotheca Digbeiana, the posthumous catalogue of his "
                "library, documents an extraordinary breadth of reading across theology, "
                "philosophy, natural science, alchemy, literature, and history in "
                "multiple languages. Digby's bibliophilia was not merely acquisitive "
                "but scholarly: as Principe's Strasbourg manuscripts show, he "
                "approached texts with the methods of a trained humanist, comparing "
                "variant readings, correcting scribal errors, and tracking textual "
                "transmission. His donation to the Bodleian, one of the most "
                "significant private gifts the library received in the seventeenth "
                "century, secured his posthumous reputation as a patron of learning "
                "and ensured that his collections would survive for future scholars."
            ),
            key_details="Allen manuscripts inheritance; Bodleian donation; 1680 Bibliotheca Digbeiana; humanist textual methods; multilingual collection; cultural capital",
            people="Kenelm Digby, Thomas Allen",
            places="Oxford, Bodleian Library, London, Paris",
            date_display="1618-1665",
            year=1618,
            significance="Digby's library was both an intellectual resource and a political tool, demonstrating that books could be a form of power in early modern England.",
            citation_ids="cit_miles_courtier_career,cit_mellick_courtier,cit_principe_manuscripts",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_courtier_civil_war_prison",
            theme="courtier_legal_thinker",
            title="Civil War Imprisonment at Winchester House",
            summary=(
                "When the English Civil War broke out in 1642, Digby was arrested by "
                "Parliament and imprisoned at Winchester House in Southwark. His "
                "offenses were twofold: he was Catholic, and he was Royalist. The "
                "combination made him doubly suspect in the eyes of a Parliament "
                "increasingly hostile to both categories. However, his social standing "
                "and powerful friends ensured that his imprisonment was relatively "
                "comfortable by the standards of the time. He was allowed to establish "
                "a laboratory, receive visitors, and maintain correspondence. The "
                "imprisonment lasted until influential friends petitioned for his "
                "release, and Parliament allowed him to go into exile rather than "
                "face further confinement. Digby chose Paris, where the exiled "
                "Royalist court was gathering around Queen Henrietta Maria. The "
                "Winchester episode reveals the precarious position of Catholic "
                "intellectuals during the Civil War: too prominent to ignore, too "
                "well-connected to execute, but too Catholic and too Royalist to "
                "trust. Digby's ability to transform his prison into a functioning "
                "laboratory was characteristic of his refusal to let circumstances "
                "dictate his activities. Even in captivity, he pursued the "
                "experimental investigations that defined his intellectual life."
            ),
            key_details="1642 arrest; Winchester House Southwark; Catholic and Royalist; privileged conditions; laboratory in prison; petitioned release; exile to Paris",
            people="Kenelm Digby",
            places="Winchester House, Southwark, London",
            date_display="1642-1643",
            year=1642,
            significance="The imprisonment crystallizes Digby's dual identity as political actor and natural philosopher, showing how he maintained intellectual productivity under political constraint.",
            citation_ids="cit_dobbs_1973_civil_war,cit_miles_courtier_career",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_courtier_restoration_rs",
            theme="courtier_legal_thinker",
            title="Restoration Return and the Royal Society",
            summary=(
                "The Restoration of Charles II in 1660 allowed Digby to return to "
                "England after years of exile, and he quickly established himself as "
                "a prominent figure in Restoration intellectual life. He became a "
                "founding member of the Royal Society, the institution that would "
                "define English science for centuries. His election was natural: he "
                "was one of the most experienced experimental philosophers in England, "
                "with decades of laboratory work and a vast international network of "
                "scientific contacts. He delivered his lecture on the Vegetation of "
                "Plants at Gresham College in January 1661, one of the earliest "
                "formal presentations to the Society. He also engaged with the "
                "younger generation of natural philosophers, particularly Robert "
                "Boyle, to whom he gave numerous alchemical manuscripts. Digby's "
                "Restoration return was not merely a political homecoming but an "
                "intellectual one: he was reunited with the institutional framework "
                "that his earlier work at Gresham College had anticipated. He also "
                "received Privy Council appointment, confirming his rehabilitation "
                "as a trusted figure in public life. The Royal Society appointment "
                "was the final chapter of a career that had traversed piracy, "
                "alchemy, imprisonment, exile, and every major political upheaval "
                "of the seventeenth century. Digby died on his birthday, 11 June "
                "1665, and bequeathed his library to the Bodleian."
            ),
            key_details="1660 return; founding Royal Society member; Vegetation of Plants lecture; Boyle manuscripts; Privy Council; died 11 June 1665; Bodleian bequest",
            people="Kenelm Digby, Charles II, Robert Boyle",
            places="London, Gresham College, Oxford",
            date_display="1660-1665",
            year=1660,
            significance="The Restoration return brought Digby's career full circle, from the son of a traitor to a founding member of England's most prestigious scientific institution.",
            citation_ids="cit_miles_courtier_career,cit_mellick_courtier,cit_dobbs_1973_lefevre",
            confidence=Confidence.HIGH.value,
        ),
    ]

    # Insert all theme records
    added_themes = 0
    for tr in pirate_themes + alchemist_themes + courtier_themes:
        if tr.id not in existing_themes:
            validate_record(tr)
            insert_record("digby_theme_records", tr.to_dict())
            added_themes += 1
    print(f"Added {added_themes} new theme records.")

    # ========================================================================
    # PAGE SECTIONS — Long narrative prose
    # ========================================================================

    # --- PIRATE PAGE SECTIONS ---
    pirate_sections = [
        PageSection(
            id="sec_pirate_intro",
            page="pirate",
            section_key="intro",
            title="The Privateer's Commission: Context and Motivation",
            body=(
                "In the autumn of 1627, Sir Kenelm Digby assembled a small fleet in the Thames and prepared to sail for the Mediterranean. He was twenty-four years old, the son of an executed Gunpowder Plotter, a Catholic in a Protestant kingdom, and a young man with everything to prove. The voyage he was about to undertake would make him famous, make him controversial, and embed the word pirate so deeply in his reputation that he would spend the rest of his life trying to dislodge it.\n\n"
                "The context of Digby's voyage was the chaotic naval policy of Caroline England. Charles I had inherited from his father James I a kingdom whose foreign policy oscillated between anti-Spanish Protestant zeal and pro-Catholic rapprochement, and whose navy had been devastated by the disastrous expeditions to Cadiz in 1625 and the Ile de Re in 1627. These campaigns had killed thousands of English sailors through disease, incompetent command, and inadequate supply, and they had left England's military reputation in tatters. Against this backdrop, the Crown quietly encouraged private naval ventures, issuing commissions that gave ambitious men like Digby legal cover to attack enemy shipping while maintaining plausible deniability if things went wrong.\n\n"
                "Digby's motives were multiple and interlocking. He needed money: his family estate at Gayhurst had been diminished by his father's attainder, and his lifestyle required income beyond what his lands provided. He needed glory: the stain of the Gunpowder Plot hung over the Digby name, and a successful military expedition would demonstrate that the son was loyal where the father had been treasonous. He needed independence: the Duke of Buckingham, the most powerful man in England after the King, had become an obstacle to Digby's ambitions, and a Mediterranean voyage offered an escape from Buckingham's influence. And he needed adventure: Digby was young, physically brave, well-read in the literature of heroic enterprise, and temperamentally inclined to seek experience rather than safety.\n\n"
                "The commission he obtained from Charles I was deliberately vague, a standard feature of Caroline privateering that served the interests of both Crown and captain. England was at war with France and Spain, which gave Digby authority to seize French and Spanish vessels, but the Mediterranean was controlled by powers with whom England was at peace, and any action against Venetian, Ottoman, or neutral shipping would push Digby from privateer into pirate. This ambiguity was not a flaw but a feature: it allowed the Crown to claim credit for successes while disowning failures, and it gave Digby the latitude to act aggressively in pursuit of prizes while maintaining a veneer of legality."
            ),
            position=0,
            citation_ids="cit_mosh_ch4_commission,cit_piracy_article,cit_miles_courtier_career",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_pirate_context",
            page="pirate",
            section_key="context",
            title="The Mediterranean World of 1628",
            body=(
                "The Mediterranean into which Digby sailed in January 1628 was a world of overlapping empires, commercial networks, and legal ambiguities. The Ottoman Empire controlled the eastern basin from Constantinople, its authority exercised through provincial governors and a web of commercial treaties with European powers. Venice dominated trade at key ports like Scanderoon (modern Iskenderun), the gateway to the overland routes through Aleppo to Persia and the Far East. The Barbary regencies of Algiers, Tunis, and Tripoli operated as semi-autonomous corsair states, raiding Christian shipping and holding thousands of European captives as slaves.\n\n"
                "Into this complex world came English merchants and sailors, relative newcomers to Mediterranean trade who depended on the Levant Company's fragile relationships with Ottoman authorities and Venetian tolerance. The English presence was commercially valuable but politically precarious: any disruption to trade could provoke retaliation against English merchants resident in Ottoman cities like Aleppo and Constantinople. This was the world Digby entered with his two armed ships and roughly 200 men, navigating not just winds and currents but a diplomatic environment where one wrong move could endanger English commercial interests across the entire eastern Mediterranean.\n\n"
                "The distinction between privateering and piracy was, in this context, not a legal technicality but a matter of life and death. A privateer operated under the authority of a sovereign state and could claim the protection of international law; a pirate was an enemy of all mankind, subject to summary execution by any nation. Digby's royal commission gave him the authority of England, but that authority was recognized only by England. To the Venetians whose ships he attacked at Scanderoon, he was simply a pirate. To the Ottoman authorities whose port he disrupted, he was a foreign troublemaker. To English merchants whose trade he endangered, he was a reckless adventurer whose personal glory came at their commercial expense."
            ),
            position=10,
            citation_ids="cit_piracy_article,cit_mosh_ch5_algiers_full",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_pirate_essay",
            page="pirate",
            section_key="essay",
            title="Scanderoon and Its Consequences",
            body=(
                "The Battle of Scanderoon on 11 June 1628 was the defining event of Digby's voyage and the source of both his greatest fame and his most persistent controversy. Entering the Turkish harbor of Scanderoon (Iskenderun), Digby found French merchant vessels, English ships, and Venetian galleasses. He sent letters announcing his identity, but the Venetian general treated his men roughly and threatened to sink his ships. After enduring eight shots patiently and offering formal salutes, Digby attacked with all his might. The battle lasted three hours in mostly calm conditions, and by nightfall Digby had maimed the Venetian oars, captured French vessels, and forced the Venetian general to sue for peace.\n\n"
                "The immediate aftermath was chaotic. English merchants at Aleppo were seized in retaliation, their goods confiscated and their persons imprisoned. The vice-consul at Scanderoon begged Digby to leave, warning that his continued presence was causing a diplomatic crisis. Sir Thomas Roe, the English ambassador at Constantinople, was furious: he saw Digby's action as a reckless Catholic adventure that endangered the Protestant commercial interests he was charged with protecting. Venetian diplomats launched a coordinated campaign to brand Digby as a pirate, flooding European courts with dispatches that called him an audacious thief who had sold all his property for the sake of robbery.\n\n"
                "The battle's significance extended far beyond its immediate military impact. It demonstrated that a small English fleet could challenge Venetian naval power in the eastern Mediterranean, a proposition that had commercial and strategic implications for English trade expansion. But it also showed the costs of uncoordinated privateering: Digby's personal triumph created problems for English merchants and diplomats that took years to resolve. The tension between individual glory and collective interest was inherent in the privateering system, and Scanderoon was its most dramatic illustration."
            ),
            position=20,
            citation_ids="cit_mosh_ch7_scanderoon_full,cit_miles_courtier_career,cit_piracy_article",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_pirate_conclusion",
            page="pirate",
            section_key="conclusion",
            title="Legacy of the Voyage",
            body=(
                "Digby's Mediterranean voyage of 1628 occupies a unique place in the history of English seafaring. It was simultaneously a military expedition, a commercial venture, an antiquarian quest, a literary experiment, and a personal crusade for redemption. No other Caroline privateer combined these dimensions with such ambition, and no other produced the remarkable body of writing that Digby generated: the detailed Journal, the autobiographical Loose Fantasies, the Observations on Spenser, and the letters that documented his experiences in real time.\n\n"
                "The voyage's legacy was contested from the moment Digby returned. To his admirers, he was a hero in the mold of Drake and Raleigh, a young Englishman who had demonstrated courage, leadership, and enterprise in the Mediterranean. To his critics, he was a reckless pirate whose Catholic loyalties made his motives suspect and whose actions had endangered English commerce. Both narratives contained truth, and neither captured the full complexity of what Digby had accomplished.\n\n"
                "As the naval historian N. A. M. Rodger observed, Digby's expedition, like its leader, was unique. This uniqueness has led to the voyage being either ignored as a mere oddity or imperfectly understood. In recent decades, Moshenska's detailed scholarship has begun to restore the voyage to its proper place in the history of the 1620s, revealing it as both a significant military event and a remarkable episode in the intersection of literature and life. Digby did not simply write a romance based on his voyage; he sought to live his life as a romance, transforming the conventions of a literary genre into a program for action. This made him, in the eyes of some, a seventeenth-century Don Quixote, but it also made him one of the most compelling figures of his era."
            ),
            position=30,
            citation_ids="cit_piracy_article,cit_mosh_ch8_aftermath",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
    ]

    # --- ALCHEMIST PAGE SECTIONS ---
    alchemist_sections = [
        PageSection(
            id="sec_alchemist_intro",
            page="alchemist",
            section_key="intro",
            title="Natural Philosophy from Napier to the Royal Society",
            body=(
                "Sir Kenelm Digby's engagement with natural philosophy spanned his entire adult life, from his adolescent studies with the physician-priest Richard Napier in Buckinghamshire to his founding membership of the Royal Society in 1660. This trajectory encompassed alchemy, chemistry, medicine, corpuscular philosophy, optics, and plant biology, making Digby one of the most wide-ranging natural philosophers of the seventeenth century. He was not, as some dismissive accounts have suggested, a dilettante or an eccentric; he was a serious experimentalist whose laboratory work extended over decades and whose alchemical manuscripts, as Principe's 2010 discovery revealed, run to over five thousand pages.\n\n"
                "Digby's natural philosophy was shaped by several overlapping intellectual traditions. From his Oxford tutor Thomas Allen, who had succeeded, as Fuller put it, to the skill and scandal of Friar Bacon, he inherited the English Hermetic tradition of John Dee and the Northumberland Circle, with its blend of astrology, alchemy, Cabalism, mathematics, and philosophy. From Napier he learned that empirical observation and occult philosophy could work hand in hand, that the natural world was animated by sympathetic forces that could be investigated and manipulated. From the Continental mechanical philosophers he encountered in Paris, including Descartes, Mersenne, and Gassendi, he absorbed the new corpuscular theories that explained natural phenomena through the motions of minute particles.\n\n"
                "What made Digby distinctive was his refusal to choose between these traditions. Where other natural philosophers were moving decisively toward mechanism and away from alchemy, Digby integrated both. His Two Treatises of 1644 developed a corpuscular theory of matter while retaining alchemical concepts; his Powder of Sympathy lecture of 1657 offered a mechanistic explanation for an apparently occult cure; his Vegetation of Plants lecture of 1661 synthesized alchemical theory with empirical observation for the Royal Society. As Betty Jo Dobbs argued, Digby's profound empiricism acted upon the study of alchemy in such a way that that branch of the occult became much less esoteric and much more a part of rational natural philosophy.\n\n"
                "The rediscovery of the Strasbourg manuscripts by Principe in 2010 transformed our understanding of Digby's alchemy from a minor interest to a central commitment. These eleven manuscripts, comprising over five thousand pages of alchemical texts, experimental records, and correspondence, reveal a sophisticated practitioner who approached alchemical literature with the methods of a trained humanist and conducted laboratory operations with the precision of an experienced experimentalist. Digby was not dabbling; he was engaged in the most serious alchemical research of his era, collaborating with an international network of practitioners and contributing to the slow transformation of alchemy into chemistry."
            ),
            position=0,
            citation_ids="cit_dobbs_1973_gresham,cit_principe_paris_circle,cit_georgescu_philosophy",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_alchemist_context",
            page="alchemist",
            section_key="context",
            title="The Paris Exile: Peak of Alchemical Activity",
            body=(
                "Digby's extended residences in Paris during the 1650s represented the peak of his alchemical activity. Living in the French capital as chancellor to Queen Henrietta Maria, he had access to the most advanced chemical practitioners in Europe, including Nicolas Le Fevre, the demonstrator at the Jardin du Roi, and a circle of collaborators whose activities are documented in the Strasbourg manuscripts. This was the period when Digby conducted his most ambitious experimental work, collected the recipes and processes that would later appear in the Chymical Secrets, and developed the mature theoretical framework expressed in his Vegetation of Plants lecture.\n\n"
                "The Paris circle was not a marginal occult gathering. As Principe has shown, several of its members were connected to the French scientific community that would later coalesce into the Academie des Sciences. They traded manuscripts, compared variant readings of alchemical texts, and collaborated on experimental projects ranging from metallic transmutation to the preparation of chemical medicines. The circle included Samuel Cottereau Duclos, whose otherwise lost notebooks survive in Digby's transcriptions, and maintained correspondence with Johann Rudolf Glauber, one of the most important chemists of the century.\n\n"
                "It was also during the Paris years that Digby absorbed Le Fevre's concept of the Universal Spirit, a subtle fluid permeating all matter that could be identified with mercury in its philosophical (not common) form. This concept became the foundation of Digby's later alchemy and appears prominently in the marginalia attributed to him in the British Library copy of the Hypnerotomachia Poliphili. Le Fevre also connected Digby to the work of Jean d'Espagnet, whose writings on the relationship between gold and the aethereal spirit informed Digby's claim, in his 1660 Royal Society lecture, that gold was nothing but the universal spirit first corporified in a pure place."
            ),
            position=10,
            citation_ids="cit_principe_paris_circle,cit_dobbs_1973_lefevre,cit_dobbs_1973_paris",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_alchemist_essay",
            page="alchemist",
            section_key="essay",
            title="From Laboratory to Library: Digby's Experimental Method",
            body=(
                "Digby's alchemical practice combined two interrelated tracks that were characteristic of serious seventeenth-century practitioners: laboratory experimentation and the careful study of texts. The Strasbourg manuscripts reveal both activities in striking detail. On the experimental side, Digby records processes carried out by himself and his collaborators, dated precisely to April 1656 and May 1657, showing the careful documentation expected of a systematic experimentalist. His Gresham College laboratory, inventoried in 1648, contained an impressive array of equipment: reverberating and calcining ovens, water baths, sand furnaces, athanors, alembics, grinding stones, and copper stills.\n\n"
                "On the textual side, Digby approached alchemical manuscripts with the methods of a trained humanist. He hired scribes to copy works from older manuscripts, then meticulously compared the copies against originals and other manuscript witnesses, noting variant readings in extensive autograph marginalia. He tracked the textual transmission of works, identified scribal errors, and assessed the reliability of different manuscript traditions. When he found a text unsatisfactory upon experimental trial, he noted this honestly, as when he wrote in one manuscript that he had made much account of a book and its practice until upon trial he found it not to answer expectation.\n\n"
                "This combination of practical experimentation and textual criticism was what distinguished Digby from both the mystical alchemists of earlier centuries and the purely theoretical mechanical philosophers of his own time. He took alchemy seriously as an empirical science while applying the critical methods of humanist scholarship to its literature. The result was a body of work that contributed to what Dobbs called the clarification and chemicalization of alchemical thought, the first stage in the long process by which alchemy was transformed into modern chemistry."
            ),
            position=20,
            citation_ids="cit_principe_manuscripts,cit_dobbs_1974_secrets,cit_dobbs_1973_gresham",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_alchemist_conclusion",
            page="alchemist",
            section_key="conclusion",
            title="Digby's Place in the History of Science",
            body=(
                "Digby's contribution to the history of science has been underestimated for centuries, partly because of the historiographic prejudice against alchemy that dominated the field until recently, and partly because his Catholic faith made him an uncomfortable figure for the Protestant narrative of English scientific progress. The standard story of the Scientific Revolution moved from Bacon through Boyle to Newton, bypassing Catholic experimentalists like Digby whose work did not fit the triumphalist narrative.\n\n"
                "Recent scholarship has begun to correct this distortion. Dobbs showed that Digby's empiricism rationalized the language of alchemy and simplified its processes, contributing to the transformation of alchemy from esoteric mysticism to operational chemistry. Principe's Strasbourg discovery revealed the scale of Digby's commitment: over five thousand pages of alchemical manuscripts, meticulously compiled and critically annotated, documenting decades of sustained engagement with the most challenging problems of seventeenth-century natural philosophy. Georgescu and Adriaenssen's 2022 edited volume has reexamined Digby's philosophical work in context, showing that his Two Treatises represented a sophisticated attempt to reconcile Catholic theology with corpuscular philosophy.\n\n"
                "Digby did not make a large contribution to positive chemical knowledge, as Dobbs acknowledged. His favorite recipes did not produce gold, and his sympathetic powder did not cure wounds at a distance. But he participated actively in the process by which alchemy was clarified, operationalized, and eventually tested against empirical evidence, a process that was essential to the emergence of modern chemistry. His career illustrates the complex, messy reality of scientific change in the seventeenth century: not a clean break from the old to the new, but a gradual transformation in which figures like Digby served as essential intermediaries between the Hermetic tradition and the experimental philosophy of the Royal Society."
            ),
            position=30,
            citation_ids="cit_dobbs_1973_gresham,cit_principe_paris_circle,cit_georgescu_philosophy",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
    ]

    # --- COURTIER PAGE SECTIONS ---
    courtier_sections = [
        PageSection(
            id="sec_courtier_intro",
            page="courtier",
            section_key="intro",
            title="The Political Animal: Navigating Factions and Confessions",
            body=(
                "Sir Kenelm Digby was, above all else, a political animal: a man who navigated the most dangerous political terrain in seventeenth-century England with a combination of personal charm, intellectual brilliance, and confessional flexibility that allowed him to survive and even thrive through civil war, exile, regicide, and restoration. Born the son of an executed traitor, educated by Jesuits, knighted by one king, imprisoned by Parliament, employed by a queen in exile, tolerated by a republican dictator, and welcomed home by a restored monarchy, Digby traversed the full spectrum of seventeenth-century English political life.\n\n"
                "His political career cannot be understood apart from his Catholic identity, which was both his greatest liability and a source of unusual opportunity. Catholics in early modern England were legally disadvantaged, socially suspect, and periodically persecuted. The memory of the Gunpowder Plot, in which Digby's own father had conspired to blow up Parliament, made the Digby name synonymous with Catholic treachery. Yet Catholicism also gave Digby access to international networks that Protestants could not easily penetrate: the French court, the papal diplomatic service, and the exile communities that formed around Catholic rulers across Europe.\n\n"
                "Digby's response to this double-edged identity was characteristic of his approach to all the contradictions of his life: he refused to choose. He converted to Protestantism when it was politically convenient in the 1620s, returned to Catholicism when circumstances changed in the 1630s, served Protestant kings and Catholic queens, befriended both Puritans and Jesuits, and maintained personal relationships across every political and confessional divide. This was not mere opportunism; it reflected a genuine conviction that intellectual and personal connections mattered more than confessional boundaries. Digby was a Catholic who believed in dialogue, a Royalist who could talk to Cromwell, and a courtier who was also a serious philosopher. These apparent contradictions were the source of his political power.\n\n"
                "Understanding Digby as a courtier requires attention to the specific mechanisms of political influence in the Stuart period: personal access to the monarch, participation in court factions, management of patronage networks, diplomatic service, and the cultivation of reputation through public gesture and private connection. Digby was skilled at all of these, and his political career illuminates the workings of court society with unusual clarity."
            ),
            position=0,
            citation_ids="cit_miles_courtier_career,cit_mellick_courtier,cit_mosh_ch3_knighthood",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_courtier_context",
            page="courtier",
            section_key="context",
            title="The Civil War and Exile",
            body=(
                "The outbreak of the English Civil War in 1642 posed an existential challenge to Digby's political position. As a Catholic Royalist, he was doubly targeted by a Parliament that was both anti-Catholic and anti-monarchical. His arrest and imprisonment at Winchester House was swift, though his treatment was relatively gentle by the standards of wartime justice. The imprisonment was productive: Digby established a laboratory, experimented with glass manufacture, and continued his alchemical studies, but it also demonstrated the fundamental fragility of his position in English political life.\n\n"
                "Released into exile, Digby joined the gathering of Royalist refugees in Paris, where he assumed the role of chancellor to Queen Henrietta Maria. The exile years were paradoxically among the most active of his life. Free from the constraints of English confessional politics, Digby could operate openly as a Catholic intellectual, engaging with French philosophers, pursuing alchemy with Le Fevre and the Paris circle, publishing his Two Treatises, and conducting diplomatic missions on behalf of the Royalist cause. His mission to Rome in 1645 to seek papal support was characteristic: ambitious, controversial, and ultimately unsuccessful, but demonstrating the kind of initiative that made Digby valuable to any faction that employed him.\n\n"
                "The execution of Charles I in January 1649 was a profound shock. Digby had been personally close to the King and had staked his political career on the Royalist cause. Yet he adapted with characteristic resilience, maintaining his position with Henrietta Maria while also exploring possibilities with the new republican regime. His meeting with Cromwell in 1654 was the most dramatic example of this adaptability: the Catholic chancellor of the exiled Queen sitting down with the man who had killed her husband to discuss matters of mutual interest."
            ),
            position=10,
            citation_ids="cit_dobbs_1973_civil_war,cit_miles_courtier_career,cit_mellick_courtier",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_courtier_essay",
            page="courtier",
            section_key="essay",
            title="Digby and the Duel: Honor Culture in the Stuart Court",
            body=(
                "One episode that crystallizes Digby's courtier identity is the duel he fought in Paris in 1641. At a banquet, a French nobleman identified as Mont le Ros spoke disparagingly about King Charles I. Digby, who had been knighted by Charles's father and served Charles personally for nearly two decades, felt bound by the codes of honor that governed aristocratic behavior to challenge the insult. He called Mont le Ros to account and, in the ensuing sword fight, killed his opponent with a thrust through the heart. A contemporary pamphlet celebrated the event, claiming that Mars himself would have been bashful to see himself exceeded by noble Digby.\n\n"
                "The duel reveals several dimensions of Digby's courtier identity. First, it demonstrates his physical courage: at thirty-eight, with decades of political life behind him, Digby was still willing to risk his life in personal combat. He had been an expert fencer since his Italian travels in the early 1620s, when an Italian publication on fencing was dedicated to him. Second, it shows his attachment to the honor culture of the Stuart court, in which personal reputation was inseparable from political influence. An insult to the King was an insult to every man who served him, and failure to respond would have been a form of political suicide. Third, the aftermath is revealing: the French King pardoned Digby on the grounds that he was defending the honor of his sovereign, and Digby was given safe conduct out of France, suggesting that even the French court recognized the legitimacy of his action within the codes of aristocratic honor.\n\n"
                "The duel also connects to Digby's broader political identity as a man who operated across national boundaries. He was an Englishman in Paris, defending an English king at a French table, pardoned by a French monarch. This cosmopolitan identity was one of Digby's greatest political assets and one of the reasons he was valued by every faction he served."
            ),
            position=20,
            citation_ids="cit_mellick_duel,cit_mellick_courtier,cit_miles_courtier_career",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
        PageSection(
            id="sec_courtier_conclusion",
            page="courtier",
            section_key="conclusion",
            title="Political Significance",
            body=(
                "Digby's political significance lies not in any single achievement but in the extraordinary range of his connections and the resilience with which he maintained them across decades of upheaval. He is one of the few figures of his era who maintained active relationships with James I, Charles I, Henrietta Maria, Oliver Cromwell, and Charles II, spanning the entire political spectrum from Stuart absolutism to republican rule and back again. His correspondents included Ben Jonson, Thomas Hobbes, Descartes, Mersenne, Fermat, Hartlib, John Winthrop Jr., and Robert Boyle, a network that crossed every boundary of nation, confession, and intellectual discipline.\n\n"
                "This political versatility was rooted in personal qualities that contemporaries repeatedly noted: exceptional physical presence, intellectual brilliance, multilingual fluency, and an ability to make genuine personal connections with people of every background. Aubrey's portrait of Digby emphasizes his height, his beauty, and his extraordinary conversational powers. But these qualities were deployed strategically, in service of a political career that required constant adaptation to changing circumstances.\n\n"
                "Digby's life also illustrates the particular challenges faced by Catholic intellectuals in early modern England. He was simultaneously insider and outsider, trusted and suspected, essential and expendable. His career demonstrates that the simple narrative of Catholic exclusion from English public life is inadequate: Catholics like Digby could and did achieve positions of influence, but they did so through personal connections rather than institutional support, making their positions inherently precarious. Digby's political career, like his alchemy, occupied the space between the old world and the new, between Catholic tradition and Protestant modernity, between courtly privilege and intellectual merit. He navigated this space with a skill that few of his contemporaries could match."
            ),
            position=30,
            citation_ids="cit_miles_courtier_career,cit_mellick_courtier,cit_piracy_article",
            source_method=SourceMethod.LLM_ASSISTED.value,
            review_status=ReviewStatus.DRAFT.value,
        ),
    ]

    # Insert all page sections
    added_sections = 0
    for ps in pirate_sections + alchemist_sections + courtier_sections:
        if ps.id not in existing_sections:
            validate_record(ps)
            insert_record("page_sections", ps.to_dict())
            added_sections += 1
    print(f"Added {added_sections} new page sections.")

    # ========================================================================
    # UPDATE existing theme records with expanded summaries
    # ========================================================================
    conn = get_connection()

    updates = [
        # Expand the existing pirate venetian label record
        (
            "thm_pirate_venetian_label",
            "After the Battle of Scanderoon on 11 June 1628, the Republic of Venice launched a coordinated and "
            "systematic campaign to brand Digby as a pirate throughout the Mediterranean and at European courts. "
            "Venetian consuls and ambassadors wrote dispatches calling him a thief, a pirate who had sold all his "
            "property for the sake of robbing, and an audacious criminal. The consul Alvise da Pesaro declared "
            "he was nothing but a thief and a pirate. Letters flew across Venetian outposts calling him this "
            "audacious pirate and the pirate Digby. The campaign was deliberate and coordinated, designed to "
            "delegitimize Digby's voyage and pressure England into disowning his actions. Even English diplomats "
            "felt its effects: Sir Thomas Roe, the ambassador at Constantinople, complained bitterly about the "
            "disruption to Levant trade, and English merchants at Aleppo were imprisoned in retaliation. The "
            "propaganda was amplified by Protestant suspicion of Digby's Catholic loyalties. Roe and other "
            "Protestant officials saw the voyage not as legitimate naval service but as a reckless Catholic "
            "adventure that endangered Protestant commercial interests. The pirate label proved remarkably "
            "durable, persisting in diplomatic correspondence and historical accounts for years. Digby's "
            "response was primarily literary: the Journal, the Loose Fantasies, and the published account "
            "of Scanderoon were all efforts to control the narrative. The episode reveals how early modern "
            "reputations were contested across diplomatic networks, and how the privateer-pirate distinction "
            "was determined by political power rather than legal principle."
        ),
        # Expand the existing alchemy Napier record
        (
            "thm_alch_napier",
            "Digby's first introduction to alchemy and natural philosophy came through his tutor Richard "
            "Napier, a physician-priest at Great Linford in Buckinghamshire. Napier, known locally as Parson "
            "Sandie, was a remarkable figure who combined conventional medical practice with astrology, alchemy, "
            "and spirit-conjuring. He maintained an extensive library and a network of astrological clients "
            "that included some of the most prominent families in Buckinghamshire. Napier cast Digby's "
            "horoscope, taught him herbal lore and botanical medicine, and demonstrated that empirical "
            "observation and occult philosophy could work hand in hand. The young Kenelm borrowed whole "
            "cloak-bags of books from Napier's library, developing the voracious reading habits that would "
            "define his intellectual life. Napier's influence on Digby was profound and lasting. The integration "
            "of empirical and occult approaches to nature that characterized Digby's mature philosophy can be "
            "traced directly to Napier's example. Where later natural philosophers would draw sharp lines "
            "between legitimate science and illegitimate magic, Napier modeled a practice in which astrology, "
            "medicine, alchemy, and natural philosophy formed a coherent whole. Digby absorbed this integrative "
            "approach and never fully abandoned it, even as he engaged with the mechanical philosophies of "
            "Descartes and Gassendi in the 1640s and 1650s. Napier also introduced Digby to the concept of "
            "sympathetic forces connecting distant objects, an idea that would later find expression in the "
            "Powder of Sympathy and in the alchemical marginalia attributed to Digby in the Hypnerotomachia."
        ),
        # Expand the existing courtier Buckingham record
        (
            "thm_courtier_buckingham",
            "The Duke of Buckingham, George Villiers, was the most powerful man in England after the King and "
            "Charles I's closest personal friend. His relationship with Digby was one of mutual antagonism that "
            "shaped the entire trajectory of the Mediterranean voyage. Buckingham controlled the Admiralty and "
            "wielded enormous influence over naval appointments, ship allocations, and maritime commissions. He "
            "actively tried to prevent Digby's expedition, obstructing his access to ships, sailors, and "
            "supplies at every turn. The reasons for Buckingham's hostility are not entirely clear but likely "
            "combined personal rivalry with political calculation: Digby was gaining favor with Charles I, and "
            "any independent success by Digby would diminish Buckingham's monopoly on royal attention. Despite "
            "this obstruction, Digby assembled his fleet through a combination of personal determination, "
            "private investment, and direct appeal to the King's authority over Buckingham's head. This "
            "circumvention of the most powerful man in England demonstrated both Digby's political skill and "
            "the depth of Charles's personal regard for him. The drama took an extraordinary turn on 23 August "
            "1628, when Buckingham was assassinated by John Felton at Portsmouth. Digby learned the news while "
            "near the Currant Islands in Greece, from a captured French captain. The assassination removed his "
            "greatest political obstacle and transformed the context of his return: without Buckingham to "
            "oppose him, Digby could hope for a more favorable reception at court. The Buckingham conflict "
            "illustrates the intensely personal nature of Caroline politics, where access to the King was the "
            "ultimate currency and personal rivalry could determine matters of war and peace."
        ),
    ]

    updated = 0
    for record_id, new_summary in updates:
        result = conn.execute(
            "SELECT id FROM digby_theme_records WHERE id = ?", (record_id,)
        ).fetchone()
        if result:
            conn.execute(
                "UPDATE digby_theme_records SET summary = ? WHERE id = ?",
                (new_summary, record_id),
            )
            updated += 1
    conn.commit()
    conn.close()
    print(f"Updated {updated} existing theme records with expanded summaries.")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    conn = get_connection()
    print("\n--- Phase 1 Content Expansion Summary ---")
    for t in ["citations", "digby_theme_records", "page_sections"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {count} records")

    # Word count estimates
    pirate_words = sum(len(s.body.split()) for s in pirate_sections)
    alch_words = sum(len(s.body.split()) for s in alchemist_sections)
    court_words = sum(len(s.body.split()) for s in courtier_sections)
    pirate_theme_words = sum(len(t.summary.split()) for t in pirate_themes)
    alch_theme_words = sum(len(t.summary.split()) for t in alchemist_themes)
    court_theme_words = sum(len(t.summary.split()) for t in courtier_themes)

    print(f"\n--- Estimated Word Counts (new content only) ---")
    print(f"  Pirate page:    ~{pirate_words + pirate_theme_words} words ({len(pirate_sections)} sections + {len(pirate_themes)} records)")
    print(f"  Alchemist page: ~{alch_words + alch_theme_words} words ({len(alchemist_sections)} sections + {len(alchemist_themes)} records)")
    print(f"  Courtier page:  ~{court_words + court_theme_words} words ({len(courtier_sections)} sections + {len(courtier_themes)} records)")
    print(f"  Total new:      ~{pirate_words + pirate_theme_words + alch_words + alch_theme_words + court_words + court_theme_words} words")

    conn.close()


if __name__ == "__main__":
    expand_content()
