// Mobile Reading & Post Content Enhancer
document.addEventListener('DOMContentLoaded', () => {
  const content = document.querySelector('.article-content');
  if (!content) return;

  // 1. Reading Progress Bar
  const progBar = document.createElement('div');
  progBar.id = 'reading-progress-bar';
  document.body.appendChild(progBar);

  window.addEventListener('scroll', () => {
    const total = document.documentElement.scrollHeight - window.innerHeight;
    const progress = total > 0 ? (window.scrollY / total) * 100 : 0;
    progBar.style.width = `${progress}%`;
  });

  // 2. Enhance Tables for Mobile (Scrollable wrapper + badge)
  const tables = content.querySelectorAll('table');
  tables.forEach(table => {
    const wrapper = document.createElement('div');
    wrapper.className = 'table-scroll-wrap';
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
  });

  // 3. Enhance Code Blocks (Copy Button + Language Badge)
  const pres = content.querySelectorAll('pre');
  pres.forEach(pre => {
    const code = pre.querySelector('code');
    if (!code) return;

    // Detect language from class (e.g. language-bash)
    let lang = 'CODE';
    code.classList.forEach(cls => {
      if (cls.startsWith('language-')) {
        lang = cls.replace('language-', '').toUpperCase();
      }
    });

    const header = document.createElement('div');
    header.className = 'code-header-bar';
    header.innerHTML = `
      <span class="code-lang-tag">${lang}</span>
      <button class="code-copy-btn" title="Copy code">📋 Copy</button>
    `;

    pre.parentNode.insertBefore(header, pre);
    header.appendChild(pre); // Wrap into container

    const copyBtn = header.querySelector('.code-copy-btn');
    copyBtn.addEventListener('click', () => {
      const textToCopy = code.innerText;
      navigator.clipboard.writeText(textToCopy).then(() => {
        copyBtn.textContent = '✅ Copied!';
        copyBtn.classList.add('copied');
        setTimeout(() => {
          copyBtn.textContent = '📋 Copy';
          copyBtn.classList.remove('copied');
        }, 2000);
      });
    });
  });

  // 4. Style GitHub Alert Callouts (e.g. > [!NOTE], > [!TIP], > [!WARNING])
  const blockquotes = content.querySelectorAll('blockquote');
  blockquotes.forEach(bq => {
    const text = bq.innerHTML;
    if (text.includes('[!NOTE]')) {
      bq.className = 'callout-box callout-note';
      bq.innerHTML = text.replace(/\[!NOTE\]/g, '<b>💡 NOTE</b>');
    } else if (text.includes('[!TIP]')) {
      bq.className = 'callout-box callout-tip';
      bq.innerHTML = text.replace(/\[!TIP\]/g, '<b>⚡ PRO TIP</b>');
    } else if (text.includes('[!WARNING]')) {
      bq.className = 'callout-box callout-warning';
      bq.innerHTML = text.replace(/\[!WARNING\]/g, '<b>⚠️ WARNING</b>');
    } else if (text.includes('[!IMPORTANT]')) {
      bq.className = 'callout-box callout-important';
      bq.innerHTML = text.replace(/\[!IMPORTANT\]/g, '<b>📌 IMPORTANT</b>');
    }
  });

  // 5. Back-to-Top Floating Button on Mobile
  const topBtn = document.createElement('button');
  topBtn.id = 'back-to-top-btn';
  topBtn.innerHTML = '▲';
  topBtn.title = 'Back to top';
  document.body.appendChild(topBtn);

  window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
      topBtn.classList.add('visible');
    } else {
      topBtn.classList.remove('visible');
    }
  });

  topBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
});
