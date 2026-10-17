#!/usr/bin/env python3
"""Cue-cleaned edit; handle-based picture dissolves, continuous clean dialogue."""
import copy,json,subprocess,sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
import render_reel07_v03 as v3
import render_reel07_v04 as caps
R=v3.R; REEL=v3.REEL; FF=v3.FF
CACHE=R/'.cache/reel-07-v05';OUT=REEL/'04_timeline/v05'

def build_plan():
 old=json.loads(v3.PLAN.read_text());p=copy.deepcopy(old)
 p['segments']=[];cursor=0
 for i,s in enumerate(old['segments']):
  if i in (0,9,14):continue
  s=copy.deepcopy(s);s['old_run_index']=i
  n=round((s['timeline_out']-s['timeline_in'])*30)
  s['timeline_in']=cursor/30;cursor+=n;s['timeline_out']=cursor/30
  p['segments'].append(s)
 def locate(sid,t):
  matches=[s for s in p['segments'] if s['source_id']==sid]
  for s in matches:
   if s['source_in']<=t<=s['source_out']:return s['timeline_in']+t-s['source_in']
  s=min(matches,key=lambda s:min(abs(t-s['source_in']),abs(t-s['source_out'])))
  return min(s['timeline_out'],max(s['timeline_in'],s['timeline_in']+t-s['source_in']))
 words=[]
 for w in old['words']:
  if w['source_id']=='0097' and w['text']=='तो':continue
  w=copy.deepcopy(w)
  if w['source_id']=='0093' and w['text']=='कालरात्रि':w['source_start']=3.575
  if w['source_id']=='0096' and w['text']=='एक' and w['source_start']==0:w['source_start']=.69
  w['start']=round(locate(w['source_id'],w['source_start']),5)
  w['end']=round(max(w['start']+.035,locate(w['source_id'],w['source_end'])),5)
  words.append(w)
 p['words']=words;p['duration_seconds']=cursor/30
 p['status']='review v05: three production cues excluded; picture dissolves; gaze cutaways'
 p['cue_exclusions']=[{'source':'0093','in':2.007,'out':2.7736667},{'source':'0096','in':0,'out':.3},{'source':'0097','in':0,'out':.7333333}]
 # Two supplied assets, with topic-appropriate cutaways over screen glances.
 # All source times here are approved received B-roll; never camera-recording audio.
 slots=[
  dict(id='gaze-intro',asset='bridge',timeline_in=locate('0093',9.7),timeline_out=locate('0093',14.0056),media_in=12.0,note='Dental model cutaway during screen-reading glances; narration retained'),
  dict(id='B01',asset='implant',timeline_in=locate('0093',20.887),timeline_out=locate('0096',8.7),media_in=.10,note='Solutions / implant explanation; covers transition into implant take and side glance'),
  dict(id='B02',asset='bridge',timeline_in=locate('0096',12.65),timeline_out=locate('0096',19.4),media_in=11.25,note='Bridge explanation and screen glance'),
  dict(id='gaze-best',asset='implant',timeline_in=locate('0097',1.655),timeline_out=locate('0097',4.15),media_in=3.2,note='Which option is best question; return to doctor for Instagram / clinical condition'),
 ]
 for s in slots:
  s['timeline_in']=round(s['timeline_in']*30)/30;s['timeline_out']=round(s['timeline_out']*30)/30
 p['broll_slots']=slots
 p['picture_transition']={'type':'cross dissolve','duration_seconds':.2,'method':'3 frames of source handles each side; narration timeline unchanged'}
 (OUT/'plan.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
 return p

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
   original=R/f'.cache/reel-07-v03/run-{s["old_run_index"]:02}.mp4'
   v3.run([FF,'-v','error','-y','-i',original,'-an','-vf',f'trim=start_frame={head}:end_frame={n-tail},setpts=PTS-STARTPTS','-c:v','libx264','-preset','fast','-crf','18',core])
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
 caps.CACHE=CACHE;caps.OUT=OUT;caps.prepare_fonts()
 caption=CACHE/'compact-word-captions.mov'
 if not caption.exists():caption=caps.captions(plan)
 deliveries=json.loads((REEL/'07_deliveries/deliveries.json').read_text())
 paths={'implant':deliveries[3]['path'],'bridge':deliveries[2]['path']}
 args=[FF,'-v','error','-nostdin','-y','-i',CACHE/'speech-picture.mp4','-i',CACHE/'dialogue-48k-float.wav']
 graph=['[0:v]eq=contrast=1.025:brightness=0.003:saturation=1.02[base]'];current='base'
 for i,s in enumerate(plan['broll_slots']):
  duration=s['timeline_out']-s['timeline_in'];index=i+2
  args+=['-ss',s['media_in'],'-t',duration,'-i',paths[s['asset']]]
  if s['asset']=='implant':graph.append(f'[{index}:v]fps=30,scale=1080:1920,setsar=1,format=rgba[b{i}]')
  else:
   graph.extend([f'[{index}:v]fps=30,split=2[bg{i}][fg{i}]',f'[bg{i}]scale=1920:1920,crop=1080:1920,gblur=sigma=35[blur{i}]',f'[fg{i}]scale=1000:1000[sharp{i}]',f'[blur{i}][sharp{i}]overlay=40:310,setsar=1,format=rgba[b{i}]'])
  graph.append(f'[b{i}]fade=t=in:st=0:d=0.23:alpha=1,fade=t=out:st={duration-.23}:d=0.23:alpha=1,setpts=PTS-STARTPTS+{s["timeline_in"]}/TB[roll{i}]')
  graph.append(f'[{current}][roll{i}]overlay=0:0:enable=between(t\\,{s["timeline_in"]}\\,{s["timeline_out"]})[pass{i}]');current=f'pass{i}'
 logo=R/'00_inbox/brand/my-dental-clinic-logo-transparent-v01.png';gradient=R/'.cache/reel-07-v03/caption-gradient.png'
 logo_i=len(plan['broll_slots'])+2;gradient_i=logo_i+1;cap_i=logo_i+2
 args+=['-i',logo,'-i',gradient,'-i',caption]
 graph.extend([f'[{current}][{gradient_i}:v]overlay=0:0[shade]',f'[{logo_i}:v]crop=1460:468:162:230,scale=255:-1,format=rgba,split=2[logo][halo]','[halo]lutrgb=r=255:g=255:b=255,gblur=sigma=1.3[whitehalo]','[shade][whitehalo]overlay=65:65[under]','[under][logo]overlay=65:65[brand]',f'[brand][{cap_i}:v]overlay=0:1100,fade=t=out:st={plan["duration_seconds"]-.12}:d=0.12,format=yuv420p[out]'])
 (OUT/'filtergraph.txt').write_text(';\n'.join(graph)+'\n')
 output=R/'05_exports/review/reel-07_clean-dissolves_v05.mp4'
 args+=['-filter_complex',';'.join(graph),'-map','[out]','-map','1:a:0','-t',plan['duration_seconds'],'-af','highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11','-c:v','libx264','-preset','fast','-crf','18','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',output]
 v3.run(args);print('Rendered',output,flush=True)

if __name__=='__main__':
 CACHE.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
 plan=build_plan();make_picture_audio(plan);render(plan)
