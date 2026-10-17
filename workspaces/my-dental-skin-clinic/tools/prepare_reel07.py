#!/usr/bin/env python3
"""Prepare a reviewable Reel-07 A-roll assembly; generated B-roll remains pending."""
import csv
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REEL = ROOT/'03_reels/reel-07'
CONFIG = json.loads((ROOT/'project.json').read_text())
FF = CONFIG['ffmpeg']
ROWS = json.loads((ROOT/'01_catalog/sources.json').read_text())
SOURCES = {r['filename'].split('_')[-2]:r for r in ROWS}


def run(args):
    p = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-5000:])
    return p.stdout


def main():
    for folder in ['01_selected_sources','02_alternate_sources','03_audio','04_timeline','05_broll_requests','06_brand']:
        (REEL/folder).mkdir(exist_ok=True)
    selected = [('0093','01_opening_and_missing_tooth_hook'),('0096','02_implant_bridge_removable_options'),('0097','03_clinical_condition_closing')]
    alternates = [('0092','opening_alternate_with_setup_chatter'),('0094','implant_pickup_ASR_unreliable'),('0095','short_pickup_ASR_unreliable')]
    for folder, items in [('01_selected_sources',selected),('02_alternate_sources',alternates)]:
        for number,label in items:
            target = REEL/folder/(label+'__'+number+'.MP4')
            if not target.exists():target.symlink_to(SOURCES[number]['paths'][0])
    logo = ROOT/'00_inbox/brand/my-dental-clinic-logo-original.png'
    if not (REEL/'06_brand/logo-original.png').exists():
        (REEL/'06_brand/logo-original.png').symlink_to(logo)
    brand = {'display_name':'My Dental Clinic','evidence':'supplied logo','logo':str(logo),'logo_resolution':[225,225],
             'accent':'#B36246','ink':'#20201E','paper':'#FFF9F2','dialogue_font':'Clinic Sans A / Manrope ExtraBold',
             'hindi_font':'Clinic Hindi / Noto Sans Devanagari Bold','logo_policy':'original retained; avoid large enlargement',
             'caption_policy':'warm white on charcoal backing; terracotta accents; 2–5 words per phrase; no added medical promises'}
    (REEL/'06_brand/brand.json').write_text(json.dumps(brand,indent=2)+'\n')
    # Broad speech boundaries and retained clinical context. Word-level final edits await audio/caption review.
    segments = [
        ('opening','0093',1.60,14.40,'Kaalratri / darkness and fear reference'),
        ('missing-tooth-hook','0093',14.90,22.65,'Missing tooth does not mean the story is over'),
        ('implant','0096',0.00,10.15,'Implant explanation'),
        ('bridge','0096',10.55,24.35,'Bridge explanation; retain the multiple-bridge qualification'),
        ('removable','0096',25.50,31.10,'Removable option qualification'),
        ('closing','0097',0.00,9.35,'Instagram versus clinical condition closing'),
    ]
    timeline=[];position=0
    for name,number,start,end,note in segments:
        r=SOURCES[number]
        # Later takes have substantial ceiling/wall; bottom anchored crop brings eyes into the upper half.
        crop = [1188,2112,270,520] if number=='0093' else [972,1728,249,1344]
        # Snap all durations to the 30 fps review timeline.
        duration=round((end-start)*30)/30
        timeline.append({'id':name,'clip_id':r['id'],'source':r['paths'][0],'source_in':start,'source_out':start+duration,
                         'timeline_in':round(position,3),'timeline_out':round(position+duration,3),
                         'crop_xywh':{'x':crop[2],'y':crop[3],'width':crop[0],'height':crop[1]},'note':note})
        position+=duration
    plan={'status':'A_ROLL_REVIEW_ASSEMBLY_BROLL_PENDING','fps':30,'canvas':[1080,1920],
          'duration_seconds':round(position,3),'transcript_status':'ASR draft; no human-listening verification available in this session',
          'segments':timeline,'broll_slots':[
              {'id':'B01','file':'reel-07_B01_implant_v01.mp4','source':'0096','source_in':3.2,'source_out':8.7,
               'timeline_in':round(timeline[2]['timeline_in']+3.2,3),'timeline_out':round(timeline[2]['timeline_in']+8.7,3)},
              {'id':'B02','file':'reel-07_B02_bridge_v01.mp4','source':'0096','source_in':13.3,'source_out':18.8,
               'timeline_in':round(timeline[3]['timeline_in']+13.3-10.55,3),'timeline_out':round(timeline[3]['timeline_in']+18.8-10.55,3)}]}
    (REEL/'04_timeline/edit-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    with (REEL/'04_timeline/selects.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['order','section','source','source_in','source_out','timeline_in','timeline_out','note'])
        for i,s in enumerate(timeline,1):w.writerow([i,s['id'],Path(s['source']).name,s['source_in'],s['source_out'],s['timeline_in'],s['timeline_out'],s['note']])
    # Reviewer labels are section headings, not unverified verbatim subtitles.
    events=[]
    labels={'opening':'कालरात्रि','missing-tooth-hook':'Missing tooth?','implant':'01  /  DENTAL IMPLANT',
            'bridge':'02  /  DENTAL BRIDGE','removable':'03  /  REMOVABLE OPTION','closing':'Clinical condition matters.'}
    def ts(t):
        return f'{int(t//3600)}:{int(t//60)%60:02}:{t%60:05.2f}'
    for s in timeline:
        font='Clinic Hindi' if s['id']=='opening' else 'Clinic Sans A'
        events.append(f"Dialogue: 0,{ts(s['timeline_in'])},{ts(s['timeline_out'])},Label,,0,0,0,,{{\\pos(510,1510)\\fn{font}\\fad(100,100)}}{labels[s['id']]}")
    ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Label,Clinic Sans A,58,&H00F2F9FF,&H00FFFFFF,&H0020201E,&H0020201E,-1,0,0,0,100,100,0,0,3,20,0,5,100,160,300,1
