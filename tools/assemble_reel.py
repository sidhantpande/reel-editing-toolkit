#!/usr/bin/env python3
"""Rebuild portrait A-roll and dialogue from a project's frame-quantized cut list."""
from pathlib import Path
import subprocess,json,hashlib,argparse
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('project');a=p.parse_args();folder=R/a.project;plan=json.loads((folder/'cut-list.json').read_text());name=plan['id'];cache=R/'.cache/edits'/name;cache.mkdir(parents=True,exist_ok=True);proxy=R/'.cache/proxies';proxy.mkdir(exist_ok=True)
grade=json.loads((folder/'colour-grade.json').read_text())['filter'];key=hashlib.sha256(grade.encode()).hexdigest()[:8];segments=[]
for i,c in enumerate(plan['cuts']):
 cx=c.get('cropX',.5);cy=c.get('cropY',.35)
 out=cache/f'{i:02d}-{c["inFrame"]}-{c["outFrame"]}-{c["zoom"]}-x{cx}-y{cy}-{key}.mkv';segments.append(out)
 if out.exists():continue
 dur=c['duration']/30;z=c['zoom'];w=round(1080*z/2)*2;h=round(1920*z/2)*2
 vf=f'scale={w}:{h},crop=1080:1920:(iw-1080)*{cx}:(ih-1920)*{cy},setsar=1,fps=30,{grade},format=yuv420p';af=f'aresample=48000,afade=t=in:d=0.004,afade=t=out:st={dur-.004}:d=0.004'
 subprocess.run(['ffmpeg','-v','error','-ss',str(c['inFrame']/30),'-i',str(R/c['source']),'-t',str(dur),'-vf',vf,'-af',af,'-ac','1','-c:v','libx264','-preset','fast','-crf','17','-c:a','pcm_s16le','-f','matroska',str(out)],check=True);print(f'Segment {i+1}/{len(plan["cuts"])}',flush=True)
concat=cache/'concat.txt';concat.write_text('\n'.join("file '"+str(f).replace("'","'\\''")+"'" for f in segments)+'\n')
subprocess.run(['ffmpeg','-v','error','-f','concat','-safe','0','-i',str(concat),'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-y',str(proxy/(name+'-aroll.mp4'))],check=True)
subprocess.run(['ffmpeg','-v','error','-f','concat','-safe','0','-i',str(concat),'-vn','-af','highpass=f=85,lowpass=f=14000,afftdn=nr=6:nf=-36:tn=1,acompressor=threshold=0.10:ratio=2:attack=8:release=100,loudnorm=I=-16:TP=-2:LRA=6','-ar','48000','-ac','1','-c:a','pcm_s24le','-y',str(proxy/(name+'-dialogue.wav'))],check=True)
print('Assembled',name,plan['dialogueFrames'],'frames.')
