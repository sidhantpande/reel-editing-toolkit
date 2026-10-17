#!/usr/bin/env python3
"""Render pause-tightened footage, word entrances, variable typography and soft B-roll transitions."""
import json
import math
import re
import subprocess
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from PIL import Image,ImageDraw,ImageFont
from fontTools.ttLib import TTFont
import clinic

R=Path(__file__).resolve().parents[1]
REEL=R/'03_reels/reel-07'
PLAN=REEL/'04_timeline/v03/plan.json'
CACHE=R/'.cache/reel-07-v03'
READY=R/'assets/fonts/ready'
FF=clinic.FF

def run(args):
 p=subprocess.run([str(x) for x in args],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr[-7000:])
 return p.stdout

def ts(t):return f'{int(t//3600)}:{int(t//60)%60:02}:{t%60:05.2f}'

CONNECT={'को','के','का','है','हैं','हम','ये','यह','भी','तो','उसके','उसको','और','पे','सा','उनका','आपका','आपकी','में','या','बाद'}
KEYS={'कालरात्रि','fierce','रूप','अंधेरा','डर','दाँत','कहानी','खत्म','solutions','option','implant','neighbouring','tooth','disturb','independently','place','second','bridge','bridges','multiple','removable','third','permissible','best','instagram','clinical','condition','decide'}
EMPHASIS={'कालरात्रि','implant','bridge','bridges','removable','independently','instagram','clinical','condition','कहानी','खत्म','डर','दाँत'}
FONT_FACTORS={}

def advance(style):
 # libass sizes these fonts against Windows ascent/descent, whereas Pillow
 # measures against em size. Match libass advances so individually revealed
 # words have normal spacing rather than large invisible gaps.
 path=style['file']
 if path not in FONT_FACTORS:
  font=TTFont(path)
  FONT_FACTORS[path]=font['head'].unitsPerEm/(font['OS/2'].usWinAscent+font['OS/2'].usWinDescent)
 return ImageFont.truetype(str(path),style['size']).getlength(style['text'])*FONT_FACTORS[path]

def word_style(word):
 latin=bool(re.fullmatch('[A-Za-z]+',word))
 key=word.lower() in KEYS
 emph=word.lower() in EMPHASIS
 if latin:
  size=112 if emph else (98 if key else 85)
  family='Clinic Sans A';file=READY/'ClinicSansA-Bold.ttf'
  display=word.upper() if key else word
 else:
  size=143 if emph else (121 if key else (88 if word in CONNECT else 112))
  family='Clinic Hindi Heavy';file=READY/'ClinicHindiHeavy-Black.ttf';display=word
 return {'text':display,'size':size,'family':family,'file':file,'key':key,'emphasis':emph}

