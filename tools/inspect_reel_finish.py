#!/usr/bin/env python3
"""Decode a finished reel, measure loudness and inspect encoded cut/graphic boundaries."""
from pathlib import Path
import argparse,json,re,subprocess
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('project');ap.add_argument('video');ap.add_argument('--output',required=True);a=ap.parse_args();out=R/a.output;out.mkdir(parents=True,exist_ok=True);video=R/a.video
plan=json.loads((R/a.project/'cut-list.json').read_text());props=json.loads((R/a.project/'reel.json').read_text())
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
scan=subprocess.run(['ffmpeg','-hide_banner','-i',str(video),'-vf','blackdetect=d=0.04:pix_th=0.08','-af','loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
(out/'decode-loudness.log').write_text(scan.stderr);loudness=json.loads(re.findall(r'\{\s*"input_i".*?\}',scan.stderr,re.S)[-1]);black=re.findall(r'black_start:[^\n]+',scan.stderr)
events=[(c['timelineFrom'],'camera cut') for c in plan['cuts'][1:]]
for c in props['broll']:events.extend([(c['from'],'graphic enters'),(c['from']+c['duration']-c.get('fadeFrames',0),'graphic leaves')])
events.append((props['endCardFrom'],'logo begins'));events.sort()
for batch in range((len(events)+7)//8):
 subset=events[batch*8:(batch+1)*8];sheet=Image.new('RGB',(752,350*len(subset)),'#E4E5DF');draw=ImageDraw.Draw(sheet)
 for i,(f,label) in enumerate(subset):
  for j,delta in enumerate([-2,0,2,6]):
   frame=max(0,min(props['durationInFrames']-1,f+delta));file=out/f'boundary-{f}-{frame}.jpg'
   subprocess.run(['ffmpeg','-v','error','-ss',str(frame/30),'-i',str(video),'-frames:v','1','-vf','scale=180:320','-y',str(file)],check=True)
   sheet.paste(Image.open(file),(j*188,i*350+27));draw.text((j*188+3,i*350+4),f'{label} {frame}',fill='black')
 sheet.save(out/f'boundaries-{batch+1:02d}.jpg')
s=next(s for s in probe['streams'] if s['codec_type']=='video');result={'video':str(video),'dimensions':[s['width'],s['height']],'frames':int(s['nb_frames']),'fps':s['r_frame_rate'],'durationSeconds':float(probe['format']['duration']),'fullDecode':'passed','audioLUFS':float(loudness['input_i']),'audioTruePeakDBTP':float(loudness['input_tp']),'loudnessRangeLU':float(loudness['input_lra']),'blackIntervals':black,'boundaryEvents':len(events)}
(out/'finish-measurements.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
