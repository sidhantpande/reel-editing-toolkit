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

# The clinic uses reviewed supplied B-roll, not Remotion native scene substitutes.
manifest=R/'workspaces/my-dental-skin-clinic/04_generated_broll/manifest.json'
clinic=[]
if manifest.is_file():
 for asset in json.loads(manifest.read_text())['assets']:
  clinic.append({'id':'clinic-'+Path(asset['path']).stem,'brand':'clinic','kind':'video','subject':asset['subject'],'repositoryFile':'workspaces/my-dental-skin-clinic/'+asset['path'],'duration':asset['duration'],'sha256':asset['sha256'],'source':asset['source'],'rights':asset['rights'],'git_storage':'lfs'})
(R/'catalog/clinic-assets.json').write_text(json.dumps(clinic,ensure_ascii=False,indent=2)+'\n')
with (R/'catalog/ASSET_INDEX.md').open('a') as f:
 f.write('\n## Clinic supplied B-roll\n\nSearch: `python3 tools/reelctl.py assets --brand clinic --query implant`.\n\n')
 for asset in clinic:f.write(f'- [{asset["subject"]}](../{asset["repositoryFile"]}) — {asset["duration"]:.2f}s; Git LFS; user supplied.\n')
print(f'Indexed {len(clinic)} clinic supplied B-roll assets separately from the native scene catalogue.')
