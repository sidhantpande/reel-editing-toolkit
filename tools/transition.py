#!/usr/bin/env python3
"""Apply any installed FFmpeg xfade transition to two clips, with audio crossfade."""
import argparse,subprocess,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('first');p.add_argument('second');p.add_argument('output');p.add_argument('--effect',default='fade');p.add_argument('--duration',type=float,default=.35);a=p.parse_args()
helptext=subprocess.check_output(['ffmpeg','-hide_banner','-h','filter=xfade'],stderr=subprocess.STDOUT,text=True)
effects=re.findall(r'^\s+(\w+)\s+\d+\s+\.\.FV',helptext,re.M)
if a.effect not in effects:p.error('Unknown transition. Options: '+', '.join(effects))
def probe(f):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',f]))
x,y=probe(a.first),probe(a.second);length=float(x['format']['duration']);d=a.duration
if d<=0 or d>=min(length,float(y['format']['duration'])):p.error('Transition must be shorter than both clips.')
normalize='scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS'
filters=[f'[0:v]{normalize}[v0]',f'[1:v]{normalize}[v1]',f'[v0][v1]xfade=transition={a.effect}:duration={d}:offset={length-d}[v]']
has_audio=all(any(s['codec_type']=='audio' for s in z['streams']) for z in [x,y])
if has_audio:filters+=['[0:a]aresample=48000,asetpts=PTS-STARTPTS[a0]','[1:a]aresample=48000,asetpts=PTS-STARTPTS[a1]',f'[a0][a1]acrossfade=d={d}[a]']
Path(a.output).parent.mkdir(parents=True,exist_ok=True)
cmd=['ffmpeg','-hide_banner','-i',a.first,'-i',a.second,'-filter_complex',';'.join(filters),'-map','[v]']
if has_audio:cmd+=['-map','[a]','-c:a','aac']
cmd+=['-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',a.output]
subprocess.run(cmd,check=True)
