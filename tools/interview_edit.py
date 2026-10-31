#!/usr/bin/env python3
"""Serial, source-owned interview rendering for Jet Kids. Outputs remain review drafts."""
from __future__ import annotations
import argparse,hashlib,json,math,re,subprocess,shutil,os
from pathlib import Path
from fractions import Fraction
from PIL import Image
from log_colour import probe,digest
from approved_delivery import assert_unlocked
from event_transitions import transition,assemble
from subject_track import crop_expression
ROOT=Path(__file__).resolve().parents[1]
FPS=30

def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def run(args):
 p=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error',*map(str,args)],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr[-4000:])
def loudness_json(stderr):
 """FFmpeg may append progress/summary lines after loudnorm's JSON object."""
 start=stderr.rfind('{')
 if start<0:raise ValueError('FFmpeg did not return loudness measurements')
 try:measurement,_=json.JSONDecoder().raw_decode(stderr[start:])
 except json.JSONDecodeError as error:raise ValueError('Invalid FFmpeg loudness measurements') from error
 if not isinstance(measurement,dict) or not {'input_i','input_tp'}<=measurement.keys():raise ValueError('Incomplete FFmpeg loudness measurements')
 return measurement

def colour_grade_filter(source):
 """Small display-space corrections only; Log transforms remain source-owned."""
 grade=source.get('colourGrade',{})
 limits={'gamma':(.85,1.2),'brightness':(-.04,.04),'contrast':(.9,1.1),'saturation':(.8,1.2),'gamma_r':(.9,1.1),'gamma_g':(.9,1.1),'gamma_b':(.9,1.1)}
 if not isinstance(grade,dict) or set(grade)-limits.keys():raise ValueError('Unsupported source colour correction')
 for key,value in grade.items():
  if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not limits[key][0]<=value<=limits[key][1]:raise ValueError('Source colour correction outside restrained range: '+key)
 return 'eq='+':'.join(f'{key}={value}' for key,value in grade.items())+':gamma_weight=0.65' if grade else ''
def validate_structure(plan,words):
 if plan.get('kind')!='jetkids-interview' or plan.get('fps')!=30:raise ValueError('Expected30fps Jet Kids interview plan')
 if not re.fullmatch(r'jetkids-[a-z0-9-]+',plan.get('id','')):raise ValueError('Use a versioned Jet Kids ID')
 if plan.get('eventPhotoInserts') is not False:raise ValueError('Event photos are excluded')
 if not 30<=plan.get('logoFrames',0)<=90:raise ValueError('Logo hold must be1–3seconds')
 for key in ['leadFrames','tailFrames']:
  if type(plan.get(key,0)) is not int or not 0<=plan.get(key,0)<=90:raise ValueError('Invalid breathing-room frames')
 cursor=plan.get('leadFrames',0)
 for c in plan['cuts']:
  if any(type(c.get(k)) is not int for k in ['inFrame','outFrame','timelineFrom','duration']):raise ValueError('Edit frames must be integers')
  if c['timelineFrom']!=cursor or c['inFrame']<0 or c['outFrame']-c['inFrame']!=c['duration'] or c['duration']<=0:raise ValueError('Discontinuous dialogue cuts')
  if c.get('speechSpeed',1)!=1:raise ValueError('Interview speech must stay at native speed')
  cursor+=c['duration']
 if cursor+plan.get('tailFrames',0)!=plan['dialogueFrames']:raise ValueError('Dialogue frame count differs')
 if not plan.get('formats') or set(plan['formats'])-{'portrait','landscape'}:raise ValueError('Specify supported picture formats')
 for fmt in plan['formats']:
  shots=plan['formats'][fmt]['shots'];at=0
  for i,s in enumerate(shots):
   if type(s['frames']) is not int or s['frames']<=0 or s['timelineFrom']!=at:raise ValueError('Discontinuous picture shots')
   for key in ['holdLeadFrames','holdTailFrames']:
    n=s.get(key,0)
    if type(n) is not int or n<0 or n>=s['frames']:raise ValueError('Invalid decoded-frame hold')
   if s.get('holdLeadFrames',0) and i!=0:raise ValueError('Lead hold belongs only to the first shot')
   if s.get('holdTailFrames',0) and i!=len(shots)-1:raise ValueError('Tail hold belongs only to the last shot')
   if s.get('holdLeadFrames',0)+s.get('holdTailFrames',0)>=s['frames']:raise ValueError('A picture shot needs decoded source frames')
   transition(s);at+=s['frames']
  if at!=plan['dialogueFrames']:raise ValueError('Picture must cover the complete dialogue')
 if not words:raise ValueError('Source-owned caption words required')
 for word in words:
  if not word.get('source_id') or not str(word.get('text','')).strip():raise ValueError('Each word needs source and text')
  a,b=word['start'],word['end']
  if not all(math.isfinite(t) for t in [a,b]) or not 0<=a<b:raise ValueError('Invalid source word timing')
  if not any(c['source_id']==word['source_id'] and c['inFrame']/30-.04<=a<b<=c['outFrame']/30+.04 for c in plan['cuts']):raise ValueError('Word is outside its selected source cut')
 if plan.get('enforceDialoguePictureSync'):validate_picture_sync(plan)
 if plan.get('captionPhrases'):caption_groups(mapped_words(plan,words),True,plan['captionPhrases'])
 return plan['dialogueFrames']

