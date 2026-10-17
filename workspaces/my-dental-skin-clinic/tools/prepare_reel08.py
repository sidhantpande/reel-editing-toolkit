#!/usr/bin/env python3
"""Curated Reel-08 selects and ASR-normalized draft caption timing."""
import copy,csv,json,re
from pathlib import Path
import clinic
R=clinic.ROOT;REEL=R/'03_reels/reel-08';OUT=REEL/'04_timeline/v01'
SPECS=[('0101',2.67,4.97,'hook'),('0101',5.48,15.0133333333,'Mahagauri / purity'),('0101',27.4,34.6,'brushing and fluoride'),('0101',39.65,44.7166666667,'after-meal rinsing'),('0101',45.8,48.2666666667,'hydration'),('0101',49.99,62.09,'all surfaces / interdental flossing'),('0101',63.24,73.0733333333,'mouthwash'),('0102',0,6.1,'dental hygiene closing')]
NORMAL={'दाथ':'दाँत','दाद':'दाँत','दातों':'दाँतों','महागवरी':'महागौरी','सिग्निफाइज':'signifies','बाउट':'about','प्यूरिटी':'purity','रिमेंबर':'remember','ब्रश':'brush','फ्लूराइट':'fluoride','पेस्ट':'paste','यूज़':'use','यूज':'use','सुभा':'सुबह','गागल':'gargle','हाइड्रेशन':'hydration','मेंटेन':'maintain','क्लीन':'clean','सर्फेस':'surface','इंट्रेंटल':'interdental','फ्लोसिंग':'flossing','विज':'बीच','फस्ता':'फँसता','वहापे':'वहाँ','उपर':'ऊपर'}
KEYS=['दाँत','महागौरी','purity','सफाई','brush','fluoride','paste','gargle','hydration','पानी','surface','interdental','flossing','mouthwash','fresh','breath','dental','hygiene','cavities']

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 sources={s['filename'].split('_')[-2]:s for s in clinic.sources()}
 raw=json.loads((OUT/'turbo-asr.json').read_text());segments=[];cursor=0
 for sid,lo,hi,note in SPECS:
  s=sources[sid];frames=round((hi-lo)*30);duration=frames/30
  crop={'x':216,'y':480,'width':1296,'height':2304} if sid=='0101' else {'x':270,'y':900,'width':1188,'height':2112}
  segments.append({'id':note,'source_id':sid,'clip_id':s['id'],'source':s['paths'][0],'source_sha256':s['sha256'],'source_duration':s['duration'],'source_in':lo,'source_out':lo+duration,'timeline_in':cursor/30,'timeline_out':(cursor+frames)/30,'crop_xywh':crop,'note':note});cursor+=frames
 # Prefer the later overlapping ASR chunk, keeping each spoken word once.
 source_words=[]
 for part in raw:
  for q in part['segments']:
   for w in q['words']:
    if part['source_id']=='0101' and part['source_in']==0 and w['start']>=27:continue
    if part['source_id']=='0101' and part['source_in']==27 and w['start']>=51:continue
    source_words.append({**w,'source_id':part['source_id']})
 words=[];notes=[]
 for seg in segments:
  chosen=[w for w in source_words if w['source_id']==seg['source_id'] and w['end']>seg['source_in']+.04 and w['start']<seg['source_out']-.04]
  rinsing=OUT/'rinsing-alignment.json'
  if seg['note']=='after-meal rinsing' and rinsing.is_file():
   chosen=[{**w,'source_id':'0101'} for w in json.loads(rinsing.read_text())['words']]
  for w in chosen:
   text=w['text'].strip().strip('.,!?।，')
   if '�' in text and w['source_id']=='0101' and 60.5<w['start']<61.3:
    text='flossing' # Corroborated independently by the small-model 60–75 s transcript.
   if not text or '�' in text or text=='exactly':
    notes.append({'source':w['source_id'],'in':w['start'],'out':w['end'],'omitted_asr_token':text,'reason':'Corrupted or low-confidence ASR token; no invented replacement. Audio retained for review.'});continue
   if w['source_id']=='0101' and 13.8<=w['start']<14.2:
    if text=='के':text='की'
    elif text=='एफ':continue
   text=NORMAL.get(text,text)
   start=max(seg['source_in'],w['start']);end=min(seg['source_out'],w['end'])
   if end-start>.95:start=max(start,end-.65)
   if end<=start:continue
   words.append({'text':text,'phrase_id':0,'source_id':w['source_id'],'source_start':start,'source_end':end,'start':round(seg['timeline_in']+start-seg['source_in'],5),'end':round(seg['timeline_in']+end-seg['source_in'],5),'alignment_probability':w['probability']})
 # Short, fixed caption groups; boundaries at speech joins and natural pauses.
 phrase=-1;group=[];previous=None
 for w in words:
  new=(not group or len(group)>=4 or (previous and w['start']-previous['end']>.24) or (previous and w['source_id']!=previous['source_id']))
  if new:phrase+=1;group=[]
  w['phrase_id']=phrase;group.append(w);previous=w
 def locate(sid,t):
  for s in segments:
   if s['source_id']==sid and s['source_in']<=t<=s['source_out']:return s['timeline_in']+t-s['source_in']
  raise ValueError((sid,t))
 approved=R/'04_generated_broll/approved'
 slots=[{'id':'B01-hook','path':str(approved/'reel-08_B01_brushing_received.mp4'),'layout':'portrait','media_in':0,'timeline_in':0,'timeline_out':segments[0]['timeline_out'],'status':'awaiting user generation','note':'Reuse first establishing seconds to cover the hook screen glance'},
 {'id':'B01-brushing','path':str(approved/'reel-08_B01_brushing_received.mp4'),'layout':'portrait','media_in':2.5,'timeline_in':round(locate('0101',27.45)*30)/30,'timeline_out':round(locate('0101',34.42)*30)/30,'status':'awaiting user generation'},
 {'id':'B02-flossing','path':str(approved/'reel-08_B02_flossing_received.mp4'),'layout':'portrait','media_in':.7,'timeline_in':round(locate('0101',56.66)*30)/30,'timeline_out':round(locate('0101',62.0)*30)/30,'status':'awaiting user generation'}]
 plan={'reel_id':'reel-08','version':'v01','fps':30,'duration_seconds':cursor/30,'status':'A-roll arrangement / normalized draft captions; pending 2 new user-generated B-rolls and final dialogue review','approved_style':'my-dental-v05-approved','segments':segments,'words':words,'broll_slots':slots,'caption_keywords':KEYS,'caption_emphasis':['दाँत','महागौरी','brush','fluoride','flossing','mouthwash','hygiene','cavities'],'cue_exclusions':[{'source':'0101','in':0,'out':2.67,'reason':'Omit campaign recap lead-in; start directly at the complete हर एक दाँत hook, not a production-cue assumption'},{'source':'0101','in':73.08,'out':97.514667,'reason':'Post-speech screen-reading / setup tail'},{'source':'0102','in':6.136,'out':8.192,'reason':'Silent ending hold'},{'source':'0103','in':0,'out':29.568,'reason':'Repeated campaign-outro pickup and setup; excluded alternate. Its spoken start is part of a sentence, not automatically a production cue.'}],'caption_review_notes':notes,'transcription_method':'Independent small and pinned turbo ASR passes; obvious dental/English spelling normalization, not human listening verification.'}
 (OUT/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
 with (OUT/'selects.csv').open('w') as f:
  writer=csv.writer(f);writer.writerow(['source','in','out','timeline_in','timeline_out','reason'])
  for s in segments:writer.writerow([s['source_id'],s['source_in'],s['source_out'],s['timeline_in'],s['timeline_out'],s['note']])
 for folder,sids in [('01_selected_sources',['0101','0102']),('02_alternate_sources',['0103'])]:
  target=REEL/folder;target.mkdir(parents=True,exist_ok=True)
  for sid in sids:
   link=target/sources[sid]['filename']
   if not link.exists():link.symlink_to(sources[sid]['paths'][0])
 print('Prepared',cursor/30,'seconds;',len(segments),'runs;',len(words),'draft words',flush=True)
 print('B-roll slots',[(q['id'],q['timeline_in'],q['timeline_out']) for q in slots],flush=True)

if __name__=='__main__':main()
