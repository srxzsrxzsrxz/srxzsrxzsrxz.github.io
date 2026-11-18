#!/usr/bin/env bash
# ==============================================================================
# 🎥 1-Click YouTube MP4 Downloader
# Downloads the highest quality video and audio merged into an MP4 container.
# ==============================================================================

set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <YouTube_URL> [output_directory]"
  echo "Example: $0 'https://www.youtube.com/watch?v=jNQXAC9IVRw' ~/Videos"
  exit 1
fi

URL="$1"
OUT_DIR="${2:-$HOME/Videos}"
mkdir -p "${OUT_DIR}"

echo "======================================================"
echo "🎥 YouTube MP4 Downloader (yt-dlp)"
echo "🔗 URL        : ${URL}"
echo "📁 Destination: ${OUT_DIR}"
echo "======================================================"

# Check if yt-dlp is installed
if ! command -v yt-dlp &>/dev/null; then
  echo "❌ Error: yt-dlp is not installed."
  echo "👉 Install with: sudo dnf install -y yt-dlp   (or: pipx install yt-dlp)"
  exit 1
fi

# yt-dlp flags:
#   -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b" : Best MP4 video + M4A audio
#   --merge-output-format mp4                   : Combine streams into .mp4
#   -o "%(title)s.%(ext)s"                      : Use video title as filename
yt-dlp \
  -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b" \
  --merge-output-format mp4 \
  -o "${OUT_DIR}/%(title)s.%(ext)s" \
  "${URL}"

echo ""
echo "✅ Download complete! Saved to ${OUT_DIR}"
