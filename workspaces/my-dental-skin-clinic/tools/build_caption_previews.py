#!/usr/bin/env python3
"""Build project-local font instances, reusable ASS presets and rendered samples."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / 'assets/fonts'
READY = FONTS / 'ready'
OUT = ROOT / 'previews/captions'
TEMPLATES = ROOT / 'templates/captions'
FF = json.loads((ROOT / 'project.json').read_text())['ffmpeg']


def instance(source, family, weight, italic=False):
    font = TTFont(source)
    axes = {a.axisTag: a.defaultValue for a in font['fvar'].axes}
    axes['wght'] = weight
    font = instantiateVariableFont(font, axes, inplace=False)
    style = ('Bold' if weight >= 700 else 'Medium') + (' Italic' if italic else '')
    # Private instance names avoid collisions with installed variable fonts.
    for name_id, value in {1: family, 2: style, 3: family + '-' + style,
                           4: family + ' ' + style, 6: (family + '-' + style).replace(' ', ''),
                           16: family, 17: style}.items():
        font['name'].removeNames(nameID=name_id)
        font['name'].setName(value, name_id, 3, 1, 0x409)
    font['OS/2'].usWeightClass = weight
    font['OS/2'].fsSelection &= ~((1 << 5) | (1 << 6))
    font['head'].macStyle &= ~1
    if weight >= 700:
        font['OS/2'].fsSelection |= 1 << 5
        font['head'].macStyle |= 1
    target = READY / ((family + '-' + style).replace(' ', '') + '.ttf')
    font.save(target)
    return target


def shell(args):
    subprocess.run([str(x) for x in args], check=True, capture_output=True)


def background(index, top, bottom):
    y, x = np.mgrid[0:1920, 0:1080]
    t = y[..., None] / 1920
    image = np.array(top) * (1-t) + np.array(bottom) * t
    glow = np.exp(-((x-730)**2/(2*310**2)+(y-680)**2/(2*500**2)))[..., None]
    image = np.uint8(np.clip(image + glow * np.array([16, 22, 20]), 0, 255))
    img = Image.fromarray(image)
    d = ImageDraw.Draw(img)
    regular = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 25)
    small = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 20)
    d.text((100, 130), f'0{index}  /  CAPTION STUDY', fill='#e4e6e3', font=regular)
    d.line((100, 190, 980, 190), fill='#6a7773', width=1)
    d.text((100, 222), 'MY DENTAL & SKIN', fill='#a2b3ad', font=small)
    d.text((100, 1620), 'SAMPLE COPY  /  FOOTAGE TO FOLLOW', fill='#a2b3ad', font=small)
    path = OUT / f'0{index}-background.png'
    img.save(path)
    return path


def ass(font, size, color, outline, shadow, body, extra=''):
    return f'''[Script Info]
Title: Clinic caption sample — replace copy and timing after audio review
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,{font},{size},{color},&H0000FFFF,&H00202020,&H70000000,-1,0,0,0,100,100,0,0,1,{outline},{shadow},5,110,160,340,1
{extra}
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:03.00,Caption,,0,0,0,,{{\\pos(510,1390)\\fad(100,120)}}{body}
'''


def main():
    READY.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    TEMPLATES.mkdir(parents=True, exist_ok=True)
    manrope = instance(next((FONTS/'manrope').glob('*.ttf')), 'Clinic Sans A', 800)
    jakarta = instance(FONTS/'plusjakartasans/PlusJakartaSans[wght].ttf', 'Clinic Sans B', 700)
    hindi = instance(next((FONTS/'notosansdevanagari').glob('*.ttf')), 'Clinic Hindi', 700)
    serif = instance(FONTS/'cormorantgaramond/CormorantGaramond-Italic[wght].ttf', 'Clinic Serif', 500, True)
    shutil.copy(FONTS/'barlowcondensed/BarlowCondensed-Bold.ttf', READY)
    for family in ['manrope','plusjakartasans','notosansdevanagari','cormorantgaramond','barlowcondensed']:
        shutil.copy(FONTS/family/'OFL.txt', READY/(family+'-OFL.txt'))

    styles = [
        {'id':'01-clean-clinic','title':'Clean clinic','fonts':'Manrope ExtraBold','font':'Clinic Sans A','size':84,
         'color':'&H00F9FAF7','outline':2,'shadow':1,
         'body':r'Healthy smile,\N{\c&H00CADB99&}confident you.',
         'top':(18,39,38),'bottom':(7,16,17), 'motion':'100 ms fade; phrase-level mint emphasis'},
        {'id':'02-bold-focus','title':'Bold word focus','fonts':'Barlow Condensed Bold','font':'Barlow Condensed','size':114,
         'color':'&H00FFFFFF','outline':3,'shadow':2,
         'body':r'{\fscx96\fscy96\t(0,140,\fscx100\fscy100)}SMILE WITH\N{\c&H00FFFFFF&\t(700,900,\c&H0092E9F4&)}CONFIDENCE.',
         'top':(28,36,45),'bottom':(9,13,18), 'motion':'140 ms 96→100% scale; one accent phrase'},
        {'id':'03-soft-editorial','title':'Soft editorial','fonts':'Plus Jakarta Sans + Cormorant Garamond','font':'Clinic Sans B','size':84,
         'color':'&H00E6EFF4','outline':0,'shadow':1,
         'body':r'Har skin ki\Nalag story.',
         'top':(68,48,44),'bottom':(24,19,23), 'motion':'Soft fade; serif for short headline only'},
        {'id':'04-hindi-clear','title':'Hindi clear','fonts':'Noto Sans Devanagari Bold','font':'Clinic Hindi','size':100,
         'color':'&H00FCFAF5','outline':2,'shadow':1,
         'body':r'आपकी मुस्कान,\N{\c&H00CADB99&}आपका आत्मविश्वास।',
         'top':(31,44,48),'bottom':(12,18,25), 'motion':'Phrase fade; full Devanagari shaping'},
    ]
    frames = []
    for i, s in enumerate(styles, 1):
        bg = background(i, s['top'], s['bottom'])
        content = ass(s['font'],s['size'],s['color'],s['outline'],s['shadow'],s['body'])
        if i == 3:
            content += r'Dialogue: 0,0:00:00.00,0:00:03.00,Caption,,0,0,0,,{\an5\pos(510,570)\fnClinic Serif\b0\i1\fs105\fad(200,180)}Your skin.\NYour routine.' + '\n'
        template = TEMPLATES/(s['id']+'.ass')
        template.write_text(content)
        vf = f'ass=filename={template}:fontsdir={READY}'
        video = OUT/(s['id']+'.mp4')
        shell([FF,'-hide_banner','-loglevel','error','-y','-loop','1','-i',bg,'-vf',vf,'-t','3','-r','30','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-an','-movflags','+faststart',video])
        frame = OUT/(s['id']+'.png')
        shell([FF,'-hide_banner','-loglevel','error','-y','-ss','1','-i',video,'-frames:v','1',frame])
        frames.append(frame)
        print('Rendered', s['id'], flush=True)
    concat = OUT/'concat.txt'
    concat.write_text('\n'.join(f"file '{(OUT/(s['id']+'.mp4')).as_posix()}'" for s in styles)+'\n')
    shell([FF,'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',concat,'-c','copy','-movflags','+faststart',OUT/'caption-styles.mp4'])
    board = Image.new('RGB',(1680,1150),'#f4f2ec')
    d = ImageDraw.Draw(board)
    heading = ImageFont.truetype(str(jakarta),54)
    label = ImageFont.truetype(str(jakarta),24)
    text = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',21)
    d.text((72,52),'Captions with a clinic feel.',font=heading,fill='#172727')
    d.text((74,130),'Four starting directions. Final colour, pacing and placement follow the real footage.',font=text,fill='#576360')
    for i,(s,frame) in enumerate(zip(styles,frames)):
        x=72+i*390
        with Image.open(frame) as image:
            board.paste(image.resize((360,640),Image.Resampling.LANCZOS),(x,200))
        d.text((x,866),f'0{i+1}  {s["title"]}',font=label,fill='#172727')
        names={'01-clean-clinic':'Manrope ExtraBold','02-bold-focus':'Barlow Condensed Bold','03-soft-editorial':'Plus Jakarta + Cormorant','04-hindi-clear':'Noto Sans Devanagari'}
        d.text((x,910),names[s['id']],font=text,fill='#576360')
    d.line((72,1000,1608,1000),fill='#c6cec8',width=1)
    d.text((72,1030),'Short phrases  /  restrained emphasis  /  reviewed timing  /  readable Hindi + English',font=text,fill='#576360')
    d.text((72,1072),'Sample copy only. Fonts and original open-source licences are stored with the project.',font=text,fill='#576360')
    board.save(OUT/'caption-style-board.png')
    (TEMPLATES/'presets.json').write_text(json.dumps({'canvas':[1080,1920],'caption_center':[510,1390],'max_lines':2,'target_words_per_phrase':[2,5],'source':'illustrative presets; replace text/timing after footage review','styles':styles},ensure_ascii=False,indent=2)+'\n')
    (READY/'derived-manifest.json').write_text(json.dumps([{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in READY.glob('*.ttf')],indent=2)+'\n')
    print(OUT/'caption-style-board.png')


if __name__ == '__main__':
    main()
