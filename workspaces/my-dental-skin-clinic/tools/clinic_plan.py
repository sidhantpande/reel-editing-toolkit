"""Portable, dependency-free clinic timeline gate."""
from pathlib import Path
import hashlib,json,subprocess

def validate_plan(plan,allow_pending=False,root=None):
 errors=[];cursor=0;source_ids=set();checked_hashes={}
 for i,s in enumerate(plan.get('segments',[])):
  source_ids.add(s['source_id'])
  duration=s['timeline_out']-s['timeline_in'];n=round(duration*30)
  if abs(s['timeline_in']-cursor)>1/3000:errors.append(f'Non-contiguous segment {i}')
  if abs(duration-n/30)>1/3000:errors.append(f'Segment {i} is not frame aligned')
  if n<7:errors.append(f'Segment {i} too short for handles')
  if abs((s['source_out']-s['source_in'])-n/30)>1/3000:errors.append(f'Source/timeline duration mismatch {i}')
  if s['source_in']<0 or not Path(s['source']).is_file():errors.append(f'Missing/invalid source {i}')
  if s.get('source_sha256') and Path(s['source']).is_file():
   if s['source'] not in checked_hashes:
    with Path(s['source']).open('rb') as stream:checked_hashes[s['source']]=hashlib.file_digest(stream,'sha256').hexdigest()
   if checked_hashes[s['source']]!=s['source_sha256']:errors.append(f'Source changed after intake: {i}')
  c=s['crop_xywh']
  if min(c['x'],c['y'])<0 or min(c['width'],c['height'])<=0:errors.append(f'Invalid crop {i}')
  if s.get('source_duration') and s['source_out']>s['source_duration']+.001:errors.append(f'Segment {i} exceeds source duration')
  for cue in plan.get('cue_exclusions',[]):
   if cue['source']==s['source_id'] and min(s['source_out'],cue['out'])>max(s['source_in'],cue['in'])+.001:errors.append(f'Recording cue retained in segment {i}')
  cursor=s['timeline_out']
 if not plan.get('segments') or abs(cursor-plan['duration_seconds'])>1/3000:errors.append('Wrong total duration')
 last=-1;previous=None
 for w in plan.get('words',[]):
  if not 0<=w['start']<w['end']<=cursor+.001:errors.append('Word outside timeline: '+w['text'])
  if w['start']<last-.001:errors.append('Words not in speech order: '+w['text'])
  if w.get('source_id') not in source_ids:errors.append('Unknown word source: '+w['text'])
  if previous and w.get('source_id')==previous.get('source_id') and w['text'].casefold()==previous['text'].casefold() and w['start']<previous['end']-.025:
   errors.append('Overlapping duplicate ASR word: '+w['text'])
  last=w['start']
  previous=w
 for slot in plan.get('broll_slots',[]):
  if not 0<=slot['timeline_in']<slot['timeline_out']<=cursor+.001:errors.append('B-roll outside timeline')
  if not Path(slot.get('path','')).is_file() and not allow_pending:errors.append('B-roll not delivered: '+slot['id'])
 for slot in plan.get('graphic_slots',[]):
  if not 0<=slot['timeline_in']<slot['timeline_out']<=cursor+.001:errors.append('Graphic outside timeline: '+slot['id'])
  if not any(s['timeline_in']<=slot['timeline_in']+.001 and s['timeline_out']>=slot['timeline_out']-.001 for s in plan.get('segments',[])):
   errors.append('Graphic crosses a cut; split into shot-local slots: '+slot['id'])
  if not Path(slot.get('path','')).is_file() and not allow_pending:errors.append('Graphic not delivered: '+slot['id'])
  if min(slot.get('x',-1),slot.get('y',-1))<0 or slot.get('width',0)<=0:errors.append('Invalid graphic placement: '+slot['id'])
  if not allow_pending and not slot.get('visual_reviewed'):errors.append('Graphic needs visual review: '+slot['id'])
  for b in plan.get('broll_slots',[]):
   if min(slot['timeline_out'],b['timeline_out'])>max(slot['timeline_in'],b['timeline_in']):errors.append('Graphic overlaps full-frame B-roll: '+slot['id'])
 if root:
  style_path=Path(root)/plan.get('style','styles/clinic-approved.json')
  if not style_path.is_file():errors.append('Missing caption style: '+str(style_path))
  if not allow_pending:
   config=json.loads((Path(root)/'project.json').read_text())
   for slot in plan.get('broll_slots',[]):
    if not Path(slot.get('path','')).is_file():continue
    result=subprocess.run([config['ffprobe'],'-v','error','-show_streams','-of','json',slot['path']],capture_output=True,text=True)
    if result.returncode:errors.append('Cannot decode B-roll: '+slot['id']);continue
    video=next((s for s in json.loads(result.stdout).get('streams',[]) if s.get('codec_type')=='video'),None)
    if video is None:errors.append('No video in B-roll: '+slot['id']);continue
    required=slot.get('media_in',0)+slot['timeline_out']-slot['timeline_in']
    if float(video.get('duration',0))+.001<required:errors.append('B-roll too short for selected range: '+slot['id'])
 if root and not (Path(root)/'styles/clinic-approved.json').is_file():errors.append('Missing approved style')
 if errors:raise ValueError('Preflight failed: '+'; '.join(errors))
 return {'segments':len(plan['segments']),'words':len(plan.get('words',[])),'duration_seconds':cursor,'broll_slots':len(plan.get('broll_slots',[])),'pending_allowed':allow_pending}
