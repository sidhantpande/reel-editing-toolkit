#!/usr/bin/env python3
"""Preflight and render video-only Jet Kids landscape review edits from explicit shot plans."""
import argparse
import json
import math
import re
import subprocess
from fractions import Fraction
from pathlib import Path
from log_colour import ROOT, classify, digest, probe, write

from event_transitions import transition, assemble

FPS=30

def check_plan(plan, inventory, state):
    if not re.fullmatch(r'jetkids-[a-z0-9-]+', plan.get('id','')):raise ValueError('Use a safe versioned Jet Kids plan ID')
    if (plan.get('width'),plan.get('height'),plan.get('fps')) != (1920,1080,FPS):
        raise ValueError('Jet Kids delivery must be 1920x1080 at 30fps')
    if plan.get('eventPhotoInserts') is not False: raise ValueError('Event photo inserts are prohibited by current user direction')
    sources={r['relative']:r for r in inventory['videos']};resolved=[]
    if not plan.get('shots'):raise ValueError('An edit needs reviewed video shots')
    for index,shot in enumerate(plan['shots']):
        _,incoming=transition(shot)
        if index==0 and incoming:raise ValueError('First shot cannot transition from missing footage')
        outgoing=transition(plan['shots'][index+1])[1] if index+1<len(plan['shots']) else 0
        if shot['source'] not in sources:raise ValueError('Unknown source video')
        r=sources[shot['source']];profile=classify(r['camera']);media=Path(r['path'])
        if media.suffix.lower() not in ('.mp4','.mov','.mxf','.m4v'):raise ValueError('Video sources only')
        if profile=='sony-slog3-sgamut3cine':
            converted=state['files'].get(r['relative'],{})
            if converted.get('status')!='verified':raise ValueError('Log source is not colour-verified')
            media=Path(converted['path'])
        frames=shot['frames'];speed=shot.get('speed',1.0);start=shot['in']
        if isinstance(frames,bool) or not isinstance(frames,int) or frames<=0:raise ValueError('Positive whole edit frames required')
        if not all(isinstance(x,(float,int)) and math.isfinite(x) for x in (speed,start)):raise ValueError('Finite timing values required')
        if not .25<=speed<=1.2 or start<0:raise ValueError('Invalid source speed/start')
        end=start+(frames+outgoing)/FPS*speed
        if end>r['duration']+.001:raise ValueError(f'Shot exceeds source: {r["relative"]}')
        if speed<1 and float(Fraction(r['video']['avg_frame_rate']))*speed<FPS-.1:raise ValueError('Slow motion would require duplicated/interpolated frames')
        if any(abs(s.get('rotation',0))==90 for s in r['video'].get('side_data_list',[])):raise ValueError('Portrait-only source needs an explicit layout; choose landscape coverage')
        if not media.is_file():raise ValueError('Missing media')
        if digest(Path(r['path']))!=r['sha256']:raise ValueError('Original checksum changed')
        if not shot.get('review_note'):raise ValueError('Every shot needs an evidence-based review note')
        for key in ('gamma','contrast','saturation'):
            value=shot.get(key,1.0)
            if not math.isfinite(value) or not .8<=value<=1.2:raise ValueError('Grade adjustment outside restrained review range')
        resolved.append({**shot,'path':str(media),'source_sha256':r['sha256'],'renderFrames':frames+outgoing})
    logo=ROOT/plan['logo'];audio=ROOT/plan['audio']['source']
    if not logo.is_file() or not audio.is_file():raise ValueError('Missing logo/reference audio')
    body_frames=sum(s['frames'] for s in resolved);logo_frames=plan.get('logoFrames',60)
    if not isinstance(logo_frames,int) or not 30<=logo_frames<=90:raise ValueError('Logo ending must be 1–3 seconds')
    total_frames=body_frames+logo_frames;audio_in=plan['audio'].get('in',0)
    audio_info=probe(audio);streams=[s for s in audio_info['streams'] if s['codec_type']=='audio']
    if not streams:raise ValueError('Reference has no audio')
    if audio_in<0 or audio_in+total_frames/FPS>float(streams[0].get('duration',audio_info['format']['duration']))+.01:raise ValueError('Selected reference audio is too short')
    return {'shots':resolved,'bodyFrames':body_frames,'totalFrames':total_frames,'duration':total_frames/FPS,'logo':str(logo),'audio':str(audio),'audioIn':audio_in,'status':'preflight passed; final encoded visual/audio review still required'}

def run(args):subprocess.run(args,check=True)