def validate_picture_sync(plan):
 """Check original camera time against native dialogue, excluding decoded holds/B-roll."""
 for fmt,settings in plan['formats'].items():
  for shot in settings['shots']:
   source=plan['sources'][shot['source_id']];sid=source.get('derivedFrom',shot['source_id'])
   lead=shot.get('holdLeadFrames',0);start=shot['timelineFrom']+lead
   end=shot['timelineFrom']+shot['frames']-shot.get('holdTailFrames',0)
   for cut in plan['cuts']:
    if cut['source_id']!=sid:continue
    a=max(start,cut['timelineFrom']);b=min(end,cut['timelineFrom']+cut['duration'])
    if b<=a:continue
    for frame in [a,b-1]:
     picture=shot['in']+source.get('sourceOffset',0)+(frame-start)/30*shot.get('speed',1)
     dialogue=(cut['inFrame']+frame-cut['timelineFrom'])/30
     if abs(picture-dialogue)>1/30+.0001:
      raise ValueError(f'Lip-sync mismatch in {fmt} {shot["source_id"]} at frame {frame}: picture offset {(picture-dialogue)*30:.2f} frames')

def verified_hash(path,expected=None):
 path=Path(path);key=str(path.resolve());folder=ROOT/'.cache/jetkids/interview-edits/source-hash-records';folder.mkdir(parents=True,exist_ok=True)
 cache=folder/(hashlib.sha256(key.encode()).hexdigest()+'.json');st=path.stat();fingerprint=[st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns]
 prior=read(cache) if cache.exists() else {}
 if prior.get('fingerprint')==fingerprint:
  value=prior['sha256']
 else:
  value=digest(path);save(cache,dict(path=key,fingerprint=fingerprint,sha256=value))
 if expected and value!=expected:raise ValueError('Source changed: '+key)
 return value

def uses_prepared_voice(plan):
 flags=[bool(plan['sources'][c['source_id']].get('preparedVoice')) for c in plan['cuts']]
 if any(flags) and not all(flags):raise ValueError('Use the same prepared-voice workflow for every dialogue cut')
 return bool(flags and all(flags))

def validate_event_scope(plan):
 """An explicit evening commission must not borrow sports footage, or vice versa."""
 event=plan.get('event','sports')
 if event not in {'sports','evening'}:raise ValueError('Unsupported interview event scope')
 for sid,source in plan.get('sources',{}).items():
  source_event=source.get('event','')
  if event=='evening':
   if source_event!='evening':raise ValueError('Evening plan requires an explicitly evening source: '+sid)
  elif 'evening' in source_event.lower():raise ValueError('Evening source requires an explicit evening plan: '+sid)

