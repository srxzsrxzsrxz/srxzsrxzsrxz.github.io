// Matrix Digital Rain & Cyber CLI Terminal with Linux man Integration
(function() {
  // 1. Matrix Digital Rain Canvas
  const canvas = document.createElement('canvas');
  canvas.id = 'matrix-canvas';
  document.body.appendChild(canvas);
  const ctx = canvas.getContext('2d');

  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const chars = '0123456789ABCDEFｦｱｳｴｵｶｷｹｺｻｼｽｾｿﾀﾂﾃﾅﾆﾇﾈﾊﾋﾎﾏﾐﾑﾒﾓﾔﾕﾗﾘﾜ'.split('');
  const fontSize = 14;
  const columns = Math.floor(width / fontSize);
  const drops = Array(columns).fill(1);

  let isMatrixRunning = true;
  let matrixTimer = null;

  function drawMatrix() {
    ctx.fillStyle = 'rgba(8, 9, 15, 0.08)';
    ctx.fillRect(0, 0, width, height);

    ctx.fillStyle = '#00ff66';
    ctx.font = `${fontSize}px monospace`;

    for (let i = 0; i < drops.length; i++) {
      const text = chars[Math.floor(Math.random() * chars.length)];
      ctx.fillText(text, i * fontSize, drops[i] * fontSize);

      if (drops[i] * fontSize > height && Math.random() > 0.975) {
        drops[i] = 0;
      }
      drops[i]++;
    }
  }

  function startMatrix() {
    if (!matrixTimer) {
      matrixTimer = setInterval(drawMatrix, 40);
    }
  }

  function stopMatrix() {
    if (matrixTimer) {
      clearInterval(matrixTimer);
      matrixTimer = null;
      ctx.clearRect(0, 0, width, height);
    }
  }

  startMatrix();

  window.toggleMatrix = function() {
    isMatrixRunning = !isMatrixRunning;
    if (isMatrixRunning) startMatrix();
    else stopMatrix();
    return isMatrixRunning;
  };

  // 2. Interactive Cyber CLI Terminal
  const termModal = document.createElement('div');
  termModal.id = 'hacker-terminal-modal';
  termModal.innerHTML = `
    <div class="term-header">
      <span>● LINUX-CLI // MAN-DB ENABLED // srxz-node</span>
      <span style="cursor:pointer;" onclick="toggleTerminal()">[ESC / CLOSE]</span>
    </div>
    <div class="term-log" id="term-log">
      <div>[LINUX] System initialized. Linux manual database loaded.</div>
      <div>[HINT] Try typing: <span style="color:#00ff66;">'man arecord'</span>, <span style="color:#00ff66;">'man ffmpeg'</span>, <span style="color:#00ff66;">'man yt-dlp'</span>, <span style="color:#00ff66;">'man grep'</span></div>
      <div>[HINT] Type <span style="color:#00ff66;">'help'</span> for all commands. Press <kbd>~</kbd> or <kbd>Esc</kbd> to toggle.</div>
      <br>
    </div>
    <div class="term-input-row">
      <span class="term-prompt">user@fedora:~$</span>
      <input type="text" id="term-cli-input" autocomplete="off" spellcheck="false">
    </div>
  `;
  document.body.appendChild(termModal);

  const termInput = document.getElementById('term-cli-input');
  const termLog = document.getElementById('term-log');
  let cachedManDb = null;

  async function fetchManDb() {
    if (cachedManDb) return cachedManDb;
    try {
      const res = await fetch('/assets/js/man_db.json');
      cachedManDb = await res.json();
      return cachedManDb;
    } catch (e) {
      return {};
    }
  }

  window.toggleTerminal = function() {
    termModal.classList.toggle('active');
    if (termModal.classList.contains('active')) {
      setTimeout(() => termInput.focus(), 50);
    }
  };

  function appendLog(line, color = '#f0fdf4') {
    const d = document.createElement('div');
    d.style.color = color;
    d.innerHTML = line;
    termLog.appendChild(d);
    termLog.scrollTop = termLog.scrollHeight;
  }

  termInput.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter') {
      const raw = termInput.value.trim();
      termInput.value = '';
      if (!raw) return;

      appendLog(`<span style="color:#00ff66;">user@fedora:~$</span> ${raw}`);
      const args = raw.split(' ');
      const cmd = args[0].toLowerCase();

      switch (cmd) {
        case 'help':
          appendLog(`Linux & Blog CLI commands:<br>
  - <b style="color:#00ff66;">man &lt;command&gt;</b> : View Linux manual (e.g. man arecord, man ffmpeg, man yt-dlp, man grep)<br>
  - <b style="color:#00ff66;">man -k &lt;keyword&gt;</b> : Search manual pages by keyword (apropos)<br>
  - <b style="color:#00ff66;">posts</b> / <b style="color:#00ff66;">ls</b> : List blog articles and vlogs<br>
  - <b style="color:#00ff66;">about</b> : Display creator profile<br>
  - <b style="color:#00ff66;">matrix</b> : Toggle digital rain<br>
  - <b style="color:#00ff66;">clear</b> : Clear terminal<br>
  - <b style="color:#00ff66;">exit</b> : Close terminal`);
          break;

        case 'man':
          if (args.length < 2) {
            appendLog("What manual page do you want? Example: <span style='color:#00ff66;'>man arecord</span>", "#ffbd2e");
            break;
          }
          const manDb = await fetchManDb();
          if (args[1] === '-k' || args[1] === '--apropos') {
            const query = (args[2] || '').toLowerCase();
            if (!query) {
              appendLog("Usage: man -k <keyword>", "#ffbd2e");
              break;
            }
            const hits = Object.keys(manDb).filter(k => k.includes(query) || (manDb[k].summary && manDb[k].summary.toLowerCase().includes(query)));
            if (hits.length === 0) {
              appendLog(`${query}: nothing appropriate.`, "#ef4444");
            } else {
              let out = `<b>Matches for "${query}":</b><br>`;
              hits.forEach(k => {
                out += `<a href="/man/?cmd=${k}" style="color:#00ff66; font-weight:700;">${k} (1)</a> - ${manDb[k].summary || 'command'}<br>`;
              });
              appendLog(out);
            }
          } else {
            const target = args[1].toLowerCase();
            const entry = manDb[target];
            if (!entry) {
              appendLog(`No manual entry for ${target}. Try <a href="/man/" style="color:#00f0ff;">viewing full Linux man database</a>.`, "#ef4444");
            } else {
              let docHtml = entry.doc
                .replace(/^[A-Z][A-Z\s]{2,}$/gm, m => `<br><span style="color:#00ff66; font-weight:bold;">${m}</span>`)
                .replace(/(^\s+-[a-zA-Z0-9_\-]+(?:,\s+--[a-zA-Z0-9_\-]+)?)/gm, m => `<span style="color:#fcee0a; font-weight:bold;">${m}</span>`);
              appendLog(`<div style="background:#020306; padding:12px; border:1px solid #22c55e44; border-radius:6px; margin:6px 0; font-size:0.88rem; line-height:1.5;">${docHtml}</div>`);
            }
          }
          break;

        case 'ls':
        case 'posts':
          try {
            const res = await fetch('/assets/js/man_db.json');
            appendLog(`Blog: <a href="/" style="color:#00f0ff;">/</a> | Linux Man: <a href="/man/" style="color:#00ff66;">/man/</a><br>Type <span style="color:#00ff66;">'man arecord'</span> or <span style="color:#00ff66;">'man ffmpeg'</span> to view docs.`);
          } catch(err) {
            appendLog("Error retrieving manifest.", "#ef4444");
          }
          break;

        case 'about':
          appendLog(`[SYSTEM] srxz.io // Linux, Cosplay, Vlogs & Cyberpunk Tools.<br>Check <a href="/man/" style="color:#00ff66;">/man/</a> for the Linux Manual Docs.`);
          break;

        case 'matrix':
          const on = window.toggleMatrix();
          appendLog(`[SYSTEM] Matrix Rain: ${on ? 'ENABLED' : 'DISABLED'}`);
          break;

        case 'clear':
          termLog.innerHTML = '';
          break;

        case 'exit':
          window.toggleTerminal();
          break;

        default:
          appendLog(`bash: ${cmd}: command not found. Type 'help' for command list.`, '#f87171');
      }
    }
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === '`' || e.key === '~') {
      if (!['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName) || document.activeElement === termInput) {
        e.preventDefault();
        window.toggleTerminal();
      }
    } else if (e.key === 'Escape' && termModal.classList.contains('active')) {
      window.toggleTerminal();
    }
  });
})();
