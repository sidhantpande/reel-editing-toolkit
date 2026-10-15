#!/usr/bin/env python3
"""Local ASR for draft content matching; English mode may paraphrase Hindi. Never final captions."""
import argparse,json
from pathlib import Path
from faster_whisper import WhisperModel
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('files',nargs='*');p.add_argument('--model',default='base');p.add_argument('--language',default='en');p.add_argument('--out',default='.cache/transcripts-en');a=p.parse_args()
model=WhisperModel(a.model,device='cpu',compute_type='int8',cpu_threads=4)
files=[Path(x) for x in a.files] if a.files else sorted((ROOT/'.cache/audio').glob('*.wav'))
out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
for f in files:
 target=out/(f.stem+'.json')
 if target.exists():continue
 print('Transcribing',f.name,flush=True)
 segments,info=model.transcribe(str(f),beam_size=1,best_of=1,temperature=0.0,compression_ratio_threshold=None,log_prob_threshold=None,word_timestamps=True,vad_filter=False,language=a.language,condition_on_previous_text=False)
 data={'source':f.name,'language':info.language,'status':'ASR_DRAFT_FOR_MATCHING_NOT_FINAL_CAPTIONS','segments':[]}
 for s in segments:
  data['segments'].append({'start':s.start,'end':s.end,'text':s.text,'words':[{'start':w.start,'end':w.end,'text':w.word,'probability':w.probability} for w in (s.words or [])]})
 target.write_text(json.dumps(data,ensure_ascii=False,indent=2));(out/(f.stem+'.txt')).write_text('\n'.join(f"[{s['start']:.2f}-{s['end']:.2f}] {s['text']}" for s in data['segments']))
 print('Done',f.name,flush=True)
