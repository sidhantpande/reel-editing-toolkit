#!/usr/bin/env python3
"""Check staged/tracked files (or git add dry-run candidates before staging)."""
import subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
r=subprocess.run(['git','ls-files','-c','-o','--exclude-standard','-z'],cwd=R,capture_output=True,check=True)
files=set(x.decode() for x in r.stdout.split(b'\0') if x);bad=[];total=0
for name in files:
 p=R/name
 if name.startswith(('media/','.cache/','node_modules/','.venv/','public/raw/','public/reference/','public/proxies/','exports/','deliverables/','Final Content/')):bad.append('Private/generated path: '+name)
 if not p.is_file():continue
 total+=p.stat().st_size
 if p.stat().st_size>95*2**20 and not name.startswith('deliverables/'):bad.append('Large unconfigured Git file: '+name)
print(f'Git candidates: {len(files)} files, {total/2**20:.1f} MiB before LFS')
if bad:print('\n'.join(bad));sys.exit(1)
print('OK: no raw footage, supplied reference media, environment or render cache in Git candidates.')
