#!/usr/bin/env python3
"""Optional macOS scratch narration. Uses installed voices, never impersonation."""
import argparse,subprocess,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('text_file');p.add_argument('--voice');p.add_argument('--rate',type=int,default=155);a=p.parse_args()
if not shutil.which('say'):p.error('This optional helper uses macOS say. Keep the recorded presenter for final voiceover.')
out=Path('.cache/guide-voice')/(Path(a.text_file).stem+'.aiff');out.parent.mkdir(parents=True,exist_ok=True)
cmd=['say','-f',a.text_file,'-r',str(a.rate),'-o',str(out)]
if a.voice:cmd+=['-v',a.voice]
subprocess.run(cmd,check=True);print(out)
