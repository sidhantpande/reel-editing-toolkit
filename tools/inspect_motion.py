#!/usr/bin/env python3
"""Measure late B-roll artwork changes in the encoded reel, excluding captions and fades."""
from pathlib import Path
import argparse,json,subprocess,numpy as np
R=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('project');ap.add_argument('video');ap.add_argument('--output',required=True);a=ap.parse_args();props=json.loads((R/a.project/'reel.json').read_text());out=R/a.output;out.mkdir(parents=True,exist_ok=True)
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(R/a.video),'-vf','fps=2,crop=1080:1220:0:0,scale=270:305','-pix_fmt','gray','-f','rawvideo','-']);frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,305,270);report=[]
for cue in props['broll']:
 start=cue['from']/30;end=(cue['from']+cue['duration'])/30;samples=[i for i in range(len(frames)) if start+1.2<=i/2<=end-.35];pairs=[]
 for i,j in zip(samples,samples[1:]):
  delta=np.abs(frames[j].astype(np.float32)-frames[i].astype(np.float32));pairs.append(dict(fromSeconds=i/2,toSeconds=j/2,meanPixelChange=round(float(delta.mean()),4),changedPixelFraction=round(float((delta>2).mean()),5)))
 report.append(dict(kind=cue['kind'],fromSeconds=start,toSeconds=end,lateFramePairs=pairs,staticLatePairs=[p for p in pairs if p['meanPixelChange']<.015]))
(out/'motion-review.json').write_text(json.dumps(report,indent=2)+'\n');print([(r['kind'],len(r['lateFramePairs']),len(r['staticLatePairs'])) for r in report])
