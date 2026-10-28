import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('organize', Path(__file__).resolve().parents[1] / 'tools/organize_deliveries.py')
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)


class DeliveryOrganizationTests(unittest.TestCase):
    def manifest(self, root):
        source = root / 'old.mp4'
        source.write_bytes(b'unchanged encoded delivery')
        return {'destination_root': str(root / 'Final Reels'), 'files': [{
            'source': str(source), 'destination': str(root / 'Final Reels' / 'Guest.mp4'),
            'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'bytes': source.stat().st_size}]}

    def test_move_keeps_locked_path_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as folder:
            manifest = self.manifest(Path(folder))
            kit.relocate(manifest)
            self.assertTrue(Path(manifest['files'][0]['source']).is_symlink())
            self.assertEqual(kit.relocate(manifest)['verified'], 1)

    def test_entire_batch_verified_before_any_move(self):
        with tempfile.TemporaryDirectory() as folder:
            manifest = self.manifest(Path(folder))
            manifest['files'].append(dict(manifest['files'][0], source=str(Path(folder) / 'missing.mp4'), destination=str(Path(folder) / 'Final Reels' / 'Other.mp4')))
            with self.assertRaises(ValueError):
                kit.relocate(manifest)
            self.assertFalse(Path(manifest['files'][0]['source']).is_symlink())

    def test_conflict_and_escape_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = self.manifest(root)
            destination = Path(manifest['files'][0]['destination'])
            destination.parent.mkdir()
            destination.write_bytes(b'existing different delivery')
            with self.assertRaises(ValueError):
                kit.relocate(manifest)
            self.assertEqual(destination.read_bytes(), b'existing different delivery')
            manifest['files'][0]['destination'] = str(root / 'outside.mp4')
            with self.assertRaises(ValueError):
                kit.preflight(manifest)

    def test_changed_delivery_detected_after_move(self):
        with tempfile.TemporaryDirectory() as folder:
            manifest = self.manifest(Path(folder))
            kit.relocate(manifest)
            Path(manifest['files'][0]['destination']).write_bytes(b'changed')
            with self.assertRaises(ValueError):
                kit.verify(manifest)
