#!/usr/bin/env python3
"""Inspect word captions in an actual encoded export, with split contact sheets for visual review."""
from pathlib import Path
import subprocess,json,re,argparse,math,difflib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('project');p.add_argument('video');p.add_argument('--output',required=True);a=p.parse_args();out=R/a.output;out.mkdir(parents=True,exist_ok=True);props=json.loads((R/a.project/'reel.json').read_text());report=[]
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',a.video]))
video_width=next(s['width'] for s in probe['streams'] if s['codec_type']=='video');scale=video_width/1080
for batch in range(math.ceil(len(props['captions'])/28)):
 subset=props['captions'][batch*28:(batch+1)*28];sheet=Image.new('RGB',(1120,180*math.ceil(len(subset)/2)),'#e4e5df');draw=ImageDraw.Draw(sheet)
 for i,page in enumerate(subset):
  idx=batch*28+i;sample=max(round(page['startMs']*.03)+1,round(page['endMs']*.03)-3)
  if sample<round(page['words'][-1]['startMs']*.03)+2:sample=round(page['endMs']*.03)-1
  frame=out/f'caption-{idx:02d}.png';top=round((page['top']-30)*scale/2)*2;cw=round(980*scale/2)*2;ch=round(290*scale/2)*2;cx=round(50*scale/2)*2
  subprocess.run(['ffmpeg','-v','error','-ss',str(sample/30),'-i',a.video,'-frames:v','1','-vf',f'crop={cw}:{ch}:{cx}:{top}','-y',str(frame)],check=True)
  ocr=subprocess.check_output(['tesseract',str(frame),'stdout','--psm','6'],stderr=subprocess.DEVNULL,text=True).strip();expected=' '.join(w['text'] for w in page['words']);norm=lambda t:re.sub('[^a-z0-9]','',t.lower());ratio=difflib.SequenceMatcher(None,norm(expected),norm(ocr)).ratio();report.append({'page':idx,'sampleFrame':sample,'expected':expected,'ocr':ocr,'similarity':round(ratio,3),'review':ratio<.65})
  im=Image.open(frame).convert('RGB');im.thumbnail((540,150));x=(i%2)*560;y=(i//2)*180;sheet.paste(im,(x,y+25));draw.text((x+4,y+4),f'{idx}: {sample/30:.2f}s / {expected}',fill='black')
 sheet.save(out/f'captions-{batch+1:02d}.jpg')
(out/'encoded-caption-check.json').write_text(json.dumps({'video':str(Path(a.video).resolve()),'probe':probe,'captions':report},indent=2)+'\n');print('Sampled',len(report),'caption groups from encoded video.')
