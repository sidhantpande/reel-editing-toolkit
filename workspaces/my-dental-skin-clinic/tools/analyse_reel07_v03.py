#!/usr/bin/env python3
"""Align caption words and prepare conservative, speech-protected pause cuts."""
import json
import re
import subprocess
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio,pad_or_trim
from faster_whisper.tokenizer import Tokenizer
from faster_whisper.vad import get_speech_timestamps,VadOptions
import clinic

R=Path(__file__).resolve().parents[1]
OUT=R/'03_reels/reel-07/04_timeline/v03'
SPECS=[
 ('0093',1.6,7.45,'कालरात्रि | सबसे fierce रूप'),
 ('0093',7.45,14.4,'उनका काम है | अंधेरा और डर मिटाना | आज हम | एक डर मिटाते हैं'),
 ('0093',14.9,22.633333,'दाँत नहीं | मतलब कहानी खत्म | ऐसा नहीं है | उसके solutions भी हैं'),
 ('0096',0,10.133333,'एक option होता है | implant | implant को हम | उसके neighbouring tooth को | disturb किए बिना | independently | implant place करके | उसके ऊपर हम | दाँत लगा सकते हैं'),
 ('0096',10.55,24.35,'उसके बाद | second option होता है | bridge | bridge में हम | क्या करते हैं | उसके आजू बाजू के | दोनों दाँत को | use करके | या तीनों दाँत को | multiple bridges भी | हो सकते हैं | आजू बाजू के दाँत को | जब हम use करते हैं | उसको हम | bridges बोलते हैं'),
 ('0096',25.5,31.1,'removable | ये third option भी | हो सकता है | कहीं कहीं पे | वो भी permissible | होता है'),
 ('0097',0,9.333333,'तो | कौन सा best है | ये आपका | Instagram | decide नहीं करेगा | आपकी clinical condition | decide करेगी'),
]

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 rows=json.loads((R/'01_catalog/sources.json').read_text())
 sources={r['filename'].split('_')[-2]:r for r in rows}
 original=json.loads((R/'03_reels/reel-07/04_timeline/edit-plan.json').read_text())
 model=WhisperModel(str(clinic.model_path()),device='cpu',compute_type='int8',cpu_threads=4)
 tokenizer=Tokenizer(model.hf_tokenizer,model.model.is_multilingual,task='transcribe',language='hi')
 data={};all_words=[];phrase_id=0
 for number in ['0093','0096','0097']:
  src=sources[number];audio=decode_audio(str(R/'02_analysis'/src['id']/'audio.wav'))
  amplified=np.clip(audio*4,-.98,.98)
  vad=get_speech_timestamps(amplified,VadOptions(threshold=.42,min_silence_duration_ms=250,speech_pad_ms=70,min_speech_duration_ms=100))
  speech=[(s['start']/16000,s['end']/16000) for s in vad]
  log=subprocess.run([clinic.FF,'-hide_banner','-i',str(R/'02_analysis'/src['id']/'audio.wav'),'-af','silencedetect=n=-44dB:d=0.25','-f','null','-'],capture_output=True,text=True,check=True).stderr
  starts=[float(x) for x in re.findall(r'silence_start: ([0-9.]+)',log)]
  ends=[float(x) for x in re.findall(r'silence_end: ([0-9.]+)',log)]
  if len(ends)<len(starts):ends.append(len(audio)/16000)
  # Join negligible energy blips only where VAD also considers the region non-speech.
  energy=[]
  for a,b in zip(starts,ends):
   if energy and a-energy[-1][1]<.13:energy[-1][1]=b
   else:energy.append([a,b])
  gaps=[];prev=0
  for a,b in speech:
   if a>prev:gaps.append((prev,a))
   prev=b
  if prev<len(audio)/16000:gaps.append((prev,len(audio)/16000))
  cuts=[]
  for a,b in energy:
   for c,d in gaps:
    left,right=max(a,c),min(b,d)
    if right-left>.27:
     # VAD already carries 70 ms speech padding; preserve another 35 ms each side.
     cuts.append([left+.035,right-.035])
  data[number]={'source':src['paths'][0],'speech':speech,'energy_silences':energy,'cuts':cuts,'duration':len(audio)/16000}
 for number,start,end,annotated in SPECS:
  src=sources[number]
  audio=decode_audio(str(R/'02_analysis'/src['id']/'audio.wav'))[round(start*16000):round(end*16000)]
  audio=np.clip(audio*4,-.98,.98)
  features=model.feature_extractor(audio)
  encoded=model.encode(pad_or_trim(features))
  phrases=[p.strip() for p in annotated.split('|')]
  expected=[]
  for phrase in phrases:
   for word in phrase.split():expected.append({'text':word,'phrase_id':phrase_id})
   phrase_id+=1
  text=' '+' '.join(w['text'] for w in expected)
  aligned=model.find_alignment(tokenizer,[tokenizer.encode(text)],encoded,features.shape[-1])[0]
  # Tokenizer word splitting is space based for this text. Keep a diagnostic on mismatches.
  clean=[w for w in aligned if w['word'].strip()]
  if len(clean)!=len(expected):
   raise RuntimeError(f'Alignment word-count mismatch in {number}: {len(clean)} vs {len(expected)}')
  for item,timing in zip(expected,clean):
   s=start+float(timing['start']);e=min(end,start+float(timing['end']))
   if e-s>.95 and item['text']!='कालरात्रि':s=max(s,e-.65)
   all_words.append({**item,'source_id':number,'source_start':s,'source_end':e,'alignment_probability':float(timing['probability'])})
  print('Aligned',number,start,end,len(expected),'words',flush=True)
 # Apply only confirmed non-speech cuts to the existing editorial selects.
 segments=[];cursor=0
 for old in original['segments']:
  number=Path(old['source']).stem.split('_')[-2]
  a,b=old['source_in'],old['source_out'];keep=[];position=a
  for ca,cb in sorted(data[number]['cuts']):
   ca=max(ca,a);cb=min(cb,b)
   if cb<=ca:continue
   if ca>position:keep.append([position,ca])
   position=max(position,cb)
  if position<b:keep.append([position,b])
  # No slivers caused by source starts/ends inside known long silence.
  keep=[(x,y) for x,y in keep if y-x>.085]
  for x,y in keep:
   duration=round((y-x)*30)/30
   if duration<=0:continue
   segments.append({**old,'source_id':number,'source_in':x,'source_out':x+duration,'timeline_in':cursor,'timeline_out':cursor+duration})
   cursor+=duration
 def mapped(number,t,end=False):
  matches=[s for s in segments if s['source_id']==number and s['source_in']-.001<=t<=s['source_out']+.001]
  if matches:
   s=matches[0];return s['timeline_in']+min(max(t-s['source_in'],0),s['timeline_out']-s['timeline_in'])
  future=[s for s in segments if s['source_id']==number and s['source_in']>t]
  past=[s for s in segments if s['source_id']==number and s['source_out']<t]
  if end and past:return past[-1]['timeline_out']
  if future:return future[0]['timeline_in']
  if past:return past[-1]['timeline_out']
  return None
 words=[]
 for word in all_words:
  a=mapped(word['source_id'],word['source_start']);b=mapped(word['source_id'],word['source_end'],True)
  if a is None or b is None:continue
  words.append({**word,'start':round(a,4),'end':round(max(a+.035,b),4)})
 # Preserve monotonic entrance timing; keep each word in reading order.
 for i,w in enumerate(words):
  if i and w['start']<words[i-1]['start']+.035:w['start']=round(words[i-1]['start']+.035,4)
  w['end']=max(w['end'],w['start']+.035)
 slots=[]
 for old in original['broll_slots']:
  a=mapped('0096',old['source_in']);b=mapped('0096',old['source_out'],True)
  slots.append({**old,'timeline_in':a,'timeline_out':b})
 plan={'status':'PAUSE_TRIMMED_WORD_ALIGNMENT_REVIEW','fps':30,'duration_seconds':round(cursor,4),'previous_duration':original['duration_seconds'],'removed_seconds':round(original['duration_seconds']-cursor,4),'segments':segments,'words':words,'broll_slots':slots,'source_detection':data,'alignment_method':'Whisper cross-attention forced alignment against corrected ASR text; not human listening verification'}
 (OUT/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
 print('Prepared',len(segments),'speech runs;',len(words),'words;',round(cursor,2),'seconds',flush=True)

if __name__=='__main__':main()