def preflight(project):
 assert_unlocked(project)
 corner_crest()
 for f in ['edit-plan.json','source-words.json','editorial.json','production-plan.md','assets-provenance.json']:
  if not (project/f).is_file():raise ValueError('Missing '+f)
 if len((project/'production-plan.md').read_text())<150:raise ValueError('Write the actual production plan')
 p=read(project/'edit-plan.json');ws=read(project/'source-words.json')['words'];validate_structure(p,ws);validate_event_scope(p)
 source_checks={}
 for sid,s in p['sources'].items():
  colour_grade_filter(s)
  path=Path(s['path']);q=probe(path);v=next(v for v in q['streams'] if v['codec_type']=='video');h=verified_hash(path,s.get('sha256'))
  if s.get('sha256') and h!=s['sha256']:raise ValueError('Source changed: '+sid)
  rotation=next((x.get('rotation',0) for x in v.get('side_data_list',[]) if 'rotation' in x),0)
  if s.get('rotate') and abs(rotation)==90:raise ValueError('Metadata already rotates source; do not apply a second manual rotation: '+sid)
  source_checks[sid]=dict(path=str(path),sha256=h,duration=float(q['format']['duration']),native_fps=float(Fraction(v['avg_frame_rate'])),width=v['width'],height=v['height'],range=v.get('color_range'),rotation=next((x.get('rotation',0) for x in v.get('side_data_list',[]) if 'rotation' in x),0))
  for audio_key in ['preparedAudio','preparedVoice']:
   if not s.get(audio_key):continue
   a=s[audio_key];verified_hash(a['path'],a['sha256']);aq=probe(a['path']);stream=next(t for t in aq['streams'] if t['codec_type']=='audio')
   if int(stream['sample_rate'])!=48000 or a['source_start']<0:raise ValueError('Prepared dialogue must retain48kHz and a valid source offset')
   for c in p['cuts']:
    if c['source_id']==sid and not a['source_start']-.001<=c['inFrame']/30<c['outFrame']/30<=a['source_start']+float(aq['format']['duration'])+.001:raise ValueError('Prepared dialogue does not cover the original selected cut')
 for c in p['cuts']:
  if c['outFrame']/30>source_checks[c['source_id']]['duration']+.04:raise ValueError('Dialogue exceeds source')
 for fmt in p['formats']:
  shots=p['formats'][fmt]['shots']
  for i,s in enumerate(shots):
   src=source_checks[s['source_id']];outgoing=transition(shots[i+1])[1] if i+1<len(shots) else 0
   if not 0<s.get('speed',1)<=1.2 or s['in']<0:raise ValueError('Invalid picture timing')
   if s.get('speed',1)<1 and s['speed']*src['native_fps']<29.9:raise ValueError('Slow motion would duplicate frames')
   if s['in']+(s['frames']+outgoing-s.get('holdTailFrames',0)-s.get('holdLeadFrames',0))/30*s.get('speed',1)>src['duration']+.04:raise ValueError('Picture exceeds source handle')
 uses_prepared_voice(p)
 if not Path(p['logo']).is_file() or not Path(p['music']).is_file():raise ValueError('Missing logo/music')
 return p,ws,source_checks

def mapped_words(plan,words):
 mapped=[]
 for c in plan['cuts']:
  for word in words:
   if word['source_id']!=c['source_id'] or word['start']<c['inFrame']/30-.04 or word['end']>c['outFrame']/30+.04:continue
   a=(word['start']-c['inFrame']/30)+c['timelineFrom']/30;b=(word['end']-c['inFrame']/30)+c['timelineFrom']/30
   mapped.append(dict(word,start=max(0,a),end=b))
 return sorted(mapped,key=lambda x:x['start'])
def caption_groups(words,compact=False,phrases=None):
 if phrases:
  groups=[];cursor=0
  for phrase in phrases:
   target=' '.join(phrase.split());group=[]
   while cursor<len(words):
    group.append(words[cursor]);cursor+=1;actual=' '.join(' '.join(w['text'] for w in group).split())
    if actual==target:break
    if not target.startswith(actual+' '):raise ValueError('Curated caption phrase differs from source words')
   if not group or actual!=target:raise ValueError('Curated caption phrase differs from source words')
   groups.append(group)
  if cursor!=len(words):raise ValueError('Curated captions omit source words')
  return groups
 groups=[];g=[]
 for word in words:
  if g and (len(g)>=(4 if compact else 5) or len(' '.join(w['text'] for w in g))+len(word['text'])>(25 if compact else 30) or word['start']-g[-1]['end']>.5 or word['end']-g[0]['start']>2.5):groups.append(g);g=[]
  g.append(word)
 if g:groups.append(g)
 return groups

def ass_time(t):
 cent=round(t*100);return f'{cent//360000}:{cent//6000%60:02}:{cent//100%60:02}.{cent%100:02}'
