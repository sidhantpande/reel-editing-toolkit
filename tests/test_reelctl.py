import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('reelctl',Path(__file__).resolve().parents[1]/'tools/reelctl.py');kit=importlib.util.module_from_spec(spec);spec.loader.exec_module(kit)
class PreflightTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve();self.p=self.root/'projects/niolearn/niolearn-test';self.p.mkdir(parents=True);self.raw=self.root/'media/raw/niolearn/niolearn-test/main.mov';self.raw.parent.mkdir(parents=True);self.raw.write_bytes(b'source')
  self.patch=patch.object(kit,'ROOT',self.root);self.patch.start();self.probe=patch.object(kit,'probe',return_value={'format':{'duration':'5'}});self.probe.start()
  self.cut={'id':'niolearn-test','fps':30,'dialogueFrames':90,'endHoldFrames':45,'totalFrames':135,'cuts':[{'source':str(self.raw.relative_to(self.root)),'inFrame':30,'outFrame':120,'timelineFrom':0,'duration':90,'zoom':1.6}]}
  kit.write(self.p/'cut-list.json',self.cut);kit.write(self.p/'source-words.json',{'words':[{'text':'Hello','start':1.2,'end':1.5}]});kit.write(self.p/'editorial.json',{'phrases':['Hello'],'broll':[]});kit.write(self.p/'colour-grade.json',{});kit.write(self.p/'assets-provenance.json',{});(self.p/'production-plan.md').write_text('Reviewed the complete source recording. Main camera-facing take retained with the full spoken sentence. Crop and caption area checked.')
 def tearDown(self):self.probe.stop();self.patch.stop();self.tmp.cleanup()
 def test_valid_cut(self):self.assertEqual(kit.check_project(self.p)['dialogueFrames'],90)
 def test_discontinuous_frames_rejected(self):
  self.cut['cuts'][0]['timelineFrom']=1;kit.write(self.p/'cut-list.json',self.cut)
  with self.assertRaisesRegex(ValueError,'Discontinuous'):kit.check_project(self.p)
 def test_past_end_rejected(self):
  self.cut['cuts'][0].update(outFrame=200,duration=170);kit.write(self.p/'cut-list.json',self.cut)
  with self.assertRaisesRegex(ValueError,'exceeds'):kit.check_project(self.p)
 def test_changed_source_rejected(self):
  kit.write(self.p/'intake.json',{'sources':[{'source':str(self.raw.relative_to(self.root)),'sha256':'incorrect'}]})
  with self.assertRaisesRegex(ValueError,'changed'):kit.check_project(self.p)
 def test_unknown_source_word_rejected(self):
  kit.write(self.p/'source-words.json',{'words':[{'text':'Hello','source':'other','start':1.2,'end':1.5}]})
  with self.assertRaisesRegex(ValueError,'source ID'):kit.check_project(self.p)
if __name__=='__main__':unittest.main()
