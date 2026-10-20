import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('approved_delivery', Path(__file__).resolve().parents[1] / 'tools/approved_delivery.py')
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)


class ApprovedDeliveryTests(unittest.TestCase):
    def test_locked_version_allows_preflight_but_refuses_render(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / 'approval-lock.json').write_text('{}')
            kit.assert_unlocked(project, preflight=True)
            with self.assertRaises(RuntimeError):
                kit.assert_unlocked(project)

    def test_changed_approved_bytes_are_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            video = project / 'approved.mp4'
            video.write_bytes(b'approved bytes')
            manifest = project / 'approval-lock.json'
            manifest.write_text(json.dumps({'files': [{'path': str(video), 'sha256': hashlib.sha256(video.read_bytes()).hexdigest(), 'bytes': video.stat().st_size}]}))
            self.assertEqual(len(kit.verify_lock(manifest)), 1)
            video.write_bytes(b'changed bytes!')
            with self.assertRaises(ValueError):
                kit.verify_lock(manifest)


if __name__ == '__main__':
    unittest.main()
