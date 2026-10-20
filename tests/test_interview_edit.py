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
 def test_editorial_caption_layout_preserves_words_and_center_geometry(self):
  import tempfile
  p=self.plan();p['captionStyle']={'treatment':'editorial'};p['captionPhrases']=['Complete thought'];p['captionLayouts']=[{'lines':[{'words':1,'size':110,'y':1350},{'words':1,'size':150,'y':1480}]}]
  with tempfile.TemporaryDirectory() as t:
   q=Path(t)/'captions.ass';groups=kit.subtitles(p,self.words(),'portrait',q)
   self.assertEqual([line['text'] for line in groups[0]['lines']],['Complete','thought'])
   self.assertEqual([line['x'] for line in groups[0]['lines']],[540,540])
   p['captionLayouts'][0]['lines'][1]['words']=2
   with self.assertRaises(ValueError):kit.subtitles(p,self.words(),'portrait',q)
 def test_vertical_crop_path_is_applied_without_changing_dialogue_speed(self):
  plan={'sources':{'V014':{'rotate':False}}};shot={'source_id':'V014','renderFrames':30,'speed':1,'zoom':1.6,'crop_path':[[0,.48],[1,.50]],'crop_path_y':[[0,.63],[1,.65]]}
  f=kit.crop_filter(plan,shot,'portrait',{'V014':{'width':1440,'height':2560}})
  self.assertIn('ih*(',f);self.assertIn('iw*(',f);self.assertIn('(PTS-STARTPTS)/1',f)
 def test_merged_alignment_unit_remains_atomic_in_curated_phrase(self):
  words=[dict(source_id='V020',text='The sports',start=1,end=1.4),dict(source_id='V020',text='is',start=1.4,end=1.6)]
  groups=kit.caption_groups(words,False,['The sports is'])
  self.assertEqual(len(groups[0]),2)
  self.assertEqual(groups[0][0]['text'],'The sports')
 def test_decoded_holds_cannot_replace_all_source_frames(self):
  for lead,tail in [(60,0),(30,30),(-1,0),(True,0)]:
   p=self.plan();p['formats']['portrait']['shots'][0].update(holdLeadFrames=lead,holdTailFrames=tail)
   with self.assertRaises(ValueError):kit.validate_structure(p,self.words())
 def test_prepared_dialogue_uses_original_source_offset(self):
  from unittest.mock import patch
  import tempfile
  p=self.plan();p['sources']={'V014':{'path':'original.mov','preparedAudio':{'path':'prepared.wav','source_start':.75}}};p['music']='music.wav'
  measured={'input_i':'-15','input_tp':'-2','input_lra':'3','input_thresh':'-25','target_offset':'0'}
  import json
  with tempfile.TemporaryDirectory() as t,patch.object(kit,'run') as run,patch.object(kit.subprocess,'run',return_value=type('Result',(),{'stderr':json.dumps(measured)})()):
   kit.normalized_audio(p,Path(t))
   first=run.call_args_list[0].args[0];self.assertEqual(first[:4],['-ss',.25,'-i','prepared.wav']);self.assertEqual(first[first.index('-t')+1],2)
 def test_second_source_word_is_not_attached_to_first_speakers_cut(self):
  p=self.plan();p['cuts'].append(dict(source_id='V015',inFrame=0,outFrame=30,timelineFrom=60,duration=30));p['dialogueFrames']=90
  for f in p['formats']:p['formats'][f]['shots'].append(dict(source_id='V015',timelineFrom=60,frames=30))
  w=self.words()+[dict(source_id='V015',text='Another',start=.1,end=.8)]
  kit.validate_structure(p,w);self.assertAlmostEqual(kit.mapped_words(p,w)[-1]['start'],2.1)
 def test_prepared_voice_does_not_receive_a_second_enhancement_or_eq_pass(self):
  from unittest.mock import patch
  import tempfile,json
  p=self.plan();p['sources']={'V014':{'path':'original.mov','preparedVoice':{'path':'enhanced-master.wav','source_start':.75}}};p['music']='music.wav';p['voiceEnhancement']={'engine':'DeepFilterNet3'}
  measured={'input_i':'-15','input_tp':'-2','input_lra':'3','input_thresh':'-25','target_offset':'0'}
  with tempfile.TemporaryDirectory() as t,patch.object(kit,'run') as run,patch.object(kit.subprocess,'run',return_value=type('Result',(),{'stderr':json.dumps(measured)})()):
   kit.normalized_audio(p,Path(t));calls=[c.args[0] for c in run.call_args_list]
   self.assertEqual(calls[0][:4],['-ss',.25,'-i','enhanced-master.wav'])
   filters=' '.join(str(c) for c in calls)
   self.assertNotIn('highpass',filters);self.assertNotIn('equalizer',filters)
   self.assertTrue((Path(t)/'prepared-voice-reuse.json').exists())
 def test_mixing_prepared_and_unprocessed_voice_is_rejected(self):
  p=self.plan();p['cuts'].append(dict(source_id='V015'));p['sources']={'V014':{'preparedVoice':{'path':'master.wav'}},'V015':{}}
  with self.assertRaises(ValueError):kit.uses_prepared_voice(p)
 def sync_plan(self):
  p=self.plan();p.update(leadFrames=6,dialogueFrames=66,enforceDialoguePictureSync=True)
  p['cuts'][0]['timelineFrom']=6
  p['sources']={'V014':{'path':'original.mov'},'STABLE':{'path':'stable.mp4','derivedFrom':'V014','sourceOffset':0}}
  for fmt in p['formats']:p['formats'][fmt]['shots']=[dict(source_id='STABLE',timelineFrom=0,frames=66,holdLeadFrames=6,**{'in':1.0})]
  return p
 def test_decoded_opening_hold_is_excluded_from_lipsync_clock(self):
  self.assertEqual(kit.validate_structure(self.sync_plan(),self.words()),66)
 def test_twelve_frame_picture_lead_is_rejected(self):
  p=self.sync_plan();p['formats']['portrait']['shots'][0]['in']+=.4
  with self.assertRaisesRegex(ValueError,'Lip-sync mismatch'):kit.validate_structure(p,self.words())
 def test_broll_can_slow_down_but_talking_head_cannot(self):
  p=self.sync_plan();p['sources']['GAME']={'path':'game.mp4'}
  p['formats']['portrait']['shots'][0].update(source_id='GAME',speed=.4)
  kit.validate_structure(p,self.words())
  p['formats']['portrait']['shots'][0].update(source_id='STABLE')
  with self.assertRaisesRegex(ValueError,'Lip-sync mismatch'):kit.validate_structure(p,self.words())
if __name__=='__main__':unittest.main()
