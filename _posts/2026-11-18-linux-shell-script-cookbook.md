---
layout: post
title: "⚡ Linux Shell Script Cookbook: Audio, Video & System Demos"
date: 2026-11-18 19:30:00 +0800
categories: [Linux, Bash, Tutorial, Audio]
---

A hands-on collection of battle-tested Bash scripts with in-depth instructions. These scripts handle **audio recording**, **YouTube MP4 downloading**, and **system hardware diagnostics** on Linux.

All scripts are located in the [`scripts/`](https://github.com/srxzsrxzsrxz/srxzsrxzsrxz.github.io/tree/main/scripts) directory of this repository and are ready to run!

---

## 🎙️ Script 1: Audio Recording with ALSA & PipeWire

Record voice notes from your microphone and immediately play them back to verify hardware audio.

### The Shell Script (`scripts/record-audio.sh`):

```bash
#!/usr/bin/env bash
set -euo pipefail

DURATION="${1:-5}"                          # Default recording duration: 5 seconds
OUTPUT_FILE="${2:-test_recording.wav}"      # Default filename
DEVICE="${3:-plughw:1,0}"                   # Card 1, Device 0 (ALC897 Analog)

echo "🎙️  Starting Audio Record (${DURATION}s) to ${OUTPUT_FILE}..."
arecord -D "${DEVICE}" -f cd -d "${DURATION}" "${OUTPUT_FILE}"

echo "🔊 Playing back audio test..."
aplay -D "${DEVICE}" "${OUTPUT_FILE}" || aplay "${OUTPUT_FILE}"
```

### 📖 Rich Flag Instruction:

| Command / Flag | Purpose & Function |
| :--- | :--- |
| `set -euo pipefail` | Strict Bash mode: halts script on error or unset variable. |
| `arecord -D plughw:1,0` | Directs ALSA to use **Sound Card 1, Device 0** (Motherboard analog mic). |
| `-f cd` | Standard CD quality: **16-bit little-endian, 44,100 Hz, Stereo**. |
| `-d 5` | Tells `arecord` to capture for exactly 5 seconds, then stop automatically. |
| `aplay` | Plays back the resulting WAV file to test speaker output. |

### 🚀 How to Run:
```bash
# Record for 5 seconds (default):
./scripts/record-audio.sh

# Record for 10 seconds to custom filename:
./scripts/record-audio.sh 10 my_voice.wav
```

---

## 🎥 Script 2: 1-Click YouTube Video MP4 Downloader

Download any YouTube video in full 1080p MP4 format with audio merged automatically.

### The Shell Script (`scripts/download-yt-mp4.sh`):

```bash
#!/usr/bin/env bash
set -euo pipefail

URL="${1:?Error: Provide a YouTube URL!}"
OUT_DIR="${2:-$HOME/Videos}"
mkdir -p "${OUT_DIR}"

yt-dlp \
  -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b" \
  --merge-output-format mp4 \
  -o "${OUT_DIR}/%(title)s.%(ext)s" \
  "${URL}"

echo "✅ Saved to ${OUT_DIR}"
```

### 📖 Rich Flag Instruction:

| Parameter | What it Does |
| :--- | :--- |
| `bv*[ext=mp4]` | Selects the **best video** stream encoded in MP4 (H.264/AVC). |
| `ba[ext=m4a]` | Selects the **best audio** stream encoded in M4A (AAC). |
| `--merge-output-format mp4` | Uses `ffmpeg` to merge the separate video and audio tracks without quality loss. |
| `-o "%(title)s.%(ext)s"` | Automatically titles the output file using the actual YouTube video title. |

### 🚀 How to Run:
```bash
./scripts/download-yt-mp4.sh "https://www.youtube.com/watch?v=jNQXAC9IVRw"
```

---

## 💻 Script 3: Instant Linux System & Audio Diagnostics

Quickly audit your operating system, memory usage, disk space, and PipeWire sound status.

### The Shell Script (`scripts/system-diag.sh`):

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== Linux System Diagnostic ==="
echo "📌 OS: $(uname -srm)"
echo "📌 RAM: $(free -h | awk 'NR==2{print $3 "/" $2}')"
echo "📌 Disk: $(df -h / | awk 'NR==2{print $3 "/" $2 " used (" $5 ")"}')"

# Audio Service Verification
if systemctl --user is-active pipewire &>/dev/null; then
  echo "📌 PipeWire Audio: ACTIVE ✅"
else
  echo "📌 PipeWire Audio: INACTIVE ❌ (Run: systemctl --user start pipewire)"
fi

echo "📌 IP: $(ip -4 addr show scope global | grep inet | awk '{print $2}')"
```

### 📖 Instruction Breakdown:

- **`free -h | awk 'NR==2{print $3 "/" $2}'`**: Extracts line 2 (RAM) and formats used vs total in human-readable gigabytes (e.g. `2.4G/15G`).
- **`systemctl --user is-active pipewire`**: Queries the user systemd daemon to verify if the modern Linux audio server is running.
- **`ip -4 addr show scope global`**: Filters network cards to show only external/LAN IPv4 addresses, skipping loopback `127.0.0.1`.

---

## 💡 Best Practices for Writing Linux Shell Scripts

1. **Always use a Shebang**: Start with `#!/usr/bin/env bash` for cross-distribution compatibility.
2. **Enable Strict Mode**: Adding `set -euo pipefail` catches typos and prevents silent failures.
3. **Set Execution Permissions**: Remember to run `chmod +x your_script.sh` before executing with `./your_script.sh`.
4. **Parameter Defaults**: Use `${1:-default_value}` to set clean fallbacks if arguments are omitted.