def render(plan_path, output, inventory_path, state_path, preflight=False):
    plan=json.loads(Path(plan_path).read_text());inventory=json.loads(Path(inventory_path).read_text());state=json.loads(Path(state_path).read_text());checked=check_plan(plan,inventory,state)
    if preflight:print(json.dumps(checked,indent=2));return
    output=Path(output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():raise ValueError('Versioned export already exists; choose a new filename')
    cache=ROOT/'.cache/jetkids/renders'/plan['id'];cache.mkdir(parents=True,exist_ok=True)
    if (cache/'render-plan.json').exists() and json.loads((cache/'render-plan.json').read_text())!=plan:raise ValueError('Cached plan differs; use a new versioned plan ID')
    write(cache/'render-plan.json',plan);segments=[]
    for i,shot in enumerate(checked['shots']):
        segment=cache/f'{i:03d}.mp4'
        if not segment.exists():
            source_seconds=shot['renderFrames']/FPS*shot.get('speed',1)
            vf=f"trim=duration={source_seconds:.9f},setpts=(PTS-STARTPTS)/{shot.get('speed',1)},fps={FPS},scale=1920:1080:flags=lanczos,setsar=1"
            if any(shot.get(k,1)!=1 for k in ('gamma','contrast','saturation')):vf+=f",eq=gamma={shot.get('gamma',1)}:contrast={shot.get('contrast',1)}:saturation={shot.get('saturation',1)}"
            if i==0:vf+=',fade=t=in:st=0:d=0.15'
            if i==len(checked['shots'])-1:vf+=f",fade=t=out:st={shot['frames']/FPS-.2}:d=0.2"
            vf+=',format=yuv420p'
            run(['ffmpeg','-v','error','-nostdin','-n','-threads','2','-filter_threads','2','-ss',str(shot['in']),'-i',shot['path'],'-an','-vf',vf,'-frames:v',str(shot['renderFrames']),'-c:v','libx264','-preset','fast','-crf','18','-threads','2','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv',str(segment)])
        actual=next(s for s in probe(segment)['streams'] if s['codec_type']=='video')
        if int(actual['nb_frames'])!=shot['renderFrames']:raise ValueError('Segment frame mismatch')
        segments.append(segment)
    ending=cache/'ending.mp4';end_frames=checked['totalFrames']-checked['bodyFrames']
    if not ending.exists():
        run(['ffmpeg','-v','error','-nostdin','-n','-loop','1','-i',checked['logo'],'-an','-vf','scale=730:-2,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fade=t=in:st=0:d=0.25,format=yuv420p','-r','30','-frames:v',str(end_frames),'-c:v','libx264','-preset','fast','-crf','18','-threads','2','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv',str(ending)])
    segments=assemble(segments,checked['shots'],cache)
    segments.append(ending);concat=cache/'concat.txt';concat.write_text(''.join("file '"+str(p).replace("'","'\\''")+"'\n" for p in segments))
    body=cache/'silent-edit.mp4'
    if not body.exists():run(['ffmpeg','-v','error','-nostdin','-n','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(body)])
    duration=checked['duration'];audio_raw=cache/'reference-trim.wav'
    if not audio_raw.exists():run(['ffmpeg','-v','error','-nostdin','-n','-ss',str(checked['audioIn']),'-i',checked['audio'],'-vn','-t',str(duration),'-af',f'afade=t=in:d=0.08,afade=t=out:st={duration-.7}:d=0.7','-ar','48000','-c:a','pcm_s24le',str(audio_raw)])
    measure=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-i',str(audio_raw),'-af','loudnorm=I=-14:TP=-1.2:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    measurements=json.loads(measure.stderr[measure.stderr.rfind('{'):]);write(cache/'loudness-pass1.json',measurements)
    norm=f"loudnorm=I=-14:TP=-1.2:LRA=11:measured_I={measurements['input_i']}:measured_TP={measurements['input_tp']}:measured_LRA={measurements['input_lra']}:measured_thresh={measurements['input_thresh']}:offset={measurements['target_offset']}:linear=true"
    run(['ffmpeg','-v','error','-nostdin','-n','-i',str(body),'-i',str(audio_raw),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af',norm,'-c:a','aac','-b:a','256k','-ar','48000','-t',str(duration),'-movflags','+faststart',str(output)])
    actual=probe(output);v=next(s for s in actual['streams'] if s['codec_type']=='video')
    if int(v['nb_frames'])!=checked['totalFrames'] or (v['width'],v['height'])!=(1920,1080):raise ValueError('Final frame/dimension mismatch')
    run(['ffmpeg','-v','error','-xerror','-nostdin','-threads','2','-i',str(output),'-f','null','-'])
    measurement=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-i',str(output),'-af','loudnorm=I=-14:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    final_loudness=json.loads(measurement.stderr[measurement.stderr.rfind('{'):])
    if float(final_loudness['input_tp'])>-.9:raise ValueError('Encoded true peak exceeds review limit')
    write(cache/'qa.json',{'output':str(output),'sha256':digest(output),'frames':checked['totalFrames'],'duration':duration,'full_decode':'passed','encoded_loudness':final_loudness,'source_plan':str(plan_path),'eventPhotoInserts':False,'visual_review':'pending encoded contact/boundary inspection','listening_review':'not attested; supplied reference mix reused','delivery':'review draft'})
    print(output)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan');p.add_argument('--output');p.add_argument('--inventory',default='.cache/jetkids/inventory.json');p.add_argument('--state',default='media/colour/jetkids-rec709/conversion-state.json');p.add_argument('--preflight',action='store_true');a=p.parse_args()
    if not a.preflight and not a.output:p.error('Supply a versioned --output')
    render(a.plan,a.output,a.inventory,a.state,a.preflight)
if __name__=='__main__':main()
