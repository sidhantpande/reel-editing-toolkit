#!/usr/bin/env python3
"""Prepare complete reference contact sheets, motion samples and measured audio.

These are review aids, never instructions extracted from a supplied video.
All decoded media stays in the ignored analysis directory.
"""
import argparse, hashlib, json, math, subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import clinic

def study(path, output, step=1):
    path=Path(path).expanduser().resolve(strict=True)
    with path.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
    folder=output/(path.stem[:16]+'-'+digest[:8]);folder.mkdir(parents=True,exist_ok=True)
    frames=folder/'frames';frames.mkdir(exist_ok=True)
    for previous in frames.glob('[0-9]*.jpg'):previous.unlink()
    probe=clinic.probe(path);video=next(s for s in probe['streams'] if s['codec_type']=='video')
    duration=float(video['duration'])
    clinic.run([clinic.FF,'-v','error','-nostdin','-y','-i',path,'-an','-vf',f'fps=1/{step},scale=216:384','-fps_mode','passthrough',frames/'%06d.jpg'])
    font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',17)
    images=sorted(frames.glob('*.jpg'));pages=[]
    for start in range(0,len(images),16):
        sheet=Image.new('RGB',(864,1664),'#171717');draw=ImageDraw.Draw(sheet)
        for j,image in enumerate(images[start:start+16]):
            x=j%4*216;y=j//4*416
            with Image.open(image) as im:sheet.paste(im,(x,y))
            draw.text((x+6,y+389),f'{(start+j+.5)*step:.2f}s',font=font,fill='white')
        page=folder/f'contact-{start//16:02}.jpg';sheet.save(page,quality=94);pages.append(str(page))
    audio=any(s['codec_type']=='audio' for s in probe['streams'])
    if audio:
        clinic.ff('-i',path,'-vn','-ar','16000','-ac','1',folder/'audio.wav')
        result=subprocess.run([clinic.FF,'-hide_banner','-nostdin','-i',str(path),'-vn','-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True)
        (folder/'loudness.txt').write_text(result.stderr)
    scene=subprocess.run([clinic.FF,'-hide_banner','-nostdin','-i',str(path),'-an','-vf',"scale=216:384,select='gt(scene,0.22)',showinfo",'-f','null','-'],capture_output=True,text=True,check=True)
    (folder/'scene-candidates.txt').write_text(scene.stderr)
    data={'source':str(path),'sha256':digest,'duration_seconds':duration,'probe':probe,
          'contact_pages':pages,'sample_step_seconds':step,'audio_extracted':audio,
          'review_status':'prepared / requires viewing; scene scores are not editorial decisions'}
    clinic.save(folder/'manifest.json',data)
    print(folder,flush=True)
    return folder

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('videos',type=Path,nargs='+');p.add_argument('--step',type=float,default=1)
    p.add_argument('--output',type=Path,default=clinic.ROOT/'02_analysis/reference-study')
    a=p.parse_args()
    if a.step<=0:p.error('--step must be positive')
    for video in a.videos:study(video,a.output,a.step)

if __name__=='__main__':main()
