import http.client
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from display import Display
import server

class LifecycleTests(unittest.TestCase):
    def test_resolution_allowlist(self):
        with self.assertRaises(ValueError):
            Display().start('1024x768; touch /tmp/oops')

    def test_unsupported_environment(self):
        with patch.dict('os.environ', {'XDG_SESSION_TYPE':'x11', 'XDG_CURRENT_DESKTOP':'KDE'}):
            self.assertTrue(any('Wayland' in p for p in Display().problems()))

    def test_failure_cleans_process(self):
        display = Display()
        process = Mock()
        process.poll.return_value = None
        with patch.object(display, 'problems', return_value=[]), patch('display.socket.socket'), patch('display.subprocess.Popen', return_value=process), patch.object(display, 'wait_port', side_effect=RuntimeError('failed')):
            with self.assertRaises(RuntimeError):
                display.start('1024x768')
        process.terminate.assert_called_once()
        self.assertEqual(display.processes, [])
        self.assertIsNone(display.password)

    def test_start_reuse_stop(self):
        display = Display()
        processes = [Mock(), Mock()]
        for process in processes:
            process.poll.return_value = None
        with patch.object(display, 'problems', return_value=[]), patch('display.socket.socket'), patch('display.subprocess.Popen', side_effect=processes) as spawn, patch.object(display, 'wait_port'):
            first = display.start('1024x768')
            self.assertTrue(first['running'])
            self.assertEqual(len(first['password']), 8)
            self.assertEqual(first['password'], display.start('1024x768')['password'])
            self.assertEqual(spawn.call_count, 2)
            with self.assertRaises(ValueError):
                display.start('1280x800')
            display.stop()
        for process in processes:
            process.terminate.assert_called_once()

class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patcher = patch.object(server, 'config', return_value={'token':'test-secret', 'buttons':[]})
        cls.patcher.start()
        cls.httpd = server.ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown(); cls.httpd.server_close(); cls.thread.join()
        cls.patcher.stop()

    def request(self, method, path, body=None, token=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.httpd.server_port)
        headers = {'X-Deck-Token':token} if token else {}
        conn.request(method, path, json.dumps(body) if body is not None else None, headers)
        response = conn.getresponse()
        result = response.status, json.loads(response.read())
        conn.close()
        return result

    def test_unauthorized_management(self):
        for method, path in [('GET','/api/display'), ('POST','/api/display/start'), ('POST','/api/display/stop')]:
            self.assertEqual(self.request(method, path, {})[0], 401)

    def test_malformed_payload(self):
        self.assertEqual(self.request('POST','/api/display/start', [], 'test-secret')[0], 400)

    def test_status_and_invalid_resolution(self):
        self.assertEqual(self.request('GET','/api/display', token='test-secret')[0], 200)
        self.assertEqual(self.request('POST','/api/display/start', {'resolution':'bad'}, 'test-secret')[0], 400)

if __name__ == '__main__':
    unittest.main()
