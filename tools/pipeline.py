#!/usr/bin/env python3
"""Single entry point to brand-specific local reel workflows."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CLINIC=ROOT/'workspaces/my-dental-skin-clinic'

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('brand',choices=['clinic','atfro','niolearn','jetkids'])
 p.add_argument('command',choices=['status','doctor','intake','analyse','transcribe','preflight','render','assets','references','matte','qa','colour','music'])
 p.add_argument('arguments',nargs=argparse.REMAINDER)
 a=p.parse_args()
 if a.brand=='jetkids':
  manifest=ROOT/'.cache/jetkids/inventory.json'
  converted=ROOT/'media/colour/jetkids-rec709'
  if a.command=='status':
   print('Jet Kids source inventory:',manifest if manifest.exists() else 'not registered')
   state=converted/'conversion-state.json'
   if state.exists():
    files=json.loads(state.read_text())['files'];print('Verified Log conversions:',sum(v['status']=='verified' for v in files.values()))
    print('Unchanged Sony display-referred clips:',sum(v['status']=='unchanged' for v in files.values()))
    print('Other profiles retained without Log LUT:',sum(v['status']=='unclassified' for v in files.values()))
   review=ROOT/'.cache/jetkids/analysis/review-index.json'
   if review.exists():print('Contact sheets generated:',len(json.loads(review.read_text())['clips']))
   notes=ROOT/'workspaces/jetkids/clip-review.json'
   if notes.exists():print('Visual clip notes:',len(json.loads(notes.read_text())['clips']))
   brief=ROOT/'workspaces/jetkids/review-status.json'
   if brief.exists():
    current=json.loads(brief.read_text())
    print('Latest recorded stage:',current.get('stage','not recorded'))
    print('Current brief:',current.get('latest_user_direction','not recorded'))
    if current.get('restart'):
     restart=current['restart']
     print('Sidhant-0 recorded snapshot:',restart.get('new_entries',0),'entries;',restart.get('with_video_stream',0),'with video streams')
     print('Review scope:',restart.get('scope','not recorded'))
     print('Mapping workbook:',restart.get('mapping_workbook','not generated'))
   else:print('Current brief: see workspaces/jetkids/AGENTS.md')
   return 0
  if a.command=='doctor': return subprocess.call([sys.executable,str(ROOT/'tools/doctor.py')],cwd=ROOT)
  if a.command=='intake':
   if not a.arguments:p.error('Supply the original footage folder')
   args=[sys.executable,str(ROOT/'tools/log_colour.py'),'inventory',a.arguments[0],'--out',str(manifest)]
  elif a.command=='colour':
   args=[sys.executable,str(ROOT/'tools/log_colour.py'),'convert',str(manifest),'--output',str(converted),*a.arguments]
  elif a.command=='analyse':
   args=[sys.executable,str(ROOT/'tools/event_review.py'),str(manifest),'--conversions',str(converted),'--out',str(ROOT/'.cache/jetkids/analysis'),*a.arguments]
  elif a.command=='music':
   return subprocess.call([sys.executable,str(ROOT/'tools/music_assets.py'),*a.arguments],cwd=ROOT)
  elif a.command in ('preflight','render'):
   if not a.arguments:p.error('Supply the reviewed event-plan JSON')
   target=Path(a.arguments[0])
   candidate=target/'edit-plan.json' if target.is_dir() else target
   interview=candidate.is_file() and json.loads(candidate.read_text()).get('kind')=='jetkids-interview'
   if interview:
    args=[sys.executable,str(ROOT/'tools/interview_edit.py'),str(candidate.parent),*a.arguments[1:]]
   else:
    args=[sys.executable,str(ROOT/'tools/event_render.py'),*a.arguments]
   if a.command=='preflight':args.append('--preflight')
  elif a.command=='assets':
   return subprocess.call([sys.executable,str(ROOT/'tools/reelctl.py'),'assets','--brand','jetkids',*a.arguments],cwd=ROOT)
  else:p.error('Jet Kids supports intake, colour, analyse, music, status, doctor, assets and reviewed event-plan preflight/render.')
  return subprocess.call(args,cwd=ROOT)
 if a.command=='colour':p.error('Use jetkids colour or tools/log_colour.py for metadata-gated colour conversion')
 if a.brand!='clinic':
  cmds={'intake':'init','analyse':'inspect'}
  command=cmds.get(a.command,a.command)
  if command not in ('doctor','init','preflight','render','assets'):
   p.error('Use tools/reelctl.py for this brand; see docs/EDITING_PIPELINE.md')
  args=[sys.executable,str(ROOT/'tools/reelctl.py'),command,*a.arguments]
  return subprocess.call(args,cwd=ROOT)
 py=CLINIC/'.venv/bin/python'
 if a.command=='status':
  for brief in sorted((CLINIC/'03_reels').glob('*/brief.md')):
   lines=brief.read_text().splitlines();status=next((s for s in lines if s.startswith('Latest status:')),'See brief')
   print(brief.parent.name+': '+status)
  return 0
 if not py.exists():p.error('Clinic runtime missing: run bash workspaces/my-dental-skin-clinic/tools/bootstrap.sh')
 if a.command in ('references','matte','qa'):
  script={'references':'study_references.py','matte':'subject_layers.py','qa':'qa_clinic_reel.py'}[a.command]
  args=[str(py),str(CLINIC/'tools'/script),*a.arguments]
 elif a.command in ('preflight','render'):
  if not a.arguments:p.error('Supply an edit-plan JSON path')
  args=[str(py),str(CLINIC/'tools/render_clinic_reel.py'),*a.arguments]
  if a.command=='preflight':args.append('--preflight')
 elif a.command=='assets':
  return subprocess.call([sys.executable,str(ROOT/'tools/reelctl.py'),'assets','--brand','clinic',*a.arguments],cwd=ROOT)
 else:
  cmd={'intake':'ingest'}.get(a.command,a.command)
  args=[str(py),str(CLINIC/'tools/clinic.py'),cmd,*a.arguments]
 return subprocess.call(args,cwd=ROOT)

if __name__=='__main__':raise SystemExit(main())