def escaped(t):return t.replace('\\','').replace('{','').replace('}','').replace('\n',' ')
def editorial_captions(plan,groups,header,path):
 """Curated centered blocks; each line owns exact source words and fixed geometry."""
 layouts=plan['captionLayouts']
 if len(layouts)!=len(groups):raise ValueError('Every phrase needs an editorial layout')
 lines=[header];checks=[]
 for i,(group,layout) in enumerate(zip(groups,layouts)):
  a=group[0]['start'];b=min(plan['dialogueFrames']/30,group[-1]['end']+.14)
  if i+1<len(groups):b=min(b,groups[i+1][0]['start']-.01)
  cursor=0;review=[]
  for spec in layout['lines']:
   count=spec['words'];owned=group[cursor:cursor+count];cursor+=count
   if len(owned)!=count or not count:raise ValueError('Caption line has missing words')
   text=' '.join(escaped(word['text']) for word in owned)
   family='Montserrat' if all(ord(c)<128 for c in text) else 'Mukta'
   size=spec['size'];x=540+spec.get('dx',0);y=spec['y']
   if not 72<=size<=176 or not 420<=x<=660 or not 1240<=y<=1690:raise ValueError('Editorial caption outside calibrated range')
   color=spec.get('color','FFFFFF')
   tags=rf'{{\an5\fn{family}\b800\fs{size}\c&H00{color}&\move({x},{y+10},{x},{y},0,110)\fad(70,55)}}'
   start=a if plan.get('captionStyle',{}).get('lineReveal')=='block' else max(a,owned[0]['start'])
   lines.append(f'Dialogue: 1,{ass_time(start)},{ass_time(b)},Main,,0,0,0,,{tags}{text}\n')
   review.append(dict(text=' '.join(word['text'] for word in owned),start=start,end=b,font=family,size=size,x=x,y=y))
  if cursor!=len(group):raise ValueError('Caption layout omits words')
  checks.append(dict(start=a,end=b,text=' '.join(word['text'] for word in group),words=group,lines=review))
 title=plan.get('speakerTitle')
 if title:
  end=title.get('end',4.4)
  # The identity was supplied by the client; credentials are not inferred from appearance.
  rows=[(title.get('eyebrow','JET KIDS  /  GUEST VOICES'),'Montserrat',24,1040,'C9DADD'),
        (title['name'],'Cormorant Garamond Light',title.get('nameSize',98),1140,'FFFFFF'),
        (title.get('qualification',''),'Montserrat',36,1222,'6CEBF5'),
        (title.get('office',''),'Montserrat',title.get('officeSize',34),1285,'FFFFFF'),
        (title.get('officeExpansion',''),'Montserrat',title.get('expansionSize',27),1335,'C9DADD')]
  for text,font,size,y,color in rows:
   if not text:continue
   tag=rf'{{\an5\fn{font}\b600\fs{size}\bord0\shad1\c&H00{color}&\move(540,{y+10},540,{y},0,260)\fad(260,300)}}'
   lines.append(f'Dialogue: 2,0:00:00.15,{ass_time(end)},Main,,0,0,0,,{tag}{escaped(text)}\n')
  lines.append(f'Dialogue: 2,0:00:00.15,{ass_time(end)},Main,,0,0,0,,'+r'{\an7\pos(490,1082)\p1\c&H006CEBF5&\bord0\shad0\fad(260,300)}m 0 0 l 100 0 l 100 2 l 0 2'+'\n')
 path.write_text(''.join(lines));return checks
