#!/usr/bin/env python3
from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[1];folder=R/'public/assets/projects/niolearn-04';props=json.loads((R/'projects/niolearn/niolearn-04/reel.json').read_text());cues=props['broll']
# Keep every thematic motion scene reusable on its own.
scenes=[('nio-parents-authority',95),('nio-parents-credential',151),('nio-parents-fees',129),('nio-parents-outcomes',123),('nio-parents-conversation',182)]
for kind,duration in scenes:
 p=folder/(kind+'-v1-props.json');p.write_text(json.dumps({'kind':kind,'duration':duration,'transparent':True},indent=2)+'\n');out=folder/(kind+'-v1.webm')
 if out.exists():continue
 subprocess.run(['node','tools/render.mjs','Nio04-'+kind,str(out),'--props='+str(p),'--codec=vp9','--pixel-format=yuva420p','--image-format=png','--crf=22'],cwd=R,check=True)
print('Saved five full-resolution alpha motion scenes.')
