#!/usr/bin/env python3
"""Side Panel: LAN-only control surface, Python standard library."""
import argparse
import atexit
import signal
import time
import re
import shlex
import os
from display import Display
import json
import secrets
import subprocess
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / 'config.json'
LOCK = threading.RLock()
PAIR_CODE = f'{secrets.randbelow(1000000):06d}'
PAIR_DEADLINE = time.monotonic() + 600
PAIR_FAILURES = 0
PAIR_BLOCKED = 0
display = Display()
atexit.register(display.stop)
DEFAULT = [
    {'id': 'mic', 'label': 'Mute Mic', 'icon': '🎙️', 'action': 'mic_toggle'},
    {'id': 'volup', 'label': 'Volume +', 'icon': '🔊', 'action': 'volume_up'},
    {'id': 'voldown', 'label': 'Volume −', 'icon': '🔉', 'action': 'volume_down'},
    {'id': 'play', 'label': 'Play/Pause', 'icon': '⏯️', 'action': 'play_pause'},
    {'id': 'obs', 'label': 'OBS Studio', 'icon': '🎬', 'action': 'launch_obs'},
    {'id': 'lock', 'label': 'Lock Screen', 'icon': '🔒', 'action': 'lock_screen'},
]
COMMANDS = {
    'mic_toggle': ['wpctl', 'set-mute', '@DEFAULT_AUDIO_SOURCE@', 'toggle'],
    'volume_up': ['wpctl', 'set-volume', '-l', '1.5', '@DEFAULT_AUDIO_SINK@', '5%+'],
    'volume_down': ['wpctl', 'set-volume', '@DEFAULT_AUDIO_SINK@', '5%-'],
    'play_pause': ['playerctl', 'play-pause'],
    'next_track': ['playerctl', 'next'],
    'previous_track': ['playerctl', 'previous'],
    'mute_audio': ['wpctl', 'set-mute', '@DEFAULT_AUDIO_SINK@', 'toggle'],
    'launch_obs': ['obs'],
    'lock_screen': ['loginctl', 'lock-session'],
}
if not CONFIG.exists():
    CONFIG.write_text(json.dumps({'token': secrets.token_urlsafe(24), 'buttons': DEFAULT}, indent=2))
    CONFIG.chmod(0o600)

def config():
    return json.loads(CONFIG.read_text())

# Preserve existing layouts while regenerating a deliberately removed credential.
_initial = config()
if not _initial.get('token'):
    _initial['token'] = secrets.token_urlsafe(24)
    CONFIG.write_text(json.dumps(_initial, indent=2))
    CONFIG.chmod(0o600)


def save_buttons(buttons, revision):
    with LOCK:
        data = config()
        if revision != data.get('revision', 0):
            raise ValueError('Deck changed on another device. Reload before editing again.')
        if not isinstance(buttons, list) or len(buttons) > 60:
            raise ValueError('Use at most 60 buttons')
        clean, ids = [], set()
        for button in buttons:
            if not isinstance(button, dict):
                raise ValueError('Invalid button')
            item = {}
            for key, limit in [('id', 80), ('label', 60), ('icon', 24), ('action', 40), ('value', 1000), ('color', 7)]:
                value = button.get(key, '' if key == 'value' else '#30475e' if key == 'color' else '⌘' if key == 'icon' else None)
                if not isinstance(value, str) or len(value) > limit or (key != 'value' and not value.strip()):
                    raise ValueError('Invalid ' + key)
                item[key] = value
            if item['id'] in ids:
                raise ValueError('Duplicate button ID')
            ids.add(item['id'])
            if not re.fullmatch(r'#[0-9a-fA-F]{6}', item['color']):
                raise ValueError('Invalid colour')
            action = item['action']
            if action == 'website':
                url = urlparse(item['value'])
                if url.scheme not in ('http', 'https') or not url.hostname:
                    raise ValueError('Website must be an http:// or https:// URL')
            elif action == 'command':
                if not shlex.split(item['value']):
                    raise ValueError('Enter an executable and optional arguments')
            elif action not in COMMANDS:
                raise ValueError('Unsupported action')
            clean.append(item)
        data['buttons'] = clean
        data['revision'] = data.get('revision', 0) + 1
        temp = CONFIG.with_suffix('.tmp')
        fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2)
        os.replace(temp, CONFIG)
        return {'buttons': clean, 'revision': data['revision']}

