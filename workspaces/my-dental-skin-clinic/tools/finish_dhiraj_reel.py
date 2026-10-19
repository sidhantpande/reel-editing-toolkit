#!/usr/bin/env python3
"""Finish a checked Dhiraj clean cut without rebuilding its dialogue joins."""
import argparse, hashlib, json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw
import clinic
import render_reel07_v04 as caps
import dhiraj_captions as directed_caps
import dhiraj_premium_captions as premium_caps
import dhiraj_audio
from clinic_plan import validate_plan
from audio_enhance import enhance

R=clinic.ROOT

def clean_picture(plan):
    """Direct source joins avoid the earlier double-face crossfade."""
    from render_dhiraj_selects import crop_filter
    key=hashlib.sha256(json.dumps(plan['segments'],sort_keys=True).encode()+b'direct-source-cuts-v1').hexdigest()[:16]
    folder=R/'.cache/dhiraj-finishing/picture'/key;folder.mkdir(parents=True,exist_ok=True)
    output=folder/'direct-joins.mp4'
    if output.exists():return output
    parts=[]
    for i,s in enumerate(plan['segments']):
        part=folder/f'{i:02}.mp4';parts.append(part)
        if not part.exists():clinic.ff('-ss',s['source_in'],'-i',s['source'],'-an','-vf',crop_filter(s,s['source_in']),'-frames:v',round((s['timeline_out']-s['timeline_in'])*30),'-c:v','h264_videotoolbox','-b:v','14M','-g','60','-pix_fmt','yuv420p',part)
    listing=folder/'concat.txt';listing.write_text('\n'.join("file '"+str(p)+"'" for p in parts)+'\n')
    clinic.ff('-f','concat','-safe','0','-i',listing,'-an','-c','copy',output)
    return output

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()

