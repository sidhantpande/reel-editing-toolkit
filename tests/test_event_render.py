import importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
TOOLS=Path(__file__).resolve().parents[1]/'tools'
with patch.object(sys,'path',[str(TOOLS),*sys.path]):
 spec=importlib.util.spec_from_file_location('event_render',TOOLS/'event_render.py');kit=importlib.util.module_from_spec(spec);spec.loader.exec_module(kit)
class LandscapeEventPreflightTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.source=self.root/'clip.MP4';self.source.write_bytes(b'original');(self.root/'logo.jpg').write_bytes(b'logo');(self.root/'reference.m4a').write_bytes(b'music')
  self.record={'relative':'clip.MP4','path':str(self.source),'duration':5,'sha256':kit.digest(self.source),'camera':{'CaptureGammaEquation':'rec709','CaptureColorPrimaries':'rec709'},'video':{'avg_frame_rate':'100/1'}};self.inventory={'videos':[self.record]};self.state={'files':{}}
  self.plan={'id':'jetkids-test-v01','width':1920,'height':1080,'fps':30,'eventPhotoInserts':False,'logo':'logo.jpg','logoFrames':60,'audio':{'source':'reference.m4a','in':0},'shots':[{'source':'clip.MP4','in':1,'frames':90,'speed':.5,'review_note':'Reviewed gesture without camera tail'}]}
  self.root_patch=patch.object(kit,'ROOT',self.root);self.root_patch.start();self.probe_patch=patch.object(kit,'probe',return_value={'format':{'duration':'60'},'streams':[{'codec_type':'audio','duration':'60'}]});self.probe_patch.start()
 def tearDown(self):self.root_patch.stop();self.probe_patch.stop();self.tmp.cleanup()
 def test_valid_landscape_100fps_slow_motion(self):self.assertEqual(kit.check_plan(self.plan,self.inventory,self.state)['totalFrames'],150)
 def test_portrait_delivery_rejected(self):
  self.plan.update(width=1080,height=1920)
  with self.assertRaisesRegex(ValueError,'1920x1080'):kit.check_plan(self.plan,self.inventory,self.state)
 def test_event_photo_inserts_rejected(self):
  self.plan['eventPhotoInserts']=True
  with self.assertRaisesRegex(ValueError,'photo'):kit.check_plan(self.plan,self.inventory,self.state)
 def test_unconverted_log_rejected(self):
  self.record['camera']={'CaptureGammaEquation':'s-log3-cine','CaptureColorPrimaries':'s-gamut3-cine'}
  with self.assertRaisesRegex(ValueError,'colour-verified'):kit.check_plan(self.plan,self.inventory,self.state)
 def test_source_overrun_rejected(self):
  self.plan['shots'][0]['in']=4
  with self.assertRaisesRegex(ValueError,'exceeds'):kit.check_plan(self.plan,self.inventory,self.state)
 def test_slow_motion_without_enough_source_frames_rejected(self):
  self.record['video']['avg_frame_rate']='25/1'
  with self.assertRaisesRegex(ValueError,'interpolated'):kit.check_plan(self.plan,self.inventory,self.state)
 def test_changed_original_rejected(self):
  self.source.write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'checksum'):kit.check_plan(self.plan,self.inventory,self.state)
 def test_unsafe_plan_id_rejected(self):
  self.plan['id']='../../elsewhere'
  with self.assertRaisesRegex(ValueError,'safe'):kit.check_plan(self.plan,self.inventory,self.state)
if __name__=='__main__':unittest.main()

class TransitionHandlePreflightTests(unittest.TestCase):
 setUp=LandscapeEventPreflightTests.setUp
 tearDown=LandscapeEventPreflightTests.tearDown
 def test_outgoing_transition_needs_real_source_handle(self):
  self.plan['shots'][0]['in']=3.5
  self.plan['shots'].append({'source':'clip.MP4','in':0,'frames':30,'speed':1,'transitionIn':{'kind':'fade','frames':6},'review_note':'Next reviewed shot'})
  with self.assertRaisesRegex(ValueError,'exceeds'):kit.check_plan(self.plan,self.inventory,self.state)
 def test_first_shot_cannot_fade_from_missing_clip(self):
  self.plan['shots'][0]['transitionIn']={'kind':'fade','frames':6}
  with self.assertRaisesRegex(ValueError,'First shot'):kit.check_plan(self.plan,self.inventory,self.state)
