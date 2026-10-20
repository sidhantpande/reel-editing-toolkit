import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('neural_beats', Path(__file__).resolve().parents[1] / 'tools/neural_beats.py')
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)


class NeuralBeatValidationTests(unittest.TestCase):
    def test_monotonic_source_times_preserved(self):
        self.assertEqual(kit.checked_times([0, .5, 1.01], 2), [0, .5, 1.01])

    def test_reject_invalid_predictions_before_edit_use(self):
        for values in ([.5, .4], [.5, .5], [float('nan')], [-.1], [2.01]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                kit.checked_times(values, 2)

    def test_empty_analysis_does_not_fabricate_beats(self):
        self.assertEqual(kit.checked_times([], 2), [])
