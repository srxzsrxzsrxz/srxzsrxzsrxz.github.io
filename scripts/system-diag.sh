#!/usr/bin/env bash
# ==============================================================================
# 💻 Linux System & Audio Diagnostic Report
# Checks OS, CPU, RAM, Disk, PipeWire, Soundcard, and Network status.
# ==============================================================================

set -euo pipefail

echo "=========================================================="
echo "🐧 Linux Quick Diagnostic Report ($(date '+%Y-%m-%d %H:%M:%S'))"
echo "=========================================================="

# 1. OS & Kernel
echo "📌 OS & KERNEL:"
uname -srm
grep -E '^(PRETTY_NAME)=' /etc/os-release | cut -d= -f2 | tr -d '"' || true

# 2. CPU & Memory
echo ""
echo "📌 MEMORY & CPU USAGE:"
free -h | awk 'NR==1{print "       " $0} NR==2{print "RAM:   " $0}'
echo "CPU Load (1m, 5m, 15m): $(cat /proc/loadavg | awk '{print $1, $2, $3}')"

# 3. Disk Space
echo ""
echo "📌 DISK SPACE (Root & Home):"
df -h / /home 2>/dev/null | awk 'NR==1{print $0} NR>1{print $0}'

# 4. Audio & Soundcards
echo ""
echo "📌 AUDIO HARDWARE (ALSA & PipeWire):"
if command -v arecord &>/dev/null; then
  echo "ALSA Capture Devices:"
  arecord -l 2>/dev/null | grep -E 'card [0-9]+:' || echo "  No ALSA capture devices found."
fi

if systemctl --user is-active pipewire &>/dev/null; then
  echo "PipeWire Service: ACTIVE ✅"
else
  echo "PipeWire Service: INACTIVE ❌ (Run: systemctl --user start pipewire pipewire-pulse)"
fi

# 5. Network & IP
echo ""
echo "📌 NETWORK:"
ip -4 addr show scope global | grep inet | awk '{print "IP: " $2 " (" $NF ")"}' || echo "No active IPv4 network interface."

echo "=========================================================="
echo "Report complete."
