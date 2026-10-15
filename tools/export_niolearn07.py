#!/usr/bin/env python3
"""Export original second-reel motion scenes as reusable full-resolution alpha clips."""
from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[1];folder=R/'public/assets/projects/niolearn-07';folder.mkdir(parents=True,exist_ok=True)
scenes=[('nio-system-diagnostic',176),('nio-system-prep',133),('nio-system-review',181),('nio-system-interview',145),('nio-system-path',158)]
for kind,duration in scenes:
 p=folder/(kind+'-v1-props.json');p.write_text(json.dumps(dict(kind=kind,duration=duration,transparent=True),indent=2)+'\n');out=folder/(kind+'-v1.webm')
 if out.exists():continue
 subprocess.run(['node','tools/render.mjs','Nio07-'+kind,str(out),'--props='+str(p),'--codec=vp9','--pixel-format=yuva420p','--image-format=png','--crf=22'],cwd=R,check=True)
print('Saved five full-resolution alpha motion scenes.')
