"""
Phase 2 content expansion: Home, Memoir, and Sources pages.

Adds narrative PageSection entries and expands memoir episode summaries
using grounded claims from the source corpus:
  - Moshenska biography (sdoc_moshenska)
  - Private Memoirs 1827 (sdoc_61a8e745 / sdoc_memoirs)
  - Wyndham Miles overview (sdoc_4a0dcb55 / sdoc_miles)
  - Mellick biographical summary (sdoc_6fc18de0 / sdoc_mellick)
"""

import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.db import init_db, insert_record, get_connection
from src.models import MemoirEpisode, PageSection, Citation, Confidence, SourceMethod, ReviewStatus
from src.validate import validate_record


# ---------------------------------------------------------------------------
# Content definitions
# ---------------------------------------------------------------------------

HOME_SECTIONS = [
    PageSection(
        id="sec_home_intro",
        page="home",
        section_key="intro",
        title="Sir Kenelm Digby (1603-1665)",
        position=0,
        citation_ids="cit_ch1_youth,cit_miles_overview,cit_mellick_bio",
        body=(
            "On 11 July 1603, four months after Elizabeth I died and James VI of Scotland "
            "ascended the English throne, Kenelm Digby was born at Gayhurst in Buckinghamshire. "
            "He entered a world already shadowed by conspiracy. His father, Sir Everard Digby, "
            "was among the Catholic plotters who attempted to blow up Parliament in November 1605. "
            "Everard was hanged, drawn, and quartered at St Paul's churchyard on 30 January 1606, "
            "when Kenelm was barely two years old. The boy inherited what he would later call "
            "a 'foul stain in his blood' -- the stigma of a traitor's son -- along with an "
            "estate of roughly three thousand pounds per annum that the crown failed to seize "
            "because it had been entailed.\n\n"

            "Raised by his Catholic mother Mary and educated by Jesuit tutors, Kenelm was sent "
            "to Gloucester Hall, Oxford, around 1618 under the guidance of the scholar Thomas "
            "Allen. He also studied with Richard Napier at Great Linford, a physician-priest who "
            "practised astrology and alchemy alongside conventional medicine. Napier cast the "
            "young man's horoscope, introduced him to alchemical philosophy, and lent him whole "
            "'cloak-bags' of books, igniting an intellectual hunger that would never abate.\n\n"

            "As a teenager Kenelm met and fell in love with Venetia Stanley, three years his "
            "senior and descended from the Earls of Derby and Northumberland. Their families' "
            "Catholic circles brought them together in Buckinghamshire, and a secret attachment "
            "took root despite his mother's fierce opposition. Venetia's beauty was already "
            "celebrated -- and already the subject of rumour.\n\n"

            "Between 1620 and 1623 Kenelm undertook a Grand Tour that carried him through "
            "France, Italy, and Spain. He encountered Marie de Medici at the French court, "
            "immersed himself in Florentine and Sienese culture, and joined Prince Charles "
            "and the Duke of Buckingham in Madrid during the ill-fated Spanish Match. These "
            "travels forged a cosmopolitan identity and a network of connections across Catholic "
            "Europe that would serve him for decades.\n\n"

            "In the spring of 1625 Kenelm and Venetia married secretly in London. Two sons "
            "followed. But domestic contentment could not quench his restlessness or silence "
            "the gossip about his father's treason. Late in 1627, despite the active obstruction "
            "of the Duke of Buckingham, Kenelm assembled a small fleet and set sail for the "
            "Mediterranean on a privateering voyage sanctioned by King Charles I.\n\n"

            "The voyage of 1628 became the defining adventure of his life. Plague struck his "
            "crew in the Mediterranean; he resupplied at Algiers and negotiated the release of "
            "English captives held by Barbary corsairs. On 11 June 1628 his ships engaged and "
            "defeated a squadron of Venetian galleasses in the Bay of Scanderoon, a victory "
            "that brought him fame in England and infamy in Venice, where he was branded a pirate. "
            "He collected ancient marbles from the deserted island of Delos, read Heliodorus "
            "and Spenser in his cabin, and at the island of Milos sat down to write his "
            "autobiographical romance, the Loose Fantasies, transforming his life into a tale "
            "of star-crossed love modelled on the Greek romances.\n\n"

            "Venetia died suddenly in her sleep on 1 May 1633. Kenelm was devastated. He "
            "commissioned Anthony van Dyck to paint her on her deathbed and retreated into "
            "grief, scholarship, and alchemy at Gresham College. During the Civil War he lived "
            "in exile in Paris, serving as chancellor to Queen Henrietta Maria, publishing his "
            "philosophical magnum opus, the Two Treatises on the nature of body and soul (1644), "
            "and corresponding with Descartes, Hobbes, and Fermat. He befriended Oliver Cromwell "
            "well enough to have his sequestration lifted, and donated books to the newly founded "
            "library at Harvard.\n\n"

            "After the Restoration in 1660, Kenelm returned to London and became a founding "
            "member of the Royal Society, delivering the first paper the Society commissioned "
            "for publication -- a discourse on the vegetation of plants that contained an early "
            "intuition about photosynthesis. He died on his birthday, 11 June 1665, at his "
            "chambers in Covent Garden, surrounded by van Dyck's paintings of Venetia, plaster "
            "casts of her hands and face, shelves of books stamped with a monogram intertwining "
            "K, D, and V, and the manuscript of the Loose Fantasies tucked into his pocket. His "
            "magnificent library was bequeathed to the Bodleian at Oxford, where it remains."
        ),
    ),
    PageSection(
        id="sec_home_significance",
        page="home",
        section_key="significance",
        title="Why Digby Matters",
        position=10,
        citation_ids="cit_miles_overview,cit_mellick_bio,cit_ch1_youth",
        body=(
            "Sir Kenelm Digby stands at one of the most crowded intersections in early modern "
            "English history. He was simultaneously a privateer and a poet, a courtier and a "
            "cook, a natural philosopher and an alchemist, a Catholic apologist and a friend "
            "to Puritans, a loyal servant to King Charles I and the son of a man executed for "
            "high treason against the crown. No other single figure embodies so many of the "
            "contradictions that defined seventeenth-century England.\n\n"

            "His significance extends across multiple fields. In the history of science, Digby's "
            "Two Treatises (1644) attempted to reconcile Aristotelian philosophy with emerging "
            "corpuscular theories of matter, while his Royal Society lecture on the vegetation "
            "of plants (1661) contained a remarkable early suggestion that plants drew sustenance "
            "from the air. In the history of ideas, his friendship and correspondence with "
            "Descartes, Hobbes, and Fermat placed him at the centre of the seventeenth-century "
            "Republic of Letters. In culinary history, The Closet of Sir Kenelm Digby Opened "
            "(1669), published posthumously by his steward, is one of the foundational English "
            "cookbooks, recording recipes gathered from courts and kitchens across Europe.\n\n"

            "Digby's Mediterranean voyage of 1628 illuminates the porous boundary between "
            "privateering and piracy in the early Stuart period, the complex diplomacy of the "
            "Levant trade, and the cultural exchanges that flowed along the sea routes connecting "
            "England, North Africa, the Ottoman Empire, and the Venetian Republic. His Loose "
            "Fantasies, written aboard ship, is one of the earliest English autobiographies and "
            "a rare example of a life deliberately reshaped through the conventions of Greek "
            "romance.\n\n"

            "For this project, Digby also matters because of a tantalising connection to the "
            "Hypnerotomachia Poliphili. A copy of the 1499 Aldine edition bearing annotations "
            "that have been tentatively attributed to Digby's circle suggests that the same "
            "alchemical reading practices he applied to Spenser and Heliodorus may have been "
            "brought to bear on Colonna's dream-romance -- another lavishly illustrated fusion "
            "of love, architecture, and hermetic philosophy."
        ),
    ),
]

