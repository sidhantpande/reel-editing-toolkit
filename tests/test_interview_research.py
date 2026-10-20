import importlib.util
import json
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('interview_research', Path(__file__).resolve().parents[1] / 'tools/interview_research.py')
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)


class InterviewResearchTests(unittest.TestCase):
    def test_measured_silence_is_accounted_without_invented_transcription(self):
        result, errors = kit.compile_one(dict(id='S463', path='/source.mp4', duration=14.4,
                                             audio_status='silent', peak=0), Path('/absent'), Path('/absent'))
        self.assertEqual(result['engine'], 'measured-silence')
        self.assertEqual(result['segments'], [])
        self.assertFalse(result['editor_listening_attestation'])
        self.assertEqual(errors, [])

    def test_duplicate_ids_and_truncated_audio_are_not_silently_merged(self):
        row = dict(id='V203', duration=40, audio_duration=40)
        with self.assertRaises(ValueError):
            kit.checked_manifest([row, row])
        with self.assertRaises(ValueError):
            kit.checked_manifest([dict(row, audio_duration=20)])

    def test_native_overrun_stays_visible_and_never_becomes_approved_cut(self):
        raw = json.dumps(dict(transcription=[dict(text='A complete thought', offsets={'from': 8000, 'to': 14000})])).encode()
        result = kit.native_research(raw, dict(id='V014', duration=10))
        seg = result['segments'][0]
        self.assertEqual((seg['start'], seg['end']), (8, 10))
        self.assertEqual(seg['original_asr_end'], 14)
        self.assertTrue(seg['timing_issues'])
        self.assertFalse(seg['cut_approved'])

    def test_invalid_native_token_bytes_do_not_hide_decoding_warning(self):
        raw = b'{"transcription":[{"text":"clear words","offsets":{"from":0,"to":1000},"tokens":[{"text":"\xe0\xa4"}]}]}'
        result = kit.native_research(raw, dict(id='V016', duration=2))
        self.assertGreater(result['invalid_utf8_replacements'], 0)
        self.assertEqual(result['segments'][0]['text'], 'clear words')

    def test_overlapping_evidence_keeps_original_source_word_ownership(self):
        doc = dict(chunks=[dict(source_start=0, language='en', segments=[dict(start=1, end=3, text='one thought', words=[dict(start=1, end=2, word='one')])]), dict(source_start=2, language='en', segments=[dict(start=2, end=4, text='thought continued')])])
        result = kit.fallback_research(doc, dict(id='V123', duration=5))
        self.assertEqual(len(result['segments']), 2)
        self.assertEqual(result['segments'][0]['words'][0]['source_id'], 'V123')
        self.assertEqual(result['segments'][1]['start'], 2)


if __name__ == '__main__':
    unittest.main()
