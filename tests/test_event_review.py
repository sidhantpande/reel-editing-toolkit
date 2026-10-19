import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
with patch.object(sys, 'path', [str(TOOLS), *sys.path]):
    spec=importlib.util.spec_from_file_location('event_review',TOOLS/'event_review.py')
    review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)

@unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg runtime needed for decode regression')
class ShortClipReviewTests(unittest.TestCase):
    def run_review(self, interrupted=False):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'short.mp4'
            subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','testsrc=size=64x36:rate=25:duration=0.12','-c:v','libx264','-pix_fmt','yuv420p',str(source)],check=True)
            manifest=root/'inventory.json';out=root/'analysis'
            manifest.write_text(json.dumps({'videos':[{'relative':'short.mp4','path':str(source),'sha256':'test','duration':.12,'camera':{'CaptureGammaEquation':'rec709','CaptureColorPrimaries':'rec709'},'video':{'nb_frames':'3','avg_frame_rate':'25/1'}}]}))
            folder=out/'clips/001-short'
            if interrupted:
                folder.mkdir(parents=True);(folder/'last.jpg').write_bytes(b'interrupted generated cache')
            rows=review.analyse(manifest,root/'conversions',out)
            self.assertEqual(len(rows),1);self.assertTrue((folder/'frame-0001.jpg').is_file());self.assertTrue((folder/'last.jpg').is_file());self.assertTrue((folder/'complete.json').is_file())
            if interrupted:self.assertEqual(len(list(folder.parent.glob('001-short-interrupted-*'))),1)
    def test_subsecond_clip_has_sample_and_exact_last_frame(self):self.run_review()
    def test_interrupted_last_frame_cache_is_retained_and_rebuilt(self):self.run_review(True)

if __name__=='__main__':unittest.main()
