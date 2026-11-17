#!/usr/bin/env python3
"""
Lightweight Local Blog Editor for Jekyll / GitHub Pages
Runs a local web server with zero external dependencies (Python 3 standard library only).
"""

import http.server
import json
import os
import re
import socket
import subprocess
import sys
import urllib.parse
from datetime import datetime

PORT = 5500
BLOG_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BLOG_DIR, "_posts")

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blog Editor &middot; srxz</title>
  <!-- Marked.js for real-time markdown preview -->
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    :root {
      --bg: #0f172a;
      --sidebar-bg: #1e293b;
      --card-bg: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #6366f1;
      --accent-hover: #4f46e5;
      --success: #10b981;
      --danger: #ef4444;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      display: flex;
      height: 100vh;
      overflow: hidden;
    }
    /* Sidebar */
    #sidebar {
      width: 280px;
      background: var(--sidebar-bg);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }
    .sidebar-header {
      padding: 16px;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .sidebar-title { font-weight: 700; font-size: 1.1rem; }
    .btn {
      background: var(--accent);
      color: white;
      border: none;
      padding: 8px 14px;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
      font-size: 0.9rem;
      transition: 0.2s;
    }
    .btn:hover { background: var(--accent-hover); }
    .btn-success { background: var(--success); }
    .btn-success:hover { background: #059669; }
    .btn-secondary { background: var(--border); color: var(--text); }
    .btn-secondary:hover { background: #475569; }

    .posts-list {
      flex: 1;
      overflow-y: auto;
      padding: 10px;
    }
    .post-item {
      padding: 12px;
      margin-bottom: 6px;
      border-radius: 8px;
      cursor: pointer;
      border: 1px solid transparent;
      transition: 0.2s;
    }
    .post-item:hover { background: #293548; }
    .post-item.active {
      background: #334155;
      border-color: var(--accent);
    }
    .post-item-title {
      font-weight: 600;
      font-size: 0.95rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .post-item-date {
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 4px;
    }

    /* Main Area */
    #main {
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }
    .topbar {
      padding: 12px 20px;
      background: var(--sidebar-bg);
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }
    .meta-inputs {
      display: flex;
      gap: 10px;
      flex: 1;
    }
    input[type="text"], input[type="date"] {
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 0.95rem;
      outline: none;
    }
    input[type="text"]:focus, input[type="date"]:focus {
      border-color: var(--accent);
    }
    #post-title { flex: 2; font-weight: 600; }
    #post-categories { flex: 1; }
    #post-date { width: 140px; }

    .toolbar {
      padding: 8px 20px;
      background: #141e30;
      border-bottom: 1px solid var(--border);
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
    }
    .tool-btn {
      background: transparent;
      border: 1px solid var(--border);
      color: var(--text);
      padding: 4px 10px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.85rem;
    }
    .tool-btn:hover { background: var(--border); }

    /* Split workspace */
    .workspace {
      display: flex;
      flex: 1;
      height: calc(100vh - 130px);
      overflow: hidden;
    }
    .editor-pane {
      flex: 1;
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
    }
    #post-content {
      flex: 1;
      width: 100%;
      height: 100%;
      background: var(--bg);
      color: #f8fafc;
      border: none;
      padding: 20px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 1rem;
      line-height: 1.6;
      resize: none;
      outline: none;
    }
    .preview-pane {
      flex: 1;
      padding: 24px;
      overflow-y: auto;
      background: #090d16;
      line-height: 1.7;
    }
    .preview-pane h1, .preview-pane h2, .preview-pane h3 { margin: 20px 0 10px; }
    .preview-pane p { margin-bottom: 14px; }
    .preview-pane code { background: #1e293b; padding: 2px 6px; border-radius: 4px; }
    .preview-pane pre { background: #1e293b; padding: 14px; border-radius: 8px; overflow-x: auto; margin-bottom: 14px; }
    .preview-pane img, .preview-pane iframe { max-width: 100%; border-radius: 8px; }

    /* Notification status */
    #status-toast {
      position: fixed;
      bottom: 20px;
      right: 20px;
      padding: 12px 20px;
      border-radius: 8px;
      background: var(--sidebar-bg);
      border: 1px solid var(--border);
      color: white;
      display: none;
      box-shadow: 0 10px 20px rgba(0,0,0,0.4);
      z-index: 1000;
    }
    @media (max-width: 768px) {
      body { flex-direction: column; }
      #sidebar { width: 100%; height: 180px; }
      .workspace { flex-direction: column; }
    }
  </style>
</head>
<body>
  <!-- Sidebar -->
  <aside id="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">📝 My Posts</span>
      <button class="btn" onclick="createNewPost()">+ New</button>
    </div>
    <div class="posts-list" id="posts-list"></div>
  </aside>

  <!-- Main Editor -->
  <main id="main">
    <div class="topbar">
      <div class="meta-inputs">
        <input type="text" id="post-title" placeholder="Post Title..." />
        <input type="date" id="post-date" />
        <input type="text" id="post-categories" placeholder="Categories (e.g. vlog, tech)" />
      </div>
      <div style="display: flex; gap: 8px;">
        <button class="btn btn-secondary" onclick="savePost()">💾 Save</button>
        <button class="btn btn-success" onclick="gitPush()" id="push-btn">🚀 Git Push</button>
      </div>
    </div>

    <!-- Formatting Toolbar -->
    <div class="toolbar">
      <button class="tool-btn" onclick="insertFormat('**', '**')"><b>B</b></button>
      <button class="tool-btn" onclick="insertFormat('*', '*')"><i>I</i></button>
      <button class="tool-btn" onclick="insertFormat('## ')">H2</button>
      <button class="tool-btn" onclick="insertFormat('### ')">H3</button>
      <button class="tool-btn" onclick="insertFormat('> ')">Quote</button>
      <button class="tool-btn" onclick="insertFormat('`', '`')">Code</button>
      <button class="tool-btn" onclick="insertYoutube()">🎥 Insert YouTube Vlog</button>
      <button class="tool-btn" onclick="insertImage()">🖼️ Insert Image</button>
      <button class="tool-btn" onclick="insertLink()">🔗 Link</button>
      <span style="flex:1;"></span>
      <a href="https://srxzsrxzsrxz.github.io" target="_blank" style="color:var(--text-muted); font-size:0.85rem; text-decoration:none;">🌐 Open Blog &rarr;</a>
    </div>

    <!-- Editor Workspace -->
    <div class="workspace">
      <div class="editor-pane">
        <textarea id="post-content" placeholder="Write your markdown content here..."></textarea>
      </div>
      <div class="preview-pane" id="preview-pane"></div>
    </div>
  </main>

  <div id="status-toast"></div>

  <script>
    let currentFilename = "";
    const textarea = document.getElementById('post-content');
    const preview = document.getElementById('preview-pane');
    const titleInput = document.getElementById('post-title');
    const dateInput = document.getElementById('post-date');
    const catInput = document.getElementById('post-categories');

    // Real-time markdown preview
    textarea.addEventListener('input', updatePreview);
    function updatePreview() {
      if (window.marked) {
        preview.innerHTML = marked.parse(textarea.value || "*Nothing to preview*");
      }
    }

    function showToast(msg, isError = false) {
      const toast = document.getElementById('status-toast');
      toast.textContent = msg;
      toast.style.borderColor = isError ? "var(--danger)" : "var(--success)";
      toast.style.display = "block";
      setTimeout(() => { toast.style.display = "none"; }, 3500);
    }

    async function loadPosts() {
      try {
        const res = await fetch('/api/posts');
        const posts = await res.json();
        const listEl = document.getElementById('posts-list');
        listEl.innerHTML = "";
        posts.forEach(p => {
          const item = document.createElement('div');
          item.className = 'post-item' + (p.filename === currentFilename ? ' active' : '');
          item.innerHTML = `<div class="post-item-title">${p.title || p.filename}</div>
                            <div class="post-item-date">${p.date || ''}</div>`;
          item.onclick = () => loadPost(p.filename);
          listEl.appendChild(item);
        });
      } catch (err) {
        console.error(err);
      }
    }

    async function loadPost(filename) {
      try {
        const res = await fetch('/api/post?name=' + encodeURIComponent(filename));
        const data = await res.json();
        currentFilename = filename;
        titleInput.value = data.title || "";
        dateInput.value = data.date || new Date().toISOString().split('T')[0];
        catInput.value = (data.categories || []).join(', ');
        textarea.value = data.body || "";
        updatePreview();
        loadPosts();
      } catch (err) {
        showToast("Error loading post", true);
      }
    }

    function createNewPost() {
      currentFilename = "";
      titleInput.value = "";
      dateInput.value = new Date().toISOString().split('T')[0];
      catInput.value = "";
      textarea.value = "# Hello World\\n\\nWrite your new post here...";
      updatePreview();
      titleInput.focus();
      loadPosts();
    }

    async function savePost() {
      const title = titleInput.value.trim();
      if (!title) {
        alert("Please enter a title for the post!");
        return;
      }
      const date = dateInput.value || new Date().toISOString().split('T')[0];
      const categories = catInput.value.split(',').map(c => c.trim()).filter(Boolean);
      const body = textarea.value;

      try {
        const res = await fetch('/api/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename: currentFilename, title, date, categories, body })
        });
        const result = await res.json();
        if (result.ok) {
          currentFilename = result.filename;
          showToast("✅ Post saved successfully!");
          loadPosts();
        } else {
          showToast("❌ " + result.error, true);
        }
      } catch (err) {
        showToast("❌ Failed to save post", true);
      }
    }

    async function gitPush() {
      const btn = document.getElementById('push-btn');
      btn.textContent = "⏳ Pushing...";
      btn.disabled = true;
      try {
        const res = await fetch('/api/git-push', { method: 'POST' });
        const result = await res.json();
        if (result.ok) {
          showToast("🚀 Successfully pushed to GitHub!");
        } else {
          showToast("❌ Push failed: " + result.output, true);
        }
      } catch (err) {
        showToast("❌ Network error pushing to Git", true);
      } finally {
        btn.textContent = "🚀 Git Push";
        btn.disabled = false;
      }
    }

    function insertFormat(prefix, suffix = "") {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const sel = textarea.value.substring(start, end);
      const text = prefix + sel + suffix;
      textarea.setRangeText(text, start, end, 'end');
      updatePreview();
    }

    function insertYoutube() {
      const url = prompt("Enter YouTube Video URL or Video ID:");
      if (!url) return;
      let videoId = url.trim();
      if (url.includes('youtu.be/')) {
        videoId = url.split('youtu.be/')[1].split(/[?#]/)[0];
      } else if (url.includes('watch?v=')) {
        videoId = url.split('watch?v=')[1].split('&')[0];
      }
      const embed = `\\n<iframe width="100%" height="360" src="https://www.youtube.com/embed/${videoId}" frameborder="0" allowfullscreen></iframe>\\n`;
      insertFormat(embed);
    }

    function insertImage() {
      const url = prompt("Image URL or /assets/images/filename.jpg:", "/assets/images/");
      if (url) insertFormat(`![Image description](${url})`);
    }

    function insertLink() {
      const url = prompt("URL:", "https://");
      if (url) insertFormat(`[Link title](${url})`);
    }

    // Initialize
    dateInput.value = new Date().toISOString().split('T')[0];
    loadPosts().then(() => {
      // Load first post if exists
      const first = document.querySelector('.post-item');
      if (first) first.click();
      else createNewPost();
    });
  </script>
</body>
</html>
"""

def parse_frontmatter(content):
    meta = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_meta = parts[1].strip()
            body = parts[2].strip()
            for line in raw_meta.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if v.startswith("[") and v.endswith("]"):
                        v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
                    meta[k] = v
    return meta, body

def dump_frontmatter(meta, body):
    lines = ["---", "layout: post"]
    for k, v in meta.items():
        if k in ("layout",):
            continue
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(v)}]")
        else:
            lines.append(f"{k}: \"{v}\"")
    lines.append("---")
    lines.append("")
    lines.append(body.strip())
    lines.append("")
    return "\n".join(lines)

def slugify(title):
    slug = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]+', '-', title).strip('-').lower()
    return slug or "post"

class BlogHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Suppress standard noise

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/" or url.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
            return

        elif url.path == "/api/posts":
            posts = []
            if os.path.exists(POSTS_DIR):
                for f in sorted(os.listdir(POSTS_DIR), reverse=True):
                    if f.endswith(".md"):
                        p_path = os.path.join(POSTS_DIR, f)
                        try:
                            with open(p_path, "r", encoding="utf-8") as fp:
                                meta, _ = parse_frontmatter(fp.read())
                                posts.append({
                                    "filename": f,
                                    "title": meta.get("title", f),
                                    "date": meta.get("date", f[:10]),
                                    "categories": meta.get("categories", [])
                                })
                        except Exception:
                            posts.append({"filename": f, "title": f})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(posts).encode("utf-8"))
            return

        elif url.path == "/api/post":
            qs = urllib.parse.parse_qs(url.query)
            filename = qs.get("name", [""])[0]
            file_path = os.path.join(POSTS_DIR, filename)
            if filename and os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as fp:
                    meta, body = parse_frontmatter(fp.read())
                    data = {
                        "filename": filename,
                        "title": meta.get("title", ""),
                        "date": meta.get("date", "")[:10] if meta.get("date") else "",
                        "categories": meta.get("categories", []) if isinstance(meta.get("categories"), list) else [meta.get("categories", "")],
                        "body": body
                    }
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode("utf-8"))
                    return

            self.send_response(404)
            self.end_headers()
            return

        super().do_GET()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length) if length > 0 else b"{}"
        
        if url.path == "/api/save":
            try:
                payload = json.loads(data.decode("utf-8"))
                filename = payload.get("filename")
                title = payload.get("title", "Untitled")
                date_str = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
                categories = payload.get("categories", [])
                body = payload.get("body", "")

                if not filename:
                    slug = slugify(title)
                    filename = f"{date_str}-{slug}.md"

                meta = {
                    "title": title,
                    "date": f"{date_str} {datetime.now().strftime('%H:%M:%S')} +0800",
                    "categories": categories
                }
                full_content = dump_frontmatter(meta, body)
                os.makedirs(POSTS_DIR, exist_ok=True)
                with open(os.path.join(POSTS_DIR, filename), "w", encoding="utf-8") as fp:
                    fp.write(full_content)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "filename": filename}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode("utf-8"))
            return

        elif url.path == "/api/git-push":
            try:
                cmd = "git add . && git commit -m 'update blog' && git push"
                proc = subprocess.run(cmd, shell=True, cwd=BLOG_DIR, capture_output=True, text=True)
                ok = (proc.returncode == 0) or ("nothing to commit" in proc.stdout)
                out = proc.stdout + proc.stderr
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": ok, "output": out}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "output": str(e)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    os.chdir(BLOG_DIR)
    lan_ip = get_lan_ip()
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), BlogHandler)
    print("=" * 60)
    print("📝 Local Blog Editor Started!")
    print(f"👉 Local Access:   http://localhost:{PORT}")
    print(f"📱 Phone / LAN:    http://{lan_ip}:{PORT}")
    print("Press Ctrl+C to stop.")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping editor server.")
