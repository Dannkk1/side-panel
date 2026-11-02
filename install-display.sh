#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [[ ${EUID} == 0 ]]; then
  echo 'Run as your normal desktop user, not with sudo.' >&2
  exit 1
fi
# Only OS dependencies require elevation. Python dependencies stay in this project.
sudo pacman -S --needed python python-pip git krfb
python -m venv .venv
echo 'Installing display bridge (requires internet)…'
.venv/bin/python -m pip --disable-pip-version-check install --timeout 20 --retries 1 'websockify==0.13.0'
mkdir -p static/vendor
if [[ ! -e static/vendor/novnc ]]; then
  tmpdir=$(mktemp -d)
  trap 'rm -rf -- "$tmpdir"' EXIT
  git clone --depth 1 --branch v1.6.0 https://github.com/novnc/noVNC.git "$tmpdir/novnc"
  rm -rf -- "$tmpdir/novnc/.git"
  mv -- "$tmpdir/novnc" static/vendor/novnc
fi
test -f static/vendor/novnc/core/rfb.js
python scripts/patch_cursor.py
printf '\nInstalled. Run: bash start.sh\n'
