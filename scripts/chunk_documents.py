"""Split markdown files into semantic chunks."""

import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MD_DIR = BASE_DIR / "md"
CHUNKS_DIR = BASE_DIR / "chunks"

TARGET_CHUNK_SIZE = 1500  # words
MIN_CHUNK_SIZE = 200  # words


def parse_frontmatter(text):
    """Extract YAML frontmatter and body from markdown."""
    if text.startswith('---'):
        end = text.find('---', 3)
        if end > 0:
            frontmatter = text[3:end].strip()
            body = text[end + 3:].strip()
            # Parse simple YAML
            meta = {}
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, _, val = line.partition(':')
                    val = val.strip().strip('"').strip("'")
                    meta[key.strip()] = val
            return meta, body
    return {}, text


def find_section_breaks(text):
    """Find natural section breaks in the text."""
    # Look for markdown headings
    heading_pattern = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
    # Look for page markers
    page_pattern = re.compile(r'^<!-- Page (\d+) -->$', re.MULTILINE)
    # Look for horizontal rules
    rule_pattern = re.compile(r'^---+$', re.MULTILINE)

    breaks = []
    for m in heading_pattern.finditer(text):
        level = len(m.group(1))
        breaks.append({
            'pos': m.start(),
            'type': 'heading',
            'level': level,
            'title': m.group(2).strip(),
        })

    for m in page_pattern.finditer(text):
        breaks.append({
            'pos': m.start(),
            'type': 'page',
            'level': 99,
            'title': f'Page {m.group(1)}',
        })

    for m in rule_pattern.finditer(text):
        breaks.append({
            'pos': m.start(),
            'type': 'rule',
            'level': 99,
            'title': '',
        })

    breaks.sort(key=lambda b: b['pos'])
    return breaks


def chunk_by_headings(text, meta):
    """Split text into chunks based on headings, page markers, and size."""
    breaks = find_section_breaks(text)
    total_words = len(text.split())

    # If we have good heading structure, split by headings
    heading_breaks = [b for b in breaks if b['type'] == 'heading']

    if len(heading_breaks) >= 3:
        chunks = []
        for i, brk in enumerate(heading_breaks):
            start = brk['pos']
            end = heading_breaks[i + 1]['pos'] if i + 1 < len(heading_breaks) else len(text)
            chunk_text = text[start:end].strip()
            word_count = len(chunk_text.split())

            if word_count >= MIN_CHUNK_SIZE:
                chunks.append({
                    'text': chunk_text,
                    'title': brk['title'],
                    'word_count': word_count,
                })
            elif chunks:
                # Merge small chunks with previous
                chunks[-1]['text'] += '\n\n' + chunk_text
                chunks[-1]['word_count'] += word_count

        # Handle text before first heading
        pre_text = text[:heading_breaks[0]['pos']].strip()
        if pre_text and len(pre_text.split()) >= MIN_CHUNK_SIZE:
            chunks.insert(0, {
                'text': pre_text,
                'title': 'Introduction',
                'word_count': len(pre_text.split()),
            })

        # If chunks are still too big (>3000 words), sub-chunk them
        final_chunks = []
        for chunk in chunks:
            if chunk['word_count'] > 3000:
                sub = chunk_by_size(chunk['text'], base_title=chunk['title'])
                final_chunks.extend(sub)
            else:
                final_chunks.append(chunk)
        return final_chunks

    # For large documents without headings, split by page markers
    page_breaks = [b for b in breaks if b['type'] == 'page']
    if page_breaks and total_words > TARGET_CHUNK_SIZE * 2:
        return chunk_by_pages(text, page_breaks)

    # Small documents: split by size if needed
    if total_words > TARGET_CHUNK_SIZE * 2:
        return chunk_by_size(text)

    # Small enough to be one chunk
    if total_words >= MIN_CHUNK_SIZE:
        return [{'text': text, 'title': meta.get('title', 'Full Text'),
                 'word_count': total_words}]
    return []


