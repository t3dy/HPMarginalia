// Marginalia Showcase — script.js

let allEntries = [];
let filteredEntries = [];
let currentIndex = 0;

async function loadData() {
    const resp = await fetch('data.json');
    const data = await resp.json();
    allEntries = data.entries;
    filteredEntries = [...allEntries];

    // Stats
    document.getElementById('stat-refs').textContent = data.stats.total_references;
    document.getElementById('stat-sigs').textContent = data.stats.unique_signatures;
    document.getElementById('stat-matches').textContent = data.stats.high_confidence_matches;

    renderGallery(allEntries);
    setupFilters();
    setupLightbox();
}

function imagePath(entry) {
    // Images are relative to the project root
    return entry.image_path;
}

function renderGallery(entries) {
    const gallery = document.getElementById('gallery');
    gallery.innerHTML = '';

    entries.forEach((entry, index) => {
        const card = document.createElement('div');
        card.className = 'card';
        card.dataset.index = index;

        const isBL = entry.manuscript === 'C.60.o.12';
        const badgeClass = isBL ? 'badge-bl' : 'badge-siena';
        const badgeText = isBL ? 'British Library' : 'Siena';

        card.innerHTML = `
            <img class="card-image"
                 src="${imagePath(entry)}"
                 alt="Folio ${entry.signature}"
                 loading="lazy">
            <div class="card-body">
                <div class="card-sig">${entry.signature}</div>
                <div class="card-ms">
                    <span class="badge ${badgeClass}">${badgeText}</span>
                    ${entry.manuscript} &mdash; folio ${entry.folio_number || '?'}${entry.side || ''}
                </div>
                ${entry.marginal_text
                    ? `<div class="card-marginal">&ldquo;${escapeHtml(entry.marginal_text)}&rdquo;</div>`
                    : ''}
            </div>
        `;

        card.addEventListener('click', () => openLightbox(index));
        gallery.appendChild(card);
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function setupFilters() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.dataset.filter;
            if (filter === 'all') {
                filteredEntries = [...allEntries];
            } else {
                filteredEntries = allEntries.filter(e => e.manuscript === filter);
            }
            renderGallery(filteredEntries);
        });
    });
}

// ===== Lightbox =====

function openLightbox(index) {
    currentIndex = index;
    const lightbox = document.getElementById('lightbox');
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
    showEntry(index);
}

function closeLightbox() {
    document.getElementById('lightbox').classList.remove('active');
    document.body.style.overflow = '';
}

function showEntry(index) {
    const entry = filteredEntries[index];
    if (!entry) return;

    document.getElementById('lightbox-img').src = imagePath(entry);
    document.getElementById('lightbox-img').alt = `Folio ${entry.signature}`;
    document.getElementById('lightbox-sig').textContent = `Signature ${entry.signature}`;

    const isBL = entry.manuscript === 'C.60.o.12';
    document.getElementById('lightbox-ms').textContent =
        `${isBL ? 'British Library' : 'Biblioteca degli Intronati, Siena'} — ${entry.manuscript}, folio ${entry.folio_number || '?'}${entry.side || ''}`;

    const marginalEl = document.getElementById('lightbox-marginal');
    if (entry.marginal_text) {
        marginalEl.textContent = `"${entry.marginal_text}"`;
        marginalEl.style.display = 'block';
    } else {
        marginalEl.style.display = 'none';
    }

    const contextEl = document.getElementById('lightbox-context');
    if (entry.context) {
        // Truncate long context for display
        const ctx = entry.context.length > 600
            ? entry.context.substring(0, 600) + '...'
            : entry.context;
        contextEl.textContent = ctx;
        contextEl.style.display = 'block';
    } else {
        contextEl.style.display = 'none';
    }

    document.getElementById('lightbox-page').textContent =
        `Russell, PhD Thesis, p. ${entry.thesis_page} (Chapter ${entry.chapter})`;
}

function setupLightbox() {
    document.getElementById('lightbox-close').addEventListener('click', closeLightbox);
    document.getElementById('lightbox').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) closeLightbox();
    });

    document.getElementById('lightbox-prev').addEventListener('click', (e) => {
        e.stopPropagation();
        if (currentIndex > 0) {
            currentIndex--;
            showEntry(currentIndex);
        }
    });

    document.getElementById('lightbox-next').addEventListener('click', (e) => {
        e.stopPropagation();
        if (currentIndex < filteredEntries.length - 1) {
            currentIndex++;
            showEntry(currentIndex);
        }
    });

    document.addEventListener('keydown', (e) => {
        if (!document.getElementById('lightbox').classList.contains('active')) return;
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowLeft' && currentIndex > 0) {
            currentIndex--;
            showEntry(currentIndex);
        }
        if (e.key === 'ArrowRight' && currentIndex < filteredEntries.length - 1) {
            currentIndex++;
            showEntry(currentIndex);
        }
    });
}

// Init
loadData();
