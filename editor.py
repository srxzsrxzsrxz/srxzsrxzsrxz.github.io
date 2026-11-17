#!/usr/bin/env python3
"""
Advanced Local Blog Studio & Editor for Jekyll / GitHub Pages
Full-featured, standalone web application. Zero external dependencies.
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
  <title>Blog Studio Pro &middot; srxz</title>
  <!-- Marked.js, Highlight.js for code syntax highlighting -->
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/atom-one-dark.min.css">
  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>
  <style>
    :root {
      --bg: #0b0f19;
      --sidebar: #111827;
      --card: #1f293d;
      --border: #2e3a50;
      --text: #f3f4f6;
      --text-muted: #94a3b8;
      --accent: #6366f1;
      --accent-hover: #4f46e5;
      --success: #10b981;
      --danger: #ef4444;
      --warning: #f59e0b;
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
      width: 320px;
      background: var(--sidebar);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      transition: all 0.25s ease;
    }
    #sidebar.collapsed { margin-left: -320px; }

    .sidebar-top {
      padding: 16px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .brand { font-size: 1.15rem; font-weight: 700; display: flex; align-items: center; gap: 8px; }
    .brand-icon { background: linear-gradient(135deg, #6366f1, #a855f7); width: 28px; height: 28px; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center; }

    .tabs {
      display: flex;
      border-bottom: 1px solid var(--border);
      background: #0d1320;
    }
    .tab-btn {
      flex: 1;
      padding: 10px;
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-weight: 600;
      font-size: 0.85rem;
      border-bottom: 2px solid transparent;
      transition: 0.2s;
    }
    .tab-btn.active { color: var(--accent); border-bottom-color: var(--accent); background: var(--sidebar); }

    .sidebar-actions {
      padding: 10px 14px;
      display: flex;
      gap: 8px;
    }
    .search-input {
      width: 100%;
      background: #090d16;
      border: 1px solid var(--border);
      color: var(--text);
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 0.85rem;
      outline: none;
    }
    .search-input:focus { border-color: var(--accent); }

    .posts-list {
      flex: 1;
      overflow-y: auto;
      padding: 10px 14px;
    }
    .post-item {
      padding: 12px 14px;
      margin-bottom: 8px;
      border-radius: 10px;
      background: #141c2d;
      border: 1px solid transparent;
      cursor: pointer;
      transition: all 0.2s ease;
      position: relative;
    }
    .post-item:hover { border-color: var(--accent); transform: translateX(2px); }
    .post-item.active { background: #1e293b; border-color: var(--accent); box-shadow: 0 4px 12px rgba(99,102,241,0.15); }
    .post-title { font-weight: 600; font-size: 0.95rem; margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .post-meta { font-size: 0.78rem; color: var(--text-muted); display: flex; justify-content: space-between; }
    .delete-btn {
      position: absolute;
      right: 10px;
      top: 10px;
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      display: none;
      padding: 4px;
      border-radius: 4px;
    }
    .post-item:hover .delete-btn { display: block; }
    .delete-btn:hover { color: var(--danger); }

    /* Main Canvas */
    #main {
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
      background: var(--bg);
    }

    /* Top Control Bar */
    .topbar {
      height: 60px;
      background: var(--sidebar);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 18px;
      gap: 12px;
    }
    .topbar-left { display: flex; align-items: center; gap: 10px; }
    .topbar-right { display: flex; align-items: center; gap: 10px; }

    .btn {
      padding: 7px 14px;
      border-radius: 8px;
      font-size: 0.88rem;
      font-weight: 600;
      border: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: 0.2s;
    }
    .btn-primary { background: var(--accent); color: white; }
    .btn-primary:hover { background: var(--accent-hover); }
    .btn-success { background: var(--success); color: white; }
    .btn-success:hover { background: #059669; }
    .btn-outline { background: transparent; border: 1px solid var(--border); color: var(--text); }
    .btn-outline:hover { background: #1e293b; border-color: var(--accent); }
    .btn-danger { background: transparent; border: 1px solid #7f1d1d; color: #f87171; }
    .btn-danger:hover { background: #7f1d1d; color: white; }

    /* Metadata Bar */
    .meta-bar {
      padding: 10px 18px;
      background: #101625;
      border-bottom: 1px solid var(--border);
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
    }
    .meta-bar input {
      background: #090d16;
      border: 1px solid var(--border);
      color: var(--text);
      padding: 7px 12px;
      border-radius: 8px;
      font-size: 0.9rem;
      outline: none;
    }
    .meta-bar input:focus { border-color: var(--accent); }
    #post-title-input { flex: 2; font-weight: 700; font-size: 1rem; }
    #post-date-input { width: 135px; }
    #post-tags-input { flex: 1; }

    /* Toolbar */
    .toolbar {
      padding: 8px 18px;
      background: #0c121e;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }
    .tool-group { display: flex; align-items: center; gap: 4px; border-right: 1px solid var(--border); padding-right: 8px; margin-right: 4px; }
    .tool-icon {
      background: transparent;
      border: 1px solid transparent;
      color: var(--text);
      padding: 5px 9px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.85rem;
    }
    .tool-icon:hover { background: #1f293d; border-color: var(--border); }
    .tool-badge { background: #1f293d; font-size: 0.75rem; padding: 2px 8px; border-radius: 12px; color: var(--text-muted); }

    /* Editor + Preview Split View */
    .workspace {
      flex: 1;
      display: flex;
      height: calc(100vh - 170px);
      overflow: hidden;
      position: relative;
    }
    .editor-pane {
      flex: 1;
      display: flex;
      flex-direction: column;
      border-right: 1px solid var(--border);
      background: #080c14;
      position: relative;
    }
    #editor {
      flex: 1;
      width: 100%;
      height: 100%;
      background: transparent;
      color: #f8fafc;
      border: none;
      padding: 24px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 1.02rem;
      line-height: 1.7;
      resize: none;
      outline: none;
      overflow-y: auto;
    }
    .preview-pane {
      flex: 1;
      padding: 30px;
      overflow-y: auto;
      background: var(--bg);
      line-height: 1.8;
      transition: width 0.2s ease;
    }

    /* Markdown Styling in Preview */
    .preview-pane h1, .preview-pane h2, .preview-pane h3 { margin: 26px 0 14px; font-weight: 700; color: #fff; }
    .preview-pane p { margin-bottom: 16px; }
    .preview-pane blockquote {
      border-left: 4px solid var(--accent);
      padding: 10px 18px;
      background: #141c2d;
      border-radius: 0 8px 8px 0;
      color: var(--text-muted);
      margin: 20px 0;
    }
    .preview-pane table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    .preview-pane th, .preview-pane td { border: 1px solid var(--border); padding: 8px 14px; text-align: left; }
    .preview-pane th { background: #141c2d; }
    .preview-pane pre {
      background: #161f30 !important;
      border: 1px solid var(--border);
      padding: 16px;
      border-radius: 10px;
      overflow-x: auto;
      margin: 20px 0;
    }
    .preview-pane img { max-width: 100%; border-radius: 10px; margin: 16px 0; box-shadow: 0 8px 16px rgba(0,0,0,0.3); }
    .preview-pane iframe { width: 100%; aspect-ratio: 16/9; border-radius: 10px; margin: 20px 0; border: none; }

    /* Drag & Drop Overlay */
    #drop-zone {
      position: absolute;
      inset: 0;
      background: rgba(99, 102, 241, 0.85);
      backdrop-filter: blur(4px);
      display: none;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      gap: 12px;
      z-index: 50;
      color: white;
      font-size: 1.3rem;
      font-weight: 700;
      pointer-events: none;
    }

    /* Footer Stats Bar */
    .footer-bar {
      height: 28px;
      background: #0a0e17;
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      font-size: 0.78rem;
      color: var(--text-muted);
    }
    .footer-bar a { color: var(--accent); text-decoration: none; }

    /* Modal */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.7);
      backdrop-filter: blur(4px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }
    .modal {
      background: #161f30;
      border: 1px solid var(--border);
      border-radius: 14px;
      width: 480px;
      max-width: 90vw;
      padding: 24px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }
    .modal-title { font-size: 1.2rem; font-weight: 700; margin-bottom: 14px; }
    .modal-body { margin-bottom: 20px; }
    .modal-input {
      width: 100%;
      background: #090d16;
      border: 1px solid var(--border);
      color: var(--text);
      padding: 10px 14px;
      border-radius: 8px;
      margin-top: 8px;
      font-size: 0.95rem;
      outline: none;
    }
    .modal-footer { display: flex; justify-content: flex-end; gap: 10px; }

    /* Notification Toast */
    #toast {
      position: fixed;
      bottom: 40px;
      right: 24px;
      background: #1e293b;
      border: 1px solid var(--border);
      padding: 12px 20px;
      border-radius: 10px;
      color: white;
      font-weight: 500;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      display: none;
      z-index: 2000;
      animation: fadeIn 0.2s ease;
    }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    /* Zen Mode */
    body.zen-mode #sidebar,
    body.zen-mode .topbar,
    body.zen-mode .meta-bar,
    body.zen-mode .preview-pane { display: none !important; }
    body.zen-mode .editor-pane { width: 100vw; max-width: 800px; margin: 0 auto; border: none; }
  </style>
</head>
<body>
  <!-- Sidebar -->
  <aside id="sidebar">
    <div class="sidebar-top">
      <div class="brand">
        <span class="brand-icon">⚡</span>
        <span>Blog Studio</span>
      </div>
      <button class="btn btn-outline" style="padding:4px 8px;" onclick="toggleSidebar()" title="Collapse">◀</button>
    </div>

    <!-- Mode Tabs: Published vs Drafts -->
    <div class="tabs">
      <button class="tab-btn active" id="tab-published" onclick="switchTab('published')">Published (<span id="pub-count">0</span>)</button>
      <button class="tab-btn" id="tab-drafts" onclick="switchTab('drafts')">Drafts (<span id="draft-count">0</span>)</button>
    </div>

    <div class="sidebar-actions">
      <input type="text" class="search-input" id="search-box" placeholder="🔍 Search posts or tags..." oninput="filterPosts()">
    </div>

    <div style="padding: 0 14px 10px; display:flex; gap:8px;">
      <button class="btn btn-primary" style="flex:1;" onclick="createNewPost(false)">+ New Post</button>
      <button class="btn btn-outline" onclick="createNewPost(true)" title="New Draft">Draft</button>
    </div>

    <div class="posts-list" id="posts-list"></div>
  </aside>

  <!-- Main Canvas -->
  <main id="main">
    <!-- Topbar -->
    <div class="topbar">
      <div class="topbar-left">
        <button class="btn btn-outline" onclick="toggleSidebar()" title="Toggle Sidebar">☰</button>
        <span id="file-status-indicator" style="font-size:0.85rem; color:var(--text-muted);">● Saved</span>
      </div>
      <div class="topbar-right">
        <button class="btn btn-outline" onclick="gitPull()" id="pull-btn" title="Sync changes from phone/GitHub">⬇️ Pull</button>
        <button class="btn btn-outline" onclick="savePost()" title="Save changes">💾 Save</button>
        <button class="btn btn-success" onclick="openPushModal()" id="push-btn">🚀 Git Push</button>
      </div>
    </div>

    <!-- Metadata Bar -->
    <div class="meta-bar">
      <input type="text" id="post-title-input" placeholder="Article Title..." oninput="markUnsaved()">
      <input type="date" id="post-date-input" onchange="markUnsaved()">
      <input type="text" id="post-tags-input" placeholder="Tags / Categories (e.g. vlog, tech, daily)" oninput="markUnsaved()">
      <button class="btn btn-outline" style="font-size:0.8rem; padding:6px 10px;" onclick="toggleDraftStatus()" id="draft-toggle-btn">Move to Drafts</button>
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="tool-group">
        <button class="tool-icon" onclick="wrapText('**', '**')" title="Bold"><b>B</b></button>
        <button class="tool-icon" onclick="wrapText('*', '*')" title="Italic"><i>I</i></button>
        <button class="tool-icon" onclick="wrapText('~~', '~~')" title="Strikethrough"><s>S</s></button>
      </div>
      <div class="tool-group">
        <button class="tool-icon" onclick="insertLine('## ')" title="Heading 2">H2</button>
        <button class="tool-icon" onclick="insertLine('### ')" title="Heading 3">H3</button>
        <button class="tool-icon" onclick="insertLine('> ')" title="Quote">Quote</button>
        <button class="tool-icon" onclick="wrapText('`', '`')" title="Inline Code">Code</button>
        <button class="tool-icon" onclick="insertCodeBlock()" title="Code Block">&lt;/&gt;</button>
      </div>
      <div class="tool-group">
        <button class="tool-icon" onclick="openYoutubeModal()" title="Insert YouTube Vlog">🎥 Vlog</button>
        <button class="tool-icon" onclick="document.getElementById('file-upload').click()" title="Upload Image">🖼️ Image</button>
        <button class="tool-icon" onclick="insertTable()" title="Insert Table">📊 Table</button>
        <button class="tool-icon" onclick="insertCallout()" title="Note / Tip / Alert">💡 Callout</button>
      </div>
      <input type="file" id="file-upload" accept="image/*" style="display:none;" onchange="handleImageFile(this.files[0])">
      <span style="flex:1;"></span>
      <button class="tool-icon" onclick="toggleZenMode()" title="Zen / Fullscreen Mode">🧘 Zen</button>
      <button class="tool-icon" onclick="togglePreviewSplit()" id="preview-toggle-btn" title="Toggle Preview">👁️ Preview</button>
    </div>

    <!-- Workspace -->
    <div class="workspace" id="workspace">
      <div class="editor-pane" id="editor-pane">
        <textarea id="editor" placeholder="Write markdown here... (Drag & Drop or Ctrl+V images directly!)"></textarea>
        <div id="drop-zone">
          <span>📥 Drop Image to Upload</span>
        </div>
      </div>
      <div class="preview-pane" id="preview-pane"></div>
    </div>

    <!-- Footer Stats -->
    <footer class="footer-bar">
      <div>
        <span id="word-count">0 words</span> &middot;
        <span id="read-time">1 min read</span> &middot;
        <span id="char-count">0 chars</span>
      </div>
      <div>
        <a href="https://srxzsrxzsrxz.github.io" target="_blank">🌐 View Live Blog &rarr;</a>
      </div>
    </footer>
  </main>

  <!-- YouTube Modal -->
  <div class="modal-backdrop" id="yt-modal">
    <div class="modal">
      <div class="modal-title">🎥 Embed YouTube Vlog</div>
      <div class="modal-body">
        <label>YouTube Video Link or ID:</label>
        <input type="text" class="modal-input" id="yt-url-input" placeholder="e.g. https://www.youtube.com/watch?v=jNQXAC9IVRw">
      </div>
      <div class="modal-footer">
        <button class="btn btn-outline" onclick="closeModal('yt-modal')">Cancel</button>
        <button class="btn btn-primary" onclick="confirmYoutubeEmbed()">Insert Video</button>
      </div>
    </div>
  </div>

  <!-- Git Push Modal -->
  <div class="modal-backdrop" id="push-modal">
    <div class="modal">
      <div class="modal-title">🚀 Publish to GitHub Pages</div>
      <div class="modal-body">
        <label>Commit Message:</label>
        <input type="text" class="modal-input" id="commit-msg-input" value="Update blog via Studio">
      </div>
      <div class="modal-footer">
        <button class="btn btn-outline" onclick="closeModal('push-modal')">Cancel</button>
        <button class="btn btn-success" id="confirm-push-btn" onclick="confirmGitPush()">Push & Publish</button>
      </div>
    </div>
  </div>

  <div id="toast"></div>

  <script>
    let currentTab = "published";
    let currentFilename = "";
    let isCurrentDraft = false;
    let allPosts = [];
    let isUnsaved = false;

    const editor = document.getElementById('editor');
    const preview = document.getElementById('preview-pane');
    const titleInput = document.getElementById('post-title-input');
    const dateInput = document.getElementById('post-date-input');
    const tagsInput = document.getElementById('post-tags-input');

    // Syntax highlighting config with marked
    marked.setOptions({
      highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
          return hljs.highlight(code, { language: lang }).value;
        }
        return hljs.highlightAuto(code).value;
      },
      breaks: true
    });

    editor.addEventListener('input', () => {
      markUnsaved();
      renderPreview();
      updateStats();
    });

    function markUnsaved() {
      isUnsaved = true;
      document.getElementById('file-status-indicator').textContent = '○ Unsaved changes';
      document.getElementById('file-status-indicator').style.color = 'var(--warning)';
    }

    function markSaved() {
      isUnsaved = false;
      document.getElementById('file-status-indicator').textContent = '● Saved';
      document.getElementById('file-status-indicator').style.color = 'var(--success)';
    }

    function renderPreview() {
      const text = editor.value;
      preview.innerHTML = marked.parse(text || "*Start writing to see live preview...*");
    }

    function updateStats() {
      const text = editor.value.trim();
      const words = text ? text.split(/\\s+/).length : 0;
      const chars = text.length;
      const readMin = Math.max(1, Math.ceil(words / 200));
      document.getElementById('word-count').textContent = words + ' words';
      document.getElementById('char-count').textContent = chars + ' chars';
      document.getElementById('read-time').textContent = readMin + ' min read';
    }

    function showToast(msg, isErr = false) {
      const toast = document.getElementById('toast');
      toast.textContent = msg;
      toast.style.borderColor = isErr ? 'var(--danger)' : 'var(--success)';
      toast.style.display = 'block';
      setTimeout(() => { toast.style.display = 'none'; }, 3500);
    }

    // Load Posts
    async function fetchPosts() {
      try {
        const res = await fetch('/api/posts');
        const data = await res.json();
        allPosts = data;
        document.getElementById('pub-count').textContent = data.filter(p => !p.is_draft).length;
        document.getElementById('draft-count').textContent = data.filter(p => p.is_draft).length;
        renderPostsList();
      } catch (err) {
        showToast("Error loading posts", true);
      }
    }

    function switchTab(tab) {
      currentTab = tab;
      document.getElementById('tab-published').classList.toggle('active', tab === 'published');
      document.getElementById('tab-drafts').classList.toggle('active', tab === 'drafts');
      renderPostsList();
    }

    function renderPostsList() {
      const listEl = document.getElementById('posts-list');
      const query = document.getElementById('search-box').value.toLowerCase();
      const filtered = allPosts.filter(p => {
        const matchesTab = currentTab === 'drafts' ? p.is_draft : !p.is_draft;
        const matchesQuery = (p.title || '').toLowerCase().includes(query) || (p.categories || []).some(c => c.toLowerCase().includes(query));
        return matchesTab && matchesQuery;
      });

      listEl.innerHTML = "";
      if (filtered.length === 0) {
        listEl.innerHTML = '<div style="color:var(--text-muted); font-size:0.85rem; text-align:center; padding:20px;">No articles found</div>';
        return;
      }

      filtered.forEach(p => {
        const item = document.createElement('div');
        item.className = 'post-item' + (p.filename === currentFilename ? ' active' : '');
        item.innerHTML = `
          <button class="delete-btn" onclick="event.stopPropagation(); deletePost('${p.filename}', ${p.is_draft})" title="Delete">🗑️</button>
          <div class="post-title">${p.title || p.filename}</div>
          <div class="post-meta">
            <span>📅 ${p.date || ''}</span>
            <span>🏷️ ${(p.categories || []).slice(0, 2).join(', ')}</span>
          </div>
        `;
        item.onclick = () => loadPost(p.filename, p.is_draft);
        listEl.appendChild(item);
      });
    }

    function filterPosts() {
      renderPostsList();
    }

    async function loadPost(filename, isDraft) {
      if (isUnsaved && !confirm("You have unsaved changes. Discard and switch post?")) return;
      try {
        const res = await fetch(`/api/post?name=${encodeURIComponent(filename)}&is_draft=${isDraft}`);
        const data = await res.json();
        currentFilename = filename;
        isCurrentDraft = isDraft;
        titleInput.value = data.title || "";
        dateInput.value = data.date || new Date().toISOString().split('T')[0];
        tagsInput.value = (data.categories || []).join(', ');
        editor.value = data.body || "";
        document.getElementById('draft-toggle-btn').textContent = isDraft ? "Publish to Posts" : "Move to Drafts";
        markSaved();
        renderPreview();
        updateStats();
        renderPostsList();
      } catch (err) {
        showToast("Error loading file", true);
      }
    }

    function createNewPost(isDraft = false) {
      if (isUnsaved && !confirm("Discard unsaved changes?")) return;
      currentFilename = "";
      isCurrentDraft = isDraft;
      titleInput.value = "";
      dateInput.value = new Date().toISOString().split('T')[0];
      tagsInput.value = "";
      editor.value = "# Hello World\\n\\nStart writing your new post or vlog note...";
      document.getElementById('draft-toggle-btn').textContent = isDraft ? "Publish to Posts" : "Move to Drafts";
      titleInput.focus();
      markSaved();
      renderPreview();
      updateStats();
      renderPostsList();
    }

    async function savePost() {
      const title = titleInput.value.trim();
      if (!title) {
        showToast("Please enter an article title!", true);
        titleInput.focus();
        return;
      }
      const date = dateInput.value || new Date().toISOString().split('T')[0];
      const categories = tagsInput.value.split(',').map(s => s.trim()).filter(Boolean);
      const body = editor.value;

      try {
        const res = await fetch('/api/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            filename: currentFilename,
            is_draft: isCurrentDraft,
            title, date, categories, body
          })
        });
        const resData = await res.json();
        if (resData.ok) {
          currentFilename = resData.filename;
          markSaved();
          showToast("💾 Saved successfully!");
          await fetchPosts();
        } else {
          showToast("Failed to save: " + resData.error, true);
        }
      } catch (err) {
        showToast("Network error saving post", true);
      }
    }

    async function deletePost(filename, isDraft) {
      if (!confirm(`Are you sure you want to delete ${filename}?`)) return;
      try {
        const res = await fetch('/api/delete', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename, is_draft: isDraft })
        });
        const d = await res.json();
        if (d.ok) {
          showToast("🗑️ Post deleted");
          if (currentFilename === filename) createNewPost(false);
          await fetchPosts();
        }
      } catch (e) {
        showToast("Error deleting file", true);
      }
    }

    function toggleDraftStatus() {
      isCurrentDraft = !isCurrentDraft;
      document.getElementById('draft-toggle-btn').textContent = isCurrentDraft ? "Publish to Posts" : "Move to Drafts";
      savePost();
    }

    // Git Operations
    async function gitPull() {
      const btn = document.getElementById('pull-btn');
      btn.textContent = "⏳ Pulling...";
      btn.disabled = true;
      try {
        const res = await fetch('/api/git-pull', { method: 'POST' });
        const data = await res.json();
        if (data.ok) {
          showToast("✅ Successfully pulled latest changes!");
          fetchPosts();
        } else {
          showToast("Pull failed: " + data.output, true);
        }
      } catch (err) {
        showToast("Network error pulling Git", true);
      } finally {
        btn.textContent = "⬇️ Pull";
        btn.disabled = false;
      }
    }

    function openPushModal() {
      document.getElementById('push-modal').style.display = 'flex';
    }

    async function confirmGitPush() {
      const msg = document.getElementById('commit-msg-input').value.trim() || "Update blog via Studio";
      const btn = document.getElementById('confirm-push-btn');
      btn.textContent = "⏳ Pushing...";
      btn.disabled = true;
      try {
        // Save first
        await savePost();
        const res = await fetch('/api/git-push', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: msg })
        });
        const data = await res.json();
        if (data.ok) {
          closeModal('push-modal');
          showToast("🚀 Successfully deployed to GitHub Pages!");
        } else {
          showToast("Push failed: " + data.output, true);
        }
      } catch (e) {
        showToast("Network error pushing to Git", true);
      } finally {
        btn.textContent = "Push & Publish";
        btn.disabled = false;
      }
    }

    // Image Upload (Paste / Drag & Drop / File Input)
    async function handleImageFile(file) {
      if (!file || !file.type.startsWith('image/')) return;
      showToast("⏳ Uploading image...");
      const reader = new FileReader();
      reader.onload = async () => {
        try {
          const res = await fetch('/api/upload-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              name: file.name,
              data: reader.result
            })
          });
          const d = await res.json();
          if (d.ok) {
            wrapText(`![${file.name}](${d.url})\\n`);
            showToast("🖼️ Image uploaded & inserted!");
          } else {
            showToast("Upload failed: " + d.error, true);
          }
        } catch (e) {
          showToast("Error uploading image", true);
        }
      };
      reader.readAsDataURL(file);
    }

    // Clipboard Paste Listener
    editor.addEventListener('paste', (e) => {
      const items = (e.clipboardData || e.originalEvent.clipboardData).items;
      for (const item of items) {
        if (item.kind === 'file' && item.type.startsWith('image/')) {
          e.preventDefault();
          const file = item.getAsFile();
          handleImageFile(file);
          return;
        }
      }
    });

    // Drag and Drop Images Listener
    const dropZone = document.getElementById('drop-zone');
    const editorPane = document.getElementById('editor-pane');

    ['dragenter', 'dragover'].forEach(name => {
      editorPane.addEventListener(name, (e) => { e.preventDefault(); dropZone.style.display = 'flex'; });
    });
    ['dragleave', 'drop'].forEach(name => {
      editorPane.addEventListener(name, (e) => { e.preventDefault(); dropZone.style.display = 'none'; });
    });
    editorPane.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0) handleImageFile(files[0]);
    });

    // Markdown Formatter Helpers
    function wrapText(before, after = "") {
      const start = editor.selectionStart;
      const end = editor.selectionEnd;
      const text = editor.value;
      const sel = text.substring(start, end);
      editor.setRangeText(before + sel + after, start, end, 'end');
      markUnsaved();
      renderPreview();
      editor.focus();
    }

    function insertLine(prefix) {
      const start = editor.selectionStart;
      const text = editor.value;
      const lineStart = text.lastIndexOf('\\n', start - 1) + 1;
      editor.setRangeText(prefix, lineStart, lineStart, 'end');
      markUnsaved();
      renderPreview();
      editor.focus();
    }

    function insertCodeBlock() {
      wrapText('\\n```javascript\\n', '\\n```\\n');
    }

    function insertTable() {
      wrapText('\\n| Column 1 | Column 2 | Column 3 |\\n| -------- | -------- | -------- |\\n| Item 1   | Value 1  | Info 1   |\\n| Item 2   | Value 2  | Info 2   |\\n');
    }

    function insertCallout() {
      wrapText('\\n> [!NOTE]\\n> Write your alert or special note here.\\n');
    }

    function openYoutubeModal() {
      document.getElementById('yt-modal').style.display = 'flex';
      document.getElementById('yt-url-input').focus();
    }

    function confirmYoutubeEmbed() {
      const url = document.getElementById('yt-url-input').value.trim();
      if (!url) return;
      let vid = url;
      if (url.includes('youtu.be/')) vid = url.split('youtu.be/')[1].split(/[?#]/)[0];
      else if (url.includes('watch?v=')) vid = url.split('watch?v=')[1].split('&')[0];

      wrapText(`\\n<iframe width="100%" height="380" src="https://www.youtube.com/embed/${vid}" frameborder="0" allowfullscreen></iframe>\\n`);
      closeModal('yt-modal');
      document.getElementById('yt-url-input').value = "";
    }

    function closeModal(id) {
      document.getElementById(id).style.display = 'none';
    }

    function toggleSidebar() {
      document.getElementById('sidebar').classList.toggle('collapsed');
    }

    function toggleZenMode() {
      document.body.classList.toggle('zen-mode');
    }

    function togglePreviewSplit() {
      const prev = document.getElementById('preview-pane');
      const isVisible = prev.style.display !== 'none';
      prev.style.display = isVisible ? 'none' : 'block';
      document.getElementById('preview-toggle-btn').style.opacity = isVisible ? '0.5' : '1';
    }

    // Keyboard Shortcuts: Ctrl+S to save
    window.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        savePost();
      }
    });

    // Init
    dateInput.value = new Date().toISOString().split('T')[0];
    fetchPosts().then(() => {
      if (allPosts.length > 0) loadPost(allPosts[0].filename, allPosts[0].is_draft);
      else createNewPost(false);
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

class StudioHandler(http.server.SimpleHTTPRequestHandler):
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

                # If moving between drafts and posts, remove old file from other directory
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
                msg = payload.get("message", "Update blog via Studio").replace('"', '\\"')
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
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), StudioHandler)
    print("=" * 64)
    print("✨ Blog Studio Pro is Running!")
    print(f"🖥️  Local PC Access:   http://localhost:{PORT}")
    print(f"📱 Phone / LAN Access: http://{lan_ip}:{PORT}")
    print("=" * 64)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Studio server.")
