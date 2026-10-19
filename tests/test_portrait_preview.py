import importlib.util,sys,unittest
from pathlib import Path
from unittest.mock import patch
TOOLS=Path(__file__).resolve().parents[1]/'tools'
with patch.object(sys,'path',[str(TOOLS),*sys.path]):
 spec=importlib.util.spec_from_file_location('portrait_preview',TOOLS/'portrait_preview.py');kit=importlib.util.module_from_spec(spec);spec.loader.exec_module(kit)
class PortraitFramingTests(unittest.TestCase):
 def test_group_fit_is_moving_video_not_still(self):
  f=kit.filter_for({'mode':'fit-video'},60);self.assertIn('split',f);self.assertIn('overlay',f);self.assertNotIn('loop',f)
 def test_following_crop_uses_both_centres(self):
  f=kit.filter_for({'mode':'crop','center_x':900,'end_center_x':750},60);self.assertIn('-150',f);self.assertIn('crop=608:1080',f)
 def test_outside_subject_centre_rejected(self):
  with self.assertRaises(ValueError):kit.filter_for({'mode':'crop','center_x':100},60)
 def test_fit_window_must_stay_inside_source(self):
  with self.assertRaises(ValueError):kit.filter_for({'mode':'fit-video','window_width':900,'center_x':1800},60)
