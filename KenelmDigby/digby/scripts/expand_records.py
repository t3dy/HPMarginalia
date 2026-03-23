"""
Expand the Digby database with additional life events, memoir episodes,
work records, and theme records extracted from the source corpus.

All claims grounded in source materials (primarily Moshenska's biography).
"""

import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.db import init_db, insert_record, get_connection
from src.models import (
    LifeEvent, WorkRecord, MemoirEpisode, DigbyThemeRecord,
    Citation, HypnerotomachiaFinding, HypnerotomachiaEvidence,
    make_id, Confidence
)
from src.validate import validate_record


def expand():
    init_db()

    # Check what already exists
    conn = get_connection()
    existing_events = {r["id"] for r in conn.execute("SELECT id FROM life_events").fetchall()}
    existing_episodes = {r["id"] for r in conn.execute("SELECT id FROM memoir_episodes").fetchall()}
    existing_themes = {r["id"] for r in conn.execute("SELECT id FROM digby_theme_records").fetchall()}
    existing_works = {r["id"] for r in conn.execute("SELECT id FROM work_records").fetchall()}
    existing_cits = {r["id"] for r in conn.execute("SELECT id FROM citations").fetchall()}
    existing_findings = {r["id"] for r in conn.execute("SELECT id FROM hypnerotomachia_findings").fetchall()}
    conn.close()

    # --- Additional Citations ---
    new_citations = [
        Citation(id="cit_ch1_youth", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 1, Section I",
                 context="Digby's childhood, father's execution, Gayhurst"),
        Citation(id="cit_ch1_venetia", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 1, Section I",
                 context="Digby meeting Venetia Stanley"),
        Citation(id="cit_ch1_napier", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 1, Section I",
                 context="Education with Richard Napier"),
        Citation(id="cit_ch2_europe", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 2",
                 context="Grand Tour: Florence, Siena, Madrid"),
        Citation(id="cit_ch3_london", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 3",
                 context="London 1623-1627, marriage, intellectual life"),
        Citation(id="cit_ch4_voyage_start", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 4",
                 context="Start of Mediterranean voyage, plague at sea"),
        Citation(id="cit_ch5_algiers", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 5",
                 context="Algiers, freeing English slaves"),
        Citation(id="cit_ch7_scanderoon", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 7",
                 context="Battle of Scanderoon, aftermath"),
        Citation(id="cit_ch8_return", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 8",
                 context="Delos antiquities, return to England"),
        Citation(id="cit_ch8_buckingham", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 8, Section II",
                 context="Assassination of Buckingham, return home"),
        Citation(id="cit_miles_overview", source_document_id="sdoc_miles",
                 page_or_location="passim",
                 context="Overview of Digby's full career"),
        Citation(id="cit_mellick_bio", source_document_id="sdoc_mellick",
                 page_or_location="passim",
                 context="Biographical summary"),
        Citation(id="cit_closet", source_document_id="sdoc_miles",
                 page_or_location="passim",
                 context="The Closet cookbook"),
        Citation(id="cit_observations", source_document_id="sdoc_moshenska",
                 page_or_location="Chapter 8",
                 context="Observations on Spenser and Browne"),
    ]

    added_cits = 0
    for c in new_citations:
        if c.id not in existing_cits:
            c.created_at = datetime.now().isoformat()
            validate_record(c)
            insert_record("citations", c.to_dict())
            added_cits += 1
    print(f"Added {added_cits} new citations.")

    # --- Expanded Life Events ---
    new_events = [
        LifeEvent(
            id="evt_father_executed",
            title="Execution of Everard Digby",
            date_display="20 January 1606",
            year=1606,
            description="Kenelm's father Sir Everard Digby was executed for his role in the Gunpowder Plot. He was hanged, drawn, and quartered at St Paul's churchyard. The infant Kenelm was just two years old. According to family tradition, young Kenelm cried out at the exact moment of his father's death.",
            life_phase="youth",
            location="St Paul's churchyard, London",
            people_involved="Everard Digby, Mary Digby, Edward Coke",
            citation_ids="cit_ch1_youth",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_childhood_gayhurst",
            title="Childhood at Gayhurst",
            date_display="1606-1617",
            year=1606,
            description="Raised by his Catholic mother Mary at Gayhurst, Buckinghamshire. Educated by Jesuit tutors including John Percy (Fisher). Learned French, Italian, horsemanship, and developed a passion for reading. Suffered several serious childhood illnesses.",
            life_phase="youth",
            location="Gayhurst, Buckinghamshire",
            people_involved="Mary Digby, John Percy (Fisher), John Digby",
            citation_ids="cit_ch1_youth",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_meets_venetia",
            title="First Meeting with Venetia Stanley",
            date_display="c. 1615-1616",
            year=1615,
            description="The young Kenelm met Venetia Stanley, three years his senior, through visits between their Catholic families in Buckinghamshire. Despite his mother's opposition (Venetia was poor despite noble blood), the two fell deeply in love. Their first kiss occurred during a hunting expedition near Gayhurst.",
            life_phase="youth",
            location="Buckinghamshire",
            people_involved="Venetia Stanley, Mary Digby, Francis and Grace Fortescue",
            citation_ids="cit_ch1_venetia",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_napier_education",
            title="Education with Richard Napier",
            date_display="c. 1615-1618",
            year=1615,
            description="Kenelm studied with Richard Napier ('Parson Sandie'), a physician-priest at Great Linford renowned for astrology and alchemy. Napier cast Kenelm's horoscope and introduced him to alchemical practices, herbal medicine, and the idea of sympathetic forces connecting the natural world.",
            life_phase="youth",
            location="Great Linford, Buckinghamshire",
            people_involved="Richard Napier",
            citation_ids="cit_ch1_napier",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_grand_tour",
            title="Grand Tour: France, Italy, Spain",
            date_display="1620-1623",
            year=1620,
            description="Digby embarked on a European Grand Tour, travelling through France (where he met Marie de Medici), Italy (Florence, Siena), and Spain (Madrid, where he joined Prince Charles and Buckingham during the Spanish Match). These travels shaped his cosmopolitan identity and intellectual horizons.",
            life_phase="grand_tour",
            location="France, Florence, Siena, Madrid",
            people_involved="Marie de Medici, Prince Charles, Duke of Buckingham",
            citation_ids="cit_ch2_europe",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_marriage_venetia",
            title="Secret Marriage to Venetia Stanley",
            date_display="Spring 1625",
            year=1625,
            description="Digby secretly married Venetia Stanley, despite opposition from his family and court gossip about her reputation. The marriage was kept private for some time. They had two sons: Kenelm and John.",
            life_phase="marriage",
            location="London",
            people_involved="Venetia Stanley",
            citation_ids="cit_ch3_london",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_plague_at_sea",
            title="Plague Strikes the Fleet",
            date_display="Late January 1628",
            year=1628,
            description="A violent pestilential disease erupted among Digby's crew shortly after entering the Mediterranean. Sixty of 150 men on the Eagle fell ill. The sick suffered delirium, believing the sea was 'a spacious and pleasant green meadow.' Despite officers urging return, Digby pressed on to Algiers for help.",
            life_phase="voyage",
            location="Mediterranean Sea",
            people_involved="Kenelm Digby, crew of the Eagle",
            citation_ids="cit_ch4_voyage_start",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_algiers",
            title="Arrival at Algiers and Freeing of English Slaves",
            date_display="February-March 1628",
            year=1628,
            description="Digby arrived at Algiers to resupply and treat his sick crew. He negotiated the release of English captives held as slaves by the Barbary corsairs, combining diplomatic skill with his growing confidence as a commander. The stay also gave him opportunity for intellectual exploration.",
            life_phase="voyage",
            location="Algiers",
            people_involved="Kenelm Digby",
            citation_ids="cit_ch5_algiers",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_delos_antiquities",
            title="Collecting Antiquities at Delos",
            date_display="28-30 August 1628",
            year=1628,
            description="Digby spent three days on the deserted island of Delos, collecting ancient marble statues and inscriptions from the ruins of Apollo's temple. He devised an ingenious pulley system to hoist a massive four-statue marble block aboard his ship. He also contemplated a colossal broken statue of Apollo.",
            life_phase="voyage",
            location="Delos, Greece",
            people_involved="Kenelm Digby, crew",
            citation_ids="cit_ch8_return",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_buckingham_death",
            title="News of Buckingham's Assassination",
            date_display="Late October 1628",
            year=1628,
            description="While near the Currant Islands, Digby learned from a captured French captain that the Duke of Buckingham had been assassinated by John Felton on 23 August. This removed Digby's greatest political obstacle and spurred his urgent return to England.",
            life_phase="voyage",
            location="Currant Islands, Greece",
            people_involved="Duke of Buckingham, John Felton",
            citation_ids="cit_ch8_buckingham",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_return_england",
            title="Return to England",
            date_display="February 1629",
            year=1629,
            description="Digby returned to England after thirteen months at sea, arriving with captured prizes, ancient marbles from Delos, exotic plant specimens, and a greatly enhanced reputation. He was received by King Charles and presented his trophies at court.",
            life_phase="return",
            location="London",
            people_involved="King Charles I, Venetia Stanley",
            citation_ids="cit_ch8_return",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_venetia_death",
            title="Death of Venetia Stanley",
            date_display="1 May 1633",
            year=1633,
            description="Venetia died suddenly in her sleep, devastating Kenelm. He commissioned Anthony van Dyck to paint her on her deathbed and retreated into intense grief and scholarly seclusion. Her death profoundly shaped the rest of his life.",
            life_phase="grief",
            location="London",
            people_involved="Venetia Stanley, Anthony van Dyck",
            citation_ids="cit_miles_overview",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_two_treatises",
            title="Publication of Two Treatises",
            date_display="1644",
            year=1644,
            description="Digby published his major philosophical work, Two Treatises: Of Bodies and Of Man's Soul, in Paris during the Civil War exile. The work attempted to reconcile Catholic theology with contemporary natural philosophy.",
            life_phase="exile",
            location="Paris",
            citation_ids="cit_two_treatises",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_paris_exile",
            title="Exile in Paris During the Civil War",
            date_display="1640s-1650s",
            year=1643,
            description="Digby spent much of the Civil War period in exile in Paris, where he became chancellor to Queen Henrietta Maria, engaged in alchemical experiments, published philosophical works, and built an active intellectual circle.",
            life_phase="exile",
            location="Paris",
            people_involved="Queen Henrietta Maria",
            citation_ids="cit_miles_overview,cit_alchemy_principe",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_royal_society",
            title="Founding Member of the Royal Society",
            date_display="1660-1661",
            year=1660,
            description="After the Restoration, Digby returned to England and became a founding member of the Royal Society. He delivered a notable lecture on the vegetation of plants at Gresham College in January 1661.",
            life_phase="restoration",
            location="London, Gresham College",
            citation_ids="cit_miles_overview,cit_mellick_bio",
            confidence=Confidence.HIGH.value,
        ),
        LifeEvent(
            id="evt_death",
            title="Death of Sir Kenelm Digby",
            date_display="11 June 1665",
            year=1665,
            description="Digby died in London on his birthday, aged 62. He was buried at Christ Church, Newgate. His library, one of the finest private collections in England, was bequeathed to the Bodleian Library at Oxford.",
            life_phase="death",
            location="London",
            citation_ids="cit_miles_overview,cit_mellick_bio",
            confidence=Confidence.HIGH.value,
        ),
    ]

    added_events = 0
    for evt in new_events:
        if evt.id not in existing_events:
            validate_record(evt)
            insert_record("life_events", evt.to_dict())
            added_events += 1
    print(f"Added {added_events} new life events.")

    # --- Expanded Memoir Episodes ---
    new_episodes = [
        MemoirEpisode(
            id="mem_father_shadow",
            title="The Shadow of the Gunpowder Plot",
            episode_number=1,
            date_display="5 November 1627",
            year=1627,
            summary="On Bonfire Night 1627, as London celebrates the foiling of the Gunpowder Plot, Digby paces his chambers haunted by the memory of his father Everard's execution. The annual celebrations force him to confront the 'foul stain in his blood' and strengthen his resolve to depart on his voyage to redeem the family name.",
            key_events="Bonfire Night, memory of father's execution, resolve to voyage",
            people="Kenelm Digby, Everard Digby",
            places="London",
            themes="memoir,biography",
            citation_ids="cit_ch1_youth",
        ),
        MemoirEpisode(
            id="mem_venetia_love",
            title="Falling in Love with Venetia Stanley",
            episode_number=2,
            date_display="c. 1615-1617",
            year=1615,
            summary="Digby meets Venetia Stanley through their Catholic families in Buckinghamshire. He is captivated by her beauty, intelligence, and character. Their first kiss occurs secretly during a hunting expedition near Gayhurst, sheltered under a tree during a rainstorm. His mother opposes the match because Venetia is poor.",
            key_events="First meeting, falling in love, first kiss during hunt, mother's opposition",
            people="Kenelm Digby, Venetia Stanley, Mary Digby",
            places="Gayhurst, Buckinghamshire",
            themes="memoir,biography",
            citation_ids="cit_ch1_venetia",
        ),
        MemoirEpisode(
            id="mem_napier_alchemy",
            title="Initiation into Alchemy with Richard Napier",
            episode_number=3,
            date_display="c. 1615-1618",
            year=1615,
            summary="Digby studies with Richard Napier, a physician-priest at Great Linford who introduces him to astrology, alchemy, and natural philosophy. Napier casts his horoscope and teaches him to read the stars. Kenelm borrows 'whole cloak-bags' of books from Napier's library, developing his lifelong passion for learning.",
            key_events="Study with Napier, horoscope cast, introduction to alchemy, library borrowing",
            people="Kenelm Digby, Richard Napier",
            places="Great Linford, Buckinghamshire",
            themes="memoir,alchemist_natural_philosopher",
            citation_ids="cit_ch1_napier",
        ),
        MemoirEpisode(
            id="mem_grand_tour",
            title="The Grand Tour: France, Italy, Spain",
            episode_number=4,
            date_display="1620-1623",
            year=1620,
            summary="Digby travels through Europe, encountering Marie de Medici in France, immersing himself in Italian culture at Florence and Siena, and joining Prince Charles and Buckingham in Madrid during the Spanish Match. These travels transform him into a cosmopolitan figure with connections across Catholic Europe.",
            key_events="Encounter with Marie de Medici, Italian sojourn, Spanish Match",
            people="Marie de Medici, Prince Charles, Duke of Buckingham",
            places="France, Florence, Siena, Madrid",
            themes="memoir,biography,courtier_legal_thinker",
            citation_ids="cit_ch2_europe",
        ),
        MemoirEpisode(
            id="mem_voyage_prep",
            title="Preparing the Voyage Against Buckingham's Opposition",
            episode_number=5,
            date_display="Late 1627",
            year=1627,
            summary="Digby assembles a fleet and crew in London while facing deliberate obstruction from the Duke of Buckingham. He negotiates ship purchases, recruits sailors scarred from the disasters at Cadiz and the Ile de Re, and stockpiles provisions. His determination to overcome Buckingham's interference reveals both his ambition and the political dangers surrounding him.",
            key_events="Fleet assembly, Buckingham's obstruction, crew recruitment",
            people="Kenelm Digby, Duke of Buckingham, King Charles I",
            places="London",
            themes="memoir,pirate,courtier_legal_thinker",
            citation_ids="cit_ch4_voyage_start",
        ),
        MemoirEpisode(
            id="mem_biscay_crossing",
            title="Crossing the Bay of Biscay and Entering the Mediterranean",
            episode_number=7,
            date_display="January 1628",
            year=1628,
            summary="Digby's ships cross the Bay of Biscay, round Cape St Vincent, and sneak through the Straits of Gibraltar at night to avoid Spanish ships. He smells rosemary wafting from the Spanish coast, triggering memories of his earlier travels and philosophical reflections on action at a distance.",
            key_events="Bay of Biscay crossing, rounding Cape St Vincent, sneaking through Gibraltar, rosemary scent",
            people="Kenelm Digby, Edward Stradling",
            places="Bay of Biscay, Cape St Vincent, Straits of Gibraltar",
            themes="memoir,pirate",
            citation_ids="cit_ch4_voyage_start",
        ),
        MemoirEpisode(
            id="mem_algiers_slaves",
            title="Algiers: Healing, Diplomacy, and Freeing Slaves",
            episode_number=8,
            date_display="February-March 1628",
            year=1628,
            summary="Digby brings his plague-stricken fleet into Algiers, negotiates with the local authorities, treats his sick crew, and arranges the release of English captives held as slaves. The stay combines practical crisis management with intellectual exploration in one of the Mediterranean's most cosmopolitan cities.",
            key_events="Arrival at Algiers, crew recovery, negotiation with authorities, freeing slaves",
            people="Kenelm Digby",
            places="Algiers",
            themes="memoir,pirate,biography",
            citation_ids="cit_ch5_algiers",
        ),
        MemoirEpisode(
            id="mem_scanderoon_fight",
            title="The Battle of Scanderoon",
            episode_number=10,
            date_display="11 June 1628",
            year=1628,
            summary="Digby's fleet engages Venetian galleasses in the Bay of Scanderoon, winning a decisive naval victory. The aftermath brings complications: English merchants are imprisoned in Aleppo, Venetians spread damaging rumors calling Digby a pirate, and the vice consul pleads repeatedly for him to leave.",
            key_events="Naval battle, victory over Venetians, English merchants imprisoned, pirate label",
            people="Kenelm Digby, Antonio Capello, Edward Stradling, Thomas Roe",
            places="Bay of Scanderoon (Iskenderun), Aleppo",
            themes="memoir,pirate",
            citation_ids="cit_ch7_scanderoon",
        ),
        MemoirEpisode(
            id="mem_egypt_reading",
            title="Becalmed off Egypt: Reading Heliodorus",
            episode_number=11,
            date_display="Late July 1628",
            year=1628,
            summary="Digby's ships are becalmed off the Egyptian coast for five sweltering days. He retreats to his cabin and reads Heliodorus's Aethiopica, a Greek romance about star-crossed lovers wandering the Mediterranean. The tale deeply resonates with his own experiences and inspires him to write his own memoir in the same style.",
            key_events="Becalmed off Egypt, reading Heliodorus, philosophical reflection, sweet Arabian winds",
            people="Kenelm Digby",
            places="Egyptian coast, Mediterranean Sea",
            themes="memoir,biography",
            citation_ids="cit_ch7_scanderoon",
        ),
        MemoirEpisode(
            id="mem_delos",
            title="Treasure Hunting at Delos",
            episode_number=12,
            date_display="28-30 August 1628",
            year=1628,
            summary="Digby spends three days on the deserted island of Delos collecting ancient marbles from the ruins of Apollo's temple. He devises an ingenious pulley system to hoist a massive marble block and stands for an hour contemplating a colossal broken statue of Apollo, too large to move.",
            key_events="Marble collection, pulley engineering, contemplation of Apollo statue, inscribed monument",
            people="Kenelm Digby, crew",
            places="Delos, Mykonos",
            themes="memoir,biography",
            citation_ids="cit_ch8_return",
        ),
        MemoirEpisode(
            id="mem_spenser",
            title="Reading Spenser at Sea: Alchemy in Poetry",
            episode_number=13,
            date_display="September 1628",
            year=1628,
            summary="While sailing around Greece, Digby reads Spenser's Faerie Queene and becomes fascinated by a dense stanza describing a castle representing the human body. He interprets it through the lenses of alchemy and astrology, finding references to salt, sulphur, mercury, the seven planets, and the nine angelic orders.",
            key_events="Reading Spenser, alchemical interpretation, letter to Stradling",
            people="Kenelm Digby, Edward Stradling",
            places="Greek waters",
            themes="memoir,alchemist_natural_philosopher",
            citation_ids="cit_ch8_return,cit_observations",
        ),
        MemoirEpisode(
            id="mem_homeward",
            title="The Homeward Voyage",
            date_display="November 1628 - February 1629",
            year=1628,
            episode_number=14,
            summary="Digby drives westward through the Mediterranean, capturing additional prizes, dodging Spanish fleets, and visiting Lampedusa. Near Sardinia he captures a Hamburg merchant ship carrying Granadan wool. He passes through the Straits of Gibraltar and crosses the Atlantic, arriving home after thirteen months at sea.",
            key_events="Prize captures, news of Buckingham confirmed, passing Lampedusa, homeward crossing",
            people="Kenelm Digby, Edward Stradling",
            places="Sicily, Malta, Lampedusa, Sardinia, Straits of Gibraltar, London",
            themes="memoir,pirate",
            citation_ids="cit_ch8_return",
        ),
    ]

    added_episodes = 0
    for ep in new_episodes:
        if ep.id not in existing_episodes:
            validate_record(ep)
            insert_record("memoir_episodes", ep.to_dict())
            added_episodes += 1
    print(f"Added {added_episodes} new memoir episodes.")

    # --- Additional Theme Records ---
    new_themes = [
        DigbyThemeRecord(
            id="thm_pirate_venetian_label",
            theme="pirate",
            title="'A Pirate Who Had Sold All His Property for the Sake of Robbing'",
            summary="After the Battle of Scanderoon, the Venetians launched a coordinated campaign to brand Digby as a pirate throughout the Mediterranean. Consul Alvise da Pesaro wrote he was 'nothing but a thief and a pirate.' Letters flew across Venetian outposts calling him 'this audacious pirate,' 'a pirate, who had sold all his property,' and 'the pirate Digby.' Even English diplomats like Thomas Roe complained about the disruption to trade.",
            key_details="Venetian propaganda campaign; English diplomats also critical; Roe called it disruption to trade; Protestant suspicion of Catholic captain",
            people="Kenelm Digby, Alvise da Pesaro, Thomas Roe, Peter Wyche",
            places="Mediterranean, Aleppo, Constantinople, Scanderoon",
            date_display="June-August 1628",
            year=1628,
            significance="Reveals how privateering glory was contested — heroes to one audience were pirates to another. Digby's Catholic identity amplified Protestant suspicion of his motives.",
            citation_ids="cit_ch7_scanderoon,cit_piracy_moshenska",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_pirate_delos",
            theme="pirate",
            title="Looting Antiquities at Delos",
            summary="Digby spent three days on the deserted island of Delos collecting ancient marbles from the ruins of Apollo's temple. Unlike other English collectors who disguised themselves and sawed statues into portable fragments, Digby arrived openly as the hero of Scanderoon and devised an ingenious pulley system using ship masts to hoist massive marbles aboard intact.",
            key_details="Three days collecting marbles; pulley system using ship masts; 300 men mobilized; took inscribed monument; contemplated unmovable Apollo colossus",
            people="Kenelm Digby, crew",
            places="Delos, Greece",
            date_display="28-30 August 1628",
            year=1628,
            significance="Demonstrates how privateering shaded into antiquarianism. Digby combined military boldness with scholarly curiosity in his approach to classical ruins.",
            citation_ids="cit_ch8_return",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_alch_napier",
            theme="alchemist_natural_philosopher",
            title="Early Alchemical Education with Richard Napier",
            summary="Digby's first introduction to alchemy and natural philosophy came through his tutor Richard Napier, a physician-priest at Great Linford. Napier practiced astrology, alchemy, and spirit-conjuring alongside conventional medicine. He cast Digby's horoscope, taught him herbal lore, and demonstrated that empirical observation and occult philosophy could work hand in hand.",
            key_details="Napier practiced astrology and alchemy; cast Digby's horoscope; taught botanical and chemical medicine; demonstrated integration of empirical and occult methods",
            people="Kenelm Digby, Richard Napier",
            places="Great Linford, Buckinghamshire",
            date_display="c. 1615-1618",
            significance="Digby's lifelong integration of empirical and occult approaches to nature traces directly to Napier's influence. The tutor modeled how alchemy, medicine, and natural philosophy could form a coherent practice.",
            citation_ids="cit_ch1_napier,cit_alchemy_dobbs",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_alch_spenser",
            theme="alchemist_natural_philosopher",
            title="Alchemical Reading of Spenser's Faerie Queene",
            summary="While sailing around Greece in September 1628, Digby read Spenser's Faerie Queene and produced an alchemical interpretation of a stanza describing a castle representing the human body. He identified references to the three alchemical principles (salt, sulphur, mercury), the seven planets, and the nine angelic hierarchies.",
            key_details="Interpreted Spenser's body-castle stanza alchemically; identified salt/sulphur/mercury as three principles; seven planets and nine angelic orders; wrote to Stradling about his reading",
            people="Kenelm Digby, Edward Stradling, Edmund Spenser",
            places="Greek waters",
            date_display="September 1628",
            year=1628,
            significance="Demonstrates Digby's characteristic method of reading literary texts through an alchemical lens — the same interpretive practice visible in the HP marginalia if Russell's attribution is correct.",
            citation_ids="cit_ch8_return,cit_observations",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_courtier_buckingham",
            theme="courtier_legal_thinker",
            title="Conflict with the Duke of Buckingham",
            summary="The Duke of Buckingham, the most powerful man in England and King Charles's closest friend, actively tried to prevent Digby's Mediterranean voyage. Despite Buckingham's obstruction, Digby assembled his fleet through determination and royal support. Buckingham's assassination on 23 August 1628 — while Digby was at sea — removed his greatest political obstacle.",
            key_details="Buckingham obstructed voyage preparations; Digby circumvented through royal favor; assassination by John Felton removed obstacle; Digby heard news near Currant Islands",
            people="Duke of Buckingham, King Charles I, John Felton",
            places="London, Portsmouth, Currant Islands",
            date_display="1627-1628",
            year=1627,
            significance="Illustrates how Digby navigated the dangerous politics of the Caroline court, where personal favor and faction determined access to power and opportunity.",
            citation_ids="cit_ch8_buckingham,cit_courtier_miles",
            confidence=Confidence.HIGH.value,
        ),
        DigbyThemeRecord(
            id="thm_courtier_catholic",
            theme="courtier_legal_thinker",
            title="Catholic Identity in Protestant England",
            summary="Digby's Catholic faith profoundly shaped his public career. The son of a Gunpowder Plotter, he carried the 'stain' of his father's treason throughout his life. His Catholicism made Protestant diplomats like Thomas Roe suspicious of his motives even after military victories. Yet he served Protestant kings, befriended both Puritans and Catholics, and eventually became chancellor to the exiled Catholic queen.",
            key_details="Son of Gunpowder Plotter; educated by Jesuits; served Protestant court; Roe's anti-Catholic suspicion; chancellor to Queen Henrietta Maria in exile",
            people="Kenelm Digby, Everard Digby, Thomas Roe, Queen Henrietta Maria",
            places="London, Paris",
            significance="Digby's life exemplifies the precarious position of Catholic intellectuals in early modern England — simultaneously insider and outsider, trusted and suspected.",
            citation_ids="cit_ch1_youth,cit_courtier_miles",
            confidence=Confidence.HIGH.value,
        ),
    ]

    added_themes = 0
    for tr in new_themes:
        if tr.id not in existing_themes:
            validate_record(tr)
            insert_record("digby_theme_records", tr.to_dict())
            added_themes += 1
    print(f"Added {added_themes} new theme records.")

    # --- Additional Works ---
    new_works = [
        WorkRecord(
            id="wrk_observations_spenser",
            title="Observations on the 22nd Stanza of the 9th Canto (Spenser)",
            year=1643,
            work_type="treatise",
            subject="Literary criticism and alchemical philosophy",
            description="Digby's alchemical and philosophical interpretation of a stanza from Spenser's Faerie Queene describing the human body as a castle. First drafted aboard ship during his voyage, published in London 1643.",
            significance="Demonstrates Digby's method of reading literary texts through alchemical and astrological frameworks.",
            citation_ids="cit_observations",
        ),
        WorkRecord(
            id="wrk_observations_browne",
            title="Observations upon Religio Medici",
            year=1643,
            work_type="treatise",
            subject="Natural philosophy and religion",
            description="Digby's critical commentary on Thomas Browne's Religio Medici, published the same year as the Spenser observations. Engages with questions of faith, reason, and the natural world.",
            significance="Shows Digby's active participation in the intellectual debates of his era.",
            citation_ids="cit_observations",
        ),
        WorkRecord(
            id="wrk_loose_fantasies",
            title="Loose Fantasies",
            year=1628,
            work_type="memoir",
            subject="Autobiography and romance",
            description="Written aboard ship at Milos in August 1628, this autobiographical romance recounts Digby's life as 'Theagenes' and Venetia as 'Stelliana.' Modelled on Heliodorus. Published posthumously.",
            significance="Composed at the climax of his voyage, it reveals how Digby shaped his life story through literary models.",
            citation_ids="cit_ch8_return",
        ),
        WorkRecord(
            id="wrk_journal",
            title="Journal of a Voyage into the Mediterranean",
            year=1628,
            work_type="memoir",
            subject="Naval journal",
            description="Digby's detailed day-by-day record of his Mediterranean voyage (1628-1629), recording navigation, weather, encounters, battles, and observations. Published by the Camden Society in 1868.",
            significance="Primary source for the voyage, combining naval reportage with philosophical reflection.",
            citation_ids="cit_ch4_voyage_start",
        ),
        WorkRecord(
            id="wrk_bibliotheca",
            title="Bibliotheca Digbeiana",
            year=1680,
            work_type="treatise",
            subject="Library catalogue",
            description="Catalogue of Digby's library, published posthumously in 1680. His collection, one of the finest in England, was bequeathed to the Bodleian Library at Oxford, where it remains.",
            significance="Documents the extraordinary breadth of Digby's reading and intellectual interests.",
            citation_ids="cit_miles_overview",
        ),
    ]

    added_works = 0
    for w in new_works:
        if w.id not in existing_works:
            validate_record(w)
            insert_record("work_records", w.to_dict())
            added_works += 1
    print(f"Added {added_works} new work records.")

    # --- Summary ---
    conn = get_connection()
    print("\n--- Expanded Database Summary ---")
    for t in ["source_documents", "citations", "life_events", "work_records",
              "memoir_episodes", "digby_theme_records",
              "hypnerotomachia_findings", "hypnerotomachia_evidence"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {count} records")
    conn.close()


if __name__ == "__main__":
    expand()
