import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import interview_question as question
import interview_edit as kit


class InterviewQuestionTests(unittest.TestCase):
    def plan(self):
        return dict(leadFrames=6, dialogueFrames=1200, logoFrames=45,
                    sources={'V211': {}})

    def opening(self):
        return dict(durationFrames=132, transitionFrames=6,
                    question='एक सवाल?', lines=['एक', 'सवाल?'],
                    englishQuestion='A question?', englishLines=['A question?'],
                    wording='condensed question, not a verbatim quotation',
                    sourceQuestion=dict(source_id='V211', start=1, end=4))

    def test_one_integer_offset_controls_both_clocks_and_complete_duration(self):
        timing = question.validate_question(self.plan(), self.opening())
        self.assertEqual(timing['bodyOffsetFrames'], 126)
        self.assertEqual(timing['totalFrames'], 1371)

    def test_transition_must_not_overlap_first_speech(self):
        opening = self.opening()
        opening['transitionFrames'] = 9
        with self.assertRaisesRegex(ValueError, 'first spoken phoneme'):
            question.validate_question(self.plan(), opening)

    def test_fifty_second_limit_includes_question_and_logo(self):
        plan = self.plan()
        plan['dialogueFrames'] = 1400
        with self.assertRaisesRegex(ValueError, '50 seconds'):
            question.validate_question(plan, self.opening())

    def test_layout_cannot_drop_question_words_or_inject_ass(self):
        opening = self.opening()
        opening['lines'] = ['एक', 'बदलाव?']
        with self.assertRaisesRegex(ValueError, 'complete authored question'):
            question.validate_question(self.plan(), opening)
        opening.update(question=r'{\p1} सवाल?', lines=[r'{\p1}', 'सवाल?'])
        with self.assertRaisesRegex(ValueError, 'plain text'):
            question.validate_question(self.plan(), opening)

    def test_original_cache_must_match_and_exist_before_replacing_delivery(self):
        with tempfile.TemporaryDirectory() as t:
            cache = Path(t)
            (cache/'signature').write_text('old')
            with self.assertRaisesRegex(ValueError, 'Changed edit plan'):
                question.assert_cached_body(cache, 'new')
            with self.assertRaisesRegex(ValueError, 'Missing original body'):
                question.assert_cached_body(cache, 'old')

    def test_bilingual_part_numbers_must_match(self):
        opening = self.opening()
        opening.update(partNumber=2, partLabel='भाग 1 / Part 2')
        with self.assertRaisesRegex(ValueError, 'matching Hindi and English'):
            question.validate_question(self.plan(), opening)
        opening['partLabel'] = 'भाग 2 / Part 2'
        question.validate_question(self.plan(), opening)

    def test_video_and_audio_use_the_same_lead_overlap(self):
        import json
        from types import SimpleNamespace
        plan = self.plan()
        plan.update(captionStyle={}, fps=30)
        opening = dict(self.opening(), cardPath='card.mkv', audioPath='prefix.wav')
        measured = dict(input_i='-14.0', input_tp='-1.5')
        with tempfile.TemporaryDirectory() as t:
            folder = Path(t)
            with patch.object(kit, 'corner_crest', return_value=folder/'crest.png'), \
                 patch.object(kit, 'subtitles', return_value=[]), \
                 patch.object(kit, 'run') as run, \
                 patch.object(kit, 'probe', return_value={'streams': [dict(codec_type='video', nb_frames=1371, width=1080, height=1920)]}), \
                 patch.object(kit.subprocess, 'run', return_value=SimpleNamespace(stderr=json.dumps(measured))):
                kit.finish_picture(plan, [], 'portrait', folder, 'master.wav', folder/'pending.mp4', question=opening)
            args = run.call_args_list[0].args[0]
            graph = args[args.index('-filter_complex')+1]
            self.assertIn('duration=0.2:offset=4.2', graph)
            self.assertIn('acrossfade=d=0.2', graph)
            self.assertEqual(args[args.index('-frames:v')+1], 1371)
            self.assertIn('master.wav', args)

    def test_standard_render_and_refinish_cannot_silently_remove_opening(self):
        with tempfile.TemporaryDirectory() as t, patch.object(kit, 'preflight') as preflight:
            project = Path(t)
            (project/'opening-question.json').write_text('{}')
            for action in [kit.render, kit.refinish_current]:
                with self.assertRaisesRegex(ValueError, 'retain the question'):
                    action(project)
            preflight.assert_not_called()


if __name__ == '__main__':
    unittest.main()
