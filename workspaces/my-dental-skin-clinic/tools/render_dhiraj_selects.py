#!/usr/bin/env python3
"""Render explicit source-aware clean selects; no logo or draft captions burned in."""
import argparse, hashlib, json, subprocess
from pathlib import Path
import numpy as np
from scipy.io import wavfile
import clinic
from clinic_plan import validate_plan

def transition_frames(segments,index):
    if index+1==len(segments):return 0
    return 6 if segments[index+1].get('join','fade')=='fade' else 0

def crop_filter(item,seek):
    c=item['crop_xywh'];x=str(c['x']);y=str(c['y'])
    keys=item.get('crop_keyframes',[])
    if keys:
        # Source-clock keyframes remain correct on cores and source-handle dissolves.
        terms=[str(keys[0]['x'])]
        for a,b in zip(keys,keys[1:]):
            delta=b['x']-a['x']
            if abs(delta)>.05:terms.append(f'({delta:.4f})*clip((t+{seek:.6f}-{a["t"]:.6f})/{b["t"]-a["t"]:.6f},0,1)')
        # A left-associated sum of hundreds of keys exceeds libavutil's
        # expression recursion limit. A balanced tree has logarithmic depth.
        while len(terms)>1:
            terms=['('+terms[i]+'+'+terms[i+1]+')' if i+1<len(terms) else terms[i] for i in range(0,len(terms),2)]
        x=terms[0]
        x="'floor(("+x+")/2)*2'"
    return f'crop={c["width"]}:{c["height"]}:{x}:{y},scale=1080:1920,setsar=1,fps=30,format=yuv420p'

def render(path):
    plan=json.loads(path.read_text());validate_plan(plan,allow_pending=True,root=clinic.ROOT)
    signature=hashlib.sha256(path.read_bytes()+Path(__file__).read_bytes()).hexdigest()[:12]
    cache=clinic.ROOT/'.cache/dhiraj'/f'{plan["reel_id"]}-{signature}';cache.mkdir(parents=True,exist_ok=True)
    dest=Path(plan['clean_export']);dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() and dest.with_suffix('.render.json').exists():
        if json.loads(dest.with_suffix('.render.json').read_text()).get('signature')==signature:
            print('CACHED',dest,flush=True);return
        raise FileExistsError('Use a new export version: '+str(dest))
    parts=[];audio=[];decoded={};segments=plan['segments']
    for i,s in enumerate(segments):
        n=round((s['timeline_out']-s['timeline_in'])*30)
        head=transition_frames(segments,i-1)//2 if i else 0
        tail=transition_frames(segments,i)//2
        if s['source'] not in decoded:
            raw=subprocess.check_output([clinic.FF,'-v','error','-nostdin','-i',s['source'],'-vn','-ar','48000','-ac','2','-f','f32le','-'])
            decoded[s['source']]=np.frombuffer(raw,dtype=np.float32).reshape(-1,2)
        start=round(s['source_in']*48000);a=decoded[s['source']][start:start+n*1600].copy()
        if len(a)!=n*1600:raise ValueError('Insufficient audio samples')
        fade=min(288,len(a)//2);a[:fade]*=np.linspace(0,1,fade)[:,None];a[-fade:]*=np.linspace(1,0,fade)[:,None];audio.append(a)
        # Same encoder settings for cores and transition inserts permit stream-copy assembly.
        encoder=['-c:v','h264_videotoolbox','-b:v','14M','-g','60','-profile:v','high','-pix_fmt','yuv420p']
        core=cache/f'core-{i:03}.mp4';parts.append(core)
        if not core.exists():clinic.ff('-ss',s['source_in']+head/30,'-i',s['source'],'-an','-vf',crop_filter(s,s['source_in']+head/30),'-frames:v',n-head-tail,*encoder,core)
        if tail:
            nxt=segments[i+1];tr=cache/f'join-{i:03}.mp4';parts.append(tr)
            if not tr.exists():
                graph=f'[0:v]{crop_filter(s,s["source_out"]-.1)},trim=end_frame=6,setpts=PTS-STARTPTS[a];[1:v]{crop_filter(nxt,nxt["source_in"]-.1)},trim=end_frame=6,setpts=PTS-STARTPTS[b];[a][b]blend=all_expr=A*(1-(N-1)/5)+B*(N-1)/5[v]'
                clinic.ff('-ss',s['source_out']-.1,'-i',s['source'],'-ss',nxt['source_in']-.1,'-i',nxt['source'],'-filter_complex',graph,'-map','[v]','-an','-frames:v','6',*encoder,tr)
        print(plan['reel_id'],'shot',i+1,'/',len(segments),flush=True)
    pcm=cache/'dialogue.wav';wavfile.write(pcm,48000,np.concatenate(audio))
    listing=cache/'parts.txt';listing.write_text('\n'.join("file '"+str(p).replace("'","'\\''")+"'" for p in parts)+'\n')
    af='highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11'
    if plan.get('audio_peak_limit'):af='highpass=f=70,loudnorm=I=-16:TP=-2:LRA=11,aresample=192000,alimiter=limit=0.78:level=false:latency=true,aresample=48000'
    clinic.ff('-f','concat','-safe','0','-i',listing,'-i',pcm,'-map','0:v:0','-map','1:a:0','-c:v','copy','-af',af,'-c:a','aac','-b:a','192k','-ar','48000','-t',plan['duration_seconds'],'-movflags','+faststart',dest)
    clinic.save(dest.with_suffix('.render.json'),{'signature':signature,'plan':str(path),'status':'CLEAN_CUT_FOR_REVIEW / B-roll planned separately; no human listening attestation','frames_expected':round(plan['duration_seconds']*30),'dialogue_pcm':str(pcm),'encoder':'h264_videotoolbox 14Mbps','sha256':hashlib.file_digest(dest.open('rb'),'sha256').hexdigest()})
    print('EXPORTED',dest,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plans',type=Path,nargs='+');a=p.parse_args()
    for path in a.plans:render(path.resolve())
