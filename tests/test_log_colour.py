import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('log_colour', Path(__file__).resolve().parents[1] / 'tools/log_colour.py')
kit = importlib.util.module_from_spec(spec); spec.loader.exec_module(kit)

class ColourSafetyTests(unittest.TestCase):
    def test_only_matching_log_gamut_gets_sony_lut(self):
        self.assertEqual(kit.classify({'CaptureGammaEquation': 's-log3-cine', 'CaptureColorPrimaries': 's-gamut3-cine'}), 'sony-slog3-sgamut3cine')
    def test_normal_camera_modes_never_get_log_lut(self):
        for gamma in ['s-cinetone', 'rec709', 'nxcam-still']:
            with self.subTest(gamma=gamma):
                self.assertEqual(kit.classify({'CaptureGammaEquation': gamma, 'CaptureColorPrimaries': 'rec709'}), 'display-referred-no-log-lut')
    def test_unknown_or_other_log_modes_require_review(self):
        for meta in [{}, {'CaptureGammaEquation': 's-log2', 'CaptureColorPrimaries': 's-gamut'}, {'CaptureGammaEquation': 's-log3', 'CaptureColorPrimaries': 's-gamut3'}, {'CaptureGammaEquation': 'hlg', 'CaptureColorPrimaries': 'bt2020'}]:
            with self.subTest(meta=meta): self.assertEqual(kit.classify(meta), 'unknown-review-required')
    def test_xml_namespace_and_serial_privacy(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'C0001.MP4'
            source.with_name('C0001M01.XML').write_text('<NonRealTimeMeta xmlns="urn:sony"><Device modelName="ILCE-7M4" serialNo="private"/><AcquisitionRecord><Item name="CaptureGammaEquation" value="s-log3-cine"/><Item name="CaptureColorPrimaries" value="s-gamut3-cine"/></AcquisitionRecord></NonRealTimeMeta>')
            meta = kit.camera_metadata(source)
            self.assertEqual(meta['modelName'], 'ILCE-7M4'); self.assertNotIn('serialNo', meta)
            self.assertEqual(kit.classify(meta), 'sony-slog3-sgamut3cine')
    def test_never_overwrite_input(self):
        with self.assertRaisesRegex(ValueError, 'original'):
            kit.ffmpeg_command('source.mov', 'source.mov', 'look.cube', 'pc')
    def test_range_must_be_explicit(self):
        with self.assertRaisesRegex(ValueError, 'range'): kit.colour_filter('look.cube', 'unknown')
    def test_float_lut_range_conversion_fps_and_audio_copy(self):
        command = kit.ffmpeg_command('source.mp4', 'copy.mov', 'look.cube', 'pc')
        self.assertIn('passthrough', command); self.assertNotIn('-r', command)
        self.assertEqual(command[command.index('-c:a')+1], 'copy')
        self.assertIn('-n', command); self.assertNotIn('-y', command)
        filters = command[command.index('-vf')+1]
        self.assertIn('format=gbrp16le', filters); self.assertIn('interp=tetrahedral', filters)
        self.assertIn('out_range=tv', filters)
    def test_target_inside_original_tree_rejected_before_download(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); manifest=root/'inventory.json'
            manifest.write_text(json.dumps({'root':str(root),'videos':[]}))
            with self.assertRaisesRegex(ValueError, 'outside original'): kit.convert(manifest,root/'converted')

if __name__=='__main__': unittest.main()
