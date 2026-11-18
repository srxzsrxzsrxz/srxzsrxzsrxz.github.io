#!/usr/bin/env python3
"""
Linux Terminal Studio & Neovim-Style Blog Editor
Zero external dependencies. Runs on Python 3 standard library.
"""

import http.server
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime

PORT = 5500
BLOG_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(BLOG_DIR, "_posts")
DRAFTS_DIR = os.path.join(BLOG_DIR, "_drafts")
IMAGES_DIR = os.path.join(BLOG_DIR, "assets", "images")

os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(DRAFTS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NVIM // Blog Terminal Studio</title>
  <!-- Marked.js, Highlight.js for code syntax highlighting -->
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/atom-one-dark.min.css">
  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>
  <style>
    :root {
      --bg: #05070c;
      --sidebar: #090d16;
      --card: #0e1320;
      --border: #1e293b;
      --text: #f0fdf4;
      --text-muted: #64748b;
      --hacker-green: #00ff66;
      --hacker-glow: rgba(0, 255, 102, 0.35);
      --cyber-cyan: #00f0ff;
      --cyber-yellow: #fcee0a;
      --cyber-pink: #ff007f;
      --danger: #ef4444;
      --mono: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--mono);
      background: var(--bg);
      color: var(--text);
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
      background-image: 
        linear-gradient(rgba(0, 255, 102, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 102, 0.02) 1px, transparent 1px);
      background-size: 24px 24px;
    }

    /* Window Header (Linux / macOS style) */
    .term-window-header {
      height: 42px;
      background: #020306;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      font-size: 0.82rem;
      user-select: none;
    }
    .window-dots { display: flex; gap: 7px; align-items: center; }
    .dot { width: 11px; height: 11px; border-radius: 50%; display: inline-block; }
    .dot-close { background: #ff5f56; }
    .dot-min { background: #ffbd2e; }
    .dot-max { background: #27c93f; }
    .window-title { color: var(--hacker-green); font-weight: 700; display: flex; align-items: center; gap: 6px; }

    /* Main Container */
    .app-body {
      display: flex;
      flex: 1;
      height: calc(100vh - 74px);
      overflow: hidden;
    }

    /* Sidebar (File tree) */
    #sidebar {
      width: 290px;
      background: var(--sidebar);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      transition: margin-left 0.2s ease;
    }
    #sidebar.collapsed { margin-left: -290px; }

    .sidebar-head {
      padding: 10px 14px;
      background: #050810;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.8rem;
      color: var(--text-muted);
    }
    .tab-bar {
      display: flex;
      border-bottom: 1px solid var(--border);
      background: #04060a;
    }
    .tab-btn {
      flex: 1;
      padding: 8px 10px;
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-family: inherit;
      font-size: 0.78rem;
      font-weight: 700;
      border-bottom: 2px solid transparent;
      transition: 0.2s;
    }
    .tab-btn.active {
      color: var(--hacker-green);
      border-bottom-color: var(--hacker-green);
      background: rgba(0, 255, 102, 0.05);
    }

    .search-box-row { padding: 8px 12px; border-bottom: 1px solid var(--border); }
    .term-input {
      width: 100%;
      background: #020306;
      border: 1px solid var(--border);
      color: var(--hacker-green);
      font-family: inherit;
      padding: 6px 10px;
      border-radius: 4px;
      font-size: 0.8rem;
      outline: none;
    }
    .term-input:focus { border-color: var(--hacker-green); box-shadow: 0 0 10px var(--hacker-glow); }

    .posts-tree { flex: 1; overflow-y: auto; padding: 8px 10px; }
    .tree-item {
      padding: 8px 10px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.82rem;
      margin-bottom: 4px;
      border: 1px solid transparent;
      display: flex;
      justify-content: space-between;
      align-items: center;
      transition: all 0.15s;
    }
    .tree-item:hover { background: #0e1424; border-color: var(--border); }
    .tree-item.active {
      background: #111a2e;
      border-color: var(--hacker-green);
      color: var(--hacker-green);
    }
    .tree-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
    .tree-del { opacity: 0; color: var(--danger); cursor: pointer; padding: 2px 6px; }
    .tree-item:hover .tree-del { opacity: 1; }

    /* Main Workspace */
    #main-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background: var(--bg);
    }

    /* Linux Control Toolbar */
    .term-toolbar {
      padding: 6px 14px;
      background: #070a12;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .cli-btn {
      background: rgba(0, 255, 102, 0.06);
      border: 1px solid var(--border);
      color: var(--text);
      font-family: inherit;
      font-size: 0.78rem;
      padding: 4px 10px;
      border-radius: 4px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: all 0.15s;
    }
    .cli-btn:hover {
      border-color: var(--hacker-green);
      color: var(--hacker-green);
      box-shadow: 0 0 8px var(--hacker-glow);
    }
    .cli-btn-primary {
      background: var(--hacker-green);
      color: #000;
      font-weight: 700;
      border-color: var(--hacker-green);
    }
    .cli-btn-primary:hover {
      background: #22c55e;
      color: #000;
      box-shadow: 0 0 12px var(--hacker-glow);
    }

    /* Metadata Config Bar */
    .meta-bar {
      padding: 8px 14px;
      background: #04060c;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 0.82rem;
    }
    .meta-tag { color: var(--cyber-cyan); font-weight: 700; }
    #post-title-in {
      flex: 2;
      background: #090d16;
      border: 1px solid var(--border);
      color: #fff;
      font-family: inherit;
      padding: 5px 10px;
      border-radius: 4px;
      font-size: 0.9rem;
      outline: none;
    }
    #post-date-in { width: 130px; }
    #post-tags-in { flex: 1; }

    /* Dual Workspace (Editor + Terminal Preview) */
    .workspace-pane {
      flex: 1;
      display: flex;
      height: calc(100% - 75px);
      overflow: hidden;
      position: relative;
    }

    .editor-wrapper {
      flex: 1;
      display: flex;
      background: #030408;
      border-right: 1px solid var(--border);
      position: relative;
      overflow: hidden;
    }

    /* Gutter line numbers */
    .line-numbers {
      width: 48px;
      padding: 16px 8px 16px 0;
      background: #020306;
      border-right: 1px solid #141b2b;
      color: #3b4b66;
      font-family: inherit;
      font-size: 0.95rem;
      line-height: 1.65;
      text-align: right;
      user-select: none;
      overflow: hidden;
    }

    #editor {
      flex: 1;
      background: transparent;
      color: #f0fdf4;
      font-family: inherit;
      font-size: 0.96rem;
      line-height: 1.65;
      padding: 16px 20px;
      border: none;
      resize: none;
      outline: none;
      white-space: pre;
      overflow-wrap: normal;
      overflow-x: auto;
      overflow-y: auto;
    }

    /* Drag & drop overlay */
    #drop-overlay {
      position: absolute;
      inset: 0;
      background: rgba(0, 255, 102, 0.85);
      color: #000;
      font-weight: 800;
      font-size: 1.3rem;
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 50;
      pointer-events: none;
    }

    /* Preview Pane */
    .preview-wrapper {
      flex: 1;
      padding: 24px 30px;
      overflow-y: auto;
      background: #05070c;
      font-size: 0.98rem;
      line-height: 1.75;
      border-left: 1px solid #141b2b;
    }
    .preview-wrapper h1, .preview-wrapper h2, .preview-wrapper h3 {
      color: var(--hacker-green);
      margin: 22px 0 10px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 4px;
    }
    .preview-wrapper p { margin-bottom: 16px; }
    .preview-wrapper a { color: var(--cyber-cyan); }
    .preview-wrapper blockquote {
      border-left: 4px solid var(--hacker-green);
      padding: 10px 16px;
      background: #080d16;
      color: #94a3b8;
      margin: 18px 0;
    }
    .preview-wrapper pre {
      background: #020306 !important;
      border: 1px solid var(--border);
      padding: 14px;
      border-radius: 4px;
      overflow-x: auto;
      margin: 18px 0;
    }
    .preview-wrapper img {
      max-width: 100%;
      border-radius: 4px;
      border: 1px solid var(--border);
      margin: 14px 0;
    }
    .preview-wrapper iframe {
      width: 100%;
      aspect-ratio: 16/9;
      border-radius: 6px;
      border: 1px solid var(--cyber-cyan);
      margin: 16px 0;
    }

    /* Tmux / Neovim Bottom Status Bar */
    .tmux-status-bar {
      height: 32px;
      background: #020306;
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 14px;
      font-size: 0.78rem;
      color: var(--text-muted);
      user-select: none;
    }
    .status-left { display: flex; align-items: center; gap: 12px; }
    .status-mode {
      background: var(--hacker-green);
      color: #000;
      font-weight: 800;
      padding: 2px 8px;
      border-radius: 2px;
    }
    .status-right { display: flex; align-items: center; gap: 12px; }

    /* Interactive Vim Command Bar */
    .vim-cmdline {
      display: flex;
      align-items: center;
      padding: 4px 14px;
      background: #04060a;
      border-top: 1px solid #141b2b;
      font-size: 0.82rem;
    }
    .vim-prompt { color: var(--hacker-green); font-weight: 800; margin-right: 6px; }
    #vim-cmd-input {
      flex: 1;
      background: transparent;
      border: none;
      color: #fff;
      font-family: inherit;
      font-size: 0.85rem;
      outline: none;
    }

    /* Modals */
    .term-modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(2, 3, 6, 0.85);
      backdrop-filter: blur(6px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }
    .term-modal {
      background: #090d16;
      border: 1px solid var(--hacker-green);
      box-shadow: 0 0 30px rgba(0, 255, 102, 0.25);
      border-radius: 6px;
      width: 520px;
      max-width: 90vw;
      padding: 20px;
    }
    .modal-hdr {
      color: var(--hacker-green);
      font-weight: 800;
      margin-bottom: 12px;
      font-size: 1rem;
    }

    /* Toast */
    #term-toast {
      position: fixed;
      bottom: 45px;
      right: 20px;
      background: #090d16;
      border: 1px solid var(--hacker-green);
      color: var(--hacker-green);
      padding: 10px 18px;
      border-radius: 4px;
      font-size: 0.85rem;
      box-shadow: 0 0 20px rgba(0, 255, 102, 0.3);
      display: none;
      z-index: 2000;
    }
  </style>
