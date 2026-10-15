#!/usr/bin/env python3
from pathlib import Path
import json,re,math
R=Path(__file__).resolve().parents[1];folder=R/'projects/atfro/atfro-01';cut=json.loads((folder/'cut-list.json').read_text());raw=json.loads((folder/'analysis/IMG_6001-alignment-draft.json').read_text());words=[dict(w) for s in raw for w in s['words']]
# Correct proper nouns, split tokens and leading-pause timestamp overhangs.
fixed=[];i=0
while i<len(words):
 w=words[i];t=w['word'].strip()
 if i==0:w['start']=.94
 if t=='doctor' and i+1<len(words) and words[i+1]['word'].strip()=='-led':w['word']='doctor-led';w['end']=words[i+1]['end'];i+=1
 elif 33.7<w['start']<34.0 and t=='That':w.update({'word':"That's",'start':34.60,'end':34.88});i+=1
 elif 67.1<w['start']<67.2 and t=='That':w['start']=68.14;w['end']=68.32
 elif 67.8<w['start']<67.9 and t=='is':w['start']=68.32;w['end']=68.50
 elif 87.6<w['start']<88 and t=='Art':w.update({'word':'ATFRO.','end':words[i+1]['end']});i+=1
 elif t=='So' and 79<w['start']<80:w.update(start=80.26,end=80.34)
 elif t=='We' and 5.4<w['start']<5.6:w['start']=5.78
 elif t=='still' and 22.3<w['start']<22.5:w['start']=22.76
 elif t.lower()=="what's" and 24.5<w['start']<24.9:w['start']=24.84
 elif t.lower()=='not' and 11.4<w['start']<11.8:w['start']=11.76
 elif t=='ATFRO,':w['word']='ATFRO.'
 fixed.append(w);i+=1
mapped=[]
for w in fixed:
 if w['end']-w['start']<.015:continue
 candidates=[]
 for c in cut['cuts']:
  start=c['inFrame']/30;end=c['outFrame']/30;overlap=max(0,min(w['end'],end)-max(w['start'],start))
  if overlap>0 and overlap>=min(.06,(w['end']-w['start'])*.4):candidates.append((overlap,c))
 if not candidates:continue
 c=max(candidates,key=lambda x:x[0])[1];start=c['inFrame']/30;end=c['outFrame']/30
 sf=round(c['timelineFrom']+(max(w['start'],start)-start)*30);ef=max(sf+1,round(c['timelineFrom']+(min(w['end'],end)-start)*30));ef=min(ef,c['timelineFrom']+c['duration'])
 if ef<=sf:ef=sf+1
 mapped.append({'text':w['word'].strip(),'startFrame':sf,'endFrame':ef,'startMs':round(sf/30*1000,3),'endMs':round(ef/30*1000,3),'sourceStart':w['start'],'sourceEnd':w['end']})
mapped.sort(key=lambda w:w['startFrame'])
# Start sentences cleanly after edit boundaries without changing spoken words.
for w in mapped:
 if w['text']=='you' and w['sourceStart']<3:w['text']='You'
 if w['text']=='what' and 3.8<w['sourceStart']<4.1:w['text']='what'
 if w['text']=="what's" and 24<w['sourceStart']<25:w['text']="What's"
 if w['text']=='Real':w['text']='real'
 if w['text']=='not' and 11<w['sourceStart']<12:w['text']='Not'
# Keep word timing data with the timeline for later manual refinement.
(folder/'captions-words.json').write_text(json.dumps({'status':'source-aligned-to-edited-frames','fps':30,'method':'Local small-model word timestamps, proper noun correction, waveform-leading-pause correction and cut-list frame mapping','words':mapped},indent=2)+'\n')
keywords={'three','months','silence','atfro','client','work','correcting','strategy','school','doctor-led','software','systems','projects','question','stopping','growing','growth','partner','understand','problem','build','useful','grow','people','back','lesson'}
# All visual cues and caption zones are derived from this revision's edited words.
def word_frame(text,after=0):return next(w['startFrame'] for w in mapped if w['text'].lower().strip('.,?!')==text and w['startFrame']>=after)
work_start=next(c['timelineFrom'] for c in cut['cuts'] if c['reason']=='School communications')
work_end=next(c['timelineFrom']+c['duration'] for c in cut['cuts'] if c['reason']=='Software systems')
process_start=word_frame('understand');process_end=word_frame('so')-1
broll=[{'from':work_start,'duration':work_end-work_start,'kind':'atfro-work','beats':[word_frame('school')-work_start,word_frame('doctor-led')-work_start,word_frame('software')-work_start],'fadeFrames':8}, {'from':process_start,'duration':process_end-process_start,'kind':'atfro-process','beats':[0,word_frame('build')-process_start,word_frame('grow')-process_start],'fadeFrames':8}]
def zone(w):return 'broll' if any(c['from']<=w['startFrame']<c['from']+c['duration'] for c in broll) else 'presenter'
pages=[];group=[]
def flush():
 global group
 if not group:return
 start=group[0]['startMs'];end=group[-1]['endMs']+100
 ws=[{k:w[k] for k in ['text','startMs','endMs']} for w in group]
 hits=[i for i,w in enumerate(ws) if re.sub(r'[^a-z-]','',w['text'].lower()) in keywords]
 if hits:ws[hits[-1]]['emphasis']=True
 paper=zone(group[0])=='broll'
 top=1340 if paper else 1240
 size=77 if paper else 75
 if group[0]['startFrame']<48:size=84
 pages.append({'startMs':start,'endMs':end,'words':ws,'top':top,'fontSize':size});group=[]
for w in mapped:
 chars=sum(len(v['text'])+1 for v in group)+len(w['text'])
 if group and (len(group)>=4 or chars>24 or w['startMs']-group[-1]['endMs']>260 or zone(w)!=zone(group[0])):flush()
 group.append(w)
 if re.search(r'[.!?,:]$',w['text']):flush()
flush()
for i,p in enumerate(pages):
 if i+1<len(pages):p['endMs']=min(p['endMs'],pages[i+1]['startMs'])
 p['endMs']=max(p['endMs'],max(w['endMs'] for w in p['words']))
(folder/'captions-pages.json').write_text(json.dumps(pages,indent=2)+'\n')
props={'brand':'atfro','captionPreset':'reference','durationInFrames':cut['totalFrames'],'dialogueAudio':'proxies/atfro-01-dialogue.wav','clips':[{'src':'proxies/atfro-01-aroll.mp4','from':0,'duration':cut['dialogueFrames'],'volume':0}],'captions':pages,'broll':broll,'endCard':True,'endCardFrom':cut['dialogueFrames'],'bottomShade':True,'music':'assets/music/atfro-01-bed-v6.wav','musicVolume':.75,'smoothMusic':True,'endHoldImage':'proxies/atfro-01-holds/end.jpg','endCardFadeFrames':10,'cutBlends':json.loads((folder/'cut-smoothing.json').read_text()),'sfx':[{'src':'assets/sfx/transition-air.wav','from':work_start,'volume':.12},{'src':'assets/sfx/soft-whoosh.wav','from':process_start,'volume':.12}],'dips':[]}
(folder/'reel.json').write_text(json.dumps(props,indent=2)+'\n');print('Words:',len(mapped),'Pages:',len(pages),'Duration:',cut['totalFrames']/30);print(' '.join(w['text'] for w in mapped));print(json.dumps(broll,indent=2))
