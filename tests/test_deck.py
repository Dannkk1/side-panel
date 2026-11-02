import copy
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch, Mock
from test_display import APITests
import server

class DeckTests(APITests):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patcher.stop()
        cls.temp = tempfile.TemporaryDirectory()
        cls.config_patch = patch.object(server, 'CONFIG', Path(cls.temp.name) / 'config.json')
        cls.config_patch.start()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.config_patch.stop()
        cls.temp.cleanup()

    def setUp(self):
        server.CONFIG.write_text('{"token":"test-secret","buttons":[],"revision":0}')
        server.PAIR_FAILURES = 0
        server.PAIR_BLOCKED = 0
        server.PAIR_DEADLINE = time.monotonic() + 600

    def test_pair_and_remembered_auth(self):
        status, body = self.request('POST','/api/pair', {'code':server.PAIR_CODE})
        self.assertEqual(status, 200)
        self.assertEqual(body['token'], 'test-secret')
        self.assertEqual(self.request('GET','/api/buttons', token=body['token'])[0],200)
        self.assertEqual(self.request('GET','/api/buttons', token=server.PAIR_CODE)[0],401)

    def test_rate_limit_and_expiry(self):
        wrong = '000000' if server.PAIR_CODE != '000000' else '999999'
        for _ in range(5):
            self.assertEqual(self.request('POST','/api/pair', {'code':wrong})[0],401)
        self.assertEqual(self.request('POST','/api/pair', {'code':server.PAIR_CODE})[0],429)
        server.PAIR_BLOCKED = 0
        server.PAIR_DEADLINE = 0
        self.assertEqual(self.request('POST','/api/pair', {'code':server.PAIR_CODE})[0],403)

    def test_save_reorder_delete_and_conflict(self):
        buttons = copy.deepcopy(server.DEFAULT)
        status, data = self.request('POST','/api/buttons', {'buttons':buttons,'revision':0},'test-secret')
        self.assertEqual(status,200)
        self.assertEqual(self.request('POST','/api/buttons', {'buttons':[],'revision':0},'test-secret')[0],400)
        updated = data['buttons'][::-1][1:]
        self.assertEqual(self.request('POST','/api/buttons', {'buttons':updated,'revision':1},'test-secret')[0],200)
        self.assertEqual(server.config()['buttons'], updated)
        self.assertEqual(server.config()['token'],'test-secret')
        self.assertEqual(server.CONFIG.stat().st_mode & 0o777, 0o600)

    def test_reject_unauthorized_and_invalid(self):
        self.assertEqual(self.request('POST','/api/buttons', {'buttons':[],'revision':0})[0],401)
        for change in [{'action':'invalid'}, {'color':'red'}, {'action':'website','value':'javascript:alert(1)'}, {'action':'command','value':'"broken'}, {'label':''}]:
            button = dict(server.DEFAULT[0], **change)
            self.assertEqual(self.request('POST','/api/buttons',{'buttons':[button],'revision':0},'test-secret')[0],400)
        self.assertEqual(server.config()['revision'],0)

    def test_execute_only_saved_button_and_no_shell(self):
        button = dict(server.DEFAULT[0], action='command', value='echo "hello world" ; touch /tmp/never')
        server.save_buttons([button],0)
        with patch('server.subprocess.Popen') as spawn:
            self.assertEqual(self.request('POST','/api/action',{'id':'mic','value':'bad'},'test-secret')[0],200)
            self.assertEqual(spawn.call_args.args[0], ['echo','hello world',';','touch','/tmp/never'])
            self.assertNotIn('shell', spawn.call_args.kwargs)
            self.assertEqual(self.request('POST','/api/action',{'id':'missing'},'test-secret')[0],400)
            self.assertEqual(spawn.call_count,1)

if __name__ == '__main__':
    unittest.main()
