let searchData = null;

async function getSearchData() {
  if (searchData) return searchData;
  try {
    const res = await fetch('/search.json');
    searchData = await res.json();
    return searchData;
  } catch (err) {
    console.error('Error loading search index:', err);
    return [];
  }
}

function escapeHtml(str) {
  return (str || '').replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[m]);
}

function highlightMatch(text, query) {
  if (!query) return escapeHtml(text);
  const regex = new RegExp(`(${query.replace(/[-[\\]{}()*+?.,\\\\^$|#\\s]/g, '\\\\$&')})`, 'gi');
  return escapeHtml(text).replace(regex, '<mark class="search-highlight">$1</mark>');
}

// Global Search Modal Logic
const searchModal = document.getElementById('search-modal');
const modalInput = document.getElementById('modal-search-input');
const modalResults = document.getElementById('modal-search-results');

function openSearchModal() {
  if (!searchModal) return;
  searchModal.classList.add('active');
  getSearchData();
  setTimeout(() => modalInput && modalInput.focus(), 50);
}

function closeSearchModal() {
  if (!searchModal) return;
  searchModal.classList.remove('active');
  if (modalInput) modalInput.value = '';
  if (modalResults) modalResults.innerHTML = '';
}

if (modalInput) {
  modalInput.addEventListener('input', async (e) => {
    const q = e.target.value.trim().toLowerCase();
    if (!q) {
      modalResults.innerHTML = '<div class="search-empty">Type to search articles, vlogs, and notes...</div>';
      return;
    }
    const posts = await getSearchData();
    const hits = posts.filter(p => 
      (p.title && p.title.toLowerCase().includes(q)) ||
      (p.category && p.category.toLowerCase().includes(q)) ||
      (p.snippet && p.snippet.toLowerCase().includes(q))
    );

    if (hits.length === 0) {
      modalResults.innerHTML = '<div class="search-empty">No matching articles found.</div>';
      return;
    }

    modalResults.innerHTML = hits.map(p => `
      <a href="${p.url}" class="search-result-item">
        <div class="search-result-title">${highlightMatch(p.title, q)}</div>
        <div class="search-result-meta">
          <span>📅 ${p.date}</span>
          ${p.category ? `<span>🏷️ ${highlightMatch(p.category, q)}</span>` : ''}
        </div>
        <div class="search-result-snippet">${highlightMatch(p.snippet, q)}</div>
      </a>
    `).join('');
  });
}

// Homepage Inline Search
const homeSearchInput = document.getElementById('home-search-input');
if (homeSearchInput) {
  homeSearchInput.addEventListener('input', (e) => {
    const q = e.target.value.trim().toLowerCase();
    const cards = document.querySelectorAll('.posts-grid .post-card');
    let visibleCount = 0;

    cards.forEach(card => {
      const text = card.textContent.toLowerCase();
      if (!q || text.includes(q)) {
        card.style.display = 'flex';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    const noMatchesEl = document.getElementById('no-search-results');
    if (noMatchesEl) {
      noMatchesEl.style.display = visibleCount === 0 ? 'block' : 'none';
    }
  });
}

// Global Keyboard Shortcut: Ctrl+K / Cmd+K or / to open search
window.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    if (searchModal && searchModal.classList.contains('active')) {
      closeSearchModal();
    } else {
      openSearchModal();
    }
  } else if (e.key === 'Escape' && searchModal && searchModal.classList.contains('active')) {
    closeSearchModal();
  }
});
