import importlib.util,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
TOOLS=Path(__file__).resolve().parents[1]/'tools'
with patch.object(sys,'path',[str(TOOLS),*sys.path]):
 spec=importlib.util.spec_from_file_location('event_transitions',TOOLS/'event_transitions.py');kit=importlib.util.module_from_spec(spec);spec.loader.exec_module(kit)
class EventTransitionTests(unittest.TestCase):
 def test_cut_is_zero_frames(self):self.assertEqual(kit.transition({'frames':30}),('cut',0))
 def test_invalid_effect_rejected(self):
  with self.assertRaises(ValueError):kit.transition({'frames':30,'transitionIn':{'kind':'randomFlash','frames':8}})
 def test_transition_longer_than_shot_rejected(self):
  with self.assertRaises(ValueError):kit.transition({'frames':8,'transitionIn':{'kind':'fade','frames':8}})
 @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg required')
 def test_source_handle_seam_has_no_timeline_drift_or_black_frame(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);red=root/'red.mp4';blue=root/'blue.mp4'
   for colour,path,frames in [('red',red,36),('blue',blue,30)]:
    subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i',f'color=c={colour}:s=64x36:r=30','-frames:v',str(frames),'-c:v','libx264','-pix_fmt','yuv420p',str(path)],check=True)
   pieces=kit.assemble([red,blue],[{'frames':30},{'frames':30,'transitionIn':{'kind':'fade','frames':6}}],root)
   lengths=[int(next(s for s in kit.probe(p)['streams'] if s['codec_type']=='video')['nb_frames']) for p in pieces]
   self.assertEqual(lengths,[30,6,24]);self.assertEqual(sum(lengths),60)
   decoded=subprocess.check_output(['ffmpeg','-v','error','-i',str(root/'seam-001.mp4'),'-f','rawvideo','-pix_fmt','rgb24','-'])
   import numpy as np
   frames=np.frombuffer(decoded,dtype=np.uint8).reshape(6,36,64,3);means=frames.mean(axis=(1,2))
   self.assertGreater(means[0,0],240);self.assertGreater(means[-1,2],190);self.assertTrue((means.sum(axis=1)>230).all())
if __name__=='__main__':unittest.main()
