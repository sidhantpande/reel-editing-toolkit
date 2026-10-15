#!/usr/bin/env python3
"""Export the second-generation art-directed scenes as reusable alpha layers."""
from pathlib import Path
import argparse,json,subprocess
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--brand',choices=['niolearn','atfro','both'],default='both');a=p.parse_args()
for brand in (['niolearn','atfro'] if a.brand=='both' else [a.brand]):
 for kind in ['paper-possibilities','paper-pathways','paper-crowd','paper-partnership']:
  out=R/f'public/assets/broll/{brand}-premium-{kind}-v3.webm'
  if out.exists():continue
  props=R/f'.cache/premium-{brand}-{kind}.json';props.write_text(json.dumps({'brand':brand,'kind':kind,'transparent':True}))
  subprocess.run(['node','tools/render.mjs','Premium-'+kind,str(out),'--props='+str(props),'--codec=vp9','--pixel-format=yuva420p','--image-format=png','--crf=24'],cwd=R,check=True)
print('Premium alpha exports complete.')
