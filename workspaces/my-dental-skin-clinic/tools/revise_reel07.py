#!/usr/bin/env python3
"""Reference-led review revision using supplied B-roll and a transparent logo."""
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
REEL = ROOT/'03_reels/reel-07'
FF = json.loads((ROOT/'project.json').read_text())['ffmpeg']
READY = ROOT/'assets/fonts/ready'
CACHE = ROOT/'.cache/reel-07-v02'
OUT = ROOT/'05_exports/review/reel-07_reference-cut_v02.mp4'


def run(args):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-7000:])
    return result.stdout


def heavy_hindi():
    source = next((ROOT/'assets/fonts/notosansdevanagari').glob('*.ttf'))
    font = TTFont(source)
    font = instantiateVariableFont(font, {'wght':900,'wdth':100}, inplace=False)
    family='Clinic Hindi Heavy'
    for key, value in {1:family,2:'Black',3:family+'-Black',4:family+' Black',6:'ClinicHindiHeavy-Black',16:family,17:'Black'}.items():
        font['name'].removeNames(nameID=key)
        font['name'].setName(value,key,3,1,0x409)
    font['OS/2'].usWeightClass=900
    font['OS/2'].fsSelection=(font['OS/2'].fsSelection & ~(1<<6)) | (1<<5)
    font['head'].macStyle |= 1
    font.save(READY/'ClinicHindiHeavy-Black.ttf')


def timestamp(t):
    return f'{int(t//3600)}:{int(t//60)%60:02}:{t%60:05.2f}'


def main():
    CACHE.mkdir(exist_ok=True)
    heavy_hindi()
    deliveries=json.loads((REEL/'07_deliveries/deliveries.json').read_text())
    implant=Path(deliveries[3]['path'])
    bridge=Path(deliveries[2]['path'])
    for source,name in [(implant,'reel-07_B01_implant_received.mp4'),(bridge,'reel-07_B02_bridge_received.mp4')]:
        target=ROOT/'04_generated_broll/approved'/name
        if not target.exists():shutil.copy2(source,target)

    # Reference 2 is the same clinic: white/yellow heavy phrases, no caption boxes.
    # These are edited keyword/phrase captions from ASR, not a claim of verified verbatim subtitles.
    cues=[
        (.20,2.95,'कालरात्रि',''),
        (3.55,5.55,'सबसे','FIERCE रूप'),
        (6.00,7.65,'उनका काम है',''),
        (7.65,9.30,'अंधेरा और','डर मिटाना'),
        (9.80,12.75,'आज हम','एक डर मिटाते हैं'),
        (13.15,16.10,'दाँत नहीं,','कहानी खत्म?'),
        (16.40,18.55,'ऐसा नहीं है',''),
        (18.60,20.50,'उसके','SOLUTIONS भी हैं'),
        (20.65,22.65,'एक OPTION','IMPLANT'),
        (22.65,24.30,'NEIGHBOURING','TOOTH'),
        (24.30,26.65,'DISTURB किए','बिना'),
        (26.65,27.55,'INDEPENDENTLY',''),
        (27.55,28.65,'IMPLANT PLACE','करके'),
        (28.65,30.60,'दाँत लगा','सकते हैं'),
        (30.80,32.90,'दूसरा OPTION','BRIDGE'),
        (33.00,34.50,'BRIDGE में','हम क्या करते हैं?'),
        (34.50,37.15,'आसपास के','दोनों दाँत'),
        (37.15,40.55,'MULTIPLE BRIDGES','भी हो सकते हैं'),
        (40.55,42.75,'आसपास के दाँत','जब हम USE करते हैं'),
        (42.75,44.40,'उसको हम','BRIDGES बोलते हैं'),
        (44.65,49.85,'REMOVABLE','तीसरा OPTION'),
        (50.20,52.55,'कौन सा','BEST है?'),
        (53.20,56.25,'INSTAGRAM','decide नहीं करेगा'),
        (56.25,57.70,'आपकी','CLINICAL CONDITION'),
        (57.70,59.40,'decide करेगी',''),
    ]
    # Mixed-script tokens use font-specific sizes to keep visual weight consistent.
    def line(text):
        import re
        parts=re.split(r'([A-Za-z][A-Za-z ]*[A-Za-z]|[A-Za-z])',text)
        return ''.join((r'{\fnClinic Sans A\fs'+('82' if len(p.strip())>=18 else '87')+'}'+p+r'{\fnClinic Hindi Heavy\fs119}') if re.fullmatch(r'[A-Za-z][A-Za-z ]*',p) else p for p in parts if p)
    ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Phrase,Clinic Hindi Heavy,119,&H00FFFFFF,&H003AF0FF,&H00202020,&H80000000,-1,0,0,0,100,100,0,0,1,2.4,2,5,105,150,320,1
