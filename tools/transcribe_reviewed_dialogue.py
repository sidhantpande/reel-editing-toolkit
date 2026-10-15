#!/usr/bin/env python3
"""Independently inspect assembled dialogue for missing or clipped speech before delivery."""
from pathlib import Path
import argparse,json
from faster_whisper import WhisperModel
R=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('projects',nargs='+');a=ap.parse_args();queue=json.loads((R/'projects/batch-queue.json').read_text())['reels'];model=WhisperModel('medium',device='cpu',compute_type='int8',cpu_threads=6)
for project in a.projects:
 P=R/project;dest=P/'analysis/edited-dialogue-medium-check.json'
 if dest.exists():print('Cached',P.name,flush=True);continue
 lang=next(x['language'] for x in queue if x['id']==P.name);segments,_=model.transcribe(str(R/'.cache/proxies'/(P.name+'-dialogue.wav')),language=lang,beam_size=5,condition_on_previous_text=False,vad_filter=True)
 out=[]
 for s in segments:out.append(dict(start=s.start,end=s.end,text=s.text));print(P.name,s.text,flush=True)
 dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
