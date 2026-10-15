#!/usr/bin/env python3
"""Group reviewed word timestamps into readable caption pages. No guessed word alignment."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('words_json');p.add_argument('output');p.add_argument('--max-words',type=int,default=5);p.add_argument('--max-chars',type=int,default=32);a=p.parse_args()
d=json.loads(Path(a.words_json).read_text())
if not d.get('reviewed'):p.error('Correct the words/timings and set reviewed=true in the input first.')
pages=[];group=[]
for w in d['words']:
 if w['startMs']<0 or w['endMs']<=w['startMs']:p.error('Invalid word timing')
 if group and (len(group)>=a.max_words or sum(len(v['text'])+1 for v in group)+len(w['text'])>a.max_chars or w['startMs']-group[-1]['endMs']>450):
  pages.append({'startMs':group[0]['startMs'],'endMs':group[-1]['endMs'],'words':group});group=[]
 group.append(w)
if group:pages.append({'startMs':group[0]['startMs'],'endMs':group[-1]['endMs'],'words':group})
Path(a.output).write_text(json.dumps(pages,indent=2,ensure_ascii=False)+'\n');print(f'{len(pages)} caption pages written.')
