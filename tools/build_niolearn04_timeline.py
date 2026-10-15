#!/usr/bin/env python3
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1];P=R/'projects/niolearn/niolearn-04';cut=json.loads((P/'cut-list.json').read_text());raw=json.loads((P/'source-words.json').read_text())['words'];mapped=[]
for w in raw:
 options=[]
 for c in cut['cuts']:
  a=c['inFrame']/30;b=c['outFrame']/30;over=max(0,min(b,w['end'])-max(a,w['start']))
  if over>=min(.045,(w['end']-w['start'])*.45):options.append((over,c))
 if not options:continue
 c=max(options,key=lambda x:x[0])[1];a=c['inFrame']/30;b=c['outFrame']/30;start=round(c['timelineFrom']+(max(a,w['start'])-a)*30);end=round(c['timelineFrom']+(min(b,w['end'])-a)*30)
 if end<=start:end=start+1
 mapped.append({'text':w['text'],'startFrame':start,'endFrame':end,'startMs':round(start/30*1000,3),'endMs':round(end/30*1000,3),'sourceStart':w['start'],'sourceEnd':w['end']})
mapped.sort(key=lambda w:w['startFrame']);(P/'captions-words.json').write_text(json.dumps({'fps':30,'status':'reviewed-source-aligned-Roman-Hinglish','words':mapped},indent=2)+'\n')
def sf(source):
 c=next(c for c in cut['cuts'] if c['inFrame']/30<=source<c['outFrame']/30)
 return round(c['timelineFrom']+(source-c['inFrame']/30)*30)
def cue(a,b,kind):
 # b is an in-source end boundary, not the next camera take.
 c=next(c for c in cut['cuts'] if c['inFrame']/30<b<=c['outFrame']/30+.02)
 end=round(c['timelineFrom']+(min(b,c['outFrame']/30)-c['inFrame']/30)*30);start=sf(a)
 return {'kind':kind,'from':start,'duration':end-start,'fadeFrames':8}
broll=[cue(6.26,9.45,'nio-parents-authority'),cue(12.79,18.03,'nio-parents-credential'),cue(18.63,24.86,'nio-parents-fees'),cue(31.75,35.87,'nio-parents-outcomes'),cue(40.55,46.88,'nio-parents-conversation')]
credential=broll[1];fee=broll[2];broll=[broll[0],{'kind':'nio-parents-credential-fees','from':credential['from'],'duration':fee['from']+fee['duration']-credential['from'],'beats':[fee['from']-credential['from']],'fadeFrames':8},*broll[3:]]
def zone(w):return 'paper' if any(c['from']<=w['startFrame']<c['from']+c['duration'] for c in broll) else 'camera'
keywords={'fee','5','sawaal','degree','recognition','credential','certification','written','total','deposits','breakdown','batch','strength','roles','outcomes','alumni','student','connect','save','parent','checklist','niolearn.com'};pages=[];group=[]
def flush():
 global group
 if not group:return
 words=[{k:w[k] for k in ['text','startMs','endMs']} for w in group];hits=[i for i,w in enumerate(words) if re.sub('[^a-z0-9.]','',w['text'].lower().rstrip('.,?!')) in keywords]
 if hits:words[hits[-1]]['emphasis']=True
 paper=zone(group[0])=='paper';pages.append({'startMs':group[0]['startMs'],'endMs':group[-1]['endMs']+100,'words':words,'top':1340 if paper else 1240,'fontSize':77 if paper else 84 if group[0]['startFrame']<80 else 75});group=[]
for w in mapped:
 if w['text']=='niolearn.com' and group:flush()
 size=sum(len(x['text'])+1 for x in group)+len(w['text'])
 if group and (len(group)>=4 or size>(30 if 54.6<=w['sourceStart']<55.73 else 24) or zone(w)!=zone(group[0]) or w['startMs']-group[-1]['endMs']>260):flush()
 group.append(w)
 if re.search('[.,?!]$',w['text']) and w['text']!='niolearn.com':flush()
flush()
for i,p in enumerate(pages):
 if i+1<len(pages):p['endMs']=min(p['endMs'],pages[i+1]['startMs'])
 p['endMs']=max(p['endMs'],max(w['endMs'] for w in p['words']))
(P/'captions-pages.json').write_text(json.dumps(pages,indent=2)+'\n')
smoothing=P/'cut-smoothing.json';blends=json.loads(smoothing.read_text()) if smoothing.exists() else []
props={'brand':'niolearn','captionPreset':'reference','durationInFrames':cut['totalFrames'],'dialogueAudio':'proxies/niolearn-04-dialogue.wav','clips':[{'src':'proxies/niolearn-04-aroll.mp4','from':0,'duration':cut['dialogueFrames'],'volume':0}],'captions':pages,'broll':broll,'endCard':True,'endCardFrom':cut['dialogueFrames'],'bottomShade':True,'cutBlends':blends,'endHoldImage':'proxies/niolearn-04-holds/end.jpg','endCardFadeFrames':10,'smoothMusic':True,'music':'assets/music/niolearn-04-bed.wav','musicVolume':.75,'sfx':[{'src':'assets/sfx/transition-air.wav','from':c['from'],'volume':.08} for c in broll]}
(P/'reel.json').write_text(json.dumps(props,indent=2)+'\n');print('Words',len(mapped),'Pages',len(pages),'Duration',cut['totalFrames']/30);print(' '.join(w['text'] for w in mapped));print(json.dumps(broll,indent=2))