def build_captions(plan):
 groups=defaultdict(list)
 for w in plan['words']:groups[w['phrase_id']].append(w)
 ordered=list(groups.values())
 events=[];layout_records=[]
 for group_index,group in enumerate(ordered):
  styles=[word_style(w['text']) for w in group]
  # A short lead line and stronger second line mimic the supplied clinic reference.
  if len(group)==1:rows=[list(range(len(group)))]
  elif len(group)==2 and not any(s['key'] for s in styles):rows=[list(range(2))]
  else:
   first_key=next((i for i,s in enumerate(styles) if s['key']),-1)
   split=first_key if 0<first_key<=2 else max(1,len(group)//2)
   rows=[list(range(split)),list(range(split,len(group)))]
   def row_width(indices):
    return sum(advance(styles[i]) for i in indices)+22*max(0,len(indices)-1)
   if max(row_width(row) for row in rows)>1000:
    choices=[(list(range(k)),list(range(k,len(group)))) for k in range(1,len(group))]
    rows=min(choices,key=lambda pair:max(row_width(pair[0]),row_width(pair[1]))+.1*abs(row_width(pair[0])-row_width(pair[1])))
  start=min(w['start'] for w in group)
  natural_end=max(w['end'] for w in group)
  next_start=ordered[group_index+1][0]['start'] if group_index+1<len(ordered) else plan['duration_seconds']
  end=min(plan['duration_seconds'],max(natural_end+.07,group[-1]['start']+.18),next_start-.018)
  reveals=[w['start']-.018 for w in group]
  for j in range(len(reveals)-1,-1,-1):
   latest=end-.11 if j==len(reveals)-1 else reveals[j+1]-.055
   reveals[j]=max(start,min(reveals[j],latest))
  y_positions=[1330] if len(rows)==1 else [1255,1388]
  for row_i,indices in enumerate(rows):
   gap=22
   widths=[advance(styles[i]) for i in indices]
   width=sum(widths)+gap*(len(indices)-1)
   scale=min(1,875/width)
   x=510-(width*scale)/2
   for i,width in zip(indices,widths):
    style=styles[i];size=round(style['size']*scale);width*=scale
    cx=x+width/2;cy=y_positions[row_i]
    reveal=reveals[i]
    colour='&H003AF0FF&' if style['key'] else '&H00FFFFFF&'
    # Words remain fixed after entry: no row reflow or position jitter.
    initial=84 if style['emphasis'] else 90
    peak=105 if style['emphasis'] else 102
    end_time=max(reveal+.05,end)
    motion=(f'{{\\an5\\pos({cx:.1f},{cy})\\fn{style["family"]}\\fs{size}\\c{colour}'
            f'\\fscx{initial}\\fscy{initial}\\fad(32,42)'
            f'\\t(0,95,0.7,\\fscx{peak}\\fscy{peak})'
            f'\\t(95,175,1.4,\\fscx100\\fscy100)}}')
    events.append(f'Dialogue: 0,{ts(reveal)},{ts(end_time)},Word,,0,0,0,,{motion}{style["text"]}')
    layout_records.append({'word':group[i]['text'],'display':style['text'],'start':reveal,'end':end_time,'font_size':size,'x':cx,'y':cy,'phrase':group[i]['phrase_id'],'yellow':style['key']})
    x+=width+gap*scale
 for slot in plan['broll_slots']:
  events.append(f'Dialogue: 1,{ts(slot["timeline_in"])},{ts(slot["timeline_out"])},Note,,0,0,0,,{{\\pos(73,1680)}}3D illustration')
 header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,Clinic Hindi Heavy,112,&H00FFFFFF,&H003AF0FF,&H00252525,&H70000000,-1,0,0,0,100,100,0,0,1,2.2,1.5,5,70,140,300,1
Style: Note,Clinic Sans B,23,&H00FFFFFF,&H00FFFFFF,&H00333333,&H80000000,0,0,0,0,100,100,0,0,1,1,0,7,70,70,70,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
 path=REEL/'04_timeline/v03/word-captions.ass';path.write_text(header+'\n'.join(events)+'\n')
 (path.parent/'caption-layout.json').write_text(json.dumps(layout_records,ensure_ascii=False,indent=2)+'\n')
 return path

def main():
 CACHE.mkdir(parents=True,exist_ok=True)
 plan=json.loads(PLAN.read_text())
 caption=build_captions(plan)
 audio_sources={}
 for s in plan['segments']:
  if s['source_id'] not in audio_sources:
   raw=subprocess.check_output([FF,'-v','error','-i',s['source'],'-vn','-ar','48000','-ac','2','-f','f32le','-'])
   audio_sources[s['source_id']]=np.frombuffer(raw,dtype=np.float32).reshape(-1,2)
 audio_parts=[]
 for i,s in enumerate(plan['segments']):
  frames=round((s['timeline_out']-s['timeline_in'])*30)
  samples=frames*1600
  start=round(s['source_in']*48000)
  audio=audio_sources[s['source_id']][start:start+samples].copy()
  if len(audio)<samples:audio=np.pad(audio,((0,samples-len(audio)),(0,0)))
  fade=min(288,len(audio)//4) # 6 ms click-prevention, inside preserved padding.
  audio[:fade]*=np.linspace(0,1,fade)[:,None]
  audio[-fade:]*=np.linspace(1,0,fade)[:,None]
  audio_parts.append(audio)
  target=CACHE/f'run-{i:02}.mp4'
  if not target.exists():
   c=s['crop_xywh']
   vf=f'crop={c["width"]}:{c["height"]}:{c["x"]}:{c["y"]},scale=1080:1920,setsar=1,fps=30,format=yuv420p'
   run([FF,'-v','error','-nostdin','-y','-ss',s['source_in'],'-i',s['source'],'-an','-vf',vf,'-frames:v',frames,'-c:v','libx264','-preset','fast','-crf','18',target])
  print('Speech run',i+1,'of',len(plan['segments']),flush=True)
 audio_path=CACHE/'dialogue-48k-float.wav'
 wavfile.write(audio_path,48000,np.concatenate(audio_parts))
 listing=CACHE/'concat.txt'
 listing.write_text('\n'.join(f"file '{CACHE/f'run-{i:02}.mp4'}'" for i in range(len(plan['segments'])))+'\n')
 base=CACHE/'speech-picture.mp4'
 run([FF,'-v','error','-nostdin','-y','-f','concat','-safe','0','-i',listing,'-c','copy',base])
 deliveries=json.loads((REEL/'07_deliveries/deliveries.json').read_text())
 implant=deliveries[3]['path'];bridge=deliveries[2]['path']
 gradient=CACHE/'caption-gradient.png'
 if not gradient.exists():
  image=Image.new('RGBA',(1080,1920),(0,0,0,0));draw=ImageDraw.Draw(image)
  for y in range(1020,1920):draw.line((0,y,1079,y),fill=(0,0,0,min(145,round((y-1020)*.18))))
  image.save(gradient)
 logo=R/'00_inbox/brand/my-dental-clinic-logo-transparent-v01.png'
 a,b=plan['broll_slots'];ad=a['timeline_out']-a['timeline_in'];bd=b['timeline_out']-b['timeline_in']
 graph=[
  '[0:v]eq=contrast=1.025:brightness=0.003:saturation=1.02[base]',
  f'[2:v]fps=30,scale=1080:1920,setsar=1,format=rgba,fade=t=in:st=0:d=0.16:alpha=1,fade=t=out:st={ad-.16}:d=0.16:alpha=1,setpts=PTS-STARTPTS+{a["timeline_in"]}/TB[implant]',
  '[3:v]fps=30,split=2[bb][bf]',
  '[bb]scale=1920:1920,crop=1080:1920,gblur=sigma=35[bg]',
  '[bf]scale=1000:1000[fg]',
  f'[bg][fg]overlay=40:310,setsar=1,format=rgba,fade=t=in:st=0:d=0.16:alpha=1,fade=t=out:st={bd-.16}:d=0.16:alpha=1,setpts=PTS-STARTPTS+{b["timeline_in"]}/TB[bridge]',
  f'[base][implant]overlay=0:0:enable=between(t\\,{a["timeline_in"]}\\,{a["timeline_out"]})[bi]',
  f'[bi][bridge]overlay=0:0:enable=between(t\\,{b["timeline_in"]}\\,{b["timeline_out"]})[br]',
  '[br][5:v]overlay=0:0[shade]',
  '[4:v]crop=1460:468:162:230,scale=255:-1,format=rgba,split=2[logo][halo]',
  '[halo]lutrgb=r=255:g=255:b=255,gblur=sigma=1.3[whitehalo]',
  '[shade][whitehalo]overlay=65:65[under]',
  '[under][logo]overlay=65:65[brand]',
  f'[brand]ass=filename={caption}:fontsdir={READY},fade=t=out:st={plan["duration_seconds"]-.10}:d=0.10,format=yuv420p[out]',
 ]
 (REEL/'04_timeline/v03/filtergraph.txt').write_text(';\n'.join(graph)+'\n')
 output=R/'05_exports/review/reel-07_word-pop_v03.mp4'
 run([FF,'-v','error','-nostdin','-y','-i',base,'-i',audio_path,
      '-ss','0.40','-t',ad,'-i',implant,'-ss','11.8','-t',bd,'-i',bridge,
      '-i',logo,'-i',gradient,'-filter_complex',';'.join(graph),'-map','[out]','-map','1:a:0','-t',plan['duration_seconds'],
      '-af','highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11',
      '-c:v','libx264','-preset','fast','-crf','18','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',output])
 print('Rendered',output,flush=True)

if __name__=='__main__':main()
