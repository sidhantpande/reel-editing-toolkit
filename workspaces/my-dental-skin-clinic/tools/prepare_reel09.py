#!/usr/bin/env python3
"""Explicit reviewed-source draft for Reel-09; never an automatic silence edit.

Dialogue spelling is manually normalized from two ASR passes plus isolated
normalized snippets. Human listening/clinical wording approval is still open.
"""
import copy,json,shutil
from pathlib import Path
import clinic
R=clinic.ROOT;OUT=R/'03_reels/reel-09';FPS=30

def write(path,data):clinic.save(path,data)

def main():
 sources={s['filename'].split('_')[-2]:s for s in clinic.sources() if '/Reel-09/' in s['paths'][0]}
 audit=json.loads((OUT/'04_timeline/source-audit.json').read_text())
 audited={s['name']:[w for seg in s['segments'] for w in seg['words']] for s in audit}
 plan={'reel_id':'reel-09','version':'v01','style':'styles/clinic-reference-bold.json','status':'DRAFT_REQUIRES_LISTENING_AND_BROLL','segments':[],'words':[],'broll_slots':[],'graphic_slots':[], 'cue_exclusions':[], 'caption_keywords':['दांत','अलग','problem','solution','छोटी','बड़ी','छोटा','बड़ा','32','teeth','ignore','शक्ति','संतुष्टि'], 'caption_emphasis':['दांत','problem','solution','32','teeth'], 'review':{'visual_source_sampling':'complete duration contacts + selected motion frames','dialogue':'independent normalized ASR snippets; no human listening attestation','corrections':'Hindi spelling and English code-switches normalized; review against recording'}}
 cursor=0;entries=[]
 def add(source_id,a,b,words,phrases,role):
  nonlocal cursor
  s=sources[source_id];a=round(a*30)/30;b=round(b*30)/30;duration=b-a
  segment={'source_id':s['id'],'source':s['paths'][0],'source_sha256':s['sha256'],'source_duration':s['duration'],'source_in':a,'source_out':b,'timeline_in':cursor,'timeline_out':cursor+duration,'crop_xywh':{'x':153,'y':430,'width':1422,'height':2528},'role':role}
  plan['segments'].append(segment);entries.append({'role':role,'source':s['filename'],'source_in':a,'source_out':b,'timeline_in':cursor,'timeline_out':cursor+duration})
  if sum(len(p) for p in phrases)!=len(words):raise ValueError(role+' phrase/word mismatch')
  corrected=[text for phrase in phrases for text in phrase];phrase_index=0;i=0
  for phrase in phrases:
   for text in phrase:
    w=words[i];start=max(a,float(w['start']));end=min(b,float(w['end']))
    if start>=end:raise ValueError(f'{role}: word outside cut {text} {w}')
    plan['words'].append({'text':text,'start':cursor+start-a,'end':cursor+end-a,'source_id':s['id'],'source_start':start,'source_end':end,'phrase_id':f'p{len(entries):02}-{phrase_index:02}'})
    i+=1
   phrase_index+=1
  cursor+=duration
 def original(id):return [w for seg in json.loads((R/'02_analysis'/sources[id]['id']/'transcript.json').read_text())['segments'] for w in seg['words']]
 opening=original('0108')
 add('0108',.10,7.233333,opening,[['सिद्धिदात्री'],['पूर्ण','शक्ति'],['पूर्ण','संतुष्टि'],['आज','कहानी'],['पूरी','होती','है']],'Complete opening / best take')
 add('0116',4.233333,10.466667,audited['question'],[['पिछले','नौ','दिन','में'],['हमने','एक'],['simple','सवाल','पूछा'],['एक','ही','दांत','से'],['क्या','फ़र्क','पड़ता','है?']],'Question / speaking off-camera; cover with B01')
 role_start=cursor
 add('0116',25.0,29.166667,audited['role'],[['फ़र्क','पड़ता','है'],['हर','दांत','का'],['अलग','रोल'],['होता','है']],'Usable direct-camera explanation')
 small=copy.deepcopy(audited['small']);small[0]['start']=29.52
 add('0116',29.3,33.333333,small,[['और','जब','problem'],['छोटी','है'],['तो','उसका','solution'],['भी','छोटा'],['होता','है']],'Small problem / solution')
 add('0116',33.333333,36.366667,audited['large'],[['problem','बड़ी','है'],['तो','उसका','solution'],['भी','बड़ा'],['होता','है']],'Large problem / solution; retain comparison')
 escalation_start=cursor
 escalation=[w for w in original('0117') if w['start']<8.71]
 add('0117',.6,8.9,escalation,[['लेकिन','जब'],['छोटी','problem','को'],['बड़ी','बनाओगे'],['या','ignore','करोगे'],['तो','वो','खुद','ही'],['बड़ी','बन','जाएगी'],['इसलिए']],'Escalation; use B02, omit superseded 32 pickup')
 last=original('0118')
 # Remove an actual silent reading pause between the opener and number.
 add('0118',.533333,2.266667,last[:2],[['याद','रखना']],'Complete remembered phrase; conservative tail')
 add('0118',3.066667,5.333333,last[2:8],[['32'],['सिर्फ','एक'],['नंबर','नहीं','है']],'Complete number / statement')
 closing=audited['closing']
 add('0118',5.6,6.733333,closing[:1],[['So']],'Keep original spoken connector')
 add('0118',7.433333,11.2,closing[1:],[['take','care'],['of','your','teeth'],['bye','bye'],['thank','you'],['so','much']],'Complete original goodbye')
 plan['duration_seconds']=cursor
 plan['graphic_slots']=[{'id':'G01','path':str(R/'assets/cutouts/molar-ivory-v01.png'),'timeline_in':role_start+.4,'timeline_out':role_start+3.9,'x':500,'y':80,'width':520,'visual_reviewed':True}]
 plan['broll_slots']=[{'id':'B01','path':str(OUT/'07_deliveries/reel-09_B01_tooth-role.mp4'),'timeline_in':entries[1]['timeline_in'],'timeline_out':entries[1]['timeline_out'],'media_in':.5,'layout':'portrait','status':'awaiting-user-video'}, {'id':'B02','path':str(OUT/'07_deliveries/reel-09_B02_problem-escalation.mp4'),'timeline_in':escalation_start,'timeline_out':entries[5]['timeline_out'],'media_in':.5,'layout':'portrait','status':'awaiting-user-video'}]
 # Excluded setup / off-camera reading / alternate takes. These do not attest
 # that every excluded sound was a command; the exact reason is explicit.
 for id,a,b,reason in [('0105',0,.150167,'Accidental nine-frame recording'),('0106',0,8.775433,'Incomplete/repeated opening; better complete take 0108'),('0116',0,4.2,'Setup and reading before usable question'),('0116',10.5,24.9,'Off-camera reading/rehearsal and long pause'),('0116',36.5,38.848,'Tail/setup after complete thought'),('0117',9.0,14.784,'Superseded number line and tail')]:
  if id in ['0105','0106']:continue
  plan['cue_exclusions'].append({'source':sources[id]['id'],'in':a,'out':b,'reason':reason})
 write(OUT/'04_timeline/v01/plan.json',plan);write(OUT/'04_timeline/v01/selects.json',entries)
 # Short end-to-end proof with the same source, captions and true occlusion.
 proof=copy.deepcopy(plan);proof.update(reel_id='reel-09-style-proof',version='v02',duration_seconds=entries[4]['timeline_out']-role_start,status='STYLE_PROOF / no human listening attestation',broll_slots=[],cue_exclusions=[])
 proof['segments']=copy.deepcopy(plan['segments'][2:5]);proof['words']=[copy.deepcopy(w) for w in plan['words'] if w['phrase_id'].startswith(('p03','p04','p05'))]
 for s in proof['segments']:s['timeline_in']-=role_start;s['timeline_out']-=role_start
 for w in proof['words']:w['start']-=role_start;w['end']-=role_start
 for s in proof['graphic_slots']:s['timeline_in']-=role_start;s['timeline_out']-=role_start
 write(OUT/'04_timeline/proof-v02/plan.json',proof)
 editorial=copy.deepcopy(proof);editorial['style']='styles/clinic-reference-editorial.json';editorial['version']='editorial-v02'
 write(OUT/'04_timeline/proof-editorial-v02/plan.json',editorial)
 print(json.dumps({'duration_seconds':cursor,'segments':len(plan['segments']),'words':len(plan['words']),'broll':plan['broll_slots']},indent=2))

if __name__=='__main__':main()
