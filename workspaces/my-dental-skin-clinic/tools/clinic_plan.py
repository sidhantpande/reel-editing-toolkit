"""Portable, dependency-free clinic timeline gate."""
from pathlib import Path

def validate_plan(plan,allow_pending=False,root=None):
 errors=[];cursor=0;source_ids=set()
 for i,s in enumerate(plan.get('segments',[])):
  source_ids.add(s['source_id'])
  duration=s['timeline_out']-s['timeline_in'];n=round(duration*30)
  if abs(s['timeline_in']-cursor)>1/3000:errors.append(f'Non-contiguous segment {i}')
  if abs(duration-n/30)>1/3000:errors.append(f'Segment {i} is not frame aligned')
  if n<7:errors.append(f'Segment {i} too short for handles')
  if abs((s['source_out']-s['source_in'])-n/30)>1/3000:errors.append(f'Source/timeline duration mismatch {i}')
  if s['source_in']<0 or not Path(s['source']).is_file():errors.append(f'Missing/invalid source {i}')
  c=s['crop_xywh']
  if min(c['x'],c['y'])<0 or min(c['width'],c['height'])<=0:errors.append(f'Invalid crop {i}')
  if s.get('source_duration') and s['source_out']>s['source_duration']+.001:errors.append(f'Segment {i} exceeds source duration')
  for cue in plan.get('cue_exclusions',[]):
   if cue['source']==s['source_id'] and min(s['source_out'],cue['out'])>max(s['source_in'],cue['in'])+.001:errors.append(f'Recording cue retained in segment {i}')
  cursor=s['timeline_out']
 if not plan.get('segments') or abs(cursor-plan['duration_seconds'])>1/3000:errors.append('Wrong total duration')
 last=-1
 for w in plan.get('words',[]):
  if not 0<=w['start']<w['end']<=cursor+.001:errors.append('Word outside timeline: '+w['text'])
  if w['start']<last-.001:errors.append('Words not in speech order: '+w['text'])
  if w.get('source_id') not in source_ids:errors.append('Unknown word source: '+w['text'])
  last=w['start']
 for slot in plan.get('broll_slots',[]):
  if not 0<=slot['timeline_in']<slot['timeline_out']<=cursor+.001:errors.append('B-roll outside timeline')
  if not Path(slot.get('path','')).is_file() and not allow_pending:errors.append('B-roll not delivered: '+slot['id'])
 if root and not (Path(root)/'styles/clinic-approved.json').is_file():errors.append('Missing approved style')
 if errors:raise ValueError('Preflight failed: '+'; '.join(errors))
 return {'segments':len(plan['segments']),'words':len(plan.get('words',[])),'duration_seconds':cursor,'broll_slots':len(plan.get('broll_slots',[])),'pending_allowed':allow_pending}
