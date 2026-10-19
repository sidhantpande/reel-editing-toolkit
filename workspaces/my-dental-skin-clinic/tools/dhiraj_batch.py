#!/usr/bin/env python3
"""Non-destructive, resumable analysis of the October Dhiraj shoot."""
import argparse, concurrent.futures, hashlib, json, subprocess
from pathlib import Path
import clinic
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=clinic.ROOT
BATCH=ROOT/'03_reels/dhiraj'
ANALYSIS=ROOT/'02_analysis/dhiraj'

def selected():
    return [r for r in clinic.sources() if any('/Dhiraj/' in p for p in r['paths'])]

def prepare(r):
    out=ANALYSIS/r['filename'].split('.')[0];out.mkdir(parents=True,exist_ok=True)
    source=r['paths'][0]
    audio=out/'audio.wav'
    if not audio.exists():clinic.ff('-i',source,'-vn','-ar','16000','-ac','1','-c:a','pcm_s16le',audio)
    frames=out/'frames';frames.mkdir(exist_ok=True)
    if not (out/'contacts.json').exists():
        clinic.run([clinic.FF,'-v','error','-nostdin','-y','-i',source,'-an','-vf','fps=1/2,scale=480:270','-fps_mode','passthrough',frames/'%05d.jpg'])
        imgs=sorted(frames.glob('[0-9][0-9][0-9][0-9][0-9].jpg'));pages=[]
        font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',19)
        for offset in range(0,len(imgs),16):
            sheet=Image.new('RGB',(1920,1200),'#15191c');d=ImageDraw.Draw(sheet)
            for i,p in enumerate(imgs[offset:offset+16]):
                x=i%4*480;y=i//4*300
                with Image.open(p) as im:sheet.paste(im,(x,y))
                d.text((x+8,y+273),f'{r["filename"]} / {(offset+i)*2+1:.1f}s',font=font,fill='white')
            dest=out/f'contact-{offset//16:02}.jpg';sheet.save(dest,quality=90);pages.append(str(dest))
        clinic.save(out/'contacts.json',{'pages':pages,'sample_step':2,'status':'requires visual review'})
    return r,out

def analyse():
    from faster_whisper import WhisperModel
    from faster_whisper.audio import decode_audio
    import numpy as np
    model=WhisperModel(str(clinic.model_path('turbo')),device='cpu',compute_type='int8',cpu_threads=4)
    rows=selected();BATCH.mkdir(parents=True,exist_ok=True)
    clinic.save(BATCH/'source-inventory.json',rows)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for r,out in pool.map(prepare,rows):
            if not (out/'transcript.json').exists():
                audio=decode_audio(str(out/'audio.wav'))
                # Normalize quiet lavalier recordings without clipping transients.
                peak=float(np.quantile(np.abs(audio),.999))
                gain=min(8,.7/max(peak,.001))
                segs,info=model.transcribe(np.clip(audio*gain,-.98,.98),language='hi',word_timestamps=True,vad_filter=True,condition_on_previous_text=False,beam_size=5)
                data=[{'start':s.start,'end':s.end,'text':s.text,'words':[{'text':w.word.strip(),'start':w.start,'end':w.end,'probability':w.probability} for w in s.words or []]} for s in segs]
                clinic.save(out/'transcript.json',{'status':'DRAFT / ASR is not listening approval','source_id':r['id'],'gain':gain,'segments':data})
                (out/'transcript.txt').write_text('\n'.join(f'[{s["start"]:.2f} - {s["end"]:.2f}] {s["text"]}' for s in data))
            print('ANALYSED',r['filename'],flush=True)
    with (BATCH/'all-transcripts-draft.md').open('w') as f:
        f.write('# Dhiraj source transcript drafts\n\nASR supporting evidence; not corrected captions or human listening approval.\n\n')
        for r in rows:
            f.write('\n## '+r['filename']+'\n\n'+(ANALYSIS/Path(r['filename']).stem/'transcript.txt').read_text()+'\n')

def second_pass():
    """Independent local Metal decoding, never synthetic dialogue."""
    for r in selected():
        out=ANALYSIS/Path(r['filename']).stem
        dest=out/'metal-pass'
        if dest.with_suffix('.json').exists():continue
        norm=out/'normalized.wav'
        if not norm.exists():clinic.ff('-i',out/'audio.wav','-af','highpass=f=70,loudnorm=I=-18:TP=-2:LRA=11','-ar','16000','-ac','1',norm)
        args=['whisper-cli','-m',str(ROOT/'.cache/models/ggml-large-v3-turbo-q5_0.bin'),'-l','hi','-bs','3','-bo','3','-ml','80','-sow','-ojf','-otxt','-of',str(dest),'-f',str(norm)]
        with (out/'metal-pass.log').open('w') as log:
            subprocess.run(args,stdout=log,stderr=log,check=True)
        print('SECOND PASS',r['filename'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['analyse','second-pass']);a=p.parse_args()
    if a.action=='analyse':analyse()
    elif a.action=='second-pass':second_pass()
