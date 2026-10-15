#!/usr/bin/env python3
import shutil,sys,json,platform,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];bad=[]
for name in ['ffmpeg','ffprobe','node','npm','git']:
 p=shutil.which(name);print(f'{name}: {p or "MISSING"}')
 if not p:bad.append(name)
print('Python:',sys.version.split()[0],platform.machine())
for rel in ['node_modules/remotion/package.json','package-lock.json','public/assets/fonts/Sora.ttf','public/assets/fonts/Inter.ttf','catalog/assets.json']:
 ok=(R/rel).exists();print(('OK ' if ok else 'MISSING ')+rel)
 if not ok:bad.append(rel)
free=shutil.disk_usage(R).free/2**30;print(f'Free disk: {free:.1f} GiB')
if free<5:print('Low disk: use tools/clean_cache.py --apply for this project cache only.')
print('Raw clips available:',len(list((R/'media/raw').rglob('*.mov'))))
if bad:sys.exit(1)
