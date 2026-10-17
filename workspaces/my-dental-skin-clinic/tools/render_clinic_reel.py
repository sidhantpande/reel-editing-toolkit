#!/usr/bin/env python3
"""Render a reviewed clinic edit plan with the user-approved v05 style."""
import argparse,copy,hashlib,json,subprocess,sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
import render_reel07_v03 as v3
import render_reel07_v04 as caps
R=v3.R; REEL=v3.REEL; FF=v3.FF
CACHE=R/'.cache/clinic';OUT=REEL/'04_timeline';STYLE=json.loads((R/'styles/clinic-approved.json').read_text())

from clinic_plan import validate_plan

def make_picture_audio(plan):
 parts=[];audio_parts=[];sources={}
 for i,s in enumerate(plan['segments']):
  n=round((s['timeline_out']-s['timeline_in'])*30)
  # Keep audio as non-overlapping speech runs, six-ms fades suppress splice clicks.
  if s['source_id'] not in sources:
   raw=subprocess.check_output([FF,'-v','error','-i',s['source'],'-vn','-ar','48000','-ac','2','-f','f32le','-'])
   sources[s['source_id']]=np.frombuffer(raw,dtype=np.float32).reshape(-1,2)
  a=round(s['source_in']*48000);audio=sources[s['source_id']][a:a+n*1600].copy()
  fade=288;audio[:fade]*=np.linspace(0,1,fade)[:,None];audio[-fade:]*=np.linspace(1,0,fade)[:,None];audio_parts.append(audio)
  head=3 if i else 0;tail=3 if i<len(plan['segments'])-1 else 0
  core=CACHE/f'core-{i:02}.mp4';parts.append(core)
  if not core.exists():
   c=s['crop_xywh']
   vf=f'crop={c["width"]}:{c["height"]}:{c["x"]}:{c["y"]},scale=1080:1920,setsar=1,fps=30,format=yuv420p'
   v3.run([FF,'-v','error','-y','-ss',s['source_in']+head/30,'-i',s['source'],'-an','-vf',vf,'-frames:v',n-head-tail,'-c:v','libx264','-preset','fast','-crf','18',core])
  if i<len(plan['segments'])-1:
   nxt=plan['segments'][i+1];transition=CACHE/f'dissolve-{i:02}.mp4';parts.append(transition)
   if not transition.exists():
    def crop(s):
     c=s['crop_xywh'];return f'crop={c["width"]}:{c["height"]}:{c["x"]}:{c["y"]},scale=1080:1920,setsar=1,fps=30,trim=end_frame=6,setpts=PTS-STARTPTS,format=yuv420p'
    # Decode picture beyond each audio cut to avoid freezing either face.
    graph=f'[0:v]{crop(s)}[a];[1:v]{crop(nxt)}[b];[a][b]blend=all_expr=A*(1-(N-1)/5)+B*(N-1)/5[out]'
    v3.run([FF,'-v','error','-y','-ss',s['source_out']-.1,'-i',s['source'],'-ss',nxt['source_in']-.1,'-i',nxt['source'],'-filter_complex',graph,'-map','[out]','-an','-frames:v','6','-c:v','libx264','-preset','fast','-crf','18',transition])
  print('Picture / dialogue run',i+1,'of',len(plan['segments']),flush=True)
 wavfile.write(CACHE/'dialogue-48k-float.wav',48000,np.concatenate(audio_parts))
 listing=CACHE/'concat.txt';listing.write_text('\n'.join(f"file '{s}'" for s in parts)+'\n')
 v3.run([FF,'-v','error','-y','-f','concat','-safe','0','-i',listing,'-c','copy',CACHE/'speech-picture.mp4'])

