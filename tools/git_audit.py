#!/usr/bin/env python3
"""Audit tracked/candidate files, local-media exclusions and clinic LFS assets."""
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
r=subprocess.run(['git','ls-files','-c','-o','--exclude-standard','-z'],cwd=R,capture_output=True,check=True)
files=set(x.decode() for x in r.stdout.split(b'\0') if x);bad=[];total=0
clinic='workspaces/my-dental-skin-clinic/'
for name in files:
 p=R/name;parts=Path(name).parts
 if name.startswith(('media/','public/raw/','public/reference/','public/proxies/','exports/','deliverables/','Final Content/')) or any(s in parts for s in ('.cache','node_modules','.venv','__pycache__')):bad.append('Local/generated path: '+name)
 if name.startswith(clinic):
  relative=name[len(clinic):]
  if relative.startswith(('02_analysis/','05_exports/','04_generated_broll/incoming/','previews/')):bad.append('Clinic local media path: '+name)
  if p.suffix.lower() in ('.mp4','.mov','.wav') and not (relative.startswith('04_generated_broll/approved/') or relative=='assets/brand/endcards/my-dental-reference-outro.mp4'):bad.append('Non-asset clinic media: '+name)
  if p.is_symlink():bad.append('Machine-specific clinic symlink: '+name)
 if not p.is_file():continue
 total+=p.stat().st_size
 if p.stat().st_size>95*2**20:bad.append('Large unconfigured Git candidate: '+name)
manifest=R/clinic/'04_generated_broll/manifest.json'
if manifest.exists():
 for asset in json.loads(manifest.read_text())['assets']:
  path=R/clinic/asset['path'];relative=str(path.relative_to(R))
  if not path.is_file():bad.append('Missing approved clinic asset: '+relative);continue
  if hashlib.sha256(path.read_bytes()).hexdigest()!=asset['sha256']:bad.append('Clinic asset checksum mismatch: '+relative)
  attr=subprocess.check_output(['git','check-attr','filter','--',relative],cwd=R,text=True).strip()
  if not attr.endswith(': lfs'):bad.append('Clinic asset lacks Git LFS: '+relative)
endcard_manifest=R/clinic/'assets/brand/endcards/manifest.json'
if endcard_manifest.is_file():
 asset=json.loads(endcard_manifest.read_text());path=R/clinic/asset['path']
 if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=asset['sha256']:bad.append('End-card checksum mismatch')
 attr=subprocess.check_output(['git','check-attr','filter','--',str(path.relative_to(R))],cwd=R,text=True).strip()
 if not attr.endswith(': lfs'):bad.append('End-card lacks Git LFS')
jetkids=R/'catalog/jetkids-assets.json'
if jetkids.is_file():
 for asset in json.loads(jetkids.read_text()):
  path=R/asset['repositoryFile']
  if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=asset['sha256']:bad.append('Jet Kids asset checksum mismatch')
  attr=subprocess.check_output(['git','check-attr','filter','--',asset['repositoryFile']],cwd=R,text=True).strip()
  if not attr.endswith(': lfs'):bad.append('Jet Kids brand asset lacks Git LFS')
transition_manifest=R/'catalog/event-transitions.json'
if transition_manifest.is_file():
 for asset in json.loads(transition_manifest.read_text())['downloaded_sources']:
  path=R/asset['file']
  if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=asset['sha256']:bad.append('Transition source checksum mismatch: '+asset['file'])
 if not (R/'vendor/gl-transitions/LICENSE').is_file():bad.append('Missing transition source licence')
print(f'Git candidates: {len(files)} files, {total/2**20:.1f} MiB before LFS')
if bad:print('\n'.join(bad));sys.exit(1)
print('OK: approved clinic assets match checksums/LFS; no raw/reference/export/cache/environment files among Git candidates.')