def finish(path):
    plan=json.loads(path.read_text()); validate_plan(plan,root=R)
    if not plan['words']: raise ValueError('Corrected caption words required')
    picture=Path(plan['clean_export'])
    previous=json.loads(picture.with_suffix('.render.json').read_text())
    if sha(picture)!=previous['sha256']: raise ValueError('Clean picture changed after review')
    style_path=R/plan['style']; style=json.loads(style_path.read_text())
    logo=R/style['logo']['path']
    if sha(logo)!=style['logo']['sha256']: raise ValueError('Supplied logo checksum changed')
    signature=hashlib.sha256(path.read_bytes()+style_path.read_bytes()+Path(__file__).read_bytes()+Path(caps.__file__).read_bytes()+Path(directed_caps.__file__).read_bytes()+Path(premium_caps.__file__).read_bytes()+Path(dhiraj_audio.__file__).read_bytes()+sha(previous['dialogue_pcm']).encode()).hexdigest()
    output=Path(plan['finished_export']); record=output.with_suffix('.render.json')
    if output.exists():
        if record.exists() and json.loads(record.read_text())['signature']==signature:
            print('Already rendered',output); return
        raise FileExistsError('Use a new version; finished export already exists')
    for slot in plan['broll_slots']:
        if sha(slot['path'])!=slot['sha256']:raise ValueError('B-roll checksum changed: '+slot['id'])
    cache=R/'.cache/dhiraj-finishing'/signature[:16];cache.mkdir(parents=True,exist_ok=True)
    engine={'directed':directed_caps,'premium':premium_caps}.get(style.get('caption',{}).get('engine'),caps)
    engine.CACHE=cache;engine.OUT=path.parent;engine.STYLE=style;engine.prepare_fonts()
    caption=cache/('premium-word-captions.mov' if engine is premium_caps else 'editorial-word-captions.mov' if engine is directed_caps else 'compact-word-captions.mov')
    if not caption.exists():caption=engine.captions(plan)
    audio_cache=R/'.cache/dhiraj-finishing/audio'/sha(previous['dialogue_pcm'])[:16]
    audio=audio_cache/'dialogue-enhanced-master.wav'
    if not audio.exists():audio,_=enhance(previous['dialogue_pcm'],audio_cache,6)
    voice=audio
    if plan.get('music'):audio=dhiraj_audio.mix(plan,voice,cache/'mix')
    if style.get('picture_joins')=='clean-cuts':picture=clean_picture(plan)
    gradient=cache/'caption-gradient.png'
    shade=Image.new('RGBA',(1080,1920),(0,0,0,0));draw=ImageDraw.Draw(shade)
    gradient_start=style.get('gradient_start',1020);gradient_strength=style.get('gradient_strength',.18)
    for y in range(gradient_start,1920):draw.line((0,y,1079,y),fill=(0,0,0,min(155,round((y-gradient_start)*gradient_strength))))
    shade.save(gradient)
    args=[clinic.FF,'-v','error','-nostdin','-y','-i',picture,'-i',audio]
    graph=['[0:v]eq=contrast=1.025:brightness=0.003:saturation=1.02[base]'];current='base'
    gi=len(plan['broll_slots'])+3
    if style.get('gradient_before_broll'):
        graph.append(f'[base][{gi}:v]overlay=0:0[baseShade]');current='baseShade'
    for i,slot in enumerate(plan['broll_slots']):
        d=slot['timeline_out']-slot['timeline_in'];idx=i+2
        args+=['-ss',slot['media_in'],'-t',d,'-i',slot['path']]
        if slot.get('transition') in ['soft-wipe','soft-rise']:
            axis='Y' if slot['transition']=='soft-rise' else 'X';span=480 if axis=='Y' else 270
            expr=f'255*min(clip((T/.30*{span+18}-{axis})/18,0,1),clip((({d}-T)/.23*{span+18}-{axis})/18,0,1))'
            graph.extend([f'[{idx}:v]fps=30,scale=1080:1920:flags=lanczos,setsar=1,format=rgb24[raw{i}]',f"color=white:s=270x480:r=30:d={d},format=gray,geq=lum='{expr}',scale=1080:1920[mask{i}]",f'[raw{i}][mask{i}]alphamerge,setpts=PTS-STARTPTS+{slot["timeline_in"]}/TB[b{i}]'])
        else:graph.append(f'[{idx}:v]fps=30,scale=1080:1920:flags=lanczos,setsar=1,format=rgba,fade=t=in:st=0:d={7/30}:alpha=1,fade=t=out:st={d-7/30}:d={7/30}:alpha=1,setpts=PTS-STARTPTS+{slot["timeline_in"]}/TB[b{i}]')
        graph.append(f'[{current}][b{i}]overlay=0:0:eof_action=pass:enable=between(t\\,{slot["timeline_in"]}\\,{slot["timeline_out"]})[p{i}]');current=f'p{i}'
    li=len(plan['broll_slots'])+2;gi=li+1;ci=li+2
    args+=['-i',logo,'-i',gradient,'-i',caption]
    mark=style['logo']
    graph += [f'[{current}]null[shade]' if style.get('gradient_before_broll') else f'[{current}][{gi}:v]overlay=0:0[shade]',f'[{li}:v]scale={mark["width"]}:-1:flags=lanczos,format=rgba[logo]']
    if mark.get('halo'):
        graph+=['[logo]split=2[ink][halo]','[halo]lutrgb=r=255:g=255:b=255,gblur=sigma=1.1[whitehalo]',f'[shade][whitehalo]overlay={mark["x"]}:{mark["y"]}[under]',f'[under][ink]overlay={mark["x"]}:{mark["y"]}[brand]']
    else:graph.append(f'[shade][logo]overlay={mark["x"]}:{mark["y"]}[brand]')
    graph.append(f'[brand][{ci}:v]overlay=0:1100,format=yuv420p[out]')
    (path.parent/'filtergraph.txt').write_text(';\n'.join(graph)+'\n')
    partial=output.with_name(output.stem+'.partial.mp4');output.parent.mkdir(parents=True,exist_ok=True)
    args+=['-filter_complex_threads','1','-filter_complex',';'.join(graph),'-map','[out]','-map','1:a:0','-frames:v',round(plan['duration_seconds']*30),'-t',plan['duration_seconds'],'-c:v','libx264','-preset','fast','-crf','18','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',partial]
    clinic.run(args);partial.replace(output)
    clinic.save(record,{'signature':signature,'plan':str(path),'sha256':sha(output),'picture_sha256':sha(picture),'enhanced_audio':str(voice),'mixed_audio':str(audio),'logo_sha256':sha(logo),'status':'FINISHED_REVIEW / full encoded QA required'})
    print('Rendered',output,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('plan',type=Path);args=parser.parse_args();finish(args.plan.resolve())
