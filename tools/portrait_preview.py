#!/usr/bin/env python3
"""Make a shot-framed9:16 companion from reviewed landscape source segments."""
import argparse,json,re,subprocess
from pathlib import Path
from log_colour import ROOT,digest,probe,write
from event_transitions import assemble

def filter_for(layout,frames):
    mode=layout['mode']
    if mode=='fit-video':
        width=layout.get('window_width',1920);centre=layout.get('center_x',960)
        if not isinstance(width,int) or not 608<=width<=1920 or not width/2<=centre<=1920-width/2:raise ValueError('Fit window outside native video')
        height=round((1080*1080/width)/2)*2
        return f'[0:v]split[bg][fg];[bg]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,gblur=sigma=12,eq=brightness=-0.20,scale=1080:1920[back];[fg]crop={width}:1080:{centre-width/2}:0,scale=1080:{height}[front];[back][front]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p[v]'
    if mode!='crop':raise ValueError('Portrait mode must be crop or fit-video')
    a=layout['center_x'];b=layout.get('end_center_x',a)
    if not all(isinstance(x,(int,float)) and 304<=x<=1616 for x in (a,b)):raise ValueError('Portrait subject centre outside native source')
    expr=f'clip({a-304}+({b-a})*n/{max(1,frames-1)},0,1312)'
    return f"[0:v]crop=608:1080:x='{expr}':y=0,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p[v]"

def run(args):subprocess.run(args,check=True)

def render(plan_path,layout_path,landscape_video,output):
    plan=json.loads(Path(plan_path).read_text());layout=json.loads(Path(layout_path).read_text())
    if not re.fullmatch('jetkids-[a-z0-9-]+',layout['id']):raise ValueError('Safe preview ID required')
    if len(plan['shots'])!=len(layout['shots']):raise ValueError('Each shot needs explicit portrait framing')
    original_cache=ROOT/'.cache/jetkids/renders'/plan['id'];cached_plan=json.loads((original_cache/'render-plan.json').read_text())
    if cached_plan!=plan:raise ValueError('Landscape segment cache does not match plan')
    cache=ROOT/'.cache/jetkids/renders'/layout['id'];cache.mkdir(parents=True,exist_ok=True)
    if (cache/'layout.json').exists() and json.loads((cache/'layout.json').read_text())!=layout:raise ValueError('Use a new preview ID for changed framing')
    write(cache/'layout.json',layout);output=Path(output).resolve()
    if output.exists():raise ValueError('Versioned output already exists')
    segments=[];hashes=[]
    for i,(shot,framing) in enumerate(zip(plan['shots'],layout['shots'])):
        source=original_cache/f'{i:03d}.mp4';target=cache/f'{i:03d}.mp4';count=int(next(s for s in probe(source)['streams'] if s['codec_type']=='video')['nb_frames']);hashes.append({'segment':str(source.relative_to(ROOT)),'sha256':digest(source)})
        if not target.exists():run(['ffmpeg','-v','error','-nostdin','-n','-threads','2','-filter_complex_threads','2','-i',str(source),'-filter_complex',filter_for(framing,count),'-map','[v]','-an','-frames:v',str(count),'-c:v','libx264','-preset','fast','-crf','18','-threads','2','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv',str(target)])
        segments.append(target)
    pieces=assemble(segments,plan['shots'],cache);ending=cache/'ending.mp4'
    if not ending.exists():run(['ffmpeg','-v','error','-nostdin','-n','-loop','1','-i',str(ROOT/plan['logo']),'-an','-vf','scale=820:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fade=t=in:st=0:d=0.25,format=yuv420p','-r','30','-frames:v',str(plan['logoFrames']),'-c:v','libx264','-preset','fast','-crf','18','-threads','2',str(ending)])
    pieces.append(ending);concat=cache/'concat.txt';concat.write_text(''.join("file '"+str(p).replace("'","'\\''")+"'\n" for p in pieces))
    total=sum(s['frames'] for s in plan['shots'])+plan['logoFrames'];silent=cache/'silent-edit.mp4'
    if not silent.exists():run(['ffmpeg','-v','error','-nostdin','-n','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(silent)])
    output.parent.mkdir(parents=True,exist_ok=True)
    run(['ffmpeg','-v','error','-nostdin','-n','-i',str(silent),'-i',str(landscape_video),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(output)])
    v=next(s for s in probe(output)['streams'] if s['codec_type']=='video')
    if (v['width'],v['height'],int(v['nb_frames']))!=(1080,1920,total):raise ValueError('Portrait dimensions/frame total mismatch')
    run(['ffmpeg','-v','error','-xerror','-nostdin','-threads','2','-i',str(output),'-f','null','-'])
    def audio_hash(path):return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-f','hash','-hash','sha256','-'])
    if audio_hash(output)!=audio_hash(landscape_video):raise ValueError('Companion audio changed')
    write(cache/'qa.json',{'output':str(output),'sha256':digest(output),'frames':total,'duration':total/30,'width':1080,'height':1920,'full_decode':'passed','audio':'Same encoded AAC / decoded PCM hash as landscape companion','source_segment_hashes':hashes,'layout':str(layout_path),'visual_review':'pending portrait contacts','delivery':'portrait comparison preview','limits':'Native1080 landscape crop is upscaled. Group fit-video shots retain full moving picture over blurred moving background. No event-photo inserts.'})
    print(output)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan');p.add_argument('layout');p.add_argument('--landscape',required=True);p.add_argument('--output',required=True);a=p.parse_args();render(a.plan,a.layout,a.landscape,a.output)
