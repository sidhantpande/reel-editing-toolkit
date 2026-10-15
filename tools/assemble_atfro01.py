#!/usr/bin/env python3
"""Rebuild the selected portrait A-roll and matching dialogue from immutable camera originals."""
from pathlib import Path
import subprocess,json,math,hashlib
R=Path(__file__).resolve().parents[1];plan=json.loads((R/'projects/atfro/atfro-01/cut-list.json').read_text());cache=R/'.cache/edits/atfro-01';cache.mkdir(parents=True,exist_ok=True);(R/'.cache/proxies').mkdir(exist_ok=True)
grade=json.loads((R/'projects/atfro/atfro-01/colour-grade.json').read_text())['filter'];grade_key=hashlib.sha256(grade.encode()).hexdigest()[:8]
segments=[]
for i,c in enumerate(plan['cuts']):
 out=cache/f'segment-{i:02d}-{c["inFrame"]}-{c["outFrame"]}-{c["zoom"]}-{grade_key}.mkv';segments.append(out)
 if out.exists():continue
 dur=c['duration']/30;z=c['zoom'];w=round(1080*z/2)*2;h=round(1920*z/2)*2
 vf=f'scale={w}:{h},crop=1080:1920:(iw-1080)/2:(ih-1920)*0.35,setsar=1,fps=30,{grade},format=yuv420p'
 af=f'aresample=48000,afade=t=in:d=0.004,afade=t=out:st={dur-.004}:d=0.004'
 subprocess.run(['ffmpeg','-v','error','-ss',str(c['inFrame']/30),'-i',str(R/c['source']),'-t',str(dur),'-vf',vf,'-af',af,'-ac','1','-c:v','libx264','-preset','fast','-crf','17','-c:a','pcm_s16le','-f','matroska',str(out)],check=True)
 print(f'Segment {i+1}/{len(plan["cuts"])}',flush=True)
concat=cache/'concat.txt';concat.write_text('\n'.join("file '"+str(f).replace("'","'\\''")+"'" for f in segments)+'\n')
video=R/'.cache/proxies/atfro-01-aroll.mp4'
subprocess.run(['ffmpeg','-v','error','-f','concat','-safe','0','-i',str(concat),'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-y',str(video)],check=True)
voice=R/'.cache/proxies/atfro-01-dialogue.wav'
subprocess.run(['ffmpeg','-v','error','-f','concat','-safe','0','-i',str(concat),'-vn','-af','highpass=f=85,lowpass=f=14000,afftdn=nr=6:nf=-36:tn=1,acompressor=threshold=0.10:ratio=2:attack=8:release=100,loudnorm=I=-16:TP=-2:LRA=6','-ar','48000','-ac','1','-c:a','pcm_s24le','-y',str(voice)],check=True)
print(video,voice,flush=True)
