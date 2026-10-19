import importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('beat_sync',Path(__file__).resolve().parents[1]/'tools/beat_sync.py');kit=importlib.util.module_from_spec(spec);spec.loader.exec_module(kit)
class BeatSyncTests(unittest.TestCase):
 def test_far_beat_does_not_move_edit(self):self.assertEqual(kit.snap(100,[110],4),100)
 def test_near_beat_snaps(self):self.assertEqual(kit.snap(100,[97,110],4),97)
 def test_action_placement_accounts_for_slow_motion(self):self.assertEqual(kit.action_in(4,300,330,.5),3.5)
 def test_invalid_action_handle_rejected(self):
  with self.assertRaises(ValueError):kit.action_in(.1,0,90,.5)
