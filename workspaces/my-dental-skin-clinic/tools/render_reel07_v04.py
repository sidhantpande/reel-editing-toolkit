#!/usr/bin/env python3
"""Compact glyph-measured Mukta/Montserrat kinetic captions."""
import json,math,re,shutil,subprocess,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
import render_reel07_v03 as v3

R=v3.R;REEL=v3.REEL;FF=v3.FF;CACHE=R/'.cache/reel-07-v04'
OUT=REEL/'04_timeline/v04'
READY=R/'assets/fonts/ready'

def prepare_fonts():
 source=next((R/'assets/fonts/montserrat').glob('*.ttf'))
 f=instantiateVariableFont(TTFont(source),{'wght':800},inplace=False)
 for key,value in {1:'Clinic Montserrat',2:'ExtraBold',3:'ClinicMontserrat-ExtraBold',4:'Clinic Montserrat ExtraBold',6:'ClinicMontserrat-ExtraBold',16:'Clinic Montserrat',17:'ExtraBold'}.items():
  f['name'].removeNames(nameID=key);f['name'].setName(value,key,3,1,0x409)
 f['OS/2'].usWeightClass=800;f['OS/2'].fsSelection=(f['OS/2'].fsSelection & ~(1<<6))|(1<<5);f['head'].macStyle|=1
 f.save(READY/'ClinicMontserrat-ExtraBold.ttf')
 shutil.copy2(R/'assets/fonts/mukta/Mukta-ExtraBold.ttf',READY/'Mukta-ExtraBold.ttf')
 shutil.copy2(R/'assets/fonts/mukta/OFL.txt',READY/'mukta-OFL.txt')
 shutil.copy2(R/'assets/fonts/montserrat/OFL.txt',READY/'montserrat-OFL.txt')

FONT_CACHE={}
STYLE={}
def glyph(word):
 latin=bool(re.fullmatch('[A-Za-z]+',word))
 key=word.lower() in v3.KEYS;emph=word.lower() in v3.EMPHASIS
 point=(118 if emph else (104 if key else 94)) if latin else (100 if emph else (90 if key else (68 if word in v3.CONNECT else 80)))
 path=READY/('ClinicMontserrat-ExtraBold.ttf' if latin else 'Mukta-ExtraBold.ttf')
 if (path,point) not in FONT_CACHE:FONT_CACHE[path,point]=ImageFont.truetype(str(path),point)
 font=FONT_CACHE[path,point];text=word.upper() if latin and key else word
 box=font.getbbox(text,anchor='ls',stroke_width=2)
 pad=8;w=box[2]-box[0];h=box[3]-box[1]
 image=Image.new('RGBA',(w+pad*2,h+pad*2),(0,0,0,0))
 origin=(pad-box[0],pad-box[1])
 shadow=Image.new('RGBA',image.size,(0,0,0,0));sd=ImageDraw.Draw(shadow)
 sd.text((origin[0],origin[1]+2),text,font=font,anchor='ls',fill=(0,0,0,165),stroke_width=2,stroke_fill=(0,0,0,140))
 image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(.8)))
 d=ImageDraw.Draw(image);colour=(255,240,58,255) if key else (255,255,255,255)
 d.text(origin,text,font=font,anchor='ls',fill=colour,stroke_width=2,stroke_fill=(32,32,32,235))
 return {'image':image,'box':box,'width':w,'ascent':-box[1],'descent':box[3],'point':point,'font':path.name,'display':text,'key':key,'emphasis':emph,'pad':pad}

