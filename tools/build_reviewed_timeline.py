#!/usr/bin/env python3
"""Build a reel only from reviewed source words, exact cuts and a per-reel editorial plan."""
from pathlib import Path
import argparse,json,re
R=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('project');a=ap.parse_args();P=R/a.project
cut=json.loads((P/'cut-list.json').read_text());editor=json.loads((P/'editorial.json').read_text());raw=json.loads((P/'source-words.json').read_text())['words'];name=cut['id'];brand=name.split('-')[0];mapped=[]
for w in raw:
 assert 0<=w["start"]<w["end"],w
 choices=[]
 for c in cut['cuts']:
  if w.get('source') and w['source'] not in [c['source'],Path(c['source']).name,Path(c['source']).stem]:continue
  start=c['inFrame']/30;end=c['outFrame']/30;over=max(0,min(end,w['end'])-max(start,w['start']))
  if over>=min(.045,(w['end']-w['start'])*.45):choices.append((over,c))
 if not choices:continue
 c=max(choices,key=lambda x:x[0])[1];start=c['inFrame']/30;end=c['outFrame']/30;f=round(c['timelineFrom']+(max(start,w['start'])-start)*30);g=max(f+1,round(c['timelineFrom']+(min(end,w['end'])-start)*30))
 mapped.append(dict(text=w['text'],startFrame=f,endFrame=g,startMs=round(f/30*1000,3),endMs=round(g/30*1000,3),sourceStart=w['start'],sourceEnd=w['end'],source=c['source']))
mapped.sort(key=lambda w:w['startFrame'])
(P/'captions-words.json').write_text(json.dumps(dict(fps=30,status='reviewed-source-aligned',words=mapped),indent=2)+'\n')
broll=[]
for b in editor['broll']:
 if 'from' in b:broll.append(b);continue
 spans=[]
 for c in cut['cuts']:
  if b.get('source') and b['source'] not in [c['source'],Path(c['source']).name,Path(c['source']).stem]:continue
  start=max(c['inFrame']/30,b['start']);end=min(c['outFrame']/30,b['end'])
  if end>start:spans.append((round(c['timelineFrom']+(start-c['inFrame']/30)*30),round(c['timelineFrom']+(end-c['inFrame']/30)*30)))
 assert spans,b
 raw_start=min(x[0] for x in spans);raw_end=max(x[1] for x in spans)
 # When a graphic nearly meets a source cut, complete its dissolve over that cut.
 previous=[c['timelineFrom'] for c in cut['cuts'] if 0<=raw_start-c['timelineFrom']<=12]
 following=[c['timelineFrom'] for c in cut['cuts'] if 0<=c['timelineFrom']-raw_end<=12]
 if previous:raw_start=max(previous)
 if following:raw_end=min(following)
 f=max(0,raw_start-b.get('leadFrames',8));g=min(cut['dialogueFrames'],raw_end+b.get('tailFrames',8))
 cue=dict(kind=b['kind'],from_=f,duration=g-f,fadeFrames=8);cue['from']=cue.pop('from_')
 if 'beats' in b:cue['beats']=b['beats']
 if 'sourceBeats' in b:
  points=[]
  for t in b['sourceBeats']:
   possible=[c for c in cut['cuts'] if (not b.get('source') or b['source'] in [c['source'],Path(c['source']).stem,Path(c['source']).name]) and c['inFrame']/30-.02<=t<c['outFrame']/30+.02]
   assert possible,('Unmatched scene beat',t,b)
   c=possible[0];points.append(round(c['timelineFrom']+(t-c['inFrame']/30)*30)-cue['from'])
  cue['beats']=points
 if 'labels' in b:cue['labels']=b['labels']
 broll.append(cue)
broll.sort(key=lambda c:c['from'])
for left,right in zip(broll,broll[1:]):assert left['from']+left['duration']<=right['from'],(left,right)
keywords=set(editor.get('accentWords',[]));normalize=lambda t:re.sub('[^a-z0-9.]','',t.lower().rstrip('.,?!:;'))
keywords.update(['niolearn','niolearn.com'] if brand=='niolearn' else ['atfro'])
pages=[];cursor=0
for phrase in editor['phrases']:
 group=mapped[cursor:cursor+len(phrase.split())];assert ' '.join(w['text'] for w in group)==phrase,(phrase,group);cursor+=len(group)
 words=[{k:w[k] for k in ['text','startMs','endMs']} for w in group];hits=[i for i,w in enumerate(words) if normalize(w['text']) in keywords]
 # Brand is always colored; keep one main emphasis per phrase.
 for i in hits:
  if i==hits[-1] or normalize(words[i]['text']) in {'niolearn','niolearns','niolearn.com','atfro','atfros'}:words[i]['accent']=True
 if hits:words[hits[-1]]['emphasis']=True
 paper=any(b['from']<=group[0]['startFrame']<b['from']+b['duration'] for b in broll)
 pages.append(dict(startMs=group[0]['startMs'],endMs=group[-1]['endMs']+100,words=words,top=1340 if paper else 1240,fontSize=77 if paper else 84 if group[0]['startFrame']<80 else 75))
assert cursor==len(mapped),(cursor,len(mapped))
for i,p in enumerate(pages):
 if i+1<len(pages):p['endMs']=min(p['endMs'],pages[i+1]['startMs'])
 p['endMs']=max(p['endMs'],max(w['endMs'] for w in p['words']))
(P/'captions-pages.json').write_text(json.dumps(pages,indent=2)+'\n')
blends=json.loads((P/'cut-smoothing.json').read_text()) if (P/'cut-smoothing.json').exists() else []
props=dict(brand=brand,captionPreset='reference',durationInFrames=cut['totalFrames'],dialogueAudio=f'proxies/{name}-dialogue.wav',clips=[dict(src=f'proxies/{name}-aroll.mp4',from_=0,duration=cut['dialogueFrames'],volume=0)],captions=pages,broll=broll,endCard=True,endCardFrom=cut['dialogueFrames'],bottomShade=True,cutBlends=blends,endHoldImage=f'proxies/{name}-holds/end.jpg',endCardFadeFrames=10,smoothMusic=True,music=f'assets/music/{name}-bed.wav',musicVolume=.75,sfx=[dict(src='assets/sfx/transition-air.wav',from_=b['from'],volume=.08) for b in broll])
for item in [*props['clips'],*props['sfx']]:item['from']=item.pop('from_')
(P/'reel.json').write_text(json.dumps(props,indent=2)+'\n');print(name,'words',len(mapped),'groups',len(pages),'seconds',cut['totalFrames']/30);print(' '.join(w['text'] for w in mapped));print(json.dumps(broll,indent=2))
