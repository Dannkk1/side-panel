"""Request server-drawn cursor for the PC mouse on tablet displays."""
from pathlib import Path
import sys

LINES = (
    'encs.push(encodings.pseudoEncodingVMwareCursor);',
    'encs.push(encodings.pseudoEncodingCursor);',
)
MARKER = '// Side Panel: cursor rendered by server instead of client.'

def patch_cursor(path):
    path = Path(path)
    source = path.read_text()
    if source.count(MARKER) == 2 and not any(line in source for line in LINES):
        return False
    if not all(source.count(line) == 1 for line in LINES):
        raise ValueError('Unexpected noVNC source; cursor patch not applied. Expected noVNC v1.6.0.')
    for line in LINES:
        source = source.replace(line, MARKER, 1)
    path.write_text(source)
    return True

if __name__ == '__main__':
    target = Path(__file__).resolve().parents[1] / 'static/vendor/novnc/core/rfb.js'
    patch_cursor(target)
    print('Server-drawn cursor enabled.')
