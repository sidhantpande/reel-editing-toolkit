#!/usr/bin/env python3
"""Serial source-handle transitions that preserve planned cut frames and total duration."""
from pathlib import Path
import subprocess
from log_colour import probe
FPS=30
EFFECTS={'fade','fadeslow','smoothleft','smoothright','hblur','zoomin'}

def transition(shot):
    value=shot.get('transitionIn',{'kind':'cut','frames':0})
    kind,frames=value.get('kind'),value.get('frames')
    if kind=='cut' and frames==0:return kind,0
    if kind not in EFFECTS or isinstance(frames,bool) or not isinstance(frames,int) or not 2<=frames<=15:raise ValueError('Unsupported transition or frame count')
    if frames>=shot['frames']:raise ValueError('Transition must fit inside incoming shot')
    return kind,frames

def run(args):subprocess.run(args,check=True)

def encode(args,output,frames,complex_filter=None):
    command=['ffmpeg','-v','error','-nostdin','-n','-threads','2','-filter_complex_threads','2',*args]
    if complex_filter is not None:command+=['-filter_complex',complex_filter,'-map','[v]']
    command+=['-an','-frames:v',str(frames),'-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv',str(output)]
    run(command)
    v=next(s for s in probe(output)['streams'] if s['codec_type']=='video')
    if int(v['nb_frames'])!=frames:raise ValueError('Transition/core frame count mismatch')

def assemble(segments,shots,cache):
    cache=Path(cache);pieces=[]
    for i,(segment,shot) in enumerate(zip(segments,shots)):
        kind,fade=transition(shot)
        if i and fade:
            previous=shots[i-1];seam=cache/f'seam-{i:03d}.mp4'
            if not seam.exists():
                filters=f"[0:v]trim=start_frame={previous['frames']}:end_frame={previous['frames']+fade},settb=1/30,setpts=N,fps=30,format=yuv444p[a];[1:v]trim=end_frame={fade},settb=1/30,setpts=N,fps=30,format=yuv444p[b];[a][b]xfade=transition={kind}:duration={fade/FPS:.9f}:offset=0,format=yuv420p[v]"
                encode(['-i',str(segments[i-1]),'-i',str(segment)],seam,fade,filters)
            pieces.append(seam)
        first=fade if i else 0;core_frames=shot['frames']-first
        next_fade=transition(shots[i+1])[1] if i+1<len(shots) else 0
        if not first and not next_fade:pieces.append(segment);continue
        core=cache/f'core-{i:03d}.mp4'
        if not core.exists():encode(['-i',str(segment),'-vf',f"trim=start_frame={first}:end_frame={shot['frames']},setpts=PTS-STARTPTS"],core,core_frames)
        pieces.append(core)
    return pieces
