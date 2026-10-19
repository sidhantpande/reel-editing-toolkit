#!/usr/bin/env python3
"""Generate traceable full-span contact sheets from colour-verified event footage."""
import argparse
import json
import math
import subprocess
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from log_colour import classify, write

ROOT = Path(__file__).resolve().parents[1]

def analyse(manifest, conversions, out, wait=False):
    data = json.loads(Path(manifest).read_text()); out = Path(out); out.mkdir(parents=True, exist_ok=True)
    conversion_path = Path(conversions) / 'conversion-state.json'; review = []
    for i, record in enumerate(data['videos'], 1):
        relative = record['relative']; profile = classify(record['camera']); path = Path(record['path'])
        if profile == 'sony-slog3-sgamut3cine':
            while True:
                state = json.loads(conversion_path.read_text()) if conversion_path.exists() else {'files': {}}
                converted = state['files'].get(relative, {})
                if converted.get('status') == 'verified': path = Path(converted['path']); break
                if not wait: raise ValueError(f'Convert and verify Log footage first: {relative}')
                time.sleep(3)
        clip_id = f'{i:03d}-' + Path(relative).stem; folder = out / 'clips' / clip_id; folder.mkdir(parents=True, exist_ok=True)
        frames = sorted(folder.glob('frame-*.jpg'))
        if not (folder/'complete.json').exists():
            if frames or (folder/'last.jpg').exists():
                archived = folder.with_name(folder.name + '-interrupted-' + str(int(time.time())))
                folder.rename(archived); folder.mkdir()
            last_index = int(record['video'].get('nb_frames', 1)) - 1
            filters = f"[0:v]split=2[s][e];[s]fps=1:start_time=0:round=up,scale=320:-2[thumb];[e]select='eq(n,{last_index})',scale=320:-2[last]"
            subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-threads', '2', '-filter_complex_threads', '2', '-i', str(path), '-an', '-filter_complex', filters, '-map', '[thumb]', '-q:v', '3', str(folder/'frame-%04d.jpg'), '-map', '[last]', '-frames:v', '1', str(folder/'last.jpg')], check=True)
            frames = sorted(folder.glob('frame-*.jpg'))
            if not frames and (folder/'last.jpg').is_file():
                import shutil
                shutil.copy2(folder/'last.jpg',folder/'frame-0001.jpg'); frames=[folder/'frame-0001.jpg']
            if not frames or not (folder/'last.jpg').is_file():
                raise ValueError(f'Missing sampled/final frame: {folder}')
            write(folder/'complete.json', {'source': str(path), 'original': record['path'], 'original_sha256': record['sha256'], 'sample_interval_seconds': 1, 'sample_count': len(frames), 'last_frame': 'decoded', 'visual_review': 'pending'})
        all_frames = frames + [folder/'last.jpg']
        for page, start in enumerate(range(0, len(all_frames), 30), 1):
            selected = all_frames[start:start+30]; rows = math.ceil(len(selected)/5)
            sheet = Image.new('RGB', (5*324, rows*210+36), '#171d23'); draw = ImageDraw.Draw(sheet)
            draw.text((8,8), f'{clip_id} | {relative} | {record["duration"]:.2f}s | {profile}', fill='white')
            for j, frame in enumerate(selected):
                im = Image.open(frame); im.thumbnail((320,180)); x=(j%5)*324; y=36+(j//5)*210; sheet.paste(im,(x,y))
                label = 'last decoded frame' if frame.name == 'last.jpg' else f'{int(frame.stem.split("-")[-1])-1:.0f}s sample'
                draw.text((x+4,y+184),label,fill='white')
            sheet.save(folder/f'contact-{page:02d}.jpg',quality=88)
        indices = [0, min(len(frames)-1, int(len(frames)*.25)), min(len(frames)-1, int(len(frames)*.5)), min(len(frames)-1, int(len(frames)*.75))]
        row = Image.new('RGB',(1280,170),'#171d23'); d=ImageDraw.Draw(row)
        for j, frame in enumerate([frames[k] for k in indices] + [folder/'last.jpg']):
            im=Image.open(frame);im.thumbnail((252,142));row.paste(im,(j*256,24))
        d.text((4,5),f'{clip_id} | {relative} | {record["duration"]:.2f}s | {record["video"]["avg_frame_rate"]} fps',fill='white');row.save(folder/'overview-row.jpg',quality=90)
        review.append({'id':clip_id,'relative':relative,'original':record['path'],'analysis_source':str(path),'duration':record['duration'],'fps':record['video']['avg_frame_rate'],'profile':profile,'folder':str(folder),'visual_review':'pending','portrait_crop':'pending shot-specific review'})
        write(out/'review-index.json', {'clips':review,'status':'contact sheets generated; human/model visual assessment recorded separately'})
        # Update each overview page as its clips become available.
        page=(i-1)//12+1; chunk=review[(page-1)*12:page*12];sheet=Image.new('RGB',(1280,len(chunk)*170),'#171d23')
        for j, entry in enumerate(chunk):sheet.paste(Image.open(Path(entry['folder'])/'overview-row.jpg'),(0,j*170))
        sheet.save(out/f'overview-{page:02d}.jpg',quality=90)
        print(f'[{i}/{len(data["videos"])}] analysed {relative}',flush=True)
    return review

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest');p.add_argument('--conversions',required=True);p.add_argument('--out',required=True);p.add_argument('--wait',action='store_true');a=p.parse_args()
    analyse(a.manifest,a.conversions,a.out,a.wait)
if __name__=='__main__':main()
