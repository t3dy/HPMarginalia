"""Extract all PDFs to markdown files with YAML frontmatter."""

import re
import os
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install PyMuPDF")
    raise

BASE_DIR = Path(__file__).resolve().parent.parent
MD_DIR = BASE_DIR / "md"
MD_DIR.mkdir(exist_ok=True)

# Known metadata mappings for better frontmatter
KNOWN_METADATA = {
    'PhD_Thesis_ _James_Russell': {
        'title': 'Hypnerotomachia Poliphili: A Study of Marginal Annotations in Six Copies',
        'author': 'James Russell',
        'year': 2024,
        'doc_type': 'DISSERTATION',
    },
    'E_Thesis_Durham_University_Self_Transfor Oneill': {
        'title': 'Self-transformation in the Hypnerotomachia Poliphili',
        'author': "James O'Neill",
        'year': 2025,
        'journal': 'Durham University (E-Thesis)',
        'doc_type': 'DISSERTATION',
    },
    'A_Narrative_in_Search_of_an_Author': {
        'title': 'A Narrative in Search of an Author: The Hypnerotomachia Poliphili',
        'author': "James O'Neill",
        'year': 2025,
        'doc_type': 'SCHOLARSHIP',
    },
    'Francesco Colonna Hypnerotomachia Poliphili Da Capo': {
        'title': 'Hypnerotomachia Poliphili (Da Capo Press edition)',
        'author': 'Francesco Colonna',
        'year': 1499,
        'doc_type': 'PRIMARY_TEXT',
    },
    'Francesco Colonna Rino Avesani': {
        'title': 'Hypnerotomachia Poliphili, Vol. 1 (Antenore critical edition)',
        'author': 'Francesco Colonna (ed. Pozzi & Ciapponi)',
        'year': 1964,
        'doc_type': 'PRIMARY_TEXT',
    },
    'Hypnerotomachia by Francesco Colonna': {
        'title': 'Hypnerotomachia Poliphili',
        'author': 'Francesco Colonna',
        'year': 1499,
        'doc_type': 'PRIMARY_TEXT',
    },
    'The HP of Ben Jonson': {
        'title': 'The HP of Ben Jonson and Kenelm Digby',
        'author': 'Unknown',
        'year': 2025,
        'doc_type': 'PRESENTATION',
    },
    'Crossing_the_text_image_boundary': {
        'title': 'Crossing the Text-Image Boundary: The French HP',
        'author': 'Unknown',
        'doc_type': 'SCHOLARSHIP',
    },
    'Dream_Narratives_and_Initiation_Processe': {
        'title': 'Dream Narratives and Initiation Processes',
        'author': 'Unknown',
        'doc_type': 'SCHOLARSHIP',
    },
    'Editions SR 25 James Gollnick': {
        'title': 'Religious Dreamworld of Apuleius Metamorphoses: Recovering a Forgotten Hermeneutic',
        'author': 'James Gollnick',
        'doc_type': 'SCHOLARSHIP',
    },
    'Elucidating_and_Enigmatizing_the_Recepti': {
        'title': 'Elucidating and Enigmatizing the Reception of the HP',
        'author': 'Unknown',
        'doc_type': 'SCHOLARSHIP',
    },
    'Eugenio Canone_ Leen Spruit': {
        'title': 'Emblematics in the Early Modern Age: Case Studies',
        'author': 'Eugenio Canone and Leen Spruit',
        'doc_type': 'SCHOLARSHIP',
    },
    'Georg Leidinger Albrecht D': {
        'title': 'Albrecht Durer und die Hypnerotomachia Poliphili',
        'author': 'Georg Leidinger',
        'doc_type': 'SCHOLARSHIP',
    },
    'Italica 1947': {
        'title': 'Some Foreign Imitators of the Hypnerotomachia Poliphili',
        'author': 'Mario Praz',
        'year': 1947,
        'journal': 'Italica 24:1',
        'doc_type': 'SCHOLARSHIP',
    },
    'Journal of the Warburg Institute 1937': {
        'title': 'The Hypnerotomachia Poliphili in 17th Century France',
        'author': 'Anthony Blunt',
        'year': 1937,
        'journal': 'Journal of the Warburg Institute 1:2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Journal of the Warburg and Courtauld Institutes vol 47': {
        'title': 'Alberti and the Hypnerotomachia Poliphili',
        'author': 'D. R. Edward Wright',
        'year': 1984,
        'journal': 'Journal of the Warburg and Courtauld Institutes 47',
        'doc_type': 'SCHOLARSHIP',
    },
    'Liane Lefaivre': {
        'title': "Leon Battista Alberti's Hypnerotomachia Poliphili: Re-Cognizing the Architectural Body",
        'author': 'Liane Lefaivre',
        'year': 1997,
        'doc_type': 'SCHOLARSHIP',
    },
    'Notes and Queries 1952': {
        'title': 'Some Notes on the Vocabulary of the Hypnerotomachia Poliphili',
        'author': 'Peter Ure',
        'year': 1952,
        'journal': 'Notes and Queries 197:26',
        'doc_type': 'SCHOLARSHIP',
    },
    'Renaissance Quarterly vol 55': {
        'title': 'The Hypnerotomachia Poliphili, Image, Text, and Vernacular Poetics',
        'author': 'Rosemary Trippe',
        'year': 2002,
        'journal': 'Renaissance Quarterly 55:4',
        'doc_type': 'SCHOLARSHIP',
    },
    'Renaissance Studies 1990': {
        'title': 'The Structural Problematic of the Hypnerotomachia Poliphili',
        'author': 'Mark Jarzombek',
        'year': 1990,
        'journal': 'Renaissance Studies 4:3',
        'doc_type': 'SCHOLARSHIP',
    },
    'Studies in Philology 2006': {
        'title': "Robert Dallington's Hypnerotomachia and the Protestant Antiquity of Elizabethan England",
        'author': 'L. E. Semler',
        'year': 2006,
        'journal': 'Studies in Philology 103:2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Teaching_Eros': {
        'title': 'Teaching Eros: The Rhetoric of Love in the Hypnerotomachia Poliphili',
        'author': 'Unknown',
        'doc_type': 'SCHOLARSHIP',
    },
    'The Modern Language Review 1955': {
        'title': 'Francesco Colonna and Rabelais',
        'author': 'Marcel Francon',
        'year': 1955,
        'journal': 'The Modern Language Review 50:1',
        'doc_type': 'SCHOLARSHIP',
    },
    'The_Narrative_Function_of_Hieroglyphs': {
        'title': 'The Narrative Function of Hieroglyphs in the Hypnerotomachia Poliphili',
        'author': 'Unknown',
        'doc_type': 'SCHOLARSHIP',
    },
    'Untangling the knot': {
        'title': "Untangling the Knot: Garden Design in Francesco Colonna's Hypnerotomachia Poliphili",
        'author': 'Unknown',
        'doc_type': 'SCHOLARSHIP',
    },
    'Walking_in_the_Boboli': {
        'title': 'Walking in the Boboli Gardens in Florence',
        'author': 'Unknown',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 1998 jan vol 14 iss 1 2 Bury John': {
        'title': 'Chapter III of the Hypnerotomachia Poliphili and the Antiquarian Culture of the Quattrocento',
        'author': 'John Bury',
        'year': 1998,
        'journal': 'Word & Image 14:1-2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 1998 jan vol 14 iss 1 2 Curran Brian': {
        'title': 'The Hypnerotomachia Poliphili and Renaissance Egyptology',
        'author': 'Brian A. Curran',
        'year': 1998,
        'journal': 'Word & Image 14:1-2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 1998 jan vol 14 iss 1 2 Griggs Tamara': {
        'title': "Promoting the Past: The Hypnerotomachia Poliphili as Antiquarian Enterprise",
        'author': 'Tamara Griggs',
        'year': 1998,
        'journal': 'Word & Image 14:1-2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 1998 jan vol 14 iss 1 2 Hunt John Dixon': {
        'title': 'Experiencing Gardens in the Hypnerotomachia Poliphili',
        'author': 'John Dixon Hunt',
        'year': 1998,
        'journal': 'Word & Image 14:1-2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 1998 jan vol 14 iss 1 2 Leslie Michael': {
        'title': 'The Hypnerotomachia Poliphili and the Elizabethan Landscape Entertainment',
        'author': 'Michael Leslie',
        'year': 1998,
        'journal': 'Word & Image 14:1-2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 1998 jan vol 14 iss 1 2 Stewering Roswitha': {
        'title': 'The Relationship between Text and Woodcuts in the Hypnerotomachia Poliphili',
        'author': 'Roswitha Stewering (trans. Lorna Maher)',
        'year': 1998,
        'journal': 'Word & Image 14:1-2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 1998 jan vol 14 iss 1 2 Temple N': {
        'title': 'The Hypnerotomachia Poliphili as a Possible Model for Garden Design',
        'author': 'N. Temple',
        'year': 1998,
        'journal': 'Word & Image 14:1-2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 2015 apr 03 vol 31 iss 2 Fabiani Giannetto': {
        'title': "Not Before Either: The Hypnerotomachia Poliphili and the Villa d'Este at Tivoli",
        'author': 'Raffaella Fabiani Giannetto',
        'year': 2015,
        'journal': 'Word & Image 31:2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 2015 apr 03 vol 31 iss 2 Farrington Lynne': {
        'title': "Though I Could Lead a Quiet Life: The Hypnerotomachia Poliphili in English Translation",
        'author': 'Lynne Farrington',
        'year': 2015,
        'journal': 'Word & Image 31:2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 2015 apr 03 vol 31 iss 2 Keller William': {
        'title': 'Hypnerotomachia Joins the Party: Reading across Word and Image',
        'author': 'William B. Keller',
        'year': 2015,
        'journal': 'Word & Image 31:2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 2015 apr 03 vol 31 iss 2 Nygren Christopher': {
        'title': 'The Hypnerotomachia Poliphili and the Woodcut as Mirror',
        'author': 'Christopher J. Nygren',
        'year': 2015,
        'journal': 'Word & Image 31:2',
        'doc_type': 'SCHOLARSHIP',
    },
    'Word Image 2015 apr 03 vol 31 iss 2 Pumroy Eric': {
        'title': "Bryn Mawr College's 1499 Edition of the Hypnerotomachia Poliphili",
        'author': 'Eric L. Pumroy',
        'year': 2015,
        'journal': 'Word & Image 31:2',
        'doc_type': 'SCHOLARSHIP',
    },
}


def find_metadata(filename):
    """Match filename against known metadata."""
    for key, meta in KNOWN_METADATA.items():
        if key in filename:
            return dict(meta)
    return {}


def clean_filename(filename):
    """Create a clean slug from filename for the markdown file."""
    stem = Path(filename).stem
    # Remove common junk
    stem = re.sub(r'-20\d{5}T\d+Z.*', '', stem)
    stem = re.sub(r'\s*\(\d+\)\s*', '', stem)
    # Replace spaces and special chars
    slug = re.sub(r'[^\w]+', '_', stem)
    slug = re.sub(r'_+', '_', slug).strip('_')
    # Truncate
    if len(slug) > 80:
        slug = slug[:80].rstrip('_')
    return slug


def extract_pdf_text(pdf_path):
    """Extract text from PDF, return list of (page_num, text) tuples."""
    doc = fitz.open(str(pdf_path))
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            pages.append((i + 1, text))
    doc.close()
    return pages


def pages_to_markdown(pages):
    """Convert extracted pages to a single markdown string."""
    parts = []
    for page_num, text in pages:
        # Clean up common PDF extraction artifacts
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Remove page headers/footers (single short lines at start/end)
        lines = text.split('\n')
        if lines and len(lines[0].strip()) < 10:
            lines = lines[1:]
        text = '\n'.join(lines)
        parts.append(f"<!-- Page {page_num} -->\n\n{text}")
    return '\n\n---\n\n'.join(parts)


def write_markdown(output_path, metadata, content, page_count):
    """Write markdown file with YAML frontmatter."""
    frontmatter_lines = ['---']
    for key in ['title', 'author', 'year', 'journal', 'source', 'doc_type']:
        if key in metadata and metadata[key]:
            val = metadata[key]
            if isinstance(val, str) and ':' in val:
                val = f'"{val}"'
            elif isinstance(val, str):
                val = f'"{val}"'
            frontmatter_lines.append(f'{key}: {val}')
    frontmatter_lines.append(f'page_count: {page_count}')
    frontmatter_lines.append('---')
    frontmatter = '\n'.join(frontmatter_lines)

    title = metadata.get('title', 'Untitled')
    header = f"# {title}\n\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"{frontmatter}\n\n{header}{content}")


def main():
    extensions = {'.pdf'}
    pdf_files = sorted([f for f in BASE_DIR.iterdir()
                       if f.suffix.lower() in extensions and f.is_file()])

    print(f"Found {len(pdf_files)} PDFs to convert")

    success = 0
    empty = 0
    errors = 0

    for pdf_path in pdf_files:
        slug = clean_filename(pdf_path.name)
        output_path = MD_DIR / f"{slug}.md"

        try:
            pages = extract_pdf_text(pdf_path)
            if not pages:
                print(f"  EMPTY: {pdf_path.name}")
                empty += 1
                continue

            metadata = find_metadata(pdf_path.name)
            metadata['source'] = pdf_path.name

            content = pages_to_markdown(pages)
            write_markdown(output_path, metadata, content, len(pages))

            word_count = len(content.split())
            print(f"  OK: {slug}.md ({len(pages)} pages, {word_count} words)")
            success += 1

        except Exception as e:
            print(f"  ERROR: {pdf_path.name}: {e}")
            errors += 1

    print(f"\nResults: {success} converted, {empty} empty, {errors} errors")


if __name__ == "__main__":
    main()
