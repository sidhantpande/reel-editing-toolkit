#!/usr/bin/env python3
"""Create opt-in SDR proxies; FFmpeg autorotation is retained. Originals untouched."""
import argparse,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('files',nargs='*');a=p.parse_args()
files=[Path(f) for f in a.files] if a.files else sorted((R/'media/raw').rglob('*.mov'))
for f in files:
 out=R/'.cache/proxies'/f.with_suffix('.mp4').name;out.parent.mkdir(parents=True,exist_ok=True)
 if out.exists():continue
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',str(f)]))['streams'][0]
 hdr=info.get('color_transfer') in ['smpte2084','arib-std-b67']
 tone='zscale=t=linear:npl=100,format=gbrpf32le,tonemap=hable:desat=0,zscale=p=bt709:t=bt709:m=bt709:r=tv,' if hdr else ''
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','warning','-i',str(f),'-vf',tone+'scale=540:960:force_original_aspect_ratio=decrease,setsar=1,format=yuv420p','-r','30','-c:v','libx264','-preset','fast','-crf','23','-c:a','aac','-b:a','128k','-movflags','+faststart','-metadata:s:v:0','rotate=0',str(out)],check=True)
 print(out,flush=True)
