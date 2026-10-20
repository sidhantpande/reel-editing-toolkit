import json,subprocess,hashlib,sys,math
from pathlib import Path
from fractions import Fraction
from PIL import Image,ImageDraw,ImageFont
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'tools'))
from event_transitions import assemble,transition
from log_colour import probe,digest
from subject_track import crop_expression
B=ROOT/'.cache/jetkids/reference-led-overview-v01';B.mkdir(exist_ok=True);PROJECT=ROOT/'workspaces/jetkids/edits/09-reference-led-overview-v01';CAT=json.loads((PROJECT/'source-catalog.json').read_text())
def run(args):
 r=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error',*args],capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stderr[-5000:])
def save(p,data):p.write_text(json.dumps(data,indent=2))
def title(w,h,p):
 Image.new('RGBA',(w,h),(0,0,0,0)).save(p)
def preflight(plan):
 assert (plan['width'],plan['height']) in [(1920,1080),(1080,1920)]
 assert plan['fps']==30 and plan['eventPhotoInserts'] is False and plan['no_evening_event']
 at=0;checks=[]
 for i,s in enumerate(plan['shots']):
  assert s['timeline_start_frame']==at and isinstance(s['frames'],int) and s['frames']>0
  c=CAT[s['source_id']];p=Path(s['source']);assert p.is_file(),p
  q=probe(p);v=next(x for x in q['streams'] if x['codec_type']=='video' and not x.get('disposition',{}).get('attached_pic'))
  native=float(Fraction(v['avg_frame_rate']));assert s['speed']>=1 or native*s['speed']>=29.9
  tail=transition(plan['shots'][i+1])[1] if i+1<len(plan['shots']) else 0
  end=s['in']+(s['frames']+tail)/30*s['speed'];assert 0<=s['in']<end<=float(q['format']['duration'])+.001,(s['source_id'],end,q['format']['duration'])
  expected=c.get('expected_media_sha256');sha=digest(p);assert not expected or sha==expected,(p,'master checksum mismatch')
  c.update(probe=q,actual_media_sha256=sha)
  if c['rotate']:assert s['source_id'].startswith('V')
  assert all(.16<=x<=.84 for x in s['crop_center'])
  if s.get('crop_path'):crop_expression(s['crop_path'])
  checks.append({'id':s['source_id'],'media_sha256':sha,'matches_recorded_master':bool(expected),'frames':s['frames'],'source_in':s['in'],'source_out_with_handle':end,'native_fps':native,'speed':s['speed']});at+=s['frames']
 assert Path(plan['logo']).is_file();assert plan['audio']['in']+(at+plan['logoFrames'])/30<=float(probe(plan['audio']['source'])['format']['duration'])+.001
 return {'status':'preflight passed','sources':checks,'body_frames':at,'total_frames':at+plan['logoFrames'],'width':plan['width'],'height':plan['height'],'notes':'Measured master hashes checked; HP originals are separately registered. No source rewrite.'}
def crop_filter(s,w,h):
 c=CAT[s['source_id']];v=next(x for x in c['probe']['streams'] if x['codec_type']=='video' and not x.get('disposition',{}).get('attached_pic'));sw,sh=v['width'],v['height']
 if c['rotate']:sw,sh=sh,sw
 zoom=s.get('zoom',1.);cw=min(sw,sh*w/h)/zoom;ch=min(sh,sw*h/w)/zoom;cw=int(cw)//2*2;ch=int(ch)//2*2
 a,z=s['crop_center'];dur=s['frames']/30
 x=f'max(0,min(iw-ow,iw*({a}+({z-a})*min(t/{dur},1))-ow/2))';y=f"max(0,min(ih-oh,ih*{s.get('crop_center_y',.5)}-oh/2))"
 if s.get('crop_path'):
  x=f"max(0,min(iw-ow,iw*({crop_expression(s['crop_path'])})-ow/2))"
 vf=f"trim=duration={s['renderFrames']/30*s['speed']:.9f},setpts=(PTS-STARTPTS)/{s['speed']},"
 if c['rotate']:vf+='transpose=2,'
 vf+=f"fps=30,crop={cw}:{ch}:x='{x}':y='{y}',scale={w}:{h}:flags=lanczos"
 if v.get('color_range')=='pc':vf+=':in_range=full:out_range=tv'
 vf+=',setsar=1'
 g=s['grade']
 if any(x!=1 for x in g.values()):vf+=f",eq=gamma={g['gamma']}:contrast={g['contrast']}:saturation={g['saturation']}"
 return vf+',format=yuv420p'
