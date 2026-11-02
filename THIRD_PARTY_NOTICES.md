# Third-party notices

Reviewed 2026-11-02 against Side Panel commit ef2607e14354509aa0d4108d47628e899bafbab9.

The root MIT license applies to Side Panel's original contributions, not to third-party software. Open source does not mean public domain or copyright-free.

## noVNC v1.6.0

Copyright (C) 2022 The noVNC authors. See upstream AUTHORS and individual file notices.

Source: https://github.com/novnc/noVNC/tree/v1.6.0
License inventory: https://github.com/novnc/noVNC/blob/v1.6.0/LICENSE.txt

The core JavaScript is MPL-2.0. Other upstream files include BSD-2-Clause HTML/CSS, SIL OFL-1.1 fonts, CC-BY-SA-3.0 images, BSD notices in core/des.js, and MIT-licensed pako. Preserve upstream AUTHORS, file notices, LICENSE.txt, docs/LICENSE.* and vendor licenses. The installer retains the upstream directory, excluding only Git metadata.

Side Panel modifies core/rfb.js through scripts/patch_cursor.py to remove the two cursor pseudo-encoding advertisements so the server draws the pointer. These modifications to MPL-covered code are made available under MPL-2.0; the resulting rfb.js is not relicensed under MIT. The patching utility itself remains MIT.

After installation, the actual modified, unminified source is directly accessible at /vendor/novnc/core/rfb.js on the companion. The rest of the installed noVNC source and notices are under /vendor/novnc/. The MPL text is at /vendor/novnc/docs/LICENSE.MPL-2.0 and a reference copy is in licenses/MPL-2.0.txt in this repository. Recipients retain their MPL rights. If distributing a minified or compiled client in future, provide the matching preferred source and clear retrieval instructions.

## websockify 0.13.0

Author: Joel Martin and contributors.
Source: https://github.com/novnc/websockify/tree/v0.13.0
License: GNU LGPL version 3; see https://github.com/novnc/websockify/blob/v0.13.0/COPYING

Installed independently through pip and launched as a separate process; no websockify source or executable is shipped in this repository. Its setup.py declares numpy, requests, jwcrypto and redis. Their versions and transitive dependencies are not pinned by Side Panel; a complete installed-environment license inventory is required before redistributing a bundled environment. Preserve all notices and comply with applicable source/relinking requirements if distribution changes.

## KDE Krfb and operating-system tools

KDE lists Krfb as GPL-2.0-or-later: https://apps.kde.org/krfb/
Source and per-file licenses: https://invent.kde.org/network/krfb

The installer requests Krfb from the user's Arch-compatible package repositories; Side Panel invokes krfb-virtualmonitor as a separate program. Its version is determined by the distribution. This review does not certify every distro build.

Python, Git, pip, WirePlumber/wpctl, playerctl, OBS Studio, xdg-utils and loginctl/systemd are separately installed or existing system tools. They are not included in the GitHub source tree. Each retains its own licensing terms. Do not copy them into a future installer without auditing the exact packages and corresponding sources.

## Redistribution

Keep Side Panel's MIT notice with copies of its code. Keep third-party notices with third-party code, and fulfill each component's license rather than describing the entire installation as MIT. Downloading a dependency separately does not waive obligations when you subsequently distribute it, including browser JavaScript.

No trademark rights or endorsement are granted. This project is independent of Apple, Elgato, KDE, Mozilla and the noVNC/websockify projects.
