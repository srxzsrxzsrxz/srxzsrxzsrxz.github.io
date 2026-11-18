# srxz.io 🌸 💻

[![Deploy Jekyll to GitHub Pages](https://github.com/srxzsrxzsrxz/srxzsrxzsrxz.github.io/actions/workflows/deploy.yml/badge.svg)](https://github.com/srxzsrxzsrxz/srxzsrxzsrxz.github.io/actions/workflows/deploy.yml)

Anime Cosplay & Cyberpunk Linux Blog hosted on GitHub Pages:
👉 **https://srxzsrxzsrxz.github.io**

---

## ⚡ CI/CD (Continuous Integration & Auto Deployment)

This repository includes a full automated CI/CD pipeline in [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml):

- **Auto CI**: On every `git push` to `main`, GitHub Actions automatically checks out the repo and builds the site.
- **Auto CD**: Deploys the built artifact directly to GitHub Pages without manual intervention.
- **Actions Visibility**: Check real-time build progress and deployment status under the repository's [Actions Tab](https://github.com/srxzsrxzsrxz/srxzsrxzsrxz.github.io/actions).

> **Important**: In your GitHub Repository, go to **Settings &rarr; Pages &rarr; Build and deployment &rarr; Source**, and select **GitHub Actions** to let this workflow handle deployments.

---

## 🐧 Linux Man Documentation Viewer

Browse and search 35+ essential Linux manual pages (including `arecord`, `aplay`, `ffmpeg`, `yt-dlp`, `grep`, `systemctl`, `sed`, `git`, etc.) directly on the site:
👉 **https://srxzsrxzsrxz.github.io/man/**

---

## 📝 Writing & Updating Posts

### Option 1: Linux Terminal Studio (Recommended)
Run the built-in Neovim-style local studio:
```bash
./run-editor.sh
```
- Open `http://localhost:5500` in your browser.
- Features: Real-time Markdown preview, line numbers, Vim commands (`:w`, `:push`, `:pull`, `:man <cmd>`), image paste (`Ctrl+V`), and 1-click Git push.

### Option 2: Mobile / Web
- **Pages CMS**: Open [app.pagescms.org](https://app.pagescms.org) &rarr; sign in with GitHub &rarr; pick this repo.
- **GitHub Mobile App / Web**: Edit files in `_posts/` and commit. Auto CD will deploy changes in ~60 seconds.
