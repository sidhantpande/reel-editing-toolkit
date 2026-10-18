import importlib.util,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('clinic_plan',Path(__file__).resolve().parents[1]/'workspaces/my-dental-skin-clinic/tools/clinic_plan.py');kit=importlib.util.module_from_spec(spec);spec.loader.exec_module(kit)
class ClinicGateTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.source=Path(self.tmp.name)/'source.mp4';self.source.write_bytes(b'fixture')
  self.plan={'duration_seconds':2,'segments':[{'source_id':'main','source':str(self.source),'source_in':1,'source_out':3,'source_duration':5,'timeline_in':0,'timeline_out':2,'crop_xywh':{'x':0,'y':0,'width':1080,'height':1920}}],'words':[{'text':'hello','start':.2,'end':.6,'source_id':'main'}],'broll_slots':[]}
 def tearDown(self):self.tmp.cleanup()
 def test_complete_contiguous_plan(self):self.assertEqual(kit.validate_plan(self.plan)['duration_seconds'],2)
 def test_overlapping_chunk_duplicate_rejected(self):
  self.plan['words'].append({'text':'hello','start':.3,'end':.6,'source_id':'main'})
  with self.assertRaisesRegex(ValueError,'Overlapping duplicate'):kit.validate_plan(self.plan)
 def test_spoken_repetition_with_distinct_times_allowed(self):
  self.plan['words'].append({'text':'hello','start':.65,'end':.9,'source_id':'main'})
  self.assertEqual(kit.validate_plan(self.plan)['words'],2)
 def test_missing_broll_blocks_full_render_but_allows_explicit_preview(self):
  self.plan['broll_slots']=[{'id':'B01','path':'/missing/unreceived.mp4','timeline_in':.5,'timeline_out':1.5}]
  with self.assertRaisesRegex(ValueError,'not delivered'):kit.validate_plan(self.plan)
  self.assertTrue(kit.validate_plan(self.plan,allow_pending=True)['pending_allowed'])
 def test_retained_recording_command_blocks_render(self):
  self.plan['cue_exclusions']=[{'source':'main','in':1.2,'out':1.4}]
  with self.assertRaisesRegex(ValueError,'Recording cue'):kit.validate_plan(self.plan)
 def test_discontinuous_picture_rejected(self):
  self.plan['segments'][0]['timeline_in']=.1
  with self.assertRaisesRegex(ValueError,'Non-contiguous'):kit.validate_plan(self.plan)
 def test_word_past_picture_end_rejected(self):
  self.plan['words'][0]['end']=3
  with self.assertRaisesRegex(ValueError,'Word outside'):kit.validate_plan(self.plan)
 def test_unknown_word_source_rejected(self):
  self.plan['words'][0]['source_id']='wrong'
  with self.assertRaisesRegex(ValueError,'Unknown word source'):kit.validate_plan(self.plan)
 def test_replaced_source_rejected(self):
  self.plan['segments'][0]['source_sha256']='incorrect'
  with self.assertRaisesRegex(ValueError,'Source changed'):kit.validate_plan(self.plan)
 def test_missing_source_rejected(self):
  self.source.unlink()
  with self.assertRaisesRegex(ValueError,'Missing/invalid source'):kit.validate_plan(self.plan)
if __name__=='__main__':unittest.main()
