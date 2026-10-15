#!/usr/bin/env python3
"""Validate catalogue integrity, project references and render-ready timing data."""
import json,hashlib,sys,argparse
ap=argparse.ArgumentParser();ap.add_argument("--require-media",action="store_true");args=ap.parse_args()
from pathlib import Path
R=Path(__file__).resolve().parents[1];errors=[]
def check(ok,msg):
 if not ok:errors.append(msg)
scripts=json.loads((R/'catalog/scripts.json').read_text());ids=[s['id'] for s in scripts]
check(len(ids)==len(set(ids)),'Duplicate script IDs')
check(sum(s['format']=='REEL' for s in scripts)==49,'Expected 49 reel scripts')
for s in scripts:
 check((R/s['script']).exists(),f'Missing script {s["id"]}')
 plan=json.loads((R/s['script']).with_name('edit-plan.json').read_text())
 for src in plan['sourceClips']:
  if args.require_media:check((R/src).exists(),f'Missing local clip {src} (restore media on new machine)')
for a in json.loads((R/'catalog/assets.json').read_text()):
 p=R/'public'/a['file'];check(p.is_file(),f'Missing asset: {p}')
 if p.is_file():check(hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'],f'Asset checksum mismatch: {p}')
for p in (R/'projects').rglob('reel.json'):
 d=json.loads(p.read_text());duration=d['durationInFrames'];check(duration>0,f'Bad duration: {p}')
 for c in d['clips']:check(c['from']>=0 and c['duration']>0 and c['from']+c['duration']<=duration,f'Bad clip range: {p}')
 for pg in d['captions']:
  check(0<=pg['startMs']<pg['endMs']<=duration/30*1000+1,f'Caption page out of range: {p}')
  for w in pg['words']:check(pg['startMs']<=w['startMs']<w['endMs']<=pg['endMs'],f'Word timing out of page: {p}')
if errors:print('\n'.join(errors));sys.exit(1)
print(f'OK: {len(scripts)} script folders, asset checksums, portable references and prepared timeline props (source media optional unless --require-media).')
