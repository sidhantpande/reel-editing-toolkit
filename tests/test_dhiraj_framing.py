"""Regression for a real FFmpeg expression-depth failure in long tracked shots."""
import importlib.util,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'workspaces/my-dental-skin-clinic'
AVAILABLE=all(importlib.util.find_spec(m) for m in ['numpy','scipy'])

@unittest.skipUnless(AVAILABLE,'Clinic NumPy/SciPy runtime required')
class DhirajFraming(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0,str(ROOT/'tools'))
        import render_dhiraj_selects,build_dhiraj_plans
        cls.renderer=render_dhiraj_selects;cls.builder=build_dhiraj_plans

    def test_long_tracking_expression_decodes_in_ffmpeg(self):
        ff=json.loads((ROOT/'project.json').read_text())['ffmpeg']
        if not Path(ff).exists():self.skipTest('Local FFmpeg unavailable')
        item={'crop_xywh':{'x':700,'y':0,'width':1214,'height':2160},
              'crop_keyframes':[{'t':i*.25,'x':700+(i%19)*7} for i in range(240)]}
        result=subprocess.run([ff,'-v','error','-f','lavfi','-i','testsrc2=size=3840x2160:rate=30',
                               '-vf',self.renderer.crop_filter(item,2.3),'-frames:v','2','-f','null','-'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr[-2000:])

    def test_brief_breaths_are_retained(self):
        import numpy as np
        from scipy.io import wavfile
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'audio.wav';x=np.full(16000*5,5000,dtype=np.int16);x[16000:24000]=0
            wavfile.write(path,16000,x)
            self.assertEqual(self.builder.quiet_gaps(path,0,5),[])

    def test_long_pause_keeps_handles(self):
        import numpy as np
        from scipy.io import wavfile
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'audio.wav';x=np.full(16000*5,5000,dtype=np.int16);x[16000*2:16000*4]=0
            wavfile.write(path,16000,x);spans=self.builder.quiet_gaps(path,0,5)
            self.assertEqual(len(spans),1)
            self.assertGreaterEqual(spans[0][0],2.16);self.assertLessEqual(spans[0][1],3.84)

if __name__=='__main__':unittest.main()
