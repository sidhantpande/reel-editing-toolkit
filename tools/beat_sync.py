#!/usr/bin/env python3
"""Suggest bounded beat snaps and calculate source action placement on30fps timelines."""
import argparse,json,math
from pathlib import Path

def snap(frame,candidates,radius=4):
    if not isinstance(frame,int) or radius<0:raise ValueError('Whole target frame and nonnegative radius required')
    if not candidates:return frame
    nearest=min(candidates,key=lambda candidate:abs(candidate-frame))
    return nearest if abs(nearest-frame)<=radius else frame

def action_in(source_action_seconds,shot_start_frame,target_action_frame,speed=1):
    if not all(math.isfinite(x) for x in (source_action_seconds,shot_start_frame,target_action_frame,speed)) or speed<=0:raise ValueError('Finite times and positive speed required')
    start=source_action_seconds-(target_action_frame-shot_start_frame)/30*speed
    if start<0:raise ValueError('Action placement would start before source')
    return start

def audit(plan,beat_data):
    boundaries=[];frame=0
    for shot in plan['shots']:
        if shot.get('timeline_start_frame',frame)!=frame:raise ValueError('Stored shot start disagrees with cumulative frames')
        boundaries.append(frame);frame+=shot['frames']
    boundaries.append(frame)
    result=[]
    for marker in beat_data['user_structure_markers']:
        target=marker['timeline_frame'];nearest=min(boundaries,key=lambda f:abs(f-target))
        result.append({'label':marker['label'],'target_frame':target,'nearest_boundary_frame':nearest,'difference_frames':nearest-target,'musical_verification':marker['status']})
    return {'planned_body_frames':frame,'total_frames':frame+plan['logoFrames'],'structure_alignment':result,'note':'Alignment to user cues is measured; automatic beat/lyric correctness is not listening-certified.'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan');p.add_argument('beats');a=p.parse_args();print(json.dumps(audit(json.loads(Path(a.plan).read_text()),json.loads(Path(a.beats).read_text())),indent=2))
