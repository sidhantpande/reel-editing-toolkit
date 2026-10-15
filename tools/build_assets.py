#!/usr/bin/env python3
"""Deterministic original vector/PNG overlays and synthesized audio; no scraped media."""
from pathlib import Path
import math,json,wave,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
R=Path(__file__).resolve().parents[1]; A=R/'public/assets'; E=A/'elements'; E.mkdir(parents=True,exist_ok=True)
paths={
'arrow-forward':'<path d="M60 256H440M320 130l126 126-126 126"/>',
'compass-route':'<circle cx="256" cy="256" r="188"/><path d="M320 180l-32 108-108 44 40-112z"/>',
'book-open':'<path d="M256 130v286M256 150Q150 80 50 130v260q100-50 206 20 106-70 206-20V130q-100-50-206 20z"/>',
'clock':'<circle cx="256" cy="256" r="190"/><path d="M256 110v150l100 55"/>',
'check-ring':'<circle cx="256" cy="256" r="190"/><path d="M145 260l75 75 150-160"/>',
'cursor':'<path d="M145 50v370l90-96 65 135 70-35-70-135 132-4z"/>',
'chat':'<path d="M70 80h372v270H210L70 440z"/><path d="M140 170h230M140 230h170"/>',
'calendar':'<rect x="70" y="100" width="372" height="340" rx="35"/><path d="M70 200h372M160 50v100M350 50v100M150 275h50M280 275h50M150 350h50"/>',
'growth-chart':'<path d="M65 60v390h390M100 365l95-110 90 45 150-185M335 115h100v100"/>',
'person':'<circle cx="256" cy="145" r="78"/><path d="M100 450v-50a156 156 0 01312 0v50z"/>',
'briefcase':'<rect x="55" y="160" width="402" height="270" rx="30"/><path d="M180 160V80h150v80M55 270q201 100 402 0M230 295h50"/>',
'lightbulb':'<path d="M190 370v-45a145 145 0 11132 0v45zM190 405h132M215 450h82M256 330V210M215 180l41 40 41-40"/>',
'network':'<circle cx="256" cy="256" r="60"/><circle cx="80" cy="80" r="35"/><circle cx="430" cy="80" r="35"/><circle cx="80" cy="430" r="35"/><circle cx="430" cy="430" r="35"/><path d="M110 110l100 100M400 110L300 210M110 400l100-100M400 400L300 300"/>',
'website':'<rect x="50" y="80" width="412" height="352" rx="28"/><path d="M50 160h412M100 120h10M150 120h10M200 120h10M100 220h120v150H100zM270 230h140M270 290h120M270 350h80"/>',
'microphone':'<rect x="190" y="40" width="132" height="270" rx="66"/><path d="M130 220v35a126 126 0 00252 0v-35M256 380v80M170 460h172"/>',
'sparkle':'<path d="M256 40l55 160 161 56-161 55-55 161-55-161L40 256l161-56z"/>'}
manifest=[]
for theme,color in [('teal','#10B39B'),('lime','#C4E54A'),('white','#F7F9FA')]:
 for name,body in paths.items():
  p=E/f'{name}-{theme}.svg';p.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" fill="none" stroke="{color}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')
  manifest.append({'id':f'{name}-{theme}','file':str(p.relative_to(R/'public')),'kind':'transparent-svg','source':'Original project geometry','tags':[name,theme]})
# True RGBA layered people for crowd/depth compositions.
for theme,c in [('navy',(11,19,32)),('teal',(16,179,155)),('lime',(196,229,74)),('white',(247,249,250))]:
 for style in ['glass-person','silhouette','glow-ring','soft-shadow']:
  im=Image.new('RGBA',(720,1000));d=ImageDraw.Draw(im)
  if style=='silhouette':
   d.ellipse((285,60,435,210),fill=c+(255,));d.rounded_rectangle((220,230,500,710),80,fill=c+(255,));d.rounded_rectangle((230,600,330,970),40,fill=c+(255,));d.rounded_rectangle((390,600,490,970),40,fill=c+(255,))
  elif style=='glass-person':
   for inset in range(115,0,-1):
    alpha=int(20+80*(1-inset/115));d.ellipse((230+inset,80+inset,490-inset,340-inset),fill=c+(alpha,))
   d.ellipse((230,80,490,340),outline=c+(150,),width=3);d.rounded_rectangle((80,400,640,1150),220,fill=c+(45,),outline=c+(110,),width=3)
   d.ellipse((305,192,315,202),fill=(255,255,255,240));d.ellipse((407,192,417,202),fill=(255,255,255,240));d.arc((327,220,395,255),0,180,fill=(255,255,255,200),width=3)
  elif style=='glow-ring':d.ellipse((80,220,640,780),outline=c+(200,),width=18);im=im.filter(ImageFilter.GaussianBlur(14))
  else:d.ellipse((80,750,640,850),fill=(0,0,0,80));im=im.filter(ImageFilter.GaussianBlur(28))
  p=E/f'{style}-{theme}.png';im.save(p);manifest.append({'id':p.stem,'file':str(p.relative_to(R/'public')),'kind':'transparent-png','source':'Original procedural artwork','tags':[style,theme]})
