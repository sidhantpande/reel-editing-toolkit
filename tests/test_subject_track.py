import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('subject_track', Path(__file__).resolve().parents[1] / 'tools/subject_track.py')
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)


class SubjectPathTests(unittest.TestCase):
    def test_invalid_time_and_offscreen_paths_rejected(self):
        for points in ([], [[0, .5], [0, .6]], [[0, .1]], [[0, float('nan')]], [[-1, .5]]):
            with self.subTest(points=points), self.assertRaises(ValueError):
                kit.crop_expression(points)

    def test_smoothing_removes_single_sample_jitter_without_constant_offset(self):
        result = kit.smooth([.5, .5, .7, .5, .5])
        self.assertEqual(result, [.5]*5)
        self.assertEqual(kit.smooth([.6]*8), [.6]*8)

    def test_expression_keeps_nonlinear_intermediate_target(self):
        expression = kit.crop_expression([[0, .3], [1, .7], [2, .4]])
        self.assertIn('lt(t,1.0000000)', expression)
        self.assertIn('0.7000000', expression)
