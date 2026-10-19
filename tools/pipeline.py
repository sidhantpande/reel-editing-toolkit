#!/usr/bin/env python3
"""Single entry point to brand-specific local reel workflows."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CLINIC=ROOT/'workspaces/my-dental-skin-clinic'

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('brand',choices=['clinic','atfro','niolearn'])
 p.add_argument('command',choices=['status','doctor','intake','analyse','transcribe','preflight','render','assets','references','matte','qa'])
 p.add_argument('arguments',nargs=argparse.REMAINDER)
 a=p.parse_args()
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