MEMOIR_SECTIONS = [
    PageSection(
        id="sec_memoir_intro",
        page="memoir",
        section_key="intro",
        title="The Private Memoirs of Sir Kenelm Digby",
        position=0,
        citation_ids="cit_ch8_return,cit_mellick_bio",
        body=(
            "In August 1628, five battle-scarred English ships sailed into the harbour of the "
            "Greek island of Milos. Their twenty-five-year-old captain, fresh from his victory "
            "over Venetian galleasses at Scanderoon and three days of collecting ancient marbles "
            "on the deserted island of Delos, banqueted with the local lord before retiring to "
            "his cabin. There, in the sweltering heat of a Mediterranean summer, with the "
            "sounds of his crew's celebrations drifting through the open windows, Sir Kenelm "
            "Digby sat down to write the story of his life.\n\n"

            "The result was the work known as the Loose Fantasies, or the Private Memoirs -- "
            "an autobiographical romance that recounts the events of Digby's life from childhood "
            "to the aftermath of Scanderoon, cast in the language and conventions of the Greek "
            "romances he had been reading at sea. Digby wrote the entire narrative in the third "
            "person, adopting pseudonyms drawn from classical literature for every person and "
            "place in the story. He became Theagenes, a name borrowed from the hero of "
            "Heliodorus's Aethiopica; Venetia Stanley became Stelliana, from the Latin for "
            "'star'; England was renamed Morea, London became Corinth, France became Athens, "
            "and Spain became Egypt. The key to these pseudonyms was added by a later hand "
            "in the manuscript now preserved in the British Library (Harleian MS 6758).\n\n"

            "Digby modelled his memoir on the Aethiopica, the late-antique Greek romance by "
            "Heliodorus that he had read while becalmed off the coast of Egypt earlier that "
            "summer. Like the Aethiopica, the Loose Fantasies tells the story of two lovers "
            "separated by fortune, tested by rivals and misfortune, and ultimately reunited. "
            "The narrative blends verifiable historical events -- Digby's education at Oxford, "
            "his Grand Tour, the political machinations of the Duke of Buckingham -- with "
            "romantic literary conventions: abductions, disguises, false reports of death, "
            "and improbable rescues. Where fact ends and literary invention begins is often "
            "impossible to determine, and Digby intended it that way.\n\n"

            "The memoir was never published in Digby's lifetime. The manuscript remained among "
            "his papers and eventually entered the Harleian Collection. It was first published "
            "in 1827 by Saunders and Otley in London, under the title Private Memoirs of Sir "
            "Kenelm Digby, with an introductory biographical essay by the editor. Vittorio "
            "Gabrieli published a scholarly edition in 1968 under Digby's original title, "
            "Loose Fantasies. The 1827 edition provides the primary text used for the episode "
            "summaries on this site."
        ),
    ),
    PageSection(
        id="sec_memoir_structure",
        page="memoir",
        section_key="structure",
        title="Structure and Literary Framework",
        position=5,
        citation_ids="cit_ch8_return,cit_mellick_bio",
        body=(
            "The Loose Fantasies follows the structural conventions of Greek romance while "
            "narrating the real events of Digby's life. Like Heliodorus's Aethiopica and "
            "the late-antique romances of Achilles Tatius and Longus, the memoir begins in "
            "medias res, opens with a scene of mystery and longing, and proceeds through a "
            "series of episodes that test the hero's constancy, courage, and virtue.\n\n"

            "The pseudonyms are not merely decorative. By renaming himself Theagenes, Digby "
            "explicitly invites comparison with Heliodorus's noble hero -- a figure of perfect "
            "fidelity separated from his beloved by the machinations of fate. By calling "
            "Venetia 'Stelliana,' he elevates her to a figure of celestial beauty and constancy, "
            "countering the gossip and scandal that had surrounded her reputation. The "
            "geographical renamings -- Morea for England, Corinth for London, Athens for France, "
            "Egypt for Spain -- transpose the story into a classical Mediterranean world where "
            "the petty politics of Stuart England assume the grandeur of ancient epic.\n\n"

            "Fact and fiction interweave throughout. Digby's account of his education at Oxford "
            "under Thomas Allen, his Grand Tour through France and Italy, and the political "
            "context of the Spanish Match can all be verified against other sources. But the "
            "romantic episodes -- Venetia's abduction by the nobleman Ursatius, her rescue by "
            "the mysterious Mardontius, the attempts of Marie de Medici to seduce the young "
            "Theagenes -- are shaped by the conventions of romance, heightened, embellished, "
            "and made to serve the purposes of the narrative. The editor of the 1827 edition "
            "observed that one should allow for the high colouring of the picture while "
            "trusting the general fidelity of the outline."
        ),
    ),
    PageSection(
        id="sec_memoir_conclusion",
        page="memoir",
        section_key="conclusion",
        title="Significance of the Memoir",
        position=99,
        citation_ids="cit_ch8_return,cit_mellick_bio,cit_miles_overview",
        body=(
            "The Loose Fantasies is one of the earliest English autobiographies and among "
            "the most unusual. It is simultaneously a love letter to Venetia Stanley, a "
            "defence of the Digby family honour, and an exercise in literary self-fashioning "
            "that draws on classical models to reshape the raw materials of a seventeenth-century "
            "English life.\n\n"

            "As a historical document, the memoir preserves details about Digby's childhood, "
            "his Catholic education, his Grand Tour, and the politics of the 1620s that are "
            "found in no other source. As a literary work, it demonstrates how thoroughly Digby "
            "absorbed the conventions of Greek romance and applied them to his own experience, "
            "anticipating by centuries the modern understanding that all autobiography is a form "
            "of narrative construction.\n\n"

            "Digby kept the manuscript with him until his death in 1665. When he left his Covent "
            "Garden chambers for the last time, he slipped the small, unprepossessing volume "
            "into his pocket alongside the enamel miniature of Venetia. The work that had begun "
            "as an act of self-transformation in the harbour at Milos had become his most "
            "intimate possession."
        ),
    ),
]