Style: Review,Clinic Sans B,24,&H00FFFFFF,&H00FFFFFF,&H0020201E,&H8020201E,0,0,0,0,100,100,0,0,1,2,0,7,60,60,60,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    ass+='\n'.join(events)+'\n'
    ass+=f'Dialogue: 1,0:00:00.00,{ts(position)},Review,,0,0,0,,{{\\pos(65,70)}}REEL 07  /  A-ROLL REVIEW  /  B-ROLL PENDING\n'
    ass_path=REEL/'04_timeline/review-labels.ass';ass_path.write_text(ass)
    cache=ROOT/'.cache/reel-07';cache.mkdir(exist_ok=True)
    for i,s in enumerate(timeline):
        target=cache/f'{i:02}.mp4'
        if target.exists():continue
        c=s['crop_xywh']
        vf=f"crop={c['width']}:{c['height']}:{c['x']}:{c['y']},scale=1080:1920,setsar=1,fps=30,format=yuv420p"
        run([FF,'-hide_banner','-loglevel','error','-nostdin','-y','-ss',s['source_in'],'-i',s['source'],'-t',s['source_out']-s['source_in'],
             '-vf',vf,'-af','highpass=f=70','-c:v','libx264','-preset','fast','-crf','20','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',target])
        print('Prepared review segment',s['id'],flush=True)
    listing=cache/'concat.txt';listing.write_text('\n'.join(f"file '{cache/f'{i:02}.mp4'}'" for i in range(len(timeline)))+'\n')
    assembled=cache/'assembly.mp4'
    run([FF,'-hide_banner','-loglevel','error','-nostdin','-y','-f','concat','-safe','0','-i',listing,'-c','copy',assembled])
    out=ROOT/'05_exports/review/reel-07_aroll-arranged_v01.mp4'
    run([FF,'-hide_banner','-loglevel','error','-nostdin','-y','-i',assembled,
         '-vf',f'ass=filename={ass_path}:fontsdir={ROOT/"assets/fonts/ready"}',
         '-af','loudnorm=I=-16:TP=-1.5:LRA=11','-c:v','libx264','-preset','fast','-crf','20','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',out])
    # Actual footage / font / logo placement sample; preserve supplied logo pixels.
    preview=REEL/'06_brand/style-preview.png'
    label=REEL/'06_brand/style-preview.ass'
    label.write_text(ass.split('[Events]')[0]+'''[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Label,,0,0,0,,{\\pos(510,1510)}DENTAL IMPLANT
''')
    run([FF,'-hide_banner','-loglevel','error','-y','-ss','5','-i',cache/'02.mp4','-i',logo,
         '-filter_complex',f'[1:v]crop=165:80:30:70,scale=248:120[mark];[0:v][mark]overlay=60:65,ass=filename={label}:fontsdir={ROOT/"assets/fonts/ready"}',
         '-frames:v','1',preview])
    print('Review assembly:',out,'duration',position,flush=True)


if __name__=='__main__':main()
