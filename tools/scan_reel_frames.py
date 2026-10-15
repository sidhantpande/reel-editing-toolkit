#!/usr/bin/env python3
"""Inspect encoded camera frames for the repeated viewport-tile artifact observed in desktop Chrome."""
from pathlib import Path
import argparse,json,subprocess
import numpy as np
R=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('project');ap.add_argument('video');ap.add_argument('--output',required=True);a=ap.parse_args();props=json.loads((R/a.project/'reel.json').read_text());out=R/a.output;out.mkdir(parents=True,exist_ok=True)
cmd=['ffmpeg','-v','error','-i',str(R/a.video),'-vf','scale=270:480','-pix_fmt','gray','-f','rawvideo','-'];p=subprocess.Popen(cmd,stdout=subprocess.PIPE);flags=[];index=0;checked=0;lowest=[];last_camera_mean=None;first_closing_mean=None
while True:
 data=p.stdout.read(270*480)
 if not data:break
 assert len(data)==270*480
 if index==props['endCardFrom']-1:last_camera_mean=float(np.frombuffer(data,dtype=np.uint8).reshape(480,270)[:300].mean())
 if index==props['endCardFrom']:first_closing_mean=float(np.frombuffer(data,dtype=np.uint8).reshape(480,270)[:300].mean())
 opaque=any(c['from']+c.get('fadeFrames',0)<=index<c['from']+c['duration']-c.get('fadeFrames',0) for c in props['broll'])
 if index<props['endCardFrom'] and not opaque:
  im=np.frombuffer(data,dtype=np.uint8).reshape(480,270).astype(np.float32);checked+=1;scores=[]
  for offset in [103,104]:
   x=im[:-offset].ravel();y=im[offset:].ravel();delta=float(np.abs(x-y).mean());corr=float(np.corrcoef(x,y)[0,1]) if x.std()>2 and y.std()>2 else 0;scores.append((delta,corr))
  d,corr=min(scores,key=lambda s:s[0]);horizontal=float(np.abs(im[:,:81]-im[:,189:]).mean());record=dict(frame=index,seconds=round(index/30,3),verticalDelta=round(d,3),horizontalDelta=round(horizontal,3),correlation=round(corr,5));lowest.append(record)
  if d<10 and horizontal<10 and corr>.94:
   flags.append(record)
 index+=1
assert p.wait()==0
ratio=first_closing_mean/max(last_camera_mean,1) if first_closing_mean is not None and last_camera_mean is not None else None
report=dict(firstClosingFrameBrightnessRatio=ratio,video=a.video,decodedFrames=index,checkedCameraFrames=checked,detector='Observed artifact repeats a 756x413 viewport inside an expected 1080x1920 frame. Detect correlated vertical/horizontal repeats on reduced encoded frames; opaque paper and logo holds excluded.',suspectedTiles=flags,lowestVerticalDelta=sorted(lowest,key=lambda s:s['verticalDelta'])[:12]);(out/'tile-scan.json').write_text(json.dumps(report,indent=2)+'\n')
for row in flags:subprocess.run(['ffmpeg','-v','error','-ss',str(row['frame']/30),'-i',str(R/a.video),'-frames:v','1','-y',str(out/f'tile-{row["frame"]}.png')],check=True)
print(a.video,'decoded',index,'camera frames checked',checked,'tile candidates',len(flags),[x['frame'] for x in flags])
