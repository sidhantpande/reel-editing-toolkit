#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for name,target in [('raw',R/'media/raw'),('reference',R/'media/reference'),('proxies',R/'.cache/proxies')]:
 target.mkdir(exist_ok=True,parents=True);link=R/'public'/name
 if not link.exists() and not link.is_symlink():link.symlink_to(target,target_is_directory=True)
print('Linked local media into Remotion public directory (Git ignored).')