def captions(plan):
 by_phrase=defaultdict(list)
 for word in plan['words']:by_phrase[word['phrase_id']].append(word)
 groups=list(by_phrase.values());assets=[];records=[]
 for k,group in enumerate(groups):
  gs=[glyph(w['text']) for w in group]
  gap=STYLE.get('caption',{}).get('ink_gap_px',11)
  def width(indices):return sum(gs[i]['width'] for i in indices)+gap*max(0,len(indices)-1)
  whole=list(range(len(group)))
  if len(group)==1 or width(whole)<=870:rows=[whole]
  else:
   options=[(list(range(j)),list(range(j,len(group)))) for j in range(1,len(group))]
   rows=min(options,key=lambda pair:max(width(pair[0]),width(pair[1]))+.12*abs(width(pair[0])-width(pair[1])))
  scales=[min(1,870/width(row)) for row in rows]
  dimensions=[(max(gs[i]['ascent'] for i in row)*scale,max(gs[i]['descent'] for i in row)*scale) for row,scale in zip(rows,scales)]
  row_gap=STYLE.get('caption',{}).get('line_gap_px',12)
  total=sum(a+d for a,d in dimensions)+row_gap*(len(rows)-1)
  top=STYLE.get('caption',{}).get('centre_y',1328)-1100-total/2
  start=min(w['start'] for w in group)
  next_start=groups[k+1][0]['start'] if k+1<len(groups) else plan['duration_seconds']
  end=min(plan['duration_seconds'],max(max(w['end'] for w in group)+.07,group[-1]['start']+.18),next_start-.018)
  reveals=[w['start']-.018 for w in group]
  for j in range(len(reveals)-1,-1,-1):
   reveals[j]=max(start,min(reveals[j],end-.11 if j==len(reveals)-1 else reveals[j+1]-.055))
  for row,(ascent,descent),scale in zip(rows,dimensions,scales):
   row_width=width(row)
   x=STYLE.get('caption',{}).get('centre_x',510)-row_width*scale/2;baseline=top+ascent
   for i in row:
    g=gs[i]
    base=g['image']
    if scale<1:base=base.resize((round(base.width*scale),round(base.height*scale)),Image.Resampling.LANCZOS)
    px=x-g['pad']*scale;py=baseline+g['box'][1]*scale-g['pad']*scale
    assets.append({'image':base,'x':px,'y':py,'start':reveals[i],'end':end,'emphasis':g['emphasis']})
    records.append({'word':group[i]['text'],'display':g['display'],'start':reveals[i],'end':end,'phrase':group[i]['phrase_id'],'font':g['font'],'point_size':g['point'],'ink_width':g['width']*scale,'x':x,'baseline':baseline,'row':len(records),'space_pixels':gap*scale})
    x+=(g['width']+gap)*scale
   top=baseline+descent+row_gap
 # Draw just the compact text region into an alpha movie, using the same glyph
 # bounds for measurement and rasterization. This avoids external renderer metrics.
 target=CACHE/'compact-word-captions.mov';width_px,height_px=1080,620
 cmd=[FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s',f'{width_px}x{height_px}','-r','30','-i','-','-an','-c:v','qtrle','-pix_fmt','argb',str(target)]
 process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 note_font=ImageFont.truetype(str(READY/'ClinicMontserrat-ExtraBold.ttf'),20)
 try:
  for frame in range(round(plan['duration_seconds']*30)):
   t=frame/30;canvas=Image.new('RGBA',(width_px,height_px),(0,0,0,0))
   for asset in assets:
    if not asset['start']<=t<asset['end']:continue
    age=t-asset['start'];tail=asset['end']-t
    initial=.87 if asset['emphasis'] else .93;peak=1.045 if asset['emphasis'] else 1.02
    if age<.095:
     z=min(1,age/.095);factor=initial+(peak-initial)*(1-(1-z)**3)
    elif age<.175:
     z=(age-.095)/.08;factor=peak+(1-peak)*(z*z*(3-2*z))
    else:factor=1
    image=asset['image']
    if factor!=1:image=image.resize((max(1,round(image.width*factor)),max(1,round(image.height*factor))),Image.Resampling.LANCZOS)
    opacity=min(1,age/.028,tail/.04)
    if opacity<1:
     image=image.copy();image.putalpha(image.getchannel('A').point(lambda p:round(p*opacity)))
    px=round(asset['x']+(asset['image'].width-image.width)/2)
    py=round(asset['y']+(asset['image'].height-image.height)/2)
    canvas.alpha_composite(image,(px,py))
   process.stdin.write(canvas.tobytes())
   if frame%300==0:print('Caption animation',round(t),'/',plan['duration_seconds'],'sec',flush=True)
  process.stdin.close();error=process.stderr.read();code=process.wait()
  if code:raise RuntimeError(error.decode()[-4000:])
 except BaseException:
  process.kill();raise
 (OUT/'caption-layout.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
 return target

def main():
 CACHE.mkdir(exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
 prepare_fonts();plan=json.loads(v3.PLAN.read_text())
 caption=CACHE/'compact-word-captions.mov' if '--reuse-captions' in sys.argv else captions(plan)
 deliveries=json.loads((REEL/'07_deliveries/deliveries.json').read_text())
 implant=deliveries[3]['path'];bridge=deliveries[2]['path']
 logo=R/'00_inbox/brand/my-dental-clinic-logo-transparent-v01.png'
 gradient=R/'.cache/reel-07-v03/caption-gradient.png'
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
  f'[brand][6:v]overlay=0:1100,fade=t=out:st={plan["duration_seconds"]-.1}:d=0.10,format=yuv420p[out]',
 ]
 (OUT/'filtergraph.txt').write_text(';\n'.join(graph)+'\n')
 output=R/'05_exports/review/reel-07_compact-captions_v04.mp4'
 v3.run([FF,'-v','error','-nostdin','-y','-i',R/'.cache/reel-07-v03/speech-picture.mp4','-i',R/'.cache/reel-07-v03/dialogue-48k-float.wav',
  '-ss','0.40','-t',ad,'-i',implant,'-ss','11.8','-t',bd,'-i',bridge,'-i',logo,'-i',gradient,'-i',caption,
  '-filter_complex',';'.join(graph),'-map','[out]','-map','1:a:0','-t',plan['duration_seconds'],
  '-af','highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11','-c:v','libx264','-preset','fast','-crf','18','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',output])
 print('Rendered',output,flush=True)

if __name__=='__main__':main()
