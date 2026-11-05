import importlib.util
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
with patch.object(sys, 'path', [str(TOOLS), *sys.path]):
    spec = importlib.util.spec_from_file_location('activity_finish', TOOLS / 'render_activity_reel.py')
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)


class ActivityColourTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required')
    def test_black_screen_overlay_preserves_neutral_colour(self):
        import numpy as np
        command = ['ffmpeg', '-v', 'error', '-filter_complex_threads', '1']
        for source in ('color=gray:s=96x160:r=30:d=1', 'color=black:s=48x80:r=30:d=1', 'color=black@0:s=96x160:r=30:d=1,format=rgba', 'color=black@0:s=96x160:r=30:d=1,format=rgba'):
            command += ['-f', 'lavfi', '-i', source]
        command += ['-filter_complex', kit.festive_filters(30, 96, 160), '-map', '[v]', '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
        data = subprocess.check_output(command)
        mean = np.frombuffer(data, dtype=np.uint8).reshape(160, 96, 3).mean(axis=(0, 1))
        self.assertLess(float(mean.max()-mean.min()), 3)
        self.assertTrue((mean > 120).all() and (mean < 135).all())
