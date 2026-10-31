import copy,importlib.util,unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import interview_edit as kit

class InterviewEditTests(unittest.TestCase):
 def test_loudnorm_json_survives_ffmpeg_trailing_progress(self):
  expected={'input_i':'-14.12','input_tp':'-1.50'}
  import json
  self.assertEqual(kit.loudness_json('[Parsed_loudnorm] '+json.dumps(expected)+'\n[out] audio:6325KiB\nsize=0 time=00:00:33.73\n'),expected)
 def test_missing_or_incomplete_loudness_is_not_treated_as_success(self):
  for text in ['no measurement','{invalid}','{"output_i":"-14"}']:
   with self.assertRaises(ValueError):kit.loudness_json(text)
 def test_corner_crest_rejects_opaque_background_and_accepts_cutout(self):
  from unittest.mock import patch
  import tempfile
  from PIL import Image
  with tempfile.TemporaryDirectory() as t,patch.object(kit,'ROOT',Path(t)):
   path=Path(t)/'public/assets/brands/jetkids/logo-transparent.png';path.parent.mkdir(parents=True)
   Image.new('RGB',(12,12),'black').save(path)
   with self.assertRaisesRegex(ValueError,'RGBA cutout'):kit.corner_crest()
   im=Image.new('RGBA',(12,12),(0,0,0,0));im.paste((255,255,255,255),(3,3,9,9));im.save(path)
   self.assertEqual(kit.corner_crest(),path)
   im.putpixel((0,0),(0,0,0,255));im.save(path)
   with self.assertRaisesRegex(ValueError,'corners must be transparent'):kit.corner_crest()
 def plan(self):
  return dict(kind='jetkids-interview',id='jetkids-test-v01',fps=30,eventPhotoInserts=False,logoFrames=45,dialogueFrames=60,cuts=[dict(source_id='V014',inFrame=30,outFrame=90,timelineFrom=0,duration=60)],formats={f:dict(shots=[dict(source_id='V014',timelineFrom=0,frames=60)]) for f in ['landscape','portrait']})
 def words(self):return [dict(source_id='V014',text='Complete',start=1.2,end=1.6),dict(source_id='V014',text='thought',start=1.6,end=2.5)]
 def test_portrait_only_delivery_does_not_require_landscape(self):
  p=self.plan();del p['formats']['landscape'];self.assertEqual(kit.validate_structure(p,self.words()),60)
 def test_evening_footage_requires_explicit_event_commission(self):
  p=self.plan();p['sources']={'V128':{'event':'evening'}}
  with self.assertRaisesRegex(ValueError,'explicit evening plan'):kit.validate_event_scope(p)
  p['event']='evening';kit.validate_event_scope(p)
 def test_evening_plan_rejects_morning_and_unassigned_broll(self):
  p=self.plan();p['event']='evening';p['sources']={'V128':{'event':'evening'}}
  for event in ['sports','']:
   p['sources']['BROLL']={'event':event}
   with self.assertRaisesRegex(ValueError,'explicitly evening source'):kit.validate_event_scope(p)
 def test_historical_sports_plans_remain_valid_without_event_field(self):
  p=self.plan();p['sources']={'V014':{},'V015':{'event':'sports'}};kit.validate_event_scope(p)
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
 def test_block_caption_lines_remain_readable_until_complete_phrase_end(self):
  import tempfile
  p=self.plan();p['captionStyle']={'treatment':'editorial','lineReveal':'block'};p['captionPhrases']=['Complete thought'];p['captionLayouts']=[{'lines':[{'words':1,'size':110,'y':1350},{'words':1,'size':150,'y':1480}]}]
  with tempfile.TemporaryDirectory() as folder:
   group=kit.subtitles(p,self.words(),'portrait',Path(folder)/'captions.ass')[0]
   self.assertEqual([line['start'] for line in group['lines']],[group['start'],group['start']])
   self.assertEqual([line['end'] for line in group['lines']],[group['end'],group['end']])
   self.assertEqual([w['text'] for w in group['words']],['Complete','thought'])
 def test_source_grade_rejects_unbounded_or_executable_values(self):
  for grade in [{'gamma':1.9},{'brightness':float('nan')},{'gamma_r':True},{'gamma':'1;movie=private'},{'lut3d':'guess.cube'}]:
   with self.assertRaises(ValueError):kit.colour_grade_filter({'colourGrade':grade})
 def test_source_grade_lifts_dark_picture_without_changing_frame_clock(self):
  import shutil,tempfile,subprocess
  if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):self.skipTest('FFmpeg integration runtime unavailable')
  with tempfile.TemporaryDirectory() as folder:
   source=Path(folder)/'source.mp4';kit.run(['-f','lavfi','-i','color=c=0x506050:size=180x320:rate=25:duration=0.24','-c:v','libx264','-y',source]);means=[]
   for i,grade in enumerate([{},dict(gamma=1.12,brightness=.01,gamma_r=1.02,gamma_g=.98,gamma_b=1.02)]):
    plan={'sources':{'V014':{'rotate':False,'colourGrade':grade}}};shot={'source_id':'V014','renderFrames':8,'speed':1};output=Path(folder)/f'picture-{i}.mp4'
    vf=kit.crop_filter(plan,shot,'portrait',{'V014':{'width':180,'height':320}})
    kit.run(['-threads','2','-filter_threads','2','-i',source,'-vf',vf,'-r','30','-fps_mode','cfr','-frames:v',8,'-c:v','libx264','-preset','ultrafast','-threads','2','-y',output])
    video=next(v for v in kit.probe(output)['streams'] if v['codec_type']=='video');self.assertEqual(int(video['nb_frames']),8);self.assertAlmostEqual(float(video['duration']),8/30,places=5)
    pixels=subprocess.check_output(['ffmpeg','-v','error','-i',str(output),'-vf','scale=16:16','-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','-']);means.append(sum(pixels)/len(pixels));self.assertLess(max(pixels),245)
   self.assertGreater(means[1],means[0]+5)
 def test_vertical_crop_path_is_applied_without_changing_dialogue_speed(self):
  plan={'sources':{'V014':{'rotate':False}}};shot={'source_id':'V014','renderFrames':30,'speed':1,'zoom':1.6,'crop_path':[[0,.48],[1,.50]],'crop_path_y':[[0,.63],[1,.65]]}
  f=kit.crop_filter(plan,shot,'portrait',{'V014':{'width':1440,'height':2560}})
  self.assertIn('ih*(',f);self.assertIn('iw*(',f);self.assertIn('(PTS-STARTPTS)/1',f)
 def test_fractional_source_end_keeps_requested_frame_count(self):
  import shutil,tempfile,subprocess
  if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):self.skipTest('FFmpeg integration runtime unavailable')
  with tempfile.TemporaryDirectory() as folder:
   source=Path(folder)/'source.mp4';output=Path(folder)/'picture.mp4'
   kit.run(['-f','lavfi','-i','testsrc2=size=180x320:rate=25:duration=1.04','-c:v','libx264','-y',source])
   plan={'sources':{'V014':{'rotate':False}}};shot={'source_id':'V014','renderFrames':38,'holdLeadFrames':6,'speed':1}
   vf=kit.crop_filter(plan,shot,'portrait',{'V014':{'width':180,'height':320}})
   kit.run(['-threads','2','-filter_threads','2','-i',source,'-vf',vf,'-r','30','-fps_mode','cfr','-frames:v',38,'-c:v','libx264','-preset','ultrafast','-threads','2','-y',output])
   video=next(v for v in kit.probe(output)['streams'] if v['codec_type']=='video')
   self.assertEqual(int(video['nb_frames']),38)
   self.assertAlmostEqual(float(video['duration']),38/30,places=5)
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
 def test_graphics_refresh_rejects_changed_edit_before_encoding(self):
  from unittest.mock import patch
  import tempfile
  p=self.plan()
  with tempfile.TemporaryDirectory() as t,patch.object(kit,'ROOT',Path(t)),patch.object(kit,'preflight',return_value=(p,self.words(),{})),patch.object(kit,'finish_picture') as finish:
   c=Path(t)/'.cache/jetkids/interview-edits'/p['id'];c.mkdir(parents=True);(c/'signature').write_text('another edit')
   with self.assertRaisesRegex(ValueError,'Changed edit plan'):kit.refinish_current(Path(t))
   finish.assert_not_called()
 def test_graphics_refresh_does_not_replace_export_when_audio_packets_change(self):
  from unittest.mock import patch
  import tempfile,json,hashlib
  p=self.plan();words=self.words()
  with tempfile.TemporaryDirectory() as t,patch.object(kit,'ROOT',Path(t)),patch.object(kit,'preflight',return_value=(p,words,{})):
   root=Path(t);c=root/'.cache/jetkids/interview-edits'/p['id'];w=c/'portrait';w.mkdir(parents=True)
   (c/'signature').write_text(hashlib.sha256(json.dumps(dict(plan=p,words=words),sort_keys=True).encode()).hexdigest());(w/'silent.mp4').write_bytes(b'cached picture');kit.save(w/'qa.json',{})
   d=root/'exports/jetkids-interview-edits'/p['id']/'portrait.mp4';d.parent.mkdir(parents=True);d.write_bytes(b'approved current export')
   with patch.object(kit,'finish_picture',return_value=({}, {}, [])),patch.object(kit.subprocess,'check_output',side_effect=['SHA256=original','SHA256=changed']):
    with self.assertRaisesRegex(ValueError,'changed encoded audio'):kit.refinish_current(root)
   self.assertEqual(d.read_bytes(),b'approved current export')
if __name__=='__main__':unittest.main()
