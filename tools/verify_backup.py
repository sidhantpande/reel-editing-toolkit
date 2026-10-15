#!/usr/bin/env python3
"""Verify all versioned reusable files against the pre-upload content manifest."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'catalog/backup-manifest.json').read_text())
errors=[]
for item in manifest['files']:
 p=ROOT/item['path']
 if not p.is_file():errors.append('Missing: '+item['path']);continue
 with p.open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
 if actual!=item['sha256'] or p.stat().st_size!=item['bytes']:errors.append('Changed: '+item['path'])
tracked=set(x.decode() for x in subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).split(b'\0') if x)
expected={x['path'] for x in manifest['files']}|{'catalog/backup-manifest.json'}
if tracked!=expected:errors.append('Versioned file list differs from backup manifest.')
if errors:raise SystemExit('\n'.join(errors))
print(f'Verified {len(manifest["files"])} original file hashes and byte counts, including hydrated LFS assets.')
