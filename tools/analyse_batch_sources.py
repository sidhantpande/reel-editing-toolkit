#!/usr/bin/env python3
"""Create private chronological source contacts and pause logs without modifying footage."""
from pathlib import Path
import subprocess,json,math
R=Path(__file__).resolve().parents[1];out=R/'.cache/batch';out.mkdir(exist_ok=True)
for reel in json.loads((R/'projects/batch-queue.json').read_text())['reels']:
 if reel['status']=='approved':continue
 plan=json.loads((R/reel['project']/'edit-plan.json').read_text())
 for take in plan['takes']:
  if take['role']=='false-start':continue
  src=R/take['path'];sheet=out/(src.stem+'-contact.jpg');pause=out/(src.stem+'-silences.log')
  if not sheet.exists():
   d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(src)]));rows=math.ceil(math.ceil(d)/8)
   subprocess.run(['ffmpeg','-v','error','-i',str(src),'-vf',f'fps=1,scale=162:288,tile=8x{rows}:padding=8:margin=8','-frames:v','1','-y',str(sheet)],check=True)
  if not pause.exists():
   with pause.open('w') as log:subprocess.run(['ffmpeg','-hide_banner','-i',str(R/'.cache/audio'/(src.stem+'.wav')),'-af','silencedetect=n=-32dB:d=0.20','-f','null','-'],stderr=log,stdout=subprocess.DEVNULL,check=True)
  print('Analysed',src.name,flush=True)