</head>
<body>
  <!-- Linux Window Frame -->
  <header class="term-window-header">
    <div class="window-dots">
      <span class="dot dot-close" onclick="alert('Close session in terminal')" title="Close"></span>
      <span class="dot dot-min" onclick="toggleSidebar()" title="Toggle Sidebar"></span>
      <span class="dot dot-max" onclick="toggleZen()" title="Zen Mode"></span>
    </div>
    <div class="window-title">
      <span>srxz@fedora:~/blog</span>
      <span style="color:var(--text-muted);">&mdash;</span>
      <span id="header-file-title" style="color:var(--cyber-cyan);">[No File]</span>
    </div>
    <div>
      <span style="color:var(--text-muted); font-size:0.75rem;">PORT: 5500</span>
    </div>
  </header>

  <div class="app-body">
    <!-- Sidebar -->
    <aside id="sidebar">
      <div class="sidebar-head">
        <span>EXPLORER // POSTS</span>
        <button class="cli-btn" style="padding:2px 6px;" onclick="toggleSidebar()">&lt;</button>
      </div>

      <div class="tab-bar">
        <button class="tab-btn active" id="tab-posts" onclick="switchSidebarTab('posts')">_posts (<span id="cnt-posts">0</span>)</button>
        <button class="tab-btn" id="tab-drafts" onclick="switchSidebarTab('drafts')">_drafts (<span id="cnt-drafts">0</span>)</button>
      </div>

      <div class="search-box-row">
        <input type="text" class="term-input" id="sidebar-search" placeholder="grep post name..." oninput="renderPostTree()">
      </div>

      <div style="padding:6px 12px; display:flex; gap:6px;">
        <button class="cli-btn cli-btn-primary" style="flex:1;" onclick="createNewFile(false)">+ :new</button>
        <button class="cli-btn" onclick="createNewFile(true)">+ :draft</button>
      </div>

      <div class="posts-tree" id="posts-tree"></div>
    </aside>

    <!-- Main Workspace -->
    <main id="main-content">
      <!-- Toolbar -->
      <div class="term-toolbar">
        <button class="cli-btn" onclick="toggleSidebar()">[ 📁 Tree ]</button>
        <button class="cli-btn cli-btn-primary" onclick="saveFile()">[ :w Save ]</button>
        <button class="cli-btn" onclick="gitPull()" id="pull-btn">[ ⬇️ git pull ]</button>
        <button class="cli-btn" onclick="openPushModal()" id="push-btn" style="color:var(--hacker-green);">[ 🚀 git push ]</button>
        <span style="color:var(--border);">|</span>
        <button class="cli-btn" onclick="openYtModal()">[ 🎥 vlog ]</button>
        <button class="cli-btn" onclick="document.getElementById('img-file-in').click()">[ 🖼️ img ]</button>
        <button class="cli-btn" onclick="insertSnippet('table')">[ 📊 table ]</button>
        <button class="cli-btn" onclick="insertSnippet('code')">[ &lt;/&gt; code ]</button>
        <button class="cli-btn" onclick="window.open('/man/', '_blank')">[ 🐧 man-db ]</button>
        <input type="file" id="img-file-in" accept="image/*" style="display:none;" onchange="handleImageUpload(this.files[0])">
        <span style="flex:1;"></span>
        <button class="cli-btn" onclick="togglePreview()" id="prev-btn">[ 👁️ Preview ]</button>
        <button class="cli-btn" onclick="toggleZen()">[ 🧘 Zen ]</button>
      </div>

      <!-- Metadata Header -->
      <div class="meta-bar">
        <span class="meta-tag">TITLE:</span>
        <input type="text" id="post-title-in" placeholder="Article Title (e.g. My Next Cosplay Vlog)" oninput="updateDirty(true)">
        <span class="meta-tag">DATE:</span>
        <input type="date" class="term-input" id="post-date-in" onchange="updateDirty(true)">
        <span class="meta-tag">TAGS:</span>
        <input type="text" class="term-input" id="post-tags-in" placeholder="Cosplay, Vlog, Linux" oninput="updateDirty(true)">
      </div>

      <!-- Editor + Preview -->
      <div class="workspace-pane">
        <div class="editor-wrapper" id="editor-wrapper">
          <div class="line-numbers" id="line-numbers">1</div>
          <textarea id="editor" placeholder="# Write markdown here... (Ctrl+V or Drag & Drop images directly!)" spellcheck="false"></textarea>
          <div id="drop-overlay">📥 DROP IMAGE TO UPLOAD</div>
        </div>
        <div class="preview-wrapper" id="preview-wrapper"></div>
      </div>

      <!-- Vim Command Line -->
      <div class="vim-cmdline">
        <span class="vim-prompt">:</span>
        <input type="text" id="vim-cmd-input" placeholder="Type vim commands (:w, :push, :pull, :man grep, :new, :zen, :help)" autocomplete="off" spellcheck="false">
      </div>

      <!-- Tmux Status Bar -->
      <footer class="tmux-status-bar">
        <div class="status-left">
          <span class="status-mode" id="status-mode">NORMAL</span>
          <span id="status-file">untitled.md</span>
          <span style="color:var(--border);">|</span>
          <span id="dirty-indicator" style="color:var(--hacker-green);">[OK]</span>
        </div>
        <div class="status-right">
          <span id="metric-words">0 words</span>
          <span id="metric-chars">0 chars</span>
          <span id="cursor-pos">LN 1, COL 1</span>
          <span style="color:var(--cyber-cyan);">UTF-8</span>
          <a href="https://srxzsrxzsrxz.github.io" target="_blank" style="color:var(--hacker-green); text-decoration:none;">[🌐 live-site]</a>
        </div>
      </footer>
    </main>
  </div>

  <!-- YouTube Modal -->
  <div class="term-modal-backdrop" id="modal-yt">
    <div class="term-modal">
      <div class="modal-hdr">&gt; INSERT_YOUTUBE_VLOG</div>
      <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:10px;">Paste YouTube Video Link or ID:</p>
      <input type="text" class="term-input" id="yt-in" style="margin-bottom:14px;" placeholder="https://www.youtube.com/watch?v=...">
      <div style="display:flex; justify-content:flex-end; gap:8px;">
        <button class="cli-btn" onclick="closeModal('modal-yt')">CANCEL</button>
        <button class="cli-btn cli-btn-primary" onclick="confirmYt()">INSERT</button>
      </div>
    </div>
  </div>

  <!-- Git Push Modal -->
  <div class="term-modal-backdrop" id="modal-push">
    <div class="term-modal">
      <div class="modal-hdr">&gt; GIT_COMMIT_AND_PUSH</div>
      <p style="font-size:0.8rem; color:var(--text-muted); margin-bottom:10px;">Commit Message:</p>
      <input type="text" class="term-input" id="push-msg-in" style="margin-bottom:14px;" value="Update blog via Linux Studio">
      <div style="display:flex; justify-content:flex-end; gap:8px;">
        <button class="cli-btn" onclick="closeModal('modal-push')">CANCEL</button>
        <button class="cli-btn cli-btn-primary" id="push-confirm-btn" onclick="confirmPush()">PUSH TO ORIGIN</button>
      </div>
    </div>
  </div>

  <!-- Linux Man Lookup Modal inside Editor -->
  <div class="term-modal-backdrop" id="modal-man">
    <div class="term-modal" style="width:720px;">
      <div class="modal-hdr" id="man-modal-title">&gt; MAN_PAGE_LOOKUP</div>
      <div id="man-modal-body" style="font-size:0.85rem; line-height:1.55; max-height:420px; overflow-y:auto; background:#020306; padding:14px; border:1px solid var(--border); border-radius:4px; margin-bottom:12px;"></div>
      <div style="display:flex; justify-content:flex-end;">
        <button class="cli-btn" onclick="closeModal('modal-man')">CLOSE</button>
      </div>
    </div>
  </div>

  <div id="term-toast"></div>

  <script>
    let currentTab = 'posts';
    let currentFile = '';
    let isDraft = false;
    let allEntries = [];
    let isDirty = false;

    const editor = document.getElementById('editor');
    const lineNums = document.getElementById('line-numbers');
    const preview = document.getElementById('preview-wrapper');
    const titleIn = document.getElementById('post-title-in');
    const dateIn = document.getElementById('post-date-in');
    const tagsIn = document.getElementById('post-tags-in');
    const vimCmd = document.getElementById('vim-cmd-input');

    // Marked.js + Highlight.js
    marked.setOptions({
      highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) return hljs.highlight(code, { language: lang }).value;
        return hljs.highlightAuto(code).value;
      },
      breaks: true
    });

    function updateLineNumbers() {
      const lines = editor.value.split('\\n').length;
      let out = '';
      for (let i = 1; i <= lines; i++) out += i + '<br>';
      lineNums.innerHTML = out;
    }

    editor.addEventListener('scroll', () => {
      lineNums.scrollTop = editor.scrollTop;
    });

    editor.addEventListener('input', () => {
      updateDirty(true);
      updateLineNumbers();
      renderPreview();
      updateMetrics();
    });

    editor.addEventListener('keyup', updateCursorPos);
    editor.addEventListener('click', updateCursorPos);

    function updateCursorPos() {
      const pos = editor.selectionStart;
      const text = editor.value.substr(0, pos);
      const line = text.split('\\n').length;
      const col = pos - text.lastIndexOf('\\n');
      document.getElementById('cursor-pos').textContent = `LN ${line}, COL ${col}`;
    }

    function updateDirty(dirty) {
      isDirty = dirty;
      const d = document.getElementById('dirty-indicator');
      if (dirty) {
        d.textContent = '[MODIFIED*]';
        d.style.color = 'var(--cyber-yellow)';
      } else {
        d.textContent = '[SAVED]';
        d.style.color = 'var(--hacker-green)';
      }
    }

    function renderPreview() {
      preview.innerHTML = marked.parse(editor.value || "*# Terminal output empty*");
    }

    function updateMetrics() {
      const val = editor.value.trim();
      const words = val ? val.split(/\\s+/).length : 0;
      document.getElementById('metric-words').textContent = words + ' words';
      document.getElementById('metric-chars').textContent = val.length + ' chars';
    }

    function toast(msg, isErr = false) {
      const t = document.getElementById('term-toast');
      t.textContent = (isErr ? '[ERR] ' : '[OK] ') + msg;
      t.style.borderColor = isErr ? 'var(--danger)' : 'var(--hacker-green)';
      t.style.color = isErr ? 'var(--danger)' : 'var(--hacker-green)';
      t.style.display = 'block';
      setTimeout(() => { t.style.display = 'none'; }, 3500);
    }

    // Load Posts & Drafts
    async function loadTree() {
      try {
        const res = await fetch('/api/posts');
        allEntries = await res.json();
        document.getElementById('cnt-posts').textContent = allEntries.filter(x => !x.is_draft).length;
        document.getElementById('cnt-drafts').textContent = allEntries.filter(x => x.is_draft).length;
        renderPostTree();
      } catch (e) {
        toast("Failed loading post directory", true);
      }
    }

    function switchSidebarTab(tab) {
      currentTab = tab;
      document.getElementById('tab-posts').classList.toggle('active', tab === 'posts');
      document.getElementById('tab-drafts').classList.toggle('active', tab === 'drafts');
      renderPostTree();
    }

    function renderPostTree() {
      const tree = document.getElementById('posts-tree');
      const q = document.getElementById('sidebar-search').value.toLowerCase();
      const list = allEntries.filter(p => {
        const matchesTab = currentTab === 'drafts' ? p.is_draft : !p.is_draft;
        const matchesQ = (p.title || '').toLowerCase().includes(q) || (p.filename || '').toLowerCase().includes(q);
        return matchesTab && matchesQ;
      });

      tree.innerHTML = '';
      if (list.length === 0) {
        tree.innerHTML = '<div style="color:var(--text-muted); padding:14px; font-size:0.8rem;">[empty]</div>';
        return;
      }

      list.forEach(item => {
        const el = document.createElement('div');
        el.className = 'tree-item' + (item.filename === currentFile ? ' active' : '');
        el.innerHTML = `
          <span class="tree-name">&gt; ${item.title || item.filename}</span>
          <span class="tree-del" onclick="event.stopPropagation(); deleteEntry('${item.filename}', ${item.is_draft})" title="rm">[x]</span>
        `;
        el.onclick = () => openFile(item.filename, item.is_draft);
        tree.appendChild(el);
      });
    }

    async function openFile(filename, draft) {
      if (isDirty && !confirm("File has unsaved changes. Discard and switch?")) return;
      try {
        const res = await fetch(`/api/post?name=${encodeURIComponent(filename)}&is_draft=${draft}`);
        const data = await res.json();
        currentFile = filename;
        isDraft = draft;
        titleIn.value = data.title || "";
        dateIn.value = data.date || new Date().toISOString().split('T')[0];
        tagsIn.value = (data.categories || []).join(', ');
        editor.value = data.body || "";
        document.getElementById('header-file-title').textContent = filename;
        document.getElementById('status-file').textContent = filename;
        updateDirty(false);
        updateLineNumbers();
        renderPreview();
        updateMetrics();
        renderPostTree();
      } catch (e) {
        toast("Error opening file", true);
      }
    }

    function createNewFile(draft = false) {
      if (isDirty && !confirm("Discard unsaved changes?")) return;
      currentFile = "";
      isDraft = draft;
      titleIn.value = "";
      dateIn.value = new Date().toISOString().split('T')[0];
      tagsIn.value = "";
      editor.value = "# Hello World\\n\\nWrite markdown or vlog notes here...";
      document.getElementById('header-file-title').textContent = draft ? "[NEW_DRAFT]" : "[NEW_POST]";
      document.getElementById('status-file').textContent = "untitled.md";
      titleIn.focus();
      updateDirty(false);
      updateLineNumbers();
      renderPreview();
      updateMetrics();
      renderPostTree();
    }

    async function saveFile() {
      const title = titleIn.value.trim();
      if (!title) {
        toast("Missing post title!", true);
        titleIn.focus();
        return;
      }
      const date = dateIn.value || new Date().toISOString().split('T')[0];
      const categories = tagsIn.value.split(',').map(s => s.trim()).filter(Boolean);
      const body = editor.value;

      try {
        const res = await fetch('/api/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename: currentFile, is_draft: isDraft, title, date, categories, body })
        });
        const d = await res.json();
        if (d.ok) {
          currentFile = d.filename;
          document.getElementById('header-file-title').textContent = d.filename;
          document.getElementById('status-file').textContent = d.filename;
          updateDirty(false);
          toast("File written successfully (:w)");
          await loadTree();
        } else {
          toast(d.error, true);
        }
      } catch (e) {
        toast("Write failure", true);
      }
    }

    async function deleteEntry(filename, draft) {
      if (!confirm(`Are you sure you want to rm ${filename}?`)) return;
      try {
        const res = await fetch('/api/delete', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename, is_draft: draft })
        });
        const d = await res.json();
        if (d.ok) {
          toast("File deleted (:rm)");
          if (currentFile === filename) createNewFile(false);
          loadTree();
        }
      } catch (e) {
        toast("Delete error", true);
      }
    }

    // Git Actions
    async function gitPull() {
      const btn = document.getElementById('pull-btn');
      btn.textContent = "[ ⏳ pulling... ]";
      try {
        const res = await fetch('/api/git-pull', { method: 'POST' });
        const d = await res.json();
        if (d.ok) {
          toast("Git pulled successfully (:pull)");
          loadTree();
        } else {
          toast("Pull failed: " + d.output, true);
        }
      } catch (e) {
        toast("Network error", true);
      } finally {
        btn.textContent = "[ ⬇️ git pull ]";
      }
    }

    function openPushModal() {
      document.getElementById('modal-push').style.display = 'flex';
      document.getElementById('push-msg-in').focus();
    }

    async function confirmPush() {
      const msg = document.getElementById('push-msg-in').value.trim() || "Update blog via Linux Studio";
      const btn = document.getElementById('push-confirm-btn');
      btn.textContent = "PUSHING...";
      try {
        await saveFile();
        const res = await fetch('/api/git-push', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: msg })
        });
        const d = await res.json();
        if (d.ok) {
          closeModal('modal-push');
          toast("Pushed to GitHub Pages (:push)");
        } else {
          toast("Push error: " + d.output, true);
        }
      } catch (e) {
        toast("Git push network failure", true);
      } finally {
        btn.textContent = "PUSH TO ORIGIN";
      }
    }

    // Clipboard & Drag-and-drop Image Upload
    async function handleImageUpload(file) {
      if (!file || !file.type.startsWith('image/')) return;
      toast("Uploading image to assets/images/...");
      const reader = new FileReader();
      reader.onload = async () => {
        try {
          const res = await fetch('/api/upload-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: file.name, data: reader.result })
          });
          const d = await res.json();
          if (d.ok) {
            insertSnippet(`![${file.name}](${d.url})\\n`);
            toast("Image saved: " + d.url);
          } else {
            toast(d.error, true);
          }
        } catch (e) {
          toast("Upload failed", true);
        }
      };
      reader.readAsDataURL(file);
    }

    editor.addEventListener('paste', (e) => {
      const items = (e.clipboardData || e.originalEvent.clipboardData).items;
      for (const item of items) {
        if (item.kind === 'file' && item.type.startsWith('image/')) {
          e.preventDefault();
          handleImageUpload(item.getAsFile());
          return;
        }
      }
    });

    const dropOverlay = document.getElementById('drop-overlay');
    const editorWrapper = document.getElementById('editor-wrapper');
    ['dragenter', 'dragover'].forEach(n => editorWrapper.addEventListener(n, (e) => { e.preventDefault(); dropOverlay.style.display = 'flex'; }));
    ['dragleave', 'drop'].forEach(n => editorWrapper.addEventListener(n, (e) => { e.preventDefault(); dropOverlay.style.display = 'none'; }));
    editorWrapper.addEventListener('drop', (e) => {
      if (e.dataTransfer.files.length > 0) handleImageUpload(e.dataTransfer.files[0]);
    });

    function insertSnippet(type) {
      if (type === 'table') {
        insertText('\\n| Option | Type | Description |\\n| :----- | :--- | :---------- |\\n| -f     | str  | Format code  |\\n| -v     | bool | Verbose mode |\\n');
      } else if (type === 'code') {
        insertText('\\n```bash\\n# Execute command\\nffmpeg -i input.mp4 output.mp3\\n```\\n');
      }
    }

    function insertText(snippet) {
      const start = editor.selectionStart;
      const end = editor.selectionEnd;
      editor.setRangeText(snippet, start, end, 'end');
      updateDirty(true);
      updateLineNumbers();
      renderPreview();
      editor.focus();
    }

    function openYtModal() {
      document.getElementById('modal-yt').style.display = 'flex';
      document.getElementById('yt-in').focus();
    }

    function confirmYt() {
      const url = document.getElementById('yt-in').value.trim();
      if (!url) return;
      let vid = url;
      if (url.includes('youtu.be/')) vid = url.split('youtu.be/')[1].split(/[?#]/)[0];
      else if (url.includes('watch?v=')) vid = url.split('watch?v=')[1].split('&')[0];
      insertText(`\\n<iframe width="100%" height="380" src="https://www.youtube.com/embed/${vid}" frameborder="0" allowfullscreen></iframe>\\n`);
      closeModal('modal-yt');
      document.getElementById('yt-in').value = '';
    }

    function closeModal(id) {
      document.getElementById(id).style.display = 'none';
    }

    function toggleSidebar() {
      document.getElementById('sidebar').classList.toggle('collapsed');
    }

    function togglePreview() {
      const p = document.getElementById('preview-wrapper');
      p.style.display = p.style.display === 'none' ? 'block' : 'none';
    }

    function toggleZen() {
      document.getElementById('sidebar').classList.toggle('collapsed');
      togglePreview();
    }

    // Vim Command Line Controller
    vimCmd.addEventListener('keydown', async (e) => {
      if (e.key === 'Enter') {
        const cmd = vimCmd.value.trim().replace(/^:/, '');
        vimCmd.value = '';
        if (!cmd) return;

        const parts = cmd.split(/\\s+/);
        const action = parts[0].toLowerCase();

        switch (action) {
          case 'w':
          case 'write':
            saveFile();
            break;
          case 'wq':
          case 'push':
            confirmPush();
            break;
          case 'pull':
            gitPull();
            break;
          case 'new':
            createNewFile(false);
            break;
          case 'draft':
            createNewFile(true);
            break;
          case 'q':
          case 'quit':
            toast("Session active on :5500");
            break;
          case 'zen':
            toggleZen();
            break;
          case 'tree':
            toggleSidebar();
            break;
          case 'man':
            if (parts.length < 2) {
              toast("Usage: :man <command> (e.g. :man grep)", true);
            } else {
              showManModal(parts[1].toLowerCase());
            }
            break;
          case 'help':
            toast("Vim commands: :w, :wq, :push, :pull, :man <cmd>, :new, :zen");
            break;
          default:
            toast("Unknown vim command :" + action, true);
        }
      }
    });

    async function showManModal(cmd) {
      try {
        const res = await fetch('/assets/js/man_db.json');
        const db = await res.json();
        const item = db[cmd];
        if (!item) {
          toast("No man entry for " + cmd, true);
          return;
        }
        document.getElementById('man-modal-title').textContent = `> MAN_${cmd.toUpperCase()}(1)`;
        let html = item.doc
          .replace(/^[A-Z][A-Z\\s]{2,}$/gm, m => `<br><span style="color:var(--hacker-green); font-weight:bold;">${m}</span>`)
          .replace(/(^\\s+-[a-zA-Z0-9_\\-]+(?:,\\s+--[a-zA-Z0-9_\\-]+)?)/gm, m => `<span style="color:var(--cyber-yellow); font-weight:bold;">${m}</span>`);
        document.getElementById('man-modal-body').innerHTML = `<pre style="white-space:pre-wrap; font-family:inherit;">${html}</pre>`;
        document.getElementById('modal-man').style.display = 'flex';
      } catch (e) {
        toast("Error loading man DB", true);
      }
    }

    // Ctrl+S to save
    window.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveFile();
      }
    });

    // Init
    dateIn.value = new Date().toISOString().split('T')[0];
    loadTree().then(() => {
      if (allEntries.length > 0) openFile(allEntries[0].filename, allEntries[0].is_draft);
      else createNewFile(false);
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
    return slug or "article"

class LinuxStudioHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
            return

        elif url.path == "/api/posts":
            posts = []
            for folder, is_draft in [(POSTS_DIR, False), (DRAFTS_DIR, True)]:
                if os.path.exists(folder):
                    for f in sorted(os.listdir(folder), reverse=True):
                        if f.endswith(".md"):
                            p_path = os.path.join(folder, f)
                            try:
                                with open(p_path, "r", encoding="utf-8") as fp:
                                    meta, body = parse_frontmatter(fp.read())
                                    posts.append({
                                        "filename": f,
                                        "is_draft": is_draft,
                                        "title": meta.get("title", f),
                                        "date": meta.get("date", f[:10]),
                                        "categories": meta.get("categories", []),
                                        "words": len(body.split())
                                    })
                            except Exception:
                                posts.append({"filename": f, "is_draft": is_draft, "title": f})

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(posts).encode("utf-8"))
            return

        elif url.path == "/api/post":
            qs = urllib.parse.parse_qs(url.query)
            filename = qs.get("name", [""])[0]
            is_draft = qs.get("is_draft", ["false"])[0].lower() == "true"
            target_dir = DRAFTS_DIR if is_draft else POSTS_DIR
            target_file = os.path.join(target_dir, filename)

            if filename and os.path.exists(target_file):
                with open(target_file, "r", encoding="utf-8") as fp:
                    meta, body = parse_frontmatter(fp.read())
                    data = {
                        "filename": filename,
                        "is_draft": is_draft,
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
                is_draft = bool(payload.get("is_draft", False))
                title = payload.get("title", "Untitled")
                date_str = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
                categories = payload.get("categories", [])
                body = payload.get("body", "")

                target_dir = DRAFTS_DIR if is_draft else POSTS_DIR
                if not filename:
                    slug = slugify(title)
                    filename = f"{date_str}-{slug}.md" if not is_draft else f"{slug}.md"

                other_dir = POSTS_DIR if is_draft else DRAFTS_DIR
                old_other_file = os.path.join(other_dir, filename)
                if os.path.exists(old_other_file):
                    os.remove(old_other_file)

                meta = {
                    "title": title,
                    "date": f"{date_str} {datetime.now().strftime('%H:%M:%S')} +0800",
                    "categories": categories
                }
                full_content = dump_frontmatter(meta, body)
                with open(os.path.join(target_dir, filename), "w", encoding="utf-8") as fp:
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

        elif url.path == "/api/delete":
            try:
                payload = json.loads(data.decode("utf-8"))
                filename = payload.get("filename")
                is_draft = bool(payload.get("is_draft", False))
                target_dir = DRAFTS_DIR if is_draft else POSTS_DIR
                target_file = os.path.join(target_dir, filename)
                if os.path.exists(target_file):
                    os.remove(target_file)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode("utf-8"))
            return

        elif url.path == "/api/upload-image":
            try:
                import base64
                payload = json.loads(data.decode("utf-8"))
                raw_data = payload.get("data", "")
                name = payload.get("name", "image.png")
                ext = os.path.splitext(name)[1] or ".png"
                clean_name = f"img_{int(time.time())}_{slugify(os.path.splitext(name)[0])}{ext}"

                if "," in raw_data:
                    raw_data = raw_data.split(",", 1)[1]
                img_bytes = base64.b64decode(raw_data)
                img_path = os.path.join(IMAGES_DIR, clean_name)
                with open(img_path, "wb") as fp:
                    fp.write(img_bytes)

                rel_url = f"/assets/images/{clean_name}"
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True, "url": rel_url}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode("utf-8"))
            return

        elif url.path == "/api/git-pull":
            try:
                cmd = "git pull --rebase"
                proc = subprocess.run(cmd, shell=True, cwd=BLOG_DIR, capture_output=True, text=True)
                ok = (proc.returncode == 0)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": ok, "output": proc.stdout + proc.stderr}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "output": str(e)}).encode("utf-8"))
            return

        elif url.path == "/api/git-push":
            try:
                payload = json.loads(data.decode("utf-8")) if data else {}
                msg = payload.get("message", "Update blog via Linux Studio").replace('"', '\\"')
                cmd = f'git add . && git commit -m "{msg}" && git push'
                proc = subprocess.run(cmd, shell=True, cwd=BLOG_DIR, capture_output=True, text=True)
                ok = (proc.returncode == 0) or ("nothing to commit" in proc.stdout)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": ok, "output": proc.stdout + proc.stderr}).encode("utf-8"))
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
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), LinuxStudioHandler)
    print("=" * 64)
    print("🐧 LINUX TERMINAL BLOG STUDIO RUNNING!")
    print(f"👉 Local Access:   http://localhost:{PORT}")
    print(f"📱 Phone / LAN:    http://{lan_ip}:{PORT}")
    print("=" * 64)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Studio server stopped.")
