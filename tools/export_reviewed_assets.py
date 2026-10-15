#!/usr/bin/env python3
"""Export original reviewed scenes, including reusable continuous graphic stories."""
from pathlib import Path
import json,subprocess,argparse
R=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('project');a=ap.parse_args();P=R/a.project;id=P.name;folder=R/'public/assets/projects'/id;folder.mkdir(parents=True,exist_ok=True)
e=json.loads((P/'editorial.json').read_text());props=json.loads((P/'reel.json').read_text())
for entry in e.get('alphaExports',[]):
 spec=dict(entry) if isinstance(entry,dict) else {'kind':entry};kind=spec['kind'];cue=next((b for b in props['broll'] if b['kind']==kind),None)
 duration=spec.get('duration') or cue['duration'];data=dict(kind=kind,duration=duration,transparent=True)
 if 'beats' in spec:data['beats']=spec['beats']
 elif cue and 'beats' in cue:data['beats']=cue['beats']
 if 'labels' in spec:data['labels']=spec['labels']
 elif cue and 'labels' in cue:data['labels']=cue['labels']
 version=e.get('assetVersion',1);p=folder/(kind+f'-v{version}-props.json');p.write_text(json.dumps(data,indent=2)+'\n');out=folder/(kind+f'-v{version}.webm')
 if out.exists():continue
 prefix='School-' if kind.startswith('atfro-school-') else 'Compare-' if kind in ['nio-story-comparison','nio-compare-board','nio-brand-services','nio-access-calendar'] else 'Project-' if kind.startswith('nio-project-') else 'Study-' if kind.startswith(('nio-study-','nio-intro-','nio-mock-','nio-story-')) else 'Nio07-' if kind.startswith('nio-system-') else 'Nio04-' if kind.startswith('nio-parents-') else 'Atfro01-'
 subprocess.run(['node','tools/render.mjs',prefix+kind,str(out),'--props='+str(p),'--codec=vp9','--pixel-format=yuva420p','--image-format=png','--crf=22'],cwd=R,check=True)
print('Reusable alpha exports prepared for',id)