def run_action(button):
    action = button['action']
    if action == 'website':
        command = ['xdg-open', button['value']]
    elif action == 'command':
        command = shlex.split(button['value'])
    elif action in COMMANDS:
        command = COMMANDS[action]
    else:
        raise ValueError('Unsupported action')
    if action in ('website', 'command', 'launch_obs'):
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, start_new_session=True)
        threading.Thread(target=process.wait, daemon=True).start()
    else:
        completed = subprocess.run(command, timeout=8, capture_output=True, text=True)
        if completed.returncode:
            raise RuntimeError('Command failed: ' + (completed.stderr.strip()[:180] or action))

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'static'), **kwargs)

    def json_response(self, obj, status=200):
        payload = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def authorized(self):
        provided = self.headers.get('X-Deck-Token', '')
        expected = config().get('token', '')
        return bool(expected) and secrets.compare_digest(provided, expected)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/display':
            if not self.authorized():
                return self.json_response({'error': 'Incorrect pairing token'}, 401)
            return self.json_response(display.status())
        if path == '/api/buttons':
            if not self.authorized():
                return self.json_response({'error': 'Incorrect pairing token'}, 401)
            return self.json_response({'buttons': config().get('buttons', []), 'revision': config().get('revision', 0)})
        if path.startswith('/api/'):
            return self.json_response({'error': 'Not found'}, 404)
        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ('/api/pair', '/api/buttons', '/api/action', '/api/display/start', '/api/display/stop'):
            return self.json_response({'error': 'Not found'}, 404)
        if path != '/api/pair' and not self.authorized():
            return self.json_response({'error': 'Please pair this device again'}, 401)
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 131072:
                raise ValueError('Invalid request size')
            body = json.loads(self.rfile.read(size))
            if not isinstance(body, dict):
                raise ValueError('Expected an object')
            if path == '/api/pair':
                global PAIR_FAILURES, PAIR_BLOCKED
                with LOCK:
                    now = time.monotonic()
                    if now < PAIR_BLOCKED:
                        return self.json_response({'error': 'Too many attempts. Wait 60 seconds.'}, 429)
                    if now > PAIR_DEADLINE:
                        return self.json_response({'error': 'Code expired. Restart the companion for a new code.'}, 403)
                    code = body.get('code', '')
                    if not isinstance(code, str) or not secrets.compare_digest(code, PAIR_CODE):
                        PAIR_FAILURES += 1
                        if PAIR_FAILURES >= 5:
                            PAIR_BLOCKED = now + 60
                            PAIR_FAILURES = 0
                        return self.json_response({'error': 'Incorrect six-digit code'}, 401)
                    PAIR_FAILURES = 0
                    return self.json_response({'token': config()['token']})
            if path == '/api/buttons':
                return self.json_response(save_buttons(body.get('buttons'), body.get('revision')))
            if path == '/api/display/start':
                return self.json_response(display.start(body.get('resolution', '1024x768')))
            if path == '/api/display/stop':
                return self.json_response(display.stop())
            button = next((b for b in config().get('buttons', []) if b['id'] == body.get('id')), None)
            if button is None:
                raise ValueError('Button is not configured; reload the deck')
            run_action(button)
            return self.json_response({'ok': True})
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            return self.json_response({'error': str(exc)}, 400)
        except subprocess.TimeoutExpired:
            return self.json_response({'error': 'Command timed out'}, 504)
        except (OSError, RuntimeError) as exc:
            return self.json_response({'error': str(exc)}, 500)

    def log_message(self, *args):
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    display.host = args.host
    signal.signal(signal.SIGTERM, lambda *_: exit(0))
    print(f'Side Panel running on http://YOUR_PC_IP:{args.port}', flush=True)
    print('Pairing code:', PAIR_CODE, '(valid for 10 minutes; restart for a new code)', flush=True)
    print('HTTP is not encrypted. Only use on a trusted private network.', flush=True)
    try:
        ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        display.stop()
