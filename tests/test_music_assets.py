import importlib.util,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
TOOLS=Path(__file__).resolve().parents[1]/'tools'
with patch.object(sys,'path',[str(TOOLS),*sys.path]):
 spec=importlib.util.spec_from_file_location('music_assets',TOOLS/'music_assets.py');kit=importlib.util.module_from_spec(spec);spec.loader.exec_module(kit)
class MusicCueTests(unittest.TestCase):
 def setUp(self):self.t={'id':'jetkids-test-04','url':'https://www.youtube.com/watch?v=fdubeMFwuGs','source_in':35,'source_out':85,'fps':30,'song':'Ilahi','markers':[{'source_seconds':52,'label':'sports'}]}
 def test_source_time_becomes_reel_time(self):
  m=kit.cue_markers(self.t)[0];self.assertEqual(m['timeline_seconds'],17);self.assertEqual(m['timeline_frame'],510);self.assertIn('not verified',m['status'])
 def test_no_search_urls(self):
  self.t['url']='https://www.google.com/search?q=Ilahi'
  with self.assertRaisesRegex(ValueError,'exact YouTube'):kit.validate(self.t)
 def test_marker_cannot_escape_slice(self):
  self.t['markers'][0]['source_seconds']=90
  with self.assertRaisesRegex(ValueError,'outside'):kit.validate(self.t)
 def test_safe_asset_id(self):
  self.t['id']='../../clip'
  with self.assertRaisesRegex(ValueError,'Safe'):kit.validate(self.t)
 def test_wrong_track_title_rejected(self):self.assertFalse(kit.title_matches(self.t,'Kabira full audio'))
 def test_explicit_title_alias(self):
  self.t.update(song='Sooraj Ki Baahon Mein',title_aliases=['Sooraj Ki Bahoon Mein']);self.assertTrue(kit.title_matches(self.t,'Sooraj Ki Bahoon Mein full song'))
 @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg required')
 def test_opus_delay_and_nonzero_start_preserve_exact_samples(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);source=root/'source.webm'
   subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=1000:sample_rate=48000:duration=2','-c:a','libopus',str(source)],check=True)
   for start,end in [(0,1),(.375,1.625)]:
    target=root/f'{start}.wav';kit.extract_pcm_slice(source,target,start,end)
    decoded=subprocess.check_output(['ffmpeg','-v','error','-i',str(target),'-f','s16le','-'])
    self.assertEqual(len(decoded)//2,round((end-start)*48000))
if __name__=='__main__':unittest.main()

class BeatFrameBoundsTests(unittest.TestCase):
 def test_rounded_end_boundary_is_not_an_edit_frame(self):
  rows=kit.beat_rows([0,44.97,44.999],0,45)
  self.assertEqual([r['frame_30fps'] for r in rows],[0,1349])