def chunk_by_pages(text, page_breaks):
    """Group page markers into chunks of ~TARGET_CHUNK_SIZE words."""
    chunks = []
    current_text = []
    current_words = 0
    current_start_page = None

    for i, brk in enumerate(page_breaks):
        start = brk['pos']
        end = page_breaks[i + 1]['pos'] if i + 1 < len(page_breaks) else len(text)
        page_text = text[start:end].strip()
        page_words = len(page_text.split())
        page_num = brk['title'].replace('Page ', '')

        if current_start_page is None:
            current_start_page = page_num

        if current_words + page_words > TARGET_CHUNK_SIZE and current_words >= MIN_CHUNK_SIZE:
            chunks.append({
                'text': '\n\n'.join(current_text),
                'title': f'Pages {current_start_page}-{page_num}',
                'word_count': current_words,
            })
            current_text = [page_text]
            current_words = page_words
            current_start_page = page_num
        else:
            current_text.append(page_text)
            current_words += page_words

    if current_text and current_words >= MIN_CHUNK_SIZE:
        chunks.append({
            'text': '\n\n'.join(current_text),
            'title': f'Pages {current_start_page}-end',
            'word_count': current_words,
        })

    return chunks


def chunk_by_size(text, base_title=None):
    """Split text into roughly equal chunks by word count."""
    paragraphs = re.split(r'\n\n+', text)
    chunks = []
    current_text = []
    current_words = 0

    for para in paragraphs:
        para_words = len(para.split())
        if current_words + para_words > TARGET_CHUNK_SIZE and current_words >= MIN_CHUNK_SIZE:
            n = len(chunks) + 1
            title = f'{base_title} (part {n})' if base_title else f'Section {n}'
            chunks.append({
                'text': '\n\n'.join(current_text),
                'title': title,
                'word_count': current_words,
            })
            current_text = [para]
            current_words = para_words
        else:
            current_text.append(para)
            current_words += para_words

    if current_text:
        n = len(chunks) + 1
        title = f'{base_title} (part {n})' if base_title and len(chunks) > 0 else (base_title or f'Section {n}')
        chunks.append({
            'text': '\n\n'.join(current_text),
            'title': title,
            'word_count': current_words,
        })

    return chunks


def slugify(title):
    """Create a filename-safe slug from a title."""
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s]+', '_', slug).strip('_')
    return slug[:50] if slug else 'untitled'


def main():
    md_files = sorted(MD_DIR.glob('*.md'))
    print(f"Found {len(md_files)} markdown files to chunk")

    total_chunks = 0

    for md_path in md_files:
        doc_slug = md_path.stem
        doc_chunks_dir = CHUNKS_DIR / doc_slug
        doc_chunks_dir.mkdir(parents=True, exist_ok=True)

        text = md_path.read_text(encoding='utf-8')
        meta, body = parse_frontmatter(text)

        chunks = chunk_by_headings(body, meta)

        # Merge very small trailing chunks
        if len(chunks) > 1 and chunks[-1]['word_count'] < MIN_CHUNK_SIZE:
            chunks[-2]['text'] += '\n\n' + chunks[-1]['text']
            chunks[-2]['word_count'] += chunks[-1]['word_count']
            chunks.pop()

        for i, chunk in enumerate(chunks):
            chunk_slug = slugify(chunk['title'])
            chunk_filename = f"chunk_{i + 1:03d}_{chunk_slug}.md"
            chunk_path = doc_chunks_dir / chunk_filename

            frontmatter = f"""---
source: "md/{md_path.name}"
chunk: {i + 1}
total_chunks: {len(chunks)}
section: "{chunk['title']}"
word_count: {chunk['word_count']}
---

"""
            chunk_path.write_text(frontmatter + chunk['text'], encoding='utf-8')

        print(f"  {doc_slug}: {len(chunks)} chunks")
        total_chunks += len(chunks)

    print(f"\nTotal: {total_chunks} chunks from {len(md_files)} documents")


if __name__ == "__main__":
    main()