SOURCES_SECTIONS = [
    PageSection(
        id="sec_sources_intro",
        page="sources",
        section_key="intro",
        title="The Digby Source Corpus",
        position=0,
        citation_ids="cit_miles_overview,cit_mellick_bio",
        body=(
            "The source corpus for this project comprises over forty documents spanning primary "
            "texts by Digby himself, modern biographies, scholarly articles, and reference "
            "materials. These sources range from the seventeenth century to the present day and "
            "cover Digby's biography, his Mediterranean voyage, his alchemical and philosophical "
            "work, his place in Stuart court politics, and the tantalising connection between "
            "his circle and the Hypnerotomachia Poliphili.\n\n"

            "The corpus divides broadly into primary sources -- works written by Digby or "
            "transcribed from his manuscripts during or shortly after his lifetime -- and "
            "secondary sources, which include modern biographies, journal articles, and "
            "reference works that interpret and contextualise his life. The most important "
            "primary sources are the Private Memoirs (Loose Fantasies), the Journal of a "
            "Voyage into the Mediterranean, and The Closet of Sir Kenelm Digby Opened. The "
            "most important secondary source is Joe Moshenska's A Stain in the Blood: The "
            "Remarkable Voyage of Sir Kenelm Digby (2016), which provides the fullest modern "
            "account of the 1628 voyage and its context.\n\n"

            "Every claim in the database is linked to at least one citation, and every citation "
            "traces back to a specific source document and location within that document. This "
            "provenance chain ensures that the site's content can be checked against the "
            "original scholarship and that the boundary between source evidence and editorial "
            "interpretation remains visible."
        ),
    ),
    PageSection(
        id="sec_sources_primary",
        page="sources",
        section_key="primary",
        title="Primary Sources",
        position=10,
        citation_ids="cit_ch8_return,cit_miles_overview",
        body=(
            "Digby was a prolific writer, and several of his works survive in both manuscript "
            "and printed form. The Private Memoirs (Loose Fantasies), written aboard ship at "
            "Milos in August 1628 and first published in 1827, is the primary source for the "
            "memoir episodes on this site. The Journal of a Voyage into the Mediterranean, "
            "a day-by-day naval record of the 1628 voyage, was published by the Camden Society "
            "in 1868 and provides the factual backbone against which the romance of the Memoirs "
            "can be measured.\n\n"

            "The Closet of Sir Kenelm Digby Opened (1669), published posthumously by his "
            "steward George Hartmann, collects recipes gathered from courts and kitchens across "
            "Europe. Digby's Chymical Secrets (1682) records alchemical and pharmaceutical "
            "recipes. His letters, collected in part by Vittorio Gabrieli as 'A New Digby "
            "Letter-Book' in the National Library of Wales Journal (1955-58), preserve intimate "
            "correspondence including the anguished letters written after Venetia's death.\n\n"

            "Among Digby's philosophical works, the Two Treatises (1644) on the nature of body "
            "and soul represents his major contribution to natural philosophy, while his "
            "Observations on Spenser (1643) and Observations upon Religio Medici (1643) show "
            "his characteristic method of reading literary and devotional texts through "
            "philosophical and alchemical lenses. The Bibliotheca Digbeiana (1680), the "
            "catalogue of his library, documents the extraordinary range of his reading."
        ),
    ),
]


