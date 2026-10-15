#!/usr/bin/env python3
"""Two-pass EBU loudness normalization, preserving rendered video frames."""
import argparse,subprocess,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('output');a=p.parse_args()
if Path(a.input).resolve()==Path(a.output).resolve():p.error('Output must differ from input.')
# Leave AAC intersample-peak headroom; verify the encoded result.
filter='loudnorm=I=-14:TP=-1.5:LRA=7'
r=subprocess.run(['ffmpeg','-hide_banner','-y','-i',a.input,'-vn','-af',filter+':print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
m=json.loads(re.findall(r'\{\s*"input_i".*?\}',r.stderr,re.S)[-1])
if m['input_i']=='-inf':p.error('No usable audio.')
measured=f':measured_I={m["input_i"]}:measured_TP={m["input_tp"]}:measured_LRA={m["input_lra"]}:measured_thresh={m["input_thresh"]}:offset={m["target_offset"]}:linear=true'
Path(a.output).parent.mkdir(parents=True,exist_ok=True)
subprocess.run(['ffmpeg','-hide_banner','-y','-i',a.input,'-map','0:v:0','-map','0:a:0','-c:v','copy','-af',filter+measured,'-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',a.output],check=True)
