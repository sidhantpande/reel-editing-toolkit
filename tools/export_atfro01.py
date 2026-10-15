#!/usr/bin/env python3
"""Export the actual revision-2 Canvas/SVG motion scenes as reusable alpha clips."""
from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[1]
props=json.loads((R/'projects/atfro/atfro-01/reel.json').read_text())
for cue in props['broll']:
 if not cue['kind'].startswith('atfro-'):continue
 folder=R/'public/assets/projects/atfro-01';folder.mkdir(exist_ok=True,parents=True)
 data={**cue,'transparent':True};propfile=folder/(cue['kind']+'-v2-props.json');propfile.write_text(json.dumps(data,indent=2)+'\n')
 out=folder/(cue['kind']+'-v2.webm')
 subprocess.run(['node','tools/render.mjs','Atfro01-'+cue['kind'],str(out),'--props='+str(propfile),'--frames=0-'+str(cue['duration']-1),'--codec=vp9','--pixel-format=yuva420p','--image-format=png','--crf=22'],cwd=R,check=True)
print('Saved reusable Canvas/SVG alpha animations.')
