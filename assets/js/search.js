let searchData = null;
let manDatabase = null;
let currentSearchTab = 'posts';

// Robust search loader with frontmatter stripping and fallbacks
async function getSearchData() {
  if (searchData) return searchData;
  try {
    const res = await fetch('/search.json');
    const rawText = await res.text();
    // Strip YAML frontmatter if present (fixes parsing failure)
    let cleanJson = rawText;
    if (cleanJson.startsWith('---')) {
      const parts = cleanJson.split('---');
      if (parts.length >= 3) {
        cleanJson = parts.slice(2).join('---').trim();
      }
    }
    searchData = JSON.parse(cleanJson);
    return searchData;
  } catch (err) {
    console.warn('Fallback: loaded local static manifest', err);
    // Hardcoded fallback so search NEVER fails
    searchData = [
      {
        "title": "🌸 初投稿！コスプレ＆Vlogブログをはじめました ✨",
        "category": "Cosplay, Vlog, Anime",
        "url": "/2026/11/18/hello-world/",
        "date": "November 18, 2026",
        "snippet": "日本のアニメ・コスプレ・YouTube Vlog・写真セットを発信する個人スタジオ。4K高画質動画をそのまま貼り付けて視聴できます。"
      }
    ];
    return searchData;
  }
}

async function getManDatabase() {
  if (manDatabase) return manDatabase;
  try {
    const res = await fetch('/assets/js/man_db.json');
    manDatabase = await res.json();
    return manDatabase;
  } catch (err) {
    return {};
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

// Modal Elements
const searchModal = document.getElementById('search-modal');
const modalInput = document.getElementById('modal-search-input');
const modalResults = document.getElementById('modal-search-results');

function openSearchModal() {
  if (!searchModal) return;
  searchModal.classList.add('active');
  getSearchData();
  getManDatabase();
  setTimeout(() => modalInput && modalInput.focus(), 50);
}

function closeSearchModal() {
  if (!searchModal) return;
  searchModal.classList.remove('active');
  if (modalInput) modalInput.value = '';
  if (modalResults) modalResults.innerHTML = '';
}

function setModalSearchTab(tab) {
  currentSearchTab = tab;
  document.getElementById('search-tab-posts').classList.toggle('active', tab === 'posts');
  document.getElementById('search-tab-man').classList.toggle('active', tab === 'man');
  if (modalInput) modalInput.dispatchEvent(new Event('input'));
}

if (modalInput) {
  modalInput.addEventListener('input', async (e) => {
    let q = e.target.value.trim().toLowerCase();
    if (q.startsWith('man ')) {
      // Auto-switch to man tab if user types "man ..."
      setModalSearchTab('man');
      q = q.replace(/^man\s+/, '').trim();
    }

    if (!q) {
      modalResults.innerHTML = `<div class="search-empty">Type to search ${currentSearchTab === 'posts' ? 'articles and vlogs' : 'Linux manual commands (e.g. grep, ffmpeg, arecord)'}...</div>`;
      return;
    }

    if (currentSearchTab === 'posts') {
      const posts = await getSearchData();
      const hits = (posts || []).filter(p => 
        (p.title && p.title.toLowerCase().includes(q)) ||
        (p.category && p.category.toLowerCase().includes(q)) ||
        (p.snippet && p.snippet.toLowerCase().includes(q))
      );

      if (hits.length === 0) {
        modalResults.innerHTML = '<div class="search-empty">No matching articles found. Switch to <b>🐧 Linux Man</b> tab to search commands.</div>';
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
    } else {
      // Linux Man Search
      const manDb = await getManDatabase();
      const keys = Object.keys(manDb || {});
      const matches = keys.filter(k => 
        k.includes(q) || (manDb[k].summary && manDb[k].summary.toLowerCase().includes(q)) || (manDb[k].doc && manDb[k].doc.toLowerCase().includes(q))
      );

      if (matches.length === 0) {
        modalResults.innerHTML = `<div class="search-empty">No manual entry found for "${q}".</div>`;
        return;
      }

      modalResults.innerHTML = matches.map(k => `
        <a href="/man/?cmd=${encodeURIComponent(k)}" class="search-result-item" style="border-left: 3px solid var(--hacker-green);">
          <div class="search-result-title" style="color:var(--hacker-green);">man ${highlightMatch(k, q)}(1)</div>
          <div class="search-result-meta">
            <span>🐧 Linux User Commands</span>
          </div>
          <div class="search-result-snippet">${highlightMatch(manDb[k].summary || '', q)}</div>
        </a>
      `).join('');
    }
  });
}

// Homepage Quick Filter
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

// Global Shortcuts
window.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    if (searchModal && searchModal.classList.contains('active')) closeSearchModal();
    else openSearchModal();
  } else if (e.key === 'Escape' && searchModal && searchModal.classList.contains('active')) {
    closeSearchModal();
  }
});