# ---------------------------------------------------------------------------
# Expanded memoir episode summaries (keyed by existing episode id)
# ---------------------------------------------------------------------------

EPISODE_UPDATES = {
    "mem_departure": (
        "On 6 January 1628, Digby's small fleet of five ships -- the Eagle (his flagship), "
        "the George and Elizabeth, the Convertine, and two smaller vessels -- weighed anchor "
        "and left the Thames. The departure was the culmination of months of preparation "
        "carried out in the teeth of deliberate obstruction by the Duke of Buckingham, the "
        "most powerful man in England and King Charles's closest favourite. Digby had used "
        "his own fortune and the king's direct support to assemble roughly 250 men, many of "
        "them scarred veterans of the disastrous English expeditions to Cadiz in 1625 and the "
        "Ile de Re in 1627. He left behind his wife Venetia and their two small sons, "
        "carrying with him the weight of his father Everard's execution for the Gunpowder "
        "Plot and a fierce determination to redeem the family name through martial glory. "
        "The fleet slipped down the Channel and turned south toward the open Atlantic, "
        "beginning a voyage that would last thirteen months and carry Digby across the "
        "entire length of the Mediterranean."
    ),
    "mem_plague_at_sea": (
        "Shortly after entering the Mediterranean through the Straits of Gibraltar, a violent "
        "pestilential disease erupted among the crew of the Eagle. Within days, sixty of the "
        "one hundred and fifty men aboard fell desperately ill. The sick suffered terrifying "
        "delirium, believing the sea around them was a spacious and pleasant green meadow, "
        "and some had to be restrained from leaping overboard to walk upon it. Digby's "
        "officers urged an immediate return to England, arguing that the voyage was doomed "
        "before it had properly begun. Digby refused. He pressed on toward the North African "
        "coast, reasoning that Algiers offered the best hope of resupply, medical assistance, "
        "and a chance to rest his stricken crew. The decision was a pivotal test of his "
        "authority as a young and untested commander -- had the plague not been checked, "
        "the entire enterprise would have ended in the first weeks. Digby's composure under "
        "pressure and his willingness to override his more experienced officers established "
        "the pattern of bold, sometimes reckless, decision-making that would characterise "
        "the rest of the voyage."
    ),
    "mem_father_shadow": (
        "On Bonfire Night 1627, while London celebrated the annual commemoration of the "
        "foiling of the Gunpowder Plot with bonfires and public revelry, Kenelm Digby paced "
        "his chambers haunted by the memory of his father's execution. Sir Everard Digby had "
        "been hanged, drawn, and quartered at St Paul's churchyard on 30 January 1606, when "
        "Kenelm was barely two years old. According to family tradition, the infant cried out "
        "at the exact moment of his father's death. Every 5 November, the national celebration "
        "of the Plot's discovery renewed the public stigma that attached to the Digby name. "
        "Kenelm grew up carrying what he called a 'foul stain in his blood,' a burden that "
        "shaped his ambitions and drove his relentless pursuit of honour. The annual Bonfire "
        "Night rituals, with their burning of Guy Fawkes effigies and public thanksgiving for "
        "Protestant deliverance, were a pointed reminder that in the eyes of much of England "
        "the Digby family remained associated with Catholic treason. This episode, set on the "
        "eve of the voyage, shows how the shadow of the Gunpowder Plot propelled Kenelm toward "
        "the Mediterranean -- a theatre far enough from England to allow him to forge a new "
        "identity through action."
    ),
    "mem_venetia_love": (
        "Kenelm first met Venetia Stanley through the Catholic family networks of "
        "Buckinghamshire. Venetia, three years his senior, was the daughter of Sir Edward "
        "Stanley of Tonge Castle, descended from the Earls of Derby and the Percys of "
        "Northumberland. Her mother Lucy had died when Venetia was only a few months old, "
        "and her father, a negligent husband turned grief-stricken recluse, placed her in "
        "the care of a kinswoman whose house stood near Lady Digby's seat at Gayhurst. "
        "Frequent visits between the two families brought the children together, and a mutual "
        "attachment arose. In the Loose Fantasies, Digby describes their first kiss occurring "
        "during a hunting expedition near Gayhurst, when they took shelter from a rainstorm "
        "under a tree. His mother Mary opposed the match fiercely -- Venetia's beauty was "
        "already famous, but her family was poor despite its noble blood, and Lady Digby had "
        "arranged a different match for her son. The tension between Kenelm's devotion to "
        "Venetia and his mother's opposition became one of the defining threads of the memoir, "
        "with Digby casting his love as a romance-hero's constancy tested by hostile fortune."
    ),
    "mem_grand_tour": (
        "Between 1620 and 1623, Digby undertook the Grand Tour that was expected of a young "
        "English gentleman of his rank, though his itinerary was shaped as much by his Catholic "
        "connections as by convention. He travelled first to France, where he enrolled at the "
        "University of Paris but soon left the city when plague broke out, retreating to "
        "Angers. In the Loose Fantasies he claims to have encountered Marie de Medici at a "
        "masquerade and to have attracted the Queen Mother's amorous attention -- an episode "
        "whose romantic embellishments are characteristic of the memoir's literary style. From "
        "France he crossed into Italy, settling for a time in Florence, where he immersed "
        "himself in the intellectual and artistic culture of the Tuscan court, and in Siena. "
        "The Italian sojourn deepened his cosmopolitan sensibility and his appreciation for "
        "visual art, classical learning, and natural philosophy. In 1623 he joined Prince "
        "Charles and the Duke of Buckingham in Madrid during the Spanish Match, the doomed "
        "attempt to arrange a marriage between the Prince and the Spanish Infanta. These "
        "travels transformed Digby from a provincial Catholic gentleman into a figure at ease "
        "in the courts and academies of continental Europe."
    ),
    "mem_scanderoon_fight": (
        "On 11 June 1628, Digby's fleet engaged a squadron of Venetian galleasses and merchant "
        "vessels anchored in the Bay of Scanderoon (modern Iskenderun) on the Turkish coast. "
        "The battle was the defining military action of the voyage. Digby attacked at dawn, "
        "closing rapidly to deny the Venetian galleys the advantage of their oar-powered "
        "manoeuvrability. The fighting was fierce: cannon fire shattered the galleasses' "
        "superstructures, and Digby's men boarded under heavy resistance. The English ships "
        "took several prizes and forced the remainder of the Venetian squadron to withdraw. "
        "The aftermath, however, proved as dangerous as the battle itself. English merchants "
        "in Aleppo were seized by Ottoman authorities under Venetian pressure, and Venetian "
        "diplomats launched a coordinated propaganda campaign across the Mediterranean, "
        "branding Digby a pirate. The consul Alvise da Pesaro called him 'nothing but a thief "
        "and a pirate,' and letters flew from Venice's network of outposts denouncing his "
        "actions. Even the English ambassador Sir Thomas Roe, a Protestant suspicious of "
        "Digby's Catholic loyalties, complained about the disruption to Levant trade. The vice "
        "consul at Scanderoon pleaded repeatedly for Digby to leave. The battle thus revealed "
        "the central paradox of Digby's voyage: actions that made him a hero in England made "
        "him a criminal in Venice."
    ),
    "mem_delos": (
        "On 28 August 1628, Digby brought his fleet to anchor off the deserted island of "
        "Delos, sacred in antiquity as the birthplace of Apollo and Artemis. He spent three "
        "days exploring the extensive ruins of the ancient temple complex, accompanied by "
        "parties of his crew. Unlike other English collectors who disguised themselves and "
        "sawed statues into portable fragments, Digby arrived openly as the victor of "
        "Scanderoon and mobilised some three hundred men in the collection effort. He devised "
        "an ingenious pulley system, using the masts and rigging of his ships, to hoist a "
        "massive marble block bearing four statues aboard intact. He also collected inscribed "
        "monuments and smaller fragments. One colossal broken statue of Apollo, far too large "
        "to move, held him transfixed: he stood contemplating it for an hour, awed by its "
        "scale and the melancholy of its ruin. The marbles from Delos were carried back to "
        "England and presented to King Charles, adding to the Stuart court's growing collection "
        "of classical antiquities. The Delos episode demonstrates how Digby combined the "
        "instincts of a privateer with the sensibility of a humanist scholar -- looting and "
        "contemplation proceeding hand in hand."
    ),
    "mem_milo_postscript": (
        "After leaving Delos, Digby sailed to the island of Milos, where he anchored in the "
        "harbour and was received by the local Greek lord. It was here, in the relative calm "
        "following the intensity of the voyage's military and archaeological episodes, that "
        "Digby sat down to write the Loose Fantasies. The choice of Milos was fitting: the "
        "island lay at the heart of the Cyclades, surrounded by the classical Greek world that "
        "pervaded the literary models Digby had been reading at sea. He wrote rapidly, in the "
        "third person, adopting the pseudonyms of Greek romance and casting the story of his "
        "life as the tale of Theagenes and Stelliana. The writing was an act of self-fashioning "
        "at a moment of triumph: Digby had defeated the Venetians, plundered the ruins of "
        "Delos, and earned the reputation he had sailed to win. The memoir fixed this moment "
        "of achievement in literary form, transforming the raw events of his life into a "
        "narrative shaped by the conventions of Heliodorus and the Greek romancers. It was "
        "also, perhaps, a private love letter to Venetia, written thousands of miles from "
        "home by a young husband who had left his wife and children behind."
    ),
    "mem_childhood_love": (
        "In the Loose Fantasies, Digby devotes considerable attention to the earliest stirrings "
        "of his attachment to Venetia Stanley, casting their childhood meetings in the language "
        "of romance destiny. The two families -- the Digbys at Gayhurst and the Stanleys "
        "nearby -- were connected through the Catholic networks of Buckinghamshire, and the "
        "children's encounters were frequent and unsupervised. Digby writes of their mutual "
        "attraction as something that 'grew with their growth,' a phrase drawn from the "
        "conventions of romance literature that presents love as fated rather than chosen. "
        "He describes Venetia's extraordinary beauty even in childhood, her intelligence, "
        "and her noble bearing despite her family's reduced circumstances. The episode "
        "establishes the memoir's central claim: that Digby's love for Venetia was the "
        "animating force of his life, present from the earliest age and constant through "
        "every trial. By placing this attachment at the beginning of his narrative, Digby "
        "frames everything that follows -- the Grand Tour, the voyage, the battle, the "
        "writing of the memoir itself -- as acts undertaken in service of a love that began "
        "in Buckinghamshire and endured to the end."
    ),
    "mem_ursatius_abduction": (
        "One of the most dramatic episodes in the Loose Fantasies recounts the attempted "
        "abduction of Venetia by the nobleman Ursatius, a powerful figure at court who had "
        "been captivated by her beauty. According to Digby's account, Venetia's governess "
        "was bribed by Ursatius to advocate his cause and to depreciate Kenelm as a suitor. "
        "When persuasion failed, the governess helped lure Venetia to a remote country house "
        "under the pretence of arranging a meeting with Digby. Ursatius arrived and pressed "
        "his suit, but Venetia refused him. That night, she escaped by lowering herself from "
        "a window and climbing down the garden wall. During her flight she was attacked by a "
        "wolf but was rescued by the young nobleman Mardontius, who escorted her to safety "
        "at the house of her relation Artesia. The episode reads like pure romance -- the "
        "imprisoned maiden, the midnight escape, the providential rescue -- and its historical "
        "basis is impossible to verify. But the 1827 editor noted that while the high "
        "colouring of the picture should be discounted, the general outline is consistent "
        "with other known facts about the dangers facing unprotected young women in early "
        "Stuart England."
    ),
    "mem_brahmin_spirit": (
        "Among the stranger episodes in the Loose Fantasies is Digby's account of an encounter "
        "with a learned Brahmin or Eastern sage during his travels, who introduced him to ideas "
        "about the transmigration of souls and the spiritual unity of the natural world. The "
        "episode reflects the cosmopolitan intellectual currents that Digby encountered during "
        "his Grand Tour and his Mediterranean voyage, where ideas from Islamic, Jewish, and "
        "Eastern philosophical traditions circulated alongside the classical and Christian "
        "learning of Western Europe. Whether the encounter was real or literary invention, it "
        "served Digby's purpose of presenting himself as a figure whose intellectual horizons "
        "extended far beyond the parochial boundaries of English Protestantism. The Brahmin's "
        "teachings about sympathetic forces connecting all things in nature resonated with "
        "the alchemical and Neoplatonic philosophy Digby had absorbed from Richard Napier "
        "and would later develop in his Two Treatises. The episode anticipates his famous "
        "discourse on the Powder of Sympathy, in which he argued that wounds could be healed "
        "at a distance through the sympathetic connection between blood and the weapon that "
        "shed it."
    ),
    "mem_madrid_ambush": (
        "During his time in Madrid in 1623, where he had joined the entourage of Prince Charles "
        "and the Duke of Buckingham for the Spanish Match, Digby found himself caught up in the "
        "dangerous intrigues of the Spanish court. In the Loose Fantasies, he recounts an "
        "episode in which he was ambushed in the streets of Madrid by armed men, possibly "
        "agents of a Spanish nobleman who resented the English presence or who had personal "
        "reasons for hostility toward Digby. The attack was beaten off, but it impressed upon "
        "the young Digby the physical dangers that attended the political world he was entering. "
        "The Spanish Match itself was a fiasco -- Prince Charles returned to England humiliated, "
        "and the failure poisoned relations between England and Spain for years afterward. For "
        "Digby, the Madrid experience was formative: it exposed him to the grandeur and menace "
        "of continental court politics, deepened his relationship with both the Prince and "
        "Buckingham (a relationship that would later sour), and gave him firsthand knowledge "
        "of Spain that would prove useful during his Mediterranean voyage when his ships "
        "needed to slip past Spanish naval patrols."
    ),
}


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def expand():
    init_db()

    conn = get_connection()
    existing_sections = {
        r["id"] for r in conn.execute("SELECT id FROM page_sections").fetchall()
    }
    existing_episodes = {
        r["id"]: r["summary"]
        for r in conn.execute("SELECT id, summary FROM memoir_episodes").fetchall()
    }
    conn.close()

    # --- Insert page sections (idempotent) ---
    all_sections = HOME_SECTIONS + MEMOIR_SECTIONS + SOURCES_SECTIONS
    added_sections = 0
    for sec in all_sections:
        if sec.id not in existing_sections:
            validate_record(sec)
            insert_record("page_sections", sec.to_dict())
            added_sections += 1
            print(f"  + {sec.id} ({sec.page}/{sec.section_key})")
        else:
            print(f"  . {sec.id} already exists, skipping")

    print(f"\nAdded {added_sections} new page sections.")

    # --- Expand memoir episode summaries via SQL UPDATE ---
    conn = get_connection()
    updated_episodes = 0
    skipped_episodes = 0
    for ep_id, new_summary in EPISODE_UPDATES.items():
        if ep_id not in existing_episodes:
            print(f"  ! {ep_id} not found in memoir_episodes, skipping update")
            skipped_episodes += 1
            continue

        current_len = len(existing_episodes[ep_id]) if existing_episodes[ep_id] else 0
        new_len = len(new_summary)

        # Only update if the new summary is substantially longer
        if new_len > current_len * 1.5:
            conn.execute(
                "UPDATE memoir_episodes SET summary = ? WHERE id = ?",
                (new_summary, ep_id),
            )
            updated_episodes += 1
            print(f"  ~ {ep_id}: {current_len} -> {new_len} chars")
        else:
            print(f"  . {ep_id} already expanded ({current_len} chars), skipping")

    conn.commit()
    conn.close()

    print(f"\nUpdated {updated_episodes} memoir episode summaries.")
    if skipped_episodes:
        print(f"Skipped {skipped_episodes} episodes (not found in database).")

    # --- Summary ---
    conn = get_connection()
    print("\n--- Content Summary ---")
    sec_count = conn.execute("SELECT COUNT(*) FROM page_sections").fetchone()[0]
    ep_count = conn.execute("SELECT COUNT(*) FROM memoir_episodes").fetchone()[0]
    avg_summary = conn.execute(
        "SELECT AVG(LENGTH(summary)) FROM memoir_episodes"
    ).fetchone()[0]
    print(f"  page_sections: {sec_count} total")
    print(f"  memoir_episodes: {ep_count} total, avg summary length: {avg_summary:.0f} chars")

    # Per-page section breakdown
    for row in conn.execute(
        "SELECT page, COUNT(*) as cnt, SUM(LENGTH(body)) as total_chars "
        "FROM page_sections GROUP BY page ORDER BY page"
    ).fetchall():
        print(f"  page '{row['page']}': {row['cnt']} sections, {row['total_chars']} chars")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    expand()
