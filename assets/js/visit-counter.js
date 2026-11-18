// Live Web Visit Counter (Busuanzi + API Fallback)
(function() {
  function updateElementText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  }

  function updateClassText(cls, val) {
    document.querySelectorAll('.' + cls).forEach(el => el.textContent = val);
  }

  // Fallback Counter using CounterAPI if Busuanzi is unreachable
  async function runFallbackCounter() {
    try {
      const namespace = 'srxz_github_io_blog';
      // Increment site counter
      const res = await fetch(`https://api.counterapi.dev/v1/${namespace}/visits/up`);
      const data = await res.json();
      if (data && data.count) {
        const countStr = Number(data.count).toLocaleString();
        updateElementText('busuanzi_value_site_pv', countStr);
        updateClassText('site-pv-val', countStr);
        // Estimate UV as ~45% of PV for fallback
        const uv = Math.max(1, Math.round(data.count * 0.45));
        updateElementText('busuanzi_value_site_uv', uv.toLocaleString());
      }
    } catch (e) {
      // Local storage fallback for offline / development
      let localHits = Number(localStorage.getItem('local_site_pv') || '128');
      localHits += 1;
      localStorage.setItem('local_site_pv', localHits);
      updateElementText('busuanzi_value_site_pv', localHits.toLocaleString());
      updateClassText('site-pv-val', localHits.toLocaleString());
      updateElementText('busuanzi_value_site_uv', Math.round(localHits * 0.5).toLocaleString());
    }
  }

  // Load Busuanzi asynchronously
  const script = document.createElement('script');
  script.src = '//busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js';
  script.async = true;
  document.head.appendChild(script);

  // Set timeout: if Busuanzi does not populate within 2.5s, trigger fallback
  setTimeout(() => {
    const pvEl = document.getElementById('busuanzi_value_site_pv');
    if (pvEl && (pvEl.textContent === '...' || pvEl.textContent === '')) {
      runFallbackCounter();
    }
  }, 2500);
})();
