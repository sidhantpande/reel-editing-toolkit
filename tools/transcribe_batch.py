#!/usr/bin/env python3
"""Cache source-language word timing for the remaining matched recordings, in source order."""
from pathlib import Path
import json,subprocess
from faster_whisper import WhisperModel
R=Path(__file__).resolve().parents[1]
model=WhisperModel('medium',device='cpu',compute_type='int8',cpu_threads=6)
queue=json.loads((R/'projects/batch-queue.json').read_text())['reels']
for reel in queue:
 if reel['status']=='approved':continue
 p=R/reel['project'];plan=json.loads((p/'edit-plan.json').read_text());(p/'analysis').mkdir(exist_ok=True)
 for take in plan['takes']:
  if take['role']=='false-start':continue
  source=R/take['path'];dest=p/'analysis'/(source.stem+'-medium-'+reel['language']+'.json')
  if dest.exists():print('Cached',dest,flush=True);continue
  wav=R/'.cache/audio'/(source.stem+'.wav')
  if not wav.exists():subprocess.run(['ffmpeg','-v','error','-i',str(source),'-vn','-ac','1','-ar','16000','-y',str(wav)],check=True)
  print('START',source.stem,flush=True)
  segments,info=model.transcribe(str(wav),language=reel['language'],beam_size=5,word_timestamps=True,condition_on_previous_text=False,vad_filter=True)
  out=[]
  for x in segments:
   out.append(dict(start=x.start,end=x.end,text=x.text,words=[dict(text=w.word,start=w.start,end=w.end,probability=w.probability) for w in x.words]));print(f'{source.stem} {x.start:.2f}-{x.end:.2f} {x.text}',flush=True)
  dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('DONE',dest,flush=True)
