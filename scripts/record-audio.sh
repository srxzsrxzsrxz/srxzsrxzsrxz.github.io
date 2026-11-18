#!/usr/bin/env bash
# ==============================================================================
# 🎙️ Linux Quick Audio Recorder Demo
# Uses ALSA (arecord) and PipeWire to record voice from your microphone.
# ==============================================================================

set -euo pipefail

DURATION="${1:-5}"                          # Default recording duration: 5 seconds
OUTPUT_FILE="${2:-test_recording.wav}"      # Default filename
DEVICE="${3:-plughw:1,0}"                   # Card 1, Device 0 (ALC897 Analog)

echo "======================================================"
echo "🎙️  Starting Audio Record Test (${DURATION} seconds)"
echo "📁  Output File : ${OUTPUT_FILE}"
echo "🎛️  Device      : ${DEVICE}"
echo "======================================================"
echo "Speak into your microphone now..."

# arecord flags explained:
#   -D : ALSA device identifier (plughw:1,0 selects Card 1, Device 0)
#   -f : format (cd = 16-bit little-endian, 44100 Hz, stereo)
#   -d : duration in seconds
arecord -D "${DEVICE}" -f cd -d "${DURATION}" "${OUTPUT_FILE}"

echo ""
echo "✅ Recording complete: ${OUTPUT_FILE} ($(du -h "${OUTPUT_FILE}" | cut -f1))"
echo "🔊 Playing back audio test..."

# Playback test
aplay -D "${DEVICE}" "${OUTPUT_FILE}" || aplay "${OUTPUT_FILE}" || true

echo "======================================================"
echo "✨ Done! If you heard your voice, your mic is working."
