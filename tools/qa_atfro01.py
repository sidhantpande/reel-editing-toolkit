#!/usr/bin/env python3
"""Inspect caption visibility in the encoded reel, not just the source composition."""
from pathlib import Path
import subprocess,json,re,argparse
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('--output',default='.cache/analysis/atfro01-final');args=p.parse_args();out=R/args.output;out.mkdir(parents=True,exist_ok=True)
props=json.loads((R/'projects/atfro/atfro-01/reel.json').read_text());report=[]
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',args.video]))
sheet=Image.new('RGB',(1120,160*19),'#e4e5df');draw=ImageDraw.Draw(sheet)
for i,page in enumerate(props['captions']):
 sample=max(round(page['startMs']*.03)+1,round(page['endMs']*.03)-3)
 if sample<round(page['words'][-1]['startMs']*.03)+2:sample=round(page['endMs']*.03)-1
 frame=out/f'caption-{i:02d}.png';top=page['top']-30
 subprocess.run(['ffmpeg','-v','error','-ss',str(sample/30),'-i',args.video,'-frames:v','1','-vf',f'crop=940:240:70:{top}','-y',str(frame)],check=True)
 ocr=subprocess.check_output(['tesseract',str(frame),'stdout','--psm','6'],stderr=subprocess.DEVNULL,text=True).strip()
 expected=' '.join(w['text'] for w in page['words']);norm=lambda x:re.sub('[^a-z]','',x.lower())
 ratio=__import__('difflib').SequenceMatcher(None,norm(expected),norm(ocr)).ratio()
 report.append({'page':i,'sampleFrame':sample,'expected':expected,'ocr':ocr,'similarity':round(ratio,3),'review':ratio<.65})
 im=Image.open(frame).convert('RGB');im.thumbnail((540,130));x=(i%2)*560;y=(i//2)*160
 sheet.paste(im,(x,y+25));draw.text((x+5,y+5),f'{sample/30:.2f}s: {expected}',fill='black')
sheet.save(out/'captions-contact.jpg')
(out/'encoded-caption-check.json').write_text(json.dumps({'video':str(Path(args.video).resolve()),'probe':probe,'captions':report},indent=2)+'\n')
print('Caption samples:',len(report));print('OCR samples to visually review:',[(x['page'],x['expected'],x['ocr']) for x in report if x['review']])