def subtitles(plan,words,fmt,path):
 w,h=(1920,1080) if fmt=='landscape' else (1080,1920);font=82 if fmt=='landscape' else plan.get('captionStyle',{}).get('fontSize',82);y=895 if fmt=='landscape' else plan.get('captionStyle',{}).get('y',1455)
 header=f'''[Script Info]\nScriptType: v4.00+\nPlayResX: {w}\nPlayResY: {h}\nScaledBorderAndShadow: yes\nWrapStyle: 2\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Main,Noto Sans Devanagari,{font},&H00FFFFFF,&H00FFFFFF,&H50201810,&H70000000,-1,0,0,0,100,100,0,0,1,0.8,1.5,5,70,70,0,1\nStyle: Label,Montserrat,28,&H00503E21,&H00FFFFFF,&H90000000,&H90000000,0,0,0,0,100,100,2,0,1,0,1,7,0,0,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
 lines=[header];groups=caption_groups(mapped_words(plan,words),plan.get('captionStyle',{}).get('progressive',False),plan.get('captionPhrases'));checks=[]
 if plan.get('captionStyle',{}).get('treatment')=='editorial':return editorial_captions(plan,groups,header,path)
 for i,g in enumerate(groups):
  a=max(0,g[0]['start']-.03);b=min(plan['dialogueFrames']/30-.025,g[-1]['end']+.10)
  if i+1<len(groups):b=min(b,groups[i+1][0]['start']-.01)
  if b-a<.12:b=a+.12
  progressive=plan.get('captionStyle',{}).get('progressive',False)
  versions=[g[:j+1] for j in range(len(g))] if progressive else [g]
  for j,shown in enumerate(versions):
   va=max(a,shown[-1]['start']) if progressive else a
   vb=min(b,g[j+1]['start']) if progressive and j+1<len(g) else b
   text=' '.join(escaped(x['text']) for x in shown)
   if not progressive and len(text)>22 and fmt=='portrait' and len(shown)>2:
    tokens=text.split();mid=len(tokens)//2;text=' '.join(tokens[:mid])+r'\N'+' '.join(tokens[mid:])
   for key in ['खेल','पढ़ाई','एनर्जी','बच्चों','स्पोर्ट्स','जेट किड्स','sports','parents','partners','confidence','potential','teamwork','physical health']:
    if key in text:text=text.replace(key,r'{\c&H006CEBF5&}'+key+r'{\c&H00FFFFFF&}',1);break
   if all(ord(c)<128 for c in ''.join(x['text'] for x in g)):text=r'{\fnMontserrat}'+text
   anchor=7 if progressive else 5;cx=112 if progressive else w//2
   if vb>va:lines.append(f'Dialogue: 1,{ass_time(va)},{ass_time(vb)},Main,,0,0,0,,{{\\an{anchor}\\pos({cx},{y})}}{text}\n')
  checks.append(dict(start=a,end=b,text=' '.join(x['text'] for x in g),words=g))
 label='JET KIDS  /  VOICES';lx=85 if fmt=='portrait' else 92;ly=150 if fmt=='portrait' else 74
 if plan.get('captionStyle',{}).get('showLabel',True):lines.append(f'Dialogue: 2,0:00:00.25,0:00:04.75,Label,,0,0,0,,{{\\pos({lx},{ly})\\fad(200,250)}}{label}\n')
 path.write_text(''.join(lines));return checks

def crop_filter(plan,s,fmt,checks):
 w,h=(1920,1080) if fmt=='landscape' else (1080,1920);src=plan['sources'][s['source_id']];q=checks[s['source_id']];sw,sh=q['width'],q['height'];vf=''
 if abs(q.get('rotation',0))==90:sw,sh=sh,sw
 if src.get('rotate'):vf+='transpose=2,';sw,sh=sh,sw
 cw=int(min(sw,sh*w/h)/s.get('zoom',1))//2*2;ch=int(min(sh,sw*h/w)/s.get('zoom',1))//2*2
 cx,cy=s.get('center',[.5,.5]);x=max(0,min(sw-cw,sw*cx-cw/2));y=max(0,min(sh-ch,sh*cy-ch/2))
 if s.get("crop_path"):
  x=f"max(0,min(iw-ow,iw*({crop_expression(s['crop_path'])})-ow/2))"
 if s.get('crop_path_y'):
  y=f"max(0,min(ih-oh,ih*({crop_expression(s['crop_path_y'])})-oh/2))"
 vf+=f"trim=duration={(s['renderFrames']-s.get('holdTailFrames',0)-s.get('holdLeadFrames',0))/30*s.get('speed',1):.7f},setpts=(PTS-STARTPTS)/{s.get('speed',1)},fps=30,crop={cw}:{ch}:x='{x}':y='{y}',scale={w}:{h}:flags=lanczos"
 if q.get('range')=='pc':vf+=':in_range=full:out_range=tv'
 grade=colour_grade_filter(src)
 if grade:vf+=','+grade
 
 if s.get('holdTailFrames'):vf+=f",tpad=stop_mode=clone:stop_duration={s['holdTailFrames']/30}"
 if s.get('holdLeadFrames'):vf+=f",tpad=start_mode=clone:start_duration={s['holdLeadFrames']/30}"
 # A ceil-rounded source end may have one fewer decoded 30fps frame. Hold
 # its last decoded frame for that fraction, then enforce the edit clock.
 return vf+f",tpad=stop_mode=clone:stop_duration={1/30},trim=end_frame={s['renderFrames']},setpts=N/(30*TB),setsar=1,format=yuv420p"

def normalized_audio(plan,cache):
 clips=[];prepared_voice=uses_prepared_voice(plan)
 for i,c in enumerate(plan['cuts']):
  source=plan['sources'][c['source_id']];prepared=source.get('preparedVoice') if prepared_voice else source.get('preparedAudio',{});audio_path=prepared.get('path',source['path']);audio_in=c['inFrame']/30-prepared.get('source_start',0)
  if audio_in<-.001:raise ValueError('Negative prepared dialogue offset')
  prefix='' if prepared_voice else 'highpass=f=65,'
  p=cache/f'voice-{i:02}.wav';run(['-ss',max(0,audio_in),'-i',audio_path,'-t',c['duration']/30,'-vn','-af',f"{prefix}afade=t=in:d=0.008,afade=t=out:st={c['duration']/30-.012}:d=0.012",'-ar','48000','-ac','2','-c:a','pcm_s24le','-y',p]);clips.append(p)
 listing=cache/'audio-concat.txt';listing.write_text(''.join("file '"+str(p)+"'\n" for p in clips));dialogue=cache/'dialogue.wav';run(['-f','concat','-safe','0','-i',listing,'-c','copy','-y',dialogue])
 voice=cache/'dialogue-normalized.wav'
 if prepared_voice:
  run(['-i',dialogue,'-ar','48000','-c:a','pcm_s24le','-y',voice])
  save(cache/'prepared-voice-reuse.json',dict(status='Source-owned enhanced master reused without a second neural/EQ pass',sources={c['source_id']:plan['sources'][c['source_id']]['preparedVoice'] for c in plan['cuts']},nativeSpeed=True))
 elif plan.get('voiceEnhancement'):
  import sys
  sys.path.insert(0,str(ROOT/'workspaces/my-dental-skin-clinic/tools'))
  import audio_enhance,shutil
  audio_enhance.FF=shutil.which('ffmpeg')
  from audio_enhance import enhance
  mastered,report=enhance(dialogue,cache/'voice-enhancement',plan['voiceEnhancement'].get('attenuationDb',12))
  run(['-i',mastered,'-af','equalizer=f=280:t=q:w=0.8:g=-1.5,equalizer=f=2800:t=q:w=0.7:g=1.5,acompressor=threshold=0.18:ratio=1.7:attack=18:release=160:makeup=1','-ar','48000','-c:a','pcm_s24le','-y',voice])
 else:run(['-i',dialogue,'-af','loudnorm=I=-15:TP=-2:LRA=9','-ar','48000','-c:a','pcm_s24le','-y',voice])
 total=(plan['dialogueFrames']+plan['logoFrames'])/30;body=plan['dialogueFrames']/30
 # Quiet instrumental at fixed native speed; original dialogue is never time-stretched.
 lead=plan.get('leadFrames',0)*1600
 raw=cache/'mix.wav';fc=f'[0:a]adelay={lead}S:all=1,apad,atrim=duration={total}[v];[1:a]volume=1.1,atrim=duration={total},afade=t=in:d=0.7,afade=t=out:st={total-.8}:d=0.8[m];[v][m]amix=inputs=2:duration=first:normalize=0[a]'
 run(['-i',voice,'-stream_loop','-1','-i',plan['music'],'-filter_complex',fc,'-map','[a]','-ar','48000','-c:a','pcm_s24le','-y',raw])
 p=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-i',str(raw),'-af','loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);m=loudness_json(p.stderr);save(cache/'loudness-input.json',m)
 filt=f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
 out=cache/'mixed-normalized.wav';run(['-i',raw,'-af',filt,'-ar','48000','-c:a','pcm_s24le','-y',out]);return out

def caption_filter(ass,fontdir):
 # The subtitles demuxer can select SIMPLE shaping despite a HarfBuzz-enabled
 # libass build. ASS with explicit COMPLEX shaping preserves Indic clusters.
 return f"ass=filename='{ass}':fontsdir='{fontdir}':shaping=complex"

def corner_crest():
 """The corner mark must have real transparency, never the closing JPEG box."""
 path=ROOT/'public/assets/brands/jetkids/logo-transparent.png'
 with Image.open(path) as im:
  if im.mode!='RGBA' or im.getchannel('A').getextrema()!=(0,255):
   raise ValueError('Corner crest requires an RGBA cutout with transparent background')
  if any(im.getpixel(p)[3]!=0 for p in [(0,0),(im.width-1,0),(0,im.height-1),(im.width-1,im.height-1)]):
   raise ValueError('Corner crest background corners must be transparent')
 return path

def finish_picture(plan,words,fmt,work,audio,target,copy_audio=False,question=None):
 crest=corner_crest()
 w,h=(1920,1080) if fmt=='landscape' else (1080,1920)
 ass=work/'captions.ass';groups=subtitles(plan,words,fmt,ass);save(work/'caption-groups.json',groups)
 gradient=work/'shade.png';im=Image.new('RGBA',(w,h));px=im.load()
 for y in range(h):
  a=int(plan.get('captionStyle',{}).get('gradientAlpha',155)*max(0,(y/h-plan.get('captionStyle',{}).get('gradientStart',.63))/(1-plan.get('captionStyle',{}).get('gradientStart',.63)))**plan.get('captionStyle',{}).get('gradientPower',1.15))
  for x in range(w):px[x,y]=(0,0,0,a)
 im.save(gradient)
 fontdir=ROOT/'.cache/jetkids/interview-edits/fonts';body=plan['dialogueFrames']/30
 fc=f"[0:v][1:v]overlay=0:0:shortest=1:enable='lt(t,{body})',{caption_filter(ass,fontdir)}[captioned];[3:v]scale=176:-2,setsar=1[crest];[captioned][crest]overlay=44:64:shortest=1:enable='lt(t,{body})'[v]"
 extra=[];audio_map='2:a';frames=plan['dialogueFrames']+plan['logoFrames']
 if question:
  if copy_audio or fmt!='portrait':raise ValueError('Question openings require portrait and a lossless audio master')
  # One integer frame offset controls both clocks. The overlap must fit wholly
  # inside the existing silent picture lead, never the first spoken phoneme.
  from interview_question import opening_timing
  timing=opening_timing(plan,question);overlap=timing['transitionFrames']/30;offset=timing['bodyOffsetFrames']/30
  fc=fc[:-3]+'[body];'+f"[4:v]settb=AVTB,setpts=PTS-STARTPTS,format=yuv420p[card];[body]settb=AVTB,setpts=PTS-STARTPTS[prepared];[card][prepared]xfade=transition=fade:duration={overlap}:offset={offset},format=yuv420p[v];[5:a]aformat=sample_rates=48000:channel_layouts=stereo[prefix];[2:a]aformat=sample_rates=48000:channel_layouts=stereo[bodyaudio];[prefix][bodyaudio]acrossfade=d={overlap}:c1=qsin:c2=qsin[a]"
  extra=['-i',question['cardPath'],'-i',question['audioPath']];audio_map='[a]';frames=timing['totalFrames']
 audio_args=['-c:a','copy'] if copy_audio else ['-c:a','aac','-b:a','256k','-ar','48000']
 run(['-threads','2','-filter_complex_threads','2','-i',work/'silent.mp4','-loop','1','-i',gradient,'-i',audio,'-loop','1','-i',crest,*extra,'-filter_complex',fc,'-map','[v]','-map',audio_map,'-r','30','-fps_mode','cfr','-frames:v',frames,'-t',frames/30,'-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p',*audio_args,'-movflags','+faststart','-y',target])
 q=probe(target);v=next(x for x in q['streams'] if x['codec_type']=='video');assert int(v['nb_frames'])==frames;assert (v['width'],v['height'])==(w,h)
 run(['-xerror','-i',target,'-f','null','-'])
 p=subprocess.run(['ffmpeg','-hide_banner','-i',str(target),'-vn','-af','loudnorm=I=-14:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);m=loudness_json(p.stderr);assert float(m['input_tp'])<=-1
 return v,m,groups

def refinish_current(project,fmt='portrait'):
 """Refresh captions/crest from the same cached picture; retain encoded audio."""
 if (project/'opening-question.json').exists():raise ValueError('Use interview_question.py to retain the question opening')
 plan,words,checks=preflight(project);cache=ROOT/'.cache/jetkids/interview-edits'/plan['id'];work=cache/fmt
 sig=hashlib.sha256(json.dumps(dict(plan=plan,words=words),sort_keys=True).encode()).hexdigest()
 if not (cache/'signature').is_file() or (cache/'signature').read_text()!=sig:raise ValueError('Changed edit plan: use --replace-current for a complete render')
 dest=ROOT/'exports/jetkids-interview-edits'/plan['id']/(fmt+'.mp4');target=dest.with_name(fmt+'.pending.mp4')
 if not dest.is_file() or not (work/'silent.mp4').is_file():raise ValueError('Current export and original cached picture are required')
 before=digest(dest);oldqa=read(work/'qa.json')
 v,m,groups=finish_picture(plan,words,fmt,work,dest,target,copy_audio=True)
 # Packet equality proves that a graphics-only correction cannot change lipsync,
 # voice, music, mastering or AAC encoder delay.
 def audio_hash(path):
  return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
 ah=audio_hash(dest)
 if audio_hash(target)!=ah:raise ValueError('Graphics refresh changed encoded audio')
 os.replace(target,dest)
 save(work/'qa.json',dict(path=str(dest),sha256=digest(dest),frames=int(v['nb_frames']),full_decode='passed',loudness=m,captions=len(groups),visual_review='Pending user graphics review',listening_review=oldqa.get('listening_review','Not attested'),status='Graphics refresh review draft',graphicsRefresh=dict(previous_sha256=before,encoded_audio_hash=ah,audio='Exact original AAC packets retained',picture='Same cached picture, cuts, crop and speed',captions='Explicit HarfBuzz complex shaping',cornerLogo='Transparent crest,176px wide at44,64 during picture body',cornerLogoSha256=digest(corner_crest()))))
 print('REFINISHED',dest,flush=True)

def render(project,formats=None,replace_current=False):
 if (project/'opening-question.json').exists():raise ValueError('Use interview_question.py to retain the question opening')
 plan,words,checks=preflight(project);cache=ROOT/'.cache/jetkids/interview-edits'/plan['id'];cache.mkdir(parents=True,exist_ok=True);sig=hashlib.sha256(json.dumps(dict(plan=plan,words=words),sort_keys=True).encode()).hexdigest();stamp=cache/'signature'
 if stamp.exists() and stamp.read_text()!=sig:
  if not replace_current:raise ValueError('Changed plan: use --replace-current to rebuild this current edit')
  # Never delete a cache that has become an input to its own project.
  inputs=[s['path'] for s in plan['sources'].values()]+[a['path'] for s in plan['sources'].values() for key in ['preparedAudio','preparedVoice'] if (a:=s.get(key))]+[plan['logo'],plan['music']]
  if any(Path(p).resolve().is_relative_to(cache.resolve()) for p in inputs):raise ValueError('Move active input assets out of this render cache before replacing it')
  shutil.rmtree(cache);cache.mkdir(parents=True)
 stamp.write_text(sig);save(cache/'preflight.json',dict(sources=checks,status='passed',editor_listening_attestation=False));audio=cache/'mixed-normalized.wav'
 if not audio.exists():audio=normalized_audio(plan,cache)
 output=ROOT/'exports/jetkids-interview-edits'/plan['id'];output.mkdir(parents=True,exist_ok=True)
 for fmt in formats or ['portrait']:
  dest=output/(fmt+'.mp4')
  if dest.exists() and not replace_current:raise ValueError('Current export already exists; use --replace-current: '+str(dest))
  target=dest.with_name(fmt+'.pending.mp4')
  work=cache/fmt;work.mkdir(exist_ok=True);shots=plan['formats'][fmt]['shots'];segments=[];w,h=(1920,1080) if fmt=='landscape' else (1080,1920)
  for i,s in enumerate(shots):
   tail=transition(shots[i+1])[1] if i+1<len(shots) else 0;s=dict(s,renderFrames=s['frames']+tail);p=work/f'{i:03}.mp4'
   if not p.exists():
    vf=crop_filter(plan,s,fmt,checks)
    if i==0:vf+=',fade=t=in:st=0:d=0.12'
    if i==len(shots)-1:vf+=f",fade=t=out:st={s['frames']/30-.16}:d=0.16"
    run(['-threads','2','-filter_threads','2','-ss',s['in'],'-i',plan['sources'][s['source_id']]['path'],'-an','-vf',vf,'-r','30','-fps_mode','cfr','-frames:v',s['renderFrames'],'-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-y',p])
   segments.append(p);print(plan['id'],fmt,'shot',i,s['source_id'],flush=True)
  pieces=assemble(segments,shots,work);ending=work/'ending.mp4'
  if not ending.exists():run(['-loop','1','-i',plan['logo'],'-an','-vf',f'scale={560 if fmt=="portrait" else 620}:-2,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fade=t=in:st=0:d=0.2,format=yuv420p','-r','30','-frames:v',plan['logoFrames'],'-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-y',ending])
  pieces.append(ending);listing=work/'concat.txt';listing.write_text(''.join("file '"+str(p)+"'\n" for p in pieces));silent=work/'silent.mp4';run(['-f','concat','-safe','0','-i',listing,'-c','copy','-y',silent])
  v,m,groups=finish_picture(plan,words,fmt,work,audio,target)
  os.replace(target,dest)
  save(work/'qa.json',dict(path=str(dest),sha256=digest(dest),frames=int(v['nb_frames']),full_decode='passed',loudness=m,captions=len(groups),cornerLogoSha256=digest(corner_crest()),visual_review='Pending encoded frame review',listening_review='Not attested',status='Review draft'))
  print('EXPORTED',dest,flush=True)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);p.add_argument('--preflight',action='store_true');p.add_argument('--format',choices=['portrait','landscape'],default='portrait');p.add_argument('--replace-current',action='store_true',help='Rebuild the same edit and atomically replace its current export');p.add_argument('--refinish-current',action='store_true',help='Refresh captions/corner crest on unchanged cached picture, copying current encoded audio');a=p.parse_args()
 if a.preflight:
  plan,words,checks=preflight(a.project);print(json.dumps(dict(id=plan['id'],dialogueFrames=plan['dialogueFrames'],words=len(words),sources=checks),indent=2));return
 if a.refinish_current:refinish_current(a.project,a.format)
 else:render(a.project,[a.format] if a.format else None,replace_current=a.replace_current)
if __name__=='__main__':main()
