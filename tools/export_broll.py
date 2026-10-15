#!/usr/bin/env python3
"""Render original brand variants as true transparent WebM files."""
from pathlib import Path
import subprocess,json,argparse,hashlib
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--brand',choices=['niolearn','atfro','both'],default='both');a=p.parse_args()
brands=['niolearn','atfro'] if a.brand=='both' else [a.brand]
for brand in brands:
 for kind in ['crowd','pathways','lead-flow','timeline','compare','countdown']:
  out=R/f'public/assets/broll/{brand}-{kind}.webm'
  if out.exists():continue
  props=R/f'.cache/{brand}-{kind}.json';props.parent.mkdir(exist_ok=True);props.write_text(json.dumps({'brand':brand,'kind':kind,'transparent':True}))
  subprocess.run(['node','tools/render.mjs',f'Broll-{kind}',str(out),'--codec=vp9','--pixel-format=yuva420p','--image-format=png','--crf=28','--props='+str(props)],cwd=R,check=True)
print('Alpha exports available in public/assets/broll/. Regenerate from source at any resolution.')
