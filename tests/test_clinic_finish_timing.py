import importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('finish_timing',Path(__file__).resolve().parents[1]/'workspaces/my-dental-skin-clinic/tools/finish_timing.py');kit=importlib.util.module_from_spec(spec);spec.loader.exec_module(kit)
class SpokenEndingTests(unittest.TestCase):
 def test_short_video_rejected_despite_full_length_audio(self):
  with self.assertRaises(ValueError):kit.validate_video_frames({'avg_frame_rate':'30/1','nb_frames':'124','duration':'4.133333'},127)
  kit.validate_video_frames({'avg_frame_rate':'30/1','nb_frames':'127','duration':'4.233333'},127)
 def test_ending_speech_follows_complete_narration(self):
  d=kit.finish_timing(1446,127)
  self.assertGreater(d['audio_outro_start_frame'],d['base_frames'])
  self.assertEqual(d['audio_outro_start_frame']+d['outro_frames'],d['total_frames'])
 def test_visual_dissolve_retains_full_outro_sound(self):
  d=kit.finish_timing(1638,127)
  self.assertEqual(d['video_outro_start_frame']+d['outro_frames']+d['outro_hold_extra_frames'],d['total_frames'])
  self.assertEqual(d['total_frames'],1769)
 def test_sample_alignment_is_exact(self):
  d=kit.finish_timing(1446,127)
  self.assertEqual(d['samples_per_frame'],1600)
  self.assertEqual(d['audio_outro_start_frame']*1600,2320000)
 def test_invalid_frame_timing_rejected(self):
  for args in [(8,127,8,4),(1446,0,8,4),(1446,127,8,-1)]:
   with self.assertRaises(ValueError):kit.finish_timing(*args)
if __name__=='__main__':unittest.main()
