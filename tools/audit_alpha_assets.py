#!/usr/bin/env python3
"""Audit all encoded alpha frames for unexpected empty interior frames."""
from pathlib import Path
import subprocess,json,argparse,numpy as np
ap=argparse.ArgumentParser();ap.add_argument('folder');ap.add_argument('--output',required=True);a=ap.parse_args();report=[]
for file in sorted(Path(a.folder).rglob('*.webm')):
 p=subprocess.Popen(['ffmpeg','-v','error','-c:v','libvpx-vp9','-i',str(file),'-vf','alphaextract,scale=108:192','-f','rawvideo','-pix_fmt','gray','-'],stdout=subprocess.PIPE);maxima=[]
 while True:
  raw=p.stdout.read(108*192)
  if not raw:break
  assert len(raw)==108*192
  maxima.append(int(np.frombuffer(raw,dtype=np.uint8).max()))
 assert p.wait()==0
 blanks=[i for i,v in enumerate(maxima) if 24<=i<len(maxima)-12 and v<20];report.append(dict(asset=str(file),frames=len(maxima),unexpectedEmptyFrames=blanks));print(file.name,len(maxima),'frames, empty interior',blanks,flush=True)
Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(report,indent=2)+'\n')
