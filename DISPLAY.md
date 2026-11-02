# Display extension · v0.4 experimental

This adds a real KDE virtual output using `krfb-virtualmonitor`, transports its VNC stream with websockify, and displays it in Safari with noVNC. It does not create a separate desktop session. Window placement is managed in KDE Display Configuration. No dummy HDMI adapter or paid service is required by this architecture.

## Install on CachyOS / Arch

Extract the archive. From the ipad-deck directory, in a terminal inside your **KDE Plasma Wayland desktop session**, run:

```bash
bash install-display.sh
bash start.sh
```

The installer uses pacman for Python, pip, Git and Krfb, installs websockify 0.13.0 into a local virtual environment, and downloads noVNC v1.6.0 from its official GitHub repository. It needs internet during installation. It does not run the companion as root, change firewall rules, or enable a system service. Existing deck action dependencies remain as documented in README.md.

On your iPad/iPhone on the same trusted home network:

1. Open `http://PC_IP:8765` in Safari and pair using the six-digit terminal code.
2. Tap **Display**, keep **1024×768**, then **Start / reconnect**.
3. Approve any KDE prompt on the PC. Open System Settings → Display Configuration. Arrange **Side-Panel** beside your main monitor; ensure displays are not mirrored. Apply.
4. Drag a window across with the PC mouse. Enable Touch control if wanted.
5. Use **Stop display** before leaving. To change resolution, stop first and then select a preset.

Fullscreen uses Safari's fullscreen API where available. Add to Home Screen is an alternative, but standalone behavior and old Safari compatibility vary. No guarantee is made for very old iPads. Start with the lowest resolution; VNC is aimed at documents/chat/utility windows, not low-latency gaming or smooth video. Audio is not streamed.

## Lifecycle and diagnostics

- Returning to Deck, losing Wi-Fi, or closing Safari leaves the display running. Reopen Display and tap Start / reconnect. This avoids moving your windows on every brief disconnect.
- Stop display or Ctrl+C in the companion terminates both managed processes. A forced kill or power failure cannot run normal cleanup.
- Only one virtual display is managed. Multiple paired devices can start/stop it; this is a single-user prototype.
- The app checks KDE Wayland, dependencies, port conflicts, process exit and listener readiness. Listener readiness does not prove successful screen capture. End-to-end rendering is confirmed only when noVNC connects and you see the desktop.
- If the screen is black, inspect the companion terminal, KDE permission prompts and Display Configuration. Confirm the physical session remains logged in. Do not run with sudo or over a bare SSH session.
- Allow TCP **8765** (app) and **6080** (browser display) only from your trusted LAN if your firewall blocks them. Krfb also uses TCP **5909**; it may listen on all interfaces. Block external access to 5909; the bridge connects over localhost. The app does not change firewall settings.
- Missing noVNC: rerun the installer. Missing websockify after install: use `bash start.sh`, which activates its executable path.

## Security boundary

This remains an **unencrypted trusted-LAN prototype**, not a secure remote desktop product. Do not port-forward any of its ports or use it on public/hotel Wi-Fi. Pairing protects the management API. The VNC connection uses a fresh random eight-character password per display session (classic VNC uses at most eight characters), but classic VNC authentication is not a modern encrypted transport. Krfb receives that password in its command arguments, visible to local users. Browser view-only mode is a convenience, not server-enforced authorization; a paired client with credentials can control the session. HTTPS/WSS and stronger access control remain future work.

## Verification and remaining hardware checks

Automated tests cover management API authentication, invalid input, unsupported environments, child-process cleanup and startup failure. Python/shell/JavaScript syntax is checked. Actual KDE output creation, NVIDIA capture, VNC negotiation, Safari rendering, touch input, fullscreen, Wi-Fi recovery and sleep/wake have **not** been tested on hardware. You need the Linux PC running to test display extension; an iPhone alone cannot create the output.

## Upstream components

- KDE Krfb: https://invent.kde.org/network/krfb (virtual monitor source: `krfb/main-virtualmonitor.cpp`)
- noVNC API: https://novnc.com/noVNC/docs/API.html
- websockify: https://github.com/novnc/websockify

Our integration remains MIT. Upstream dependencies are installed separately and retain their own licenses and notices; the installer preserves noVNC's bundled licenses.
