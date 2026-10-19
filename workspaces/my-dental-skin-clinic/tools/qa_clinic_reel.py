#!/usr/bin/env python3
"""Decode and measure a clinic review export; prepare phrase/cut contact sheets.

This records measured evidence. It never upgrades ASR to human listening or
marks a video approved merely because its numeric checks passed.
"""
import argparse,collections,hashlib,json,math,re,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import clinic
from finish_timing import finish_timing

def qa(plan_path,video,out,ending=False):
 plan=json.loads(plan_path.read_text());out.mkdir(parents=True,exist_ok=True)
 probe=clinic.probe(video);v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
 base=round(plan['duration_seconds']*30)
 expected=finish_timing(base,127)['total_frames'] if ending else base
 decode=subprocess.run([clinic.FF,'-hide_banner','-nostdin','-xerror','-i',str(video),'-vf','blackdetect=d=0.02:pix_th=0.08:pic_th=0.98','-af','ebur128=peak=true','-progress','pipe:1','-nostats','-f','null','-'],capture_output=True,text=True)
 (out/'decode-audio.txt').write_text(decode.stderr)
 frames=int(re.findall(r'frame=(\d+)',decode.stdout)[-1]) if re.findall(r'frame=(\d+)',decode.stdout) else None
 loudness=re.findall(r'Integrated loudness:\s+I:\s+(-?[\d.]+) LUFS',decode.stderr)
 peak=re.findall(r'True peak:\s+Peak:\s+(-?[\d.]+) dBFS',decode.stderr)
 assert decode.returncode==0,'Decode failed'
 assert frames==expected,f'Expected {expected} frames, got {frames}'
 assert (v['width'],v['height'])==(1080,1920),'Wrong canvas'
 assert v['avg_frame_rate']=='30/1','Wrong fps'
 grouped=collections.defaultdict(list)
 for w in plan['words']:grouped[w['phrase_id']].append(w)
 captures=[]
 layout_path=plan_path.parent/'caption-layout.json'
 layout=json.loads(layout_path.read_text()) if layout_path.is_file() else []
 for phrase,words in grouped.items():
  # Natural word ends can coincide with the next phrase. Sample the actual
  # rendered reveal/exit window, not a frame after the old group vanished.
  rendered=[w for w in layout if w['phrase']==phrase]
  if rendered:
   last=max(w['start'] for w in rendered);end=min(w['end'] for w in rendered)
   t=math.floor((last+min(.20,(end-last)*.5))*30)/30
  else:t=min(max(w['start'] for w in words)+.12,plan['duration_seconds']-.04)
  captures.append((t,phrase+' '+' '.join(w['text'] for w in words)))
 for i,s in enumerate(plan['segments'][1:],1):
  for delta in [-.1,0,.1]:captures.append((max(0,s['timeline_in']+delta),f'cut{i} {delta:+.1f}s'))
 for layer in plan.get('broll_slots',[])+plan.get('graphic_slots',[]):
  start,end=layer['timeline_in'],layer['timeline_out']
  for t,phase in [(start-.067,'before'),(start+.133,'in'),((start+end)/2,'mid'),(end-.133,'out'),(end+.067,'after')]:
   if 0<=t<plan['duration_seconds']:captures.append((t,layer['id']+' '+phase))
 if ending:
  for t in [plan['duration_seconds']-.2,plan['duration_seconds'],plan['duration_seconds']+.3,expected/30-.2]:captures.append((t,'ending'))
 font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',14)
 contacts=[];sheet=None
 for i,(t,label) in enumerate(captures):
  page=i//12;slot=i%12
  if slot==0:sheet=Image.new('RGB',(864,1284),'#171717');draw=ImageDraw.Draw(sheet)
  frame=out/f'frame-{i:03}.jpg'
  clinic.ff('-ss',t,'-i',video,'-frames:v','1','-vf','scale=216:384',frame)
  x=slot%4*216;y=slot//4*428
  with Image.open(frame) as image:sheet.paste(image,(x,y))
  draw.text((x+4,y+387),f'{t:.3f}s | {label[:25]}',font=font,fill='white')
  if slot==11 or i==len(captures)-1:
   target=out/f'contact-{page:02}.jpg';sheet.save(target,quality=94);contacts.append(str(target))
 with video.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
 report={'video':str(video.resolve()),'sha256':digest,'full_decode':'passed','frames':frames,'expected_frames':expected,'resolution':[v['width'],v['height']],'fps':v['avg_frame_rate'],'video_duration':v['duration'],'audio_duration':a['duration'],'integrated_lufs':float(loudness[-1]) if loudness else None,'true_peak_dbtp':float(peak[-1]) if peak else None,'caption_phrases':len(grouped),'contacts':contacts,'visual_review':'prepared / inspect contacts and motion','dialogue_review':'independent normalized ASR snippets; human listening still required','status':'review export / not final approval'}
 report['black_intervals']=[{'start':float(s),'end':float(e)} for s,e in re.findall(r'black_start:([\d.]+) black_end:([\d.]+)',decode.stderr)]
 clinic.save(out/'qa.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan',type=Path);p.add_argument('video',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--ending',action='store_true');a=p.parse_args();qa(a.plan,a.video,a.out,a.ending)
if __name__=='__main__':main()
