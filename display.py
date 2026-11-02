"""Experimental KDE Wayland virtual display lifecycle. No shell execution."""
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import threading
import time

ROOT = Path(__file__).resolve().parent
NOVNC = ROOT / 'static' / 'vendor' / 'novnc'
PRESETS = ('1024x768', '1280x800', '1600x1200', '1920x1080')

class Display:
    def __init__(self):
        self.lock = threading.RLock()
        self.processes = []
        self.password = None
        self.resolution = None
        self.host = '0.0.0.0'
        self.port = 6080
        self.vnc_port = 5909

    def problems(self):
        problems = []
        if os.environ.get('XDG_SESSION_TYPE') != 'wayland' or 'KDE' not in os.environ.get('XDG_CURRENT_DESKTOP', '').upper():
            problems.append('Start the companion inside your KDE Plasma Wayland desktop session.')
        for program in ('krfb-virtualmonitor', 'websockify'):
            if not shutil.which(program):
                problems.append('Missing dependency: ' + program + '. See DISPLAY.md.')
        if not (NOVNC / 'core' / 'rfb.js').is_file():
            problems.append('noVNC is missing. Run bash install-display.sh on your PC.')
        return problems

    def status(self):
        with self.lock:
            active = len(self.processes) == 2 and all(p.poll() is None for p in self.processes)
            failed = bool(self.processes) and not active
            if failed:
                self.stop()
            return {'running': active, 'resolution': self.resolution, 'port': self.port,
                    'password': self.password if active else None,
                    'problems': self.problems(), 'failed': failed}

    def wait_port(self, port, process):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError('Display component exited. Check the companion terminal.')
            try:
                with socket.create_connection(('127.0.0.1', port), timeout=.25):
                    return
            except OSError:
                time.sleep(.1)
        raise RuntimeError('Display startup timed out. Check the companion terminal and KDE permissions.')

    def start(self, resolution):
        with self.lock:
            if resolution not in PRESETS:
                raise ValueError('Choose a supported display resolution')
            if self.status()['running']:
                if resolution != self.resolution:
                    raise ValueError('Stop the display before changing resolution')
                return self.status()
            problems = self.problems()
            if problems:
                raise RuntimeError(' '.join(problems))
            # Refuse occupied ports rather than connecting to an unrelated service.
            for port in (self.port, self.vnc_port):
                with socket.socket() as sock:
                    sock.bind(('0.0.0.0', port))
            self.password = ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(8))
            self.resolution = resolution
            try:
                self.processes.append(subprocess.Popen(['krfb-virtualmonitor', '--name', 'Side-Panel', '--resolution', resolution,
                    '--scale', '1', '--port', str(self.vnc_port), '--password', self.password]))
                self.wait_port(self.vnc_port, self.processes[0])
                self.processes.append(subprocess.Popen(['websockify', f'{self.host}:{self.port}', f'127.0.0.1:{self.vnc_port}']))
                self.wait_port(self.port, self.processes[1])
                return self.status()
            except Exception:
                self.stop()
                raise

    def stop(self):
        with self.lock:
            for process in reversed(self.processes):
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=3)
            self.processes = []
            self.password = None
            self.resolution = None
            return {'running': False}
