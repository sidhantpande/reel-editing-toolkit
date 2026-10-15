#!/usr/bin/env python3
"""Dry run by default. Only generated project caches are eligible; never media/assets."""
import argparse,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');a=p.parse_args()
for rel in ['.cache/audio','.cache/proxies','.cache/analysis','node_modules/.cache']:
 d=R/rel
 if not d.exists():continue
 size=sum(f.stat().st_size for f in d.rglob('*') if f.is_file())
 print(f'{"REMOVE" if a.apply else "WOULD REMOVE"}: {rel} ({size/2**20:.1f} MiB)')
 if a.apply:shutil.rmtree(d)
print('Transcripts, raw media, references, assets and exports retained.')