def render(fmt):
 plan=json.loads((PROJECT/(fmt+'-plan.json')).read_text());cache=B/fmt;cache.mkdir(exist_ok=True);report=preflight(plan);save(cache/'preflight.json',report);print(fmt,'PREFLIGHT',report['total_frames'],flush=True)
 save(B/'verified-source-catalog.json',CAT)
 if '--preflight' in sys.argv:return
 w,h=plan['width'],plan['height'];segments=[];changed=set()
 for i,s in enumerate(plan['shots']):
  tail=transition(plan['shots'][i+1])[1] if i+1<len(plan['shots']) else 0;s['renderFrames']=s['frames']+tail;dest=cache/f'{i:03d}.mp4';vf=crop_filter(s,w,h)
  if i==len(plan['shots'])-1:vf+=f",fade=t=out:st={s['frames']/30-.16}:d=0.16"
  signature=hashlib.sha256(json.dumps({'shot':s,'vf':vf,'width':w,'height':h},sort_keys=True).encode()).hexdigest();meta=dest.with_suffix('.signature')
  if dest.exists():
   try:
    actual=next(x for x in probe(dest)['streams'] if x['codec_type']=='video');valid=int(actual['nb_frames'])==s['renderFrames']
   except Exception:valid=False
   if not valid or (meta.exists() and meta.read_text()!=signature):dest.unlink()
  if not dest.exists():
   changed.add(i)
   inputs=['-threads','2','-filter_threads','2','-filter_complex_threads','2','-ss',str(s['in']),'-i',s['source']]
   if i==0:
    overlay=cache/'title.png';title(w,h,overlay);inputs+=['-loop','1','-framerate','30','-i',str(overlay)]
    filters=f'[0:v]{vf},fade=t=in:st=0:d=0.12[base];[1:v]format=rgba,fade=t=in:st=0:d=0.22:alpha=1,fade=t=out:st=1.92:d=0.25:alpha=1[title];[base][title]overlay=0:0:shortest=1[v]';inputs+=['-filter_complex',filters,'-map','[v]']
   else:inputs+=['-vf',vf]
   run([*inputs,'-an','-frames:v',str(s['renderFrames']),'-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-y',str(dest)])
  actual=next(x for x in probe(dest)['streams'] if x['codec_type']=='video');assert int(actual['nb_frames'])==s['renderFrames'];meta.write_text(signature)
  segments.append(dest);print(fmt,i,s['source_id'],s['frames'],'frames',flush=True)
 dirty=bool(changed)
 for i,s in enumerate(plan['shots']):
  for name,expected,depends in [(f'core-{i:03d}.mp4',s['frames']-transition(s)[1],{i}),(f'seam-{i:03d}.mp4',transition(s)[1],{i-1,i})]:
   q=cache/name
   if not q.exists():continue
   try:actual=int(next(v for v in probe(q)['streams'] if v['codec_type']=='video')['nb_frames'])
   except Exception:actual=-1
   if actual!=expected or (depends & changed):q.unlink();dirty=True
 if dirty and (cache/'silent.mp4').exists():(cache/'silent.mp4').unlink()
 pieces=assemble(segments,plan['shots'],cache)
 ending=cache/'ending.mp4'
 if not ending.exists():
  run(['-loop','1','-i',plan['logo'],'-an','-vf',f'scale=740:-2,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fade=t=in:st=0:d=0.22,format=yuv420p','-r','30','-frames:v',str(plan['logoFrames']),'-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-y',str(ending)])
 pieces.append(ending);concat=cache/'concat.txt';concat.write_text(''.join("file '"+str(p).replace("'","'\\''")+"'\n" for p in pieces));silent=cache/'silent.mp4'
 if not silent.exists():run(['-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart','-y',str(silent)])
 duration=report['total_frames']/30;norm_audio=Path(plan['audio']['source'])
 output=ROOT/'exports/jetkids-reference-led-overview-v01';output.mkdir(exist_ok=True);dest=output/(fmt+'.mp4')
 run(['-i',str(silent),'-i',str(norm_audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-t',str(duration),'-movflags','+faststart','-y',str(dest)])
 q=probe(dest);v=next(x for x in q['streams'] if x['codec_type']=='video');assert int(v['nb_frames'])==report['total_frames'];assert (v['width'],v['height'])==(w,h)
 run(['-xerror','-i',str(dest),'-f','null','-']);r=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-i',str(dest),'-vn','-af','loudnorm=I=-14:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);m=json.loads(r.stderr[r.stderr.rfind('{'):]);assert float(m['input_tp'])<=-1
 save(cache/'encoded-qa.json',{'file':str(dest),'sha256':digest(dest),'frames':v['nb_frames'],'full_decode':'passed','loudness':m,'visual_review':'pending','listening_review':'not attested'});print('EXPORTED',dest,flush=True)
for fmt in (['portrait'] if '--portrait-only' in sys.argv else ['landscape'] if '--landscape-only' in sys.argv else ['landscape','portrait']):render(fmt)
