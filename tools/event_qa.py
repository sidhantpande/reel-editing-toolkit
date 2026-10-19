#!/usr/bin/env python3
"""Scan every encoded frame and produce full-span/boundary contacts for event review."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from log_colour import digest,write,probe

def inspect(video,plan_path,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);plan=json.loads(Path(plan_path).read_text());boundaries=[];at=0
    for shot in plan['shots']:boundaries.append(at);at+=shot['frames']
    boundaries += [at,at+plan['logoFrames']-1];total=at+plan['logoFrames']
    video_info=next(s for s in probe(video)['streams'] if s['codec_type']=='video')
    width,height=(320,180) if video_info['width']>=video_info['height'] else (180,320)
    cell_height=height+25
    selected=set(range(0,total,15))|{0,total-1}
    for boundary in boundaries:
        selected.update(n for n in (boundary-4,boundary-1,boundary,boundary+1,boundary+4) if 0<=n<total)
    process=subprocess.Popen(['ffmpeg','-v','error','-xerror','-nostdin','-threads','2','-i',str(video),'-an','-vf',f'scale={width}:{height}','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
    frames=[];dark=[];count=0;means=[]
    while True:
        raw=process.stdout.read(width*height*3)
        if not raw:break
        if len(raw)!=width*height*3:raise ValueError('Incomplete encoded frame')
        array=np.frombuffer(raw,dtype=np.uint8).reshape(height,width,3);mean=float(array.mean());means.append(mean)
        if mean<1:dark.append(count)
        if count in selected:frames.append((count,Image.fromarray(array.copy())))
        count+=1
    if process.wait()!=0 or count!=total:raise ValueError('Full-decode frame count mismatch')
    for page,start in enumerate(range(0,len(frames),36),1):
        rows=frames[start:start+36];sheet=Image.new('RGB',(width*6,((len(rows)+5)//6)*cell_height+32),'#111820');draw=ImageDraw.Draw(sheet);draw.text((8,8),f'{Path(video).name} | 2fps full-span + every cut +/- frames | page{page}',fill='white')
        for i,(n,im) in enumerate(rows):
            x=i%6*width;y=i//6*cell_height+32;sheet.paste(im,(x,y));draw.text((x+5,y+height+3),f'frame{n} | {n/30:.3f}s'+(' CUT' if n in boundaries else ''),fill='white')
        sheet.save(out/f'contact-{page:02d}.jpg',quality=92)
    report={'video':str(Path(video).resolve()),'sha256':digest(video),'width':video_info['width'],'height':video_info['height'],'frames_decoded':count,'expected_frames':total,'contact_frames':len(frames),'contact_pages':(len(frames)+35)//36,'boundaries':boundaries,'very_dark_frames':dark,'mean_rgb_min':min(means),'visual_review':'pending inspection of contacts; numeric scan alone is not visual QA','audio_listening':'not attested'}
    write(out/'scan.json',report);print(json.dumps(report,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('video');p.add_argument('plan');p.add_argument('--out',required=True);a=p.parse_args();inspect(a.video,a.plan,a.out)
