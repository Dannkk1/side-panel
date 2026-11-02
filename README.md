# Side Panel

**Give your tablet a place beside your PC.**

Turn your iPad or phone into a customizable control deck and an extra display for Linux. Free, open source, and hosted on your own PC.

> **Beta · v0.4.1** — Display extension and the server-drawn cursor workaround have been reported working by the creator on CachyOS/KDE Wayland. Other hardware and older Safari versions still need testing. This is a trusted-home-network prototype with unencrypted connections.

## What it does

- **Custom control deck:** create, edit, delete and reorder up to 60 buttons, with names, emoji and colours.
- **Useful actions:** microphone/speaker mute, volume, music playback, next/previous track, OBS launch and screen lock.
- **Your own buttons:** launch apps or commands, or open websites on your PC.
- **Second display:** move windows onto your tablet using KDE’s virtual monitor and a Safari-compatible noVNC viewer.
- **Easy pairing:** type a six-digit code once; the browser remembers its credential.
- **Display controls:** resolution presets, reconnect, optional touch input and fullscreen where the browser supports it.
- **Local operation:** no account, subscription or analytics. Internet is needed to install dependencies.

## Requirements

- CachyOS or Arch Linux with **KDE Plasma on Wayland** for display extension.
- A phone/tablet browser that can run the bundled noVNC version. Very old Safari versions are not guaranteed.
- PC and tablet on the same trusted home network. Ethernet on the PC and strong Wi-Fi on the tablet are recommended.

Windows/macOS hosts and other Linux desktops are not supported by this beta’s display mode. VNC is intended for chat, documents and utility windows; expect latency with games/video. Audio is not streamed.

## Install and start

This release uses a source installer. A desktop launcher and downloadable Arch package are planned, but are not included yet.

Download **Code → Download ZIP**, extract it and open a terminal inside the extracted folder. Alternatively:

```bash
sudo pacman -S --needed git
git clone https://github.com/Dannkk1/side-panel.git
cd side-panel
```

Install once, then start:

```bash
bash install.sh
bash start.sh
```

The installer requests sudo only for system packages. It installs the Python bridge in `.venv`, downloads noVNC v1.6.0 and applies the cursor fix automatically. Run the app as your normal desktop user. Keep its terminal open; Ctrl+C stops it and its virtual display.

Find your PC’s local address:

```bash
ip -4 addr show scope global
```

On the tablet, open `http://YOUR_PC_IP:8765` and enter the six-digit code from the terminal. Use the PC’s address, not the tablet’s. Codes expire after 10 minutes; restart the companion for a new code. Previously paired browsers stay paired.

## Make your deck

Choose **Edit deck → Add button**. Set the name, emoji, colour and action, then **Apply to draft → Save deck**. Tap existing tiles while editing to change or delete them. Use arrows to reorder. Layouts are stored on the PC and shared across paired devices.

Command examples: `firefox`, `konsole`, `flatpak run com.spotify.Client`. Quote arguments containing spaces. Commands execute as your desktop user without a shell; pipes, redirects and shell expansion are not interpreted. Do not use commands that need an interactive terminal or sudo. Paired devices can configure powerful commands: pair only devices you trust.

OBS launch is not OBS scene switching. Keyboard shortcut emulation and multi-action macros are not implemented yet.

## Extend your display

1. Tap **Display**, select **1024 × 768**, then **Start / reconnect**.
2. Approve any KDE prompt on your PC.
3. In **System Settings → Display Configuration**, place **Side-Panel** beside a physical screen and turn mirroring off.
4. Apply, then move a window across that edge.

Use **Stop display** before changing resolutions. Closing the browser leaves the virtual display running so windows do not move on every disconnect. Fullscreen availability depends on Safari. See [DISPLAY.md](DISPLAY.md) for details.

## Connection troubleshooting

**Works on PC but not tablet:** confirm both devices are on the same non-guest network and that the server is running. If UFW is active, allow the tablet’s IP on TCP ports 8765 and 6080. Replace the example tablet address below:

```bash
sudo ufw allow from 192.168.1.100 to any port 8765 proto tcp
sudo ufw allow from 192.168.1.100 to any port 6080 proto tcp
```

A changed tablet IP needs updated rules. The installer does not change your firewall. Do not expose these ports to the internet; block external access to the backend VNC port 5909.

**Module script failed / 404:** run `bash install-display.sh` and check that `static/vendor/novnc/core/rfb.js` exists. If installation pauses, inspect the terminal and check the PC’s internet connection. If the file loads but Safari still reports a module error, check browser compatibility.

**Invisible PC cursor:** installation applies a noVNC patch requesting a server-drawn cursor. Rerun `python scripts/patch_cursor.py`, stop the display and reload Safari before reconnecting. The patch is checked against the expected noVNC source and refuses unfamiliar versions.

**Port already in use:** stop the previous companion before starting another copy.

## Updating an existing prototype

Stop the companion. Keep a private backup of `config.json` (contains your pairing credential and layout). For a Git checkout, use `git pull --ff-only`, rerun `bash install-display.sh`, then `bash start.sh`.

When moving from an older `ipad-deck` ZIP, copy your private `config.json` into the new project folder and run `bash install.sh` there. Never upload that configuration. The monitor name is now **Side-Panel**; you may need to arrange it again in KDE.

## Privacy and security

HTTP and VNC traffic are **unencrypted**. Use only on a trusted LAN, never public/hotel Wi-Fi, and do not port-forward. The six-digit code exchanges for a longer credential behind the scenes; it does not add encryption. Five failed attempts trigger a global 60-second cooldown.

Disconnect forgets the credential in that browser. To revoke all browsers, stop the app, remove only the `token` field from `config.json`, and restart; the layout is preserved. Never share this file. `.gitignore` excludes credentials, installed dependencies and generated files.

## Development

Python standard library for the companion; websockify, KDE Krfb and noVNC for display mode.

```bash
python -m unittest discover -s tests -v
```

Tests cover pairing, layout validation/persistence, authorization, process handling and cursor patching. They do not replace real KDE/iPad testing. When reporting issues, include distro, desktop session, browser/iOS version and error messages, but omit pairing codes, tokens and `config.json`.

## License and credits

Side Panel is [MIT licensed](LICENSE). KDE Krfb, [noVNC](https://github.com/novnc/noVNC) and [websockify](https://github.com/novnc/websockify) retain their own licenses. Dependencies are downloaded separately; the installer preserves noVNC’s license files. This project is not affiliated with Apple or Elgato.
