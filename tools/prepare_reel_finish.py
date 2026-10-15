#!/usr/bin/env python3
"""Generate approved still blends and a continuous original music bed for any prepared reel."""
from pathlib import Path
import subprocess,json,argparse
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('project');p.add_argument('--bed',default='calm-focus');a=p.parse_args();folder=R/a.project;plan=json.loads((folder/'cut-list.json').read_text());props=json.loads((folder/'reel.json').read_text());name=plan['id'];out=R/'.cache/proxies'/(name+'-holds');out.mkdir(parents=True,exist_ok=True);proxy=R/'.cache/proxies'/(name+'-aroll.mp4')
# Select decoded frame indices in one pass. Timestamp seeks can land after the
# final PTS of concat-generated proxies even when the declared last frame exists.
needed={plan['dialogueFrames']-1:'end.jpg'};blends=[]
for c in plan['cuts'][1:]:
 f=c['timelineFrom']
 if any(b['from']+b.get('fadeFrames',0)<=f and f+3<=b['from']+b['duration']-b.get('fadeFrames',0) for b in props['broll']):continue
 needed[f-1]=f'cut-{f}.jpg';blends.append({'from':f,'duration':3,'src':f'proxies/{name}-holds/cut-{f}.jpg'})
frames=sorted(needed);stage=out/'decoded';stage.mkdir(exist_ok=True)
select='+'.join(f'eq(n\\,{frame})' for frame in frames)
subprocess.run(['ffmpeg','-v','error','-i',str(proxy),'-vf','select='+select,'-fps_mode','vfr','-q:v','2','-start_number','0','-y',str(stage/'frame-%04d.jpg')],check=True)
for i,frame in enumerate(frames):
 image=stage/f'frame-{i:04d}.jpg'
 if not image.is_file():raise RuntimeError(f'Missing decoded source frame {frame} for {name}')
 image.replace(out/needed[frame])
(folder/'cut-smoothing.json').write_text(json.dumps(blends,indent=2)+'\n')
source=R/'public/assets/music'/(a.bed+'.wav');music=R/'public/assets/music'/(name+'-bed.wav');length=plan['totalFrames']/30+2
subprocess.run(['ffmpeg','-v','error','-i',str(source),'-i',str(source),'-filter_complex',f'[0:a][1:a]acrossfade=d=4:c1=qsin:c2=qsin,highpass=f=55,lowpass=f=5500,afade=t=in:d=1.2,atrim=duration={length},loudnorm=I=-27:TP=-8:LRA=7[a]','-map','[a]','-ar','48000','-c:a','pcm_s24le','-y',str(music)],check=True)
print('Prepared',len(blends),'short blends and continuous quiet bed.')