Style: Note,Clinic Sans B,23,&H00FFFFFF,&H00FFFFFF,&H00303030,&H80000000,0,0,0,0,100,100,0,0,1,1,0,7,70,70,70,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    for start,end,white,yellow in cues:
        # Bold yellow second line; restrained 100 ms scale settle, no black rectangles.
        body=line(white)
        if yellow:body+=r'\N{\c&H003AF0FF&}'+line(yellow)
        elif white.isascii():body=r'{\c&H003AF0FF&}'+body
        tag=r'{\pos(510,1320)\fad(35,35)\fscx98\fscy98\t(0,100,\fscx100\fscy100)}'
        ass+=f'Dialogue: 0,{timestamp(start)},{timestamp(end)},Phrase,,0,0,0,,{tag}{body}\n'
    for start,end in [(23.733,29.233),(33.417,38.917)]:
        ass+=f'Dialogue: 1,{timestamp(start)},{timestamp(end)},Note,,0,0,0,,{{\pos(74,1670)}}3D illustration\n'
    caption=REEL/'04_timeline/reference-captions-v02.ass'
    caption.write_text(ass)
    (REEL/'04_timeline/reference-captions-v02.json').write_text(json.dumps({'status':'EDITED_PHRASE_CAPTIONS_ASR_DRAFT','style_reference':'delivery-02; restrained motion from delivery-01','cues':[{'start':a,'end':b,'white':c,'yellow':d} for a,b,c,d in cues]},ensure_ascii=False,indent=2)+'\n')
    gradient=Image.new('RGBA',(1080,1920),(0,0,0,0))
    draw=ImageDraw.Draw(gradient)
    for y in range(950,1920):
        alpha=min(155,round((y-950)*.19))
        draw.line((0,y,1079,y),fill=(0,0,0,alpha))
    gradient_path=CACHE/'caption-gradient.png';gradient.save(gradient_path)
    logo=ROOT/'00_inbox/brand/my-dental-clinic-logo-transparent-v01.png'
    graph=[
        '[0:v]eq=contrast=1.025:brightness=0.003:saturation=1.02,setsar=1[base]',
        '[1:v]fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,setpts=PTS-STARTPTS+23.733/TB[implant]',
        "[2:v]fps=30,split=2[bg0][fg0]",
        '[bg0]scale=1920:1920,crop=1080:1920,gblur=sigma=35[bg]',
        '[fg0]scale=1000:1000[fg]',
        '[bg][fg]overlay=40:310,setsar=1,setpts=PTS-STARTPTS+33.417/TB[bridge]',
        "[base][implant]overlay=0:0:enable='between(t,23.733,29.233)'[withimplant]",
        "[withimplant][bridge]overlay=0:0:enable='between(t,33.417,38.917)'[withbroll]",
        '[withbroll][4:v]overlay=0:0[shaded]',
        '[3:v]crop=1460:468:162:230,scale=270:-1,format=rgba[logo]',
        '[shaded][logo]overlay=405:75[branded]',
        f'[branded]ass=filename={caption}:fontsdir={READY},format=yuv420p[out]',
    ]
    (REEL/'04_timeline/reference-filtergraph-v02.txt').write_text(';\n'.join(graph)+'\n')
    run([FF,'-hide_banner','-loglevel','error','-nostdin','-y',
         '-i',ROOT/'.cache/reel-07/assembly.mp4',
         '-ss','0.40','-t','5.5','-i',implant,
         '-ss','11.8','-t','5.5','-i',bridge,
         '-i',logo,'-i',gradient_path,
         '-filter_complex',';'.join(graph),'-map','[out]','-map','0:a:0','-t','59.4',
         '-af','loudnorm=I=-16:TP=-1.5:LRA=11',
         '-c:v','libx264','-preset','fast','-crf','18','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',OUT])
    print(OUT,flush=True)


if __name__=='__main__':main()