def render(plan):
 caps.CACHE=CACHE;caps.OUT=OUT;caps.STYLE=STYLE;caps.prepare_fonts()
 caption=CACHE/'compact-word-captions.mov'
 if not caption.exists():caption=caps.captions(plan)
 args=[FF,'-v','error','-nostdin','-y','-i',CACHE/'speech-picture.mp4','-i',CACHE/'dialogue-48k-float.wav']
 graph=['[0:v]eq=contrast=1.025:brightness=0.003:saturation=1.02[base]'];current='base'
 for i,s in enumerate(plan['broll_slots']):
  duration=s['timeline_out']-s['timeline_in'];index=i+2
  args+=['-ss',s['media_in'],'-t',duration,'-i',s['path']]
  if s.get('layout','portrait')=='portrait':graph.append(f'[{index}:v]fps=30,scale=1080:1920,setsar=1,format=rgba[b{i}]')
  else:
   graph.extend([f'[{index}:v]fps=30,split=2[bg{i}][fg{i}]',f'[bg{i}]scale=1920:1920,crop=1080:1920,gblur=sigma=35[blur{i}]',f'[fg{i}]scale=1000:1000[sharp{i}]',f'[blur{i}][sharp{i}]overlay=40:310,setsar=1,format=rgba[b{i}]'])
  graph.append(f'[b{i}]fade=t=in:st=0:d=0.23:alpha=1,fade=t=out:st={duration-.23}:d=0.23:alpha=1,setpts=PTS-STARTPTS+{s["timeline_in"]}/TB[roll{i}]')
  graph.append(f'[{current}][roll{i}]overlay=0:0:enable=between(t\\,{s["timeline_in"]}\\,{s["timeline_out"]})[pass{i}]');current=f'pass{i}'
 logo=R/'00_inbox/brand/my-dental-clinic-logo-transparent-v01.png';gradient=CACHE/'caption-gradient.png'
 from PIL import Image,ImageDraw
 image=Image.new('RGBA',(1080,1920),(0,0,0,0));draw=ImageDraw.Draw(image)
 for y in range(1020,1920):draw.line((0,y,1079,y),fill=(0,0,0,min(145,round((y-1020)*.18))))
 image.save(gradient)
 logo_i=len(plan['broll_slots'])+2;gradient_i=logo_i+1;cap_i=logo_i+2
 args+=['-i',logo,'-i',gradient,'-i',caption]
 graph.extend([f'[{current}][{gradient_i}:v]overlay=0:0[shade]',f'[{logo_i}:v]crop=1460:468:162:230,scale=255:-1,format=rgba,split=2[logo][halo]','[halo]lutrgb=r=255:g=255:b=255,gblur=sigma=1.3[whitehalo]','[shade][whitehalo]overlay=65:65[under]','[under][logo]overlay=65:65[brand]',f'[brand][{cap_i}:v]overlay=0:1100,fade=t=out:st={plan["duration_seconds"]-.12}:d=0.12,format=yuv420p[out]'])
 (OUT/'filtergraph.txt').write_text(';\n'.join(graph)+'\n')
 output=EXPORT
 args+=['-filter_complex',';'.join(graph),'-map','[out]','-map','1:a:0','-t',plan['duration_seconds'],'-af','highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11','-c:v','libx264','-preset','fast','-crf','18','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',output]
 v3.run(args);print('Rendered',output,flush=True)

def main():
 global CACHE,OUT,REEL,EXPORT
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('plan',type=Path);parser.add_argument('--aroll-only',action='store_true');parser.add_argument('--preflight',action='store_true')
 args=parser.parse_args();path=args.plan.resolve();plan=json.loads(path.read_text())
 summary=validate_plan(plan,allow_pending=args.aroll_only,root=R);print(json.dumps(summary),flush=True)
 if args.preflight:return
 OUT=path.parent;REEL=path.parents[2]
 # Include renderer versions in the cache signature, so edits cannot reuse stale output.
 signature=path.read_bytes()+Path(__file__).read_bytes()+Path(caps.__file__).read_bytes()+(R/'styles/clinic-approved.json').read_bytes()
 digest=hashlib.sha256(signature).hexdigest()[:12]
 CACHE=R/'.cache'/f'{plan["reel_id"]}-{digest}'
 CACHE.mkdir(parents=True,exist_ok=True)
 suffix='aroll-preview' if args.aroll_only else 'review'
 EXPORT=R/'05_exports/review'/f'{plan["reel_id"]}_{suffix}_{plan.get("version","v01")}.mp4'
 EXPORT.parent.mkdir(parents=True,exist_ok=True)
 if args.aroll_only:plan['broll_slots']=[]
 if plan.get('caption_keywords'):v3.KEYS.update(plan['caption_keywords'])
 if plan.get('caption_emphasis'):v3.EMPHASIS.update(plan['caption_emphasis'])
 make_picture_audio(plan);render(plan)

if __name__=='__main__':main()
