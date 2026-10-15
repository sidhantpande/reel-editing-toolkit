#!/usr/bin/env python3
"""Prepare an uncut assembly, preferring main takes over false starts."""
import argparse,json,subprocess,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('project_id');p.add_argument('--clip',type=int);a=p.parse_args()
folders=list((R/'projects').glob('*/'+a.project_id))
if len(folders)!=1:p.error('Unknown project ID')
folder=folders[0];plan=json.loads((folder/'edit-plan.json').read_text())
if not plan['sourceClips']:p.error('No matched source footage for this script')
if a.clip is not None:
 if a.clip<0 or a.clip>=len(plan['sourceClips']):p.error('Clip index outside project mapping')
 selected=[plan['sourceClips'][a.clip]]
else:
 takes=plan.get('takes',[]);main=[c['path'] for c in takes if c['role'].startswith('main')];parts=[c['path'] for c in takes if c['role'].startswith('part-')]
 selected=main[:1] or parts or plan['sourceClips'][:1]
clips=[];offset=0
for src in selected:
 f=R/src;dur=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-of','json',str(f)]))['format']['duration']);frames=math.ceil(dur*30)
 clips.append({'src':'raw/'+str(f.relative_to(R/'media/raw')),'from':offset,'duration':frames,'trimBefore':0,'volume':1});offset+=frames
props={'captionPreset':'clean' if plan['brand']=='atfro' else 'kinetic','brand':plan['brand'],'durationInFrames':offset+60,'clips':clips,'captions':[],'broll':[],'endCard':True,'music':'assets/music/calm-focus.wav','musicVolume':.12}
(folder/'reel.json').write_text(json.dumps(props,indent=2)+'\n');print(folder/'reel.json');print('Uncut assembly only; main/continuation takes selected. Review pickups, cuts and captions before final rendering.')
