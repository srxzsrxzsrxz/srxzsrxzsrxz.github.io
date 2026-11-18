// Matrix Digital Rain & Cyber CLI Terminal
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
      <span>● CYBER-CLI v2.0 // CONNECTED TO srxz-node</span>
      <span style="cursor:pointer;" onclick="toggleTerminal()">[ESC / CLOSE]</span>
    </div>
    <div class="term-log" id="term-log">
      <div>[SYSTEM] Welcome to srxz's Cyber Terminal.</div>
      <div>[SYSTEM] Type <span style="color:#00ff66;">'help'</span> for list of commands. Press <kbd>~</kbd> or <kbd>Esc</kbd> to toggle.</div>
      <br>
    </div>
    <div class="term-input-row">
      <span class="term-prompt">guest@srxz-net:~$</span>
      <input type="text" id="term-cli-input" autocomplete="off" spellcheck="false">
    </div>
  `;
  document.body.appendChild(termModal);

  const termInput = document.getElementById('term-cli-input');
  const termLog = document.getElementById('term-log');

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

      appendLog(`<span style="color:#00ff66;">guest@srxz-net:~$</span> ${raw}`);
      const args = raw.split(' ');
      const cmd = args[0].toLowerCase();

      switch (cmd) {
        case 'help':
          appendLog(`Available commands:<br>
  - <b style="color:#00ff66;">posts</b> / <b style="color:#00ff66;">ls</b> : List all published posts & vlogs<br>
  - <b style="color:#00ff66;">about</b> : Display author & cyber-profile<br>
  - <b style="color:#00ff66;">matrix</b> : Toggle background Matrix rain<br>
  - <b style="color:#00ff66;">date</b> : Show current system time<br>
  - <b style="color:#00ff66;">clear</b> : Clear terminal screen<br>
  - <b style="color:#00ff66;">exit</b> : Close terminal`);
          break;

        case 'ls':
        case 'posts':
          try {
            const res = await fetch('/search.json');
            const data = await res.json();
            let html = "Available blog entries:<br>";
            data.forEach((p, idx) => {
              html += `[${idx+1}] <a href="${p.url}" style="color:#00f0ff;">${p.title}</a> (${p.date})<br>`;
            });
            appendLog(html);
          } catch(err) {
            appendLog("Error retrieving post manifest.", "#ef4444");
          }
          break;

        case 'about':
          appendLog(`[IDENT] srxz // ACG Cosplayer & Tech Hacker<br>
[VLOG] YouTube 4K Vlog & Event Coverage<br>
[NODE] srxzsrxzsrxz.github.io<br>
[STATUS] ARMED & READY`);
          break;

        case 'matrix':
          const on = window.toggleMatrix();
          appendLog(`[SYSTEM] Matrix Rain: ${on ? 'ENABLED' : 'DISABLED'}`);
          break;

        case 'date':
          appendLog(new Date().toString());
          break;

        case 'clear':
          termLog.innerHTML = '';
          break;

        case 'exit':
          window.toggleTerminal();
          break;

        default:
          appendLog(`command not found: ${cmd}. Type 'help' for available commands.`, '#f87171');
      }
    }
  });

  // Hotkey ~ / ` or Esc to toggle terminal
  window.addEventListener('keydown', (e) => {
    if (e.key === '`' || e.key === '~') {
      // If not currently typing in a real textarea or input
      if (!['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName) || document.activeElement === termInput) {
        e.preventDefault();
        window.toggleTerminal();
      }
    } else if (e.key === 'Escape' && termModal.classList.contains('active')) {
      window.toggleTerminal();
    }
  });
})();
