#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [[ ${EUID} == 0 ]]; then
  echo 'Run bash install.sh as your normal desktop user, not with sudo.' >&2
  exit 1
fi
if ! command -v pacman >/dev/null; then
  echo 'This beta installer supports CachyOS/Arch Linux only.' >&2
  exit 1
fi
sudo pacman -S --needed python wireplumber playerctl obs-studio xdg-utils
bash install-display.sh
printf '\nSide Panel is ready. Start it with: bash start.sh\n'