sr=48000;rng=np.random.default_rng(1941)
def wav(name,x,folder='sfx'):
 p=A/folder/(name+'.wav');p.parent.mkdir(exist_ok=True,parents=True);x=np.clip(x,-1,1);pcm=(x*32767).astype('<i2')
 with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(pcm.tobytes())
 manifest.append({'id':name,'file':str(p.relative_to(R/'public')),'kind':'original-synth-audio','source':'Deterministic numpy synthesis','peak_dbfs':round(20*np.log10(max(abs(x).max(),1e-8)),2)})
for name,dur in [('soft-whoosh',.5),('reverse-whoosh',.65),('whip',.23),('low-impact',.7),('caption-pop',.12),('ui-click',.07),('soft-tick',.05),('sparkle',.7),('riser',1.2),('transition-air',.45),('notification',.5),('page-turn',.3)]:
 t=np.arange(int(sr*dur))/sr;n=rng.normal(0,1,len(t));smooth=np.convolve(n,np.ones(13)/13,mode='same');env=np.sin(np.pi*t/dur)**2
 if 'whoosh' in name or name in ['whip','transition-air','page-turn','riser']:x=smooth*env*(t/dur if name=='riser' else 1)
 elif name=='low-impact':x=np.sin(2*np.pi*(65*t-25*t*t))*np.exp(-9*t)
 elif name in ['notification','sparkle']:x=(np.sin(2*np.pi*880*t)+.5*np.sin(2*np.pi*1320*t))*np.exp(-8*t)
 else:x=(np.sin(2*np.pi*(430*t-350*t*t))+.15*n)*np.exp(-65*t)
 x=x/max(abs(x).max(),1e-8)*.22;wav(name,x)
for name,notes in [('calm-focus',[48,55,60,64]),('soft-momentum',[45,52,57,60])]:
 dur=32;t=np.arange(sr*dur)/sr;x=np.zeros(len(t))
 for bar in range(8):
  for j,n in enumerate(notes):
   start=int((bar*4+j*.65)*sr);length=min(int(3*sr),len(t)-start);u=np.arange(length)/sr;hz=440*2**((n+12*(bar%2)-69)/12)
   x[start:start+length]+=(np.sin(2*np.pi*hz*u)+.18*np.sin(4*np.pi*hz*u))*(1-np.exp(-15*u))*np.exp(-2*u)*.045
 x*=np.minimum(t/2,1)*np.minimum((dur-t)/2,1);wav(name,x,'music')
for p in sorted((A/'broll').glob('*.webm')):
 manifest.append({'id':p.stem,'file':str(p.relative_to(R/'public')),'kind':'transparent-video','source':'Original src/Broll.tsx rendered via Remotion','tags':['broll','alpha',p.stem.split('-')[0]]})
for p in sorted((A/'premium/cutouts').glob('*.png')):
 manifest.append({'id':'premium-'+p.stem,'file':str(p.relative_to(R/'public')),'kind':'transparent-generated','source':'Original text-to-image asset via built-in ImageGen','promptFile':'docs/PREMIUM_ASSET_PROMPTS.json','tags':['premium','paper','cutout']})
for p in sorted((A/'premium/textures').glob('*.svg')):
 manifest.append({'id':'premium-'+p.stem,'file':str(p.relative_to(R/'public')),'kind':'transparent-svg','source':'Original procedural texture','tags':['premium','texture']})
# Reel-specific art and finished animation layers belong in the reusable library too.
for p in sorted((A/'projects').rglob('*')):
 if not p.is_file() or p.suffix not in ['.png','.svg','.webm']:continue
 kind={'.png':'transparent-generated','.svg':'transparent-svg','.webm':'transparent-video'}[p.suffix]
 manifest.append({'id':p.parent.name+'-'+p.stem,'file':str(p.relative_to(R/'public')),'kind':kind,'source':'Original reel-specific Canvas/SVG motion and project-generated cutouts','promptFile':f'projects/{p.parent.name.split("-")[0]}/{p.parent.name}/assets-provenance.json','tags':[p.parent.name.split('-')[0],'premium','reel-specific','canvas' if p.suffix=='.webm' else 'cutout']})
for p in sorted((A/'music').glob('*-bed*.wav')):
 manifest.append({'id':p.stem,'file':str(p.relative_to(R/'public')),'kind':'original-synth-audio','source':'Original project synthesized composition; per-reel provenance records continuous joining, filtering and dialogue-bed normalization','tags':['music',p.stem.split('-')[0],'dialogue-bed']})
for e in manifest:
 p=R/'public'/e['file'];e['bytes']=p.stat().st_size;e['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
(R/'catalog/assets.json').write_text(json.dumps(manifest,indent=2)+'\n');print(f'Built {len(manifest)} original reusable assets.')
