import copy,importlib.util,unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import interview_edit as kit

class InterviewEditTests(unittest.TestCase):
 def plan(self):
  return dict(kind='jetkids-interview',id='jetkids-test-v01',fps=30,eventPhotoInserts=False,logoFrames=45,dialogueFrames=60,cuts=[dict(source_id='V014',inFrame=30,outFrame=90,timelineFrom=0,duration=60)],formats={f:dict(shots=[dict(source_id='V014',timelineFrom=0,frames=60)]) for f in ['landscape','portrait']})
 def words(self):return [dict(source_id='V014',text='Complete',start=1.2,end=1.6),dict(source_id='V014',text='thought',start=1.6,end=2.5)]
 def test_portrait_only_delivery_does_not_require_landscape(self):
  p=self.plan();del p['formats']['landscape'];self.assertEqual(kit.validate_structure(p,self.words()),60)
 def test_dialogue_speed_change_is_rejected(self):
  p=self.plan();p['cuts'][0]['speechSpeed']=.6
  with self.assertRaises(ValueError):kit.validate_structure(p,self.words())
 def test_different_source_and_zero_word_duration_rejected(self):
  for changes in [dict(source_id='V015'),dict(start=1.6,end=1.6)]:
   w=self.words();w[0].update(changes)
   with self.assertRaises(ValueError):kit.validate_structure(self.plan(),w)
 def test_picture_gap_cannot_silently_shorten_speech(self):
  p=self.plan();p['formats']['portrait']['shots'][0]['frames']=59
  with self.assertRaises(ValueError):kit.validate_structure(p,self.words())
 def test_source_times_map_to_native_rate_without_stretch(self):
  self.assertEqual(kit.validate_structure(self.plan(),self.words()),60)
  w=kit.mapped_words(self.plan(),self.words())
  self.assertAlmostEqual(w[0]['start'],.2);self.assertAlmostEqual(w[-1]['end'],1.5)
 def test_breathing_room_shifts_words_and_does_not_shorten_speech(self):
  p=self.plan();p.update(leadFrames=12,tailFrames=18,dialogueFrames=90);p['cuts'][0]['timelineFrom']=12
  for f in p['formats']:p['formats'][f]['shots'][0]['frames']=90
  kit.validate_structure(p,self.words());self.assertAlmostEqual(kit.mapped_words(p,self.words())[0]['start'],.6)
 def test_progressive_captions_never_show_next_word_early(self):
  import tempfile
  p=self.plan();p['captionStyle']={'progressive':True}
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'captions.ass';kit.subtitles(p,self.words(),'portrait',a);text=a.read_text()
   self.assertIn('0:00:00.60',text);self.assertIn('Complete thought',text)
   self.assertIn(r'\an7\pos(112,1455)',text)
 def test_curated_phrases_preserve_every_source_word(self):
  words=self.words();self.assertEqual(len(kit.caption_groups(words,True,['Complete thought'])),1)
  for bad in [['Complete'],['Invented thought']]:
   with self.assertRaises(ValueError):kit.caption_groups(words,True,bad)
 def test_mixed_phrase_uses_consistent_font_during_reveal(self):
  import tempfile
  p=self.plan();p['captionStyle']={'progressive':True};words=self.words();words[1]['text']='है'
  with tempfile.TemporaryDirectory() as t:
   a=Path(t)/'captions.ass';kit.subtitles(p,words,'portrait',a)
   self.assertNotIn(r'\fnMontserrat',a.read_text())
 def test_second_source_word_is_not_attached_to_first_speakers_cut(self):
  p=self.plan();p['cuts'].append(dict(source_id='V015',inFrame=0,outFrame=30,timelineFrom=60,duration=30));p['dialogueFrames']=90
  for f in p['formats']:p['formats'][f]['shots'].append(dict(source_id='V015',timelineFrom=60,frames=30))
  w=self.words()+[dict(source_id='V015',text='Another',start=.1,end=.8)]
  kit.validate_structure(p,w);self.assertAlmostEqual(kit.mapped_words(p,w)[-1]['start'],2.1)
if __name__=='__main__':unittest.main()
