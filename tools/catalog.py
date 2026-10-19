#!/usr/bin/env python3
"""Build text and JSON indexes for an AI editor; no dashboard required."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
families=[('School','src/projects/SchoolBroll.tsx','SchoolKind','atfro',240),('Compare','src/projects/ComparisonBroll.tsx','ComparisonKind','niolearn',600),('Project','src/projects/ProjectBroll.tsx','ProjectKind','niolearn',240),('Study','src/projects/StudyBroll.tsx','StudyKind','niolearn',180),('Nio07','src/projects/Nio07Broll.tsx','Nio07Kind','niolearn',180),('Nio04','src/projects/Nio04Broll.tsx','Nio04Kind','niolearn',180),('Atfro01','src/projects/Atfro01Broll.tsx','Atfro01Kind','atfro',180),('Premium','src/premium/PaperScene.tsx','PaperKind','shared',180)]
scenes=[]
for prefix,source,union,brand,duration in families:
 found=re.search(r'export type\s+'+union+r'\s*=\s*([^;]+);',(R/source).read_text())
 assert found,union
 for kind in re.findall(r"'([^']+)'",found.group(1)):
  scenes.append(dict(kind=kind,composition=prefix+'-'+kind,brand=brand,source=source,defaultDurationFrames=688 if kind=='nio-story-mock' else 239 if kind=='nio-story-profile' else duration,fps=30,width=1080,height=1920,transparentSupported=True,tags=kind.split('-')))
for kind in ['crowd','pathways','lead-flow','timeline','compare','countdown']:
 scenes.append(dict(kind=kind,composition='Broll-'+kind,brand='shared',source='src/Broll.tsx',defaultDurationFrames=180,fps=30,width=1080,height=1920,transparentSupported=True,tags=[kind,'legacy']))
(R/'catalog/motion-scenes.json').write_text(json.dumps(scenes,indent=2)+'\n')
assets=json.loads((R/'catalog/assets.json').read_text())
lines=['# AI editing asset index','',f'{len(assets)} reusable assets and {len(scenes)} native motion kinds.','', 'Search: `python3 tools/reelctl.py assets --query clock` or `python3 tools/reelctl.py scenes --query interview`.','', '## Native motion','', '| Kind | Brand | Composition | Source |','|---|---|---|---|']
for s in scenes:lines.append(f'| {s["kind"]} | {s["brand"]} | {s["composition"]} | [{Path(s["source"]).name}](../{s["source"]}) |')
lines+=['','## Files','','| ID | Kind | Asset |','|---|---|---|']
for a in sorted(assets,key=lambda a:a['id']):lines.append(f'| {a["id"]} | {a["kind"]} | [{Path(a["file"]).name}](../public/{a["file"]}) |')
(R/'catalog/ASSET_INDEX.md').write_text('\n'.join(lines)+'\n')
print(f'Indexed {len(assets)} assets and {len(scenes)} motion kinds.')

# Clinic footage, endings and generated transparent cutouts retain provenance.
manifest=R/'workspaces/my-dental-skin-clinic/04_generated_broll/manifest.json'
clinic=[]
if manifest.is_file():
 for asset in json.loads(manifest.read_text())['assets']:
  clinic.append({'id':'clinic-'+Path(asset['path']).stem,'brand':'clinic','kind':'video','subject':asset['subject'],'repositoryFile':'workspaces/my-dental-skin-clinic/'+asset['path'],'duration':asset['duration'],'sha256':asset['sha256'],'source':asset['source'],'rights':asset['rights'],'git_storage':'lfs'})
ending=R/'workspaces/my-dental-skin-clinic/assets/brand/endcards/manifest.json'
if ending.is_file():
 asset=json.loads(ending.read_text())
 clinic.append({'id':'clinic-reference-logo-outro','brand':'clinic','kind':'ending','subject':'white logo end-card with supplied spoken signature','repositoryFile':'workspaces/my-dental-skin-clinic/'+asset['path'],'duration':asset['duration'],'sha256':asset['sha256'],'source':'user supplied reference ending','rights':asset['rights'],'git_storage':'lfs'})
cutouts=R/'workspaces/my-dental-skin-clinic/assets/cutouts/manifest.json'
if cutouts.is_file():
 for asset in json.loads(cutouts.read_text())['assets']:
  clinic.append({'id':'clinic-'+asset['id'],'brand':'clinic','kind':'transparent-image','subject':asset.get('subject','ivory molar tooth teaching model'),'repositoryFile':'workspaces/my-dental-skin-clinic/'+asset['path'],'sha256':asset['sha256'],'source':asset['source'],'git_storage':'lfs'})
dhiraj_logo=R/'workspaces/my-dental-skin-clinic/assets/brand/dhiraj/provenance.json'
if dhiraj_logo.is_file():
 asset=json.loads(dhiraj_logo.read_text()).get('transparent_version')
 if asset:
  clinic.append({'id':'dhiraj-supplied-clinic-logo-transparent','brand':'clinic','kind':'brand-logo','subject':'Dhiraj shoot — supplied clinic logo with transparent background; use only for this identity','repositoryFile':'workspaces/my-dental-skin-clinic/'+asset['path'],'sha256':asset['sha256'],'source':'User-supplied logo; built-in imagegen background extraction','git_storage':'lfs'})
(R/'catalog/clinic-assets.json').write_text(json.dumps(clinic,ensure_ascii=False,indent=2)+'\n')
with (R/'catalog/ASSET_INDEX.md').open('a') as f:
 f.write('\n## Clinic B-roll, ending and cutouts\n\nSearch: `python3 tools/reelctl.py assets --brand clinic --query implant`.\n\n')
 for asset in clinic:
  duration=f'{asset["duration"]:.2f}s; ' if 'duration' in asset else ''
  f.write(f'- [{asset["subject"]}](../{asset["repositoryFile"]}) — {duration}Git LFS; {asset["source"]}.\n')
print(f'Indexed {len(clinic)} clinic reusable media assets separately from the native scene catalogue.')

# Keep user-supplied Jet Kids identity distinct from generated/shared overlays.
jetkids_provenance=R/'workspaces/jetkids/brand-provenance.json'
if jetkids_provenance.is_file():
 asset=json.loads(jetkids_provenance.read_text())
 jetkids=[{'id':'jetkids-school-crest-original','brand':'jetkids','kind':'logo','subject':'Jet Kids International School original JKIS crest','repositoryFile':asset['logo'],'sha256':asset['sha256'],'source':asset['source'],'treatment':asset['treatment'],'git_storage':'lfs'}]
 music=R/'workspaces/jetkids/music-assets.json'
 if music.is_file():jetkids+=json.loads(music.read_text())['assets']
 (R/'catalog/jetkids-assets.json').write_text(json.dumps(jetkids,ensure_ascii=False,indent=2)+'\n')
 with (R/'catalog/ASSET_INDEX.md').open('a') as f:
  f.write('\n## Jet Kids supplied identity\n\nSearch: `python3 tools/reelctl.py assets --brand jetkids --query crest`.\n\n')
  for asset in jetkids:f.write(f'- [{asset["subject"]}](../{asset["repositoryFile"]}) — {asset["kind"]}; Git LFS.\n')
 print('Indexed Jet Kids original school crest separately from generated overlays.')
