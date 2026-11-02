import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.patch_cursor import patch_cursor, LINES, MARKER

class CursorTests(unittest.TestCase):
    def test_patch_preserves_decoder_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'rfb.js'
            p.write_text('\n'.join(LINES) + '\ncase encodings.pseudoEncodingCursor:\n')
            self.assertTrue(patch_cursor(p))
            self.assertFalse(patch_cursor(p))
            self.assertEqual(p.read_text().count(MARKER), 2)
            self.assertIn('case encodings.pseudoEncodingCursor:', p.read_text())

    def test_unknown_source_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'rfb.js'
            p.write_text('unexpected source')
            with self.assertRaises(ValueError):
                patch_cursor(p)
            self.assertEqual(p.read_text(), 'unexpected source')
