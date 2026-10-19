#!/usr/bin/env python3
"""Compile explicit editorial choices plus conservative measured silence splices."""
import argparse,json,math,shutil
from pathlib import Path
import numpy as np
from scipy.io import wavfile
import clinic
from clinic_plan import validate_plan
ROOT=clinic.ROOT;BATCH=ROOT/'03_reels/dhiraj';ANALYSIS=ROOT/'02_analysis/dhiraj'
DELIVERY=Path('/Users/sidhant/Desktop/Video-Editing/Dhiraj-Edits')

def frame(t):return round(t*30)/30

def quiet_gaps(path,a,b):
    """Only remove >0.9s continuous sub -44dBFS normalized energy; keep breaths."""
    sr,data=wavfile.read(path)
    data=data.astype(np.float64)/(32768 if np.issubdtype(data.dtype,np.integer) else 1)
    if data.ndim==2:data=data.mean(axis=1)
    step=round(sr*.02);n=len(data)//step
    rms=np.sqrt(np.mean(data[:n*step].reshape(n,step)**2,axis=1)+1e-16)
    low=rms<10**(-44/20);changes=np.diff(np.r_[False,low,False].astype(int));spans=[]
    for x,y in zip(np.where(changes==1)[0],np.where(changes==-1)[0]):
        left=max(a,x*.02);right=min(b,y*.02)
        if right-left>=.9 and left>a+.3 and right<b-.3:spans.append((frame(left+.18),frame(right-.18)))
    return spans

def build(spec):
    rows={r['filename'].split('.')[0]:r for r in clinic.sources() if any('/Dhiraj/' in q for q in r['paths'])}
    crops=json.loads((ANALYSIS/'crop-candidates.json').read_text())
    name=spec['id'];folder=BATCH/name;timeline=folder/'04_timeline/v01';timeline.mkdir(parents=True,exist_ok=True)
    deliver=DELIVERY/name;deliver.mkdir(parents=True,exist_ok=True)
    plan={'reel_id':'dhiraj-'+name,'version':'v01','title':spec['title'],'style':'styles/clinic-approved.json','status':'CLEAN_SELECTS_FOR_REVIEW / logo deferred by user; B-roll planning separate','segments':[],'words':[],'broll_slots':[],'graphic_slots':[],'cue_exclusions':[], 'clean_export':str(deliver/(name+'_clean-9x16_v01.mp4')),'review':{'source_visual':'complete 2-second chronological contact sheets and framing proofs','dialogue':'two local ASR decoders; no human listening attestation','captions':'not burned into clean-cut delivery; draft ASR retained separately','brand':'user requested clean edit and logo later'}}
    cursor=0;silences=[];notes=[]
    for take in spec['takes']:
        key='MVI_'+str(take['clip']);r=rows[key];a=frame(take['in']);b=frame(take['out'])
        gaps=quiet_gaps(ANALYSIS/key/'normalized.wav',a,b) if take.get('shorten_silence',True) else []
        intervals=[];current=a
        for start,end in gaps:
            if start-current<.35 or b-end<.35:continue
            intervals.append((current,start));silences.append({'source':r['id'],'in':start,'out':end,'reason':'continuous normalized energy below -44 dBFS for >=0.9s; 180ms handles retained'});current=end
        intervals.append((current,b))
        for index,(left,right) in enumerate(intervals):
            duration=frame(right-left)
            if duration<7/30:raise ValueError('Editorial range too short')
            crop=crops[take.get('crop',key)]
            plan['segments'].append({'source_id':r['id'],'source':r['paths'][0],'source_sha256':r['sha256'],'source_duration':r['duration'],'source_in':left,'source_out':left+duration,'timeline_in':cursor,'timeline_out':cursor+duration,'crop_xywh':crop,'role':take['role'],'speaker':take.get('speaker','doctor'),'join':take.get('join','fade') if index==0 else 'fade'})
            cursor+=duration
        notes.append({'source':r['filename'],'in':a,'out':b,'role':take['role'],'speaker':take.get('speaker','doctor')})
        src=deliver/'source-links';src.mkdir(exist_ok=True);link=src/r['filename']
        if not link.exists():link.symlink_to(r['paths'][0])
    plan['duration_seconds']=frame(cursor);plan['silence_splices']=silences;plan['editorial_notes']=spec.get('notes',[])
    validate_plan(plan,allow_pending=True,root=ROOT);clinic.save(timeline/'plan.json',plan);clinic.save(timeline/'selects.json',notes)
    clinic.save(deliver/'timeline.json',plan)
    text=f'# {name} — {spec["title"]}\n\nClean portrait cut for review. Logo deferred by user. Original camera files unchanged. B-roll/graphics are planned separately; this is not a finished B-roll edit.\n\n'
    text+='| Source | In | Out | Choice |\n|---|---:|---:|---|\n'+''.join(f'| {s["source"]} | {s["in"]:.3f} | {s["out"]:.3f} | {s["role"]} |\n' for s in notes)
    text+=f'\nOutput {plan["duration_seconds"]:.3f}s / 1080×1920 / 30fps. {len(silences)} conservative silence splices. Short six-frame dissolves join dialogue; speaker changes use clean cuts. Original voice/pitch/speed retained.\n\n'
    text+='\n'.join('- '+n for n in spec.get('notes',[]))+'\n\nReview limitations: two local ASR decoding passes support dialogue selection; no human listening approval is claimed. Draft transcripts are not verified final captions.\n'
    (folder/'brief.md').write_text(text);(deliver/'edit-notes.md').write_text(text)
    return plan

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--only',nargs='*');a=p.parse_args()
    specs=json.loads((BATCH/'editorial-specs.json').read_text())
    for spec in specs:
        if not a.only or spec['id'] in a.only:
            plan=build(spec);print(plan['reel_id'],plan['duration_seconds'],len(plan['segments']),flush=True)
