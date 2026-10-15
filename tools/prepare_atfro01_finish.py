#!/usr/bin/env python3
"""Keep the approved dialogue timing while adding short visual-only cut blends and a continuous bed."""
from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parents[1];folder=R/'projects/atfro/atfro-01';plan=json.loads((folder/'cut-list.json').read_text());props=json.loads((folder/'reel.json').read_text());out=R/'.cache/proxies/atfro-01-holds';out.mkdir(parents=True,exist_ok=True)
proxy=R/'.cache/proxies/atfro-01-aroll.mp4'
def still(frame,name):
 p=out/name
 subprocess.run(['ffmpeg','-v','error','-ss',str(frame/30),'-i',str(proxy),'-frames:v','1','-q:v','2','-y',str(p)],check=True)
 return 'proxies/atfro-01-holds/'+name
blends=[]
for cut in plan['cuts'][1:]:
 f=cut['timelineFrom']
 # B-roll already covers these edits; avoid layering a second transition at its edges.
 if any(c['from']-10<=f<=c['from']+c['duration']+10 for c in props['broll']):continue
 blends.append({'from':f,'duration':3,'src':still(f-1,f'cut-{f}.jpg')})
still(plan['dialogueFrames']-1,'end.jpg')
(folder/'cut-smoothing.json').write_text(json.dumps(blends,indent=2)+'\n')
# Overlap the existing original bed by four seconds, so its 32-second restart is inaudible.
source=R/'public/assets/music/atfro-01-bed.wav';music=R/'public/assets/music/atfro-01-bed-v6.wav'
subprocess.run(['ffmpeg','-v','error','-i',str(source),'-i',str(source),'-filter_complex','[0:a][1:a]acrossfade=d=4:c1=qsin:c2=qsin,highpass=f=55,lowpass=f=5500,afade=t=in:d=1.2,atrim=duration=42[a]','-map','[a]','-ar','48000','-c:a','pcm_s24le','-y',str(music)],check=True)
print(f'Prepared {len(blends)} short video-only blends, a logo-transition hold and a continuous softened music bed.')
