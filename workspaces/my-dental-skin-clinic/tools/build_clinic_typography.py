#!/usr/bin/env python3
"""Original transparent dimensional typography using the licensed clinic font."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import clinic

def build(text,output):
    font=ImageFont.truetype(str(clinic.ROOT/'assets/fonts/ready/ClinicMontserrat-ExtraBold.ttf'),720)
    box=font.getbbox(text,stroke_width=8)
    width,height=box[2]-box[0]+180,box[3]-box[1]+180
    origin=(90-box[0],80-box[1])
    image=Image.new('RGBA',(width,height),(0,0,0,0))
    shadow=Image.new('RGBA',image.size,(0,0,0,0))
    ImageDraw.Draw(shadow).text((origin[0]+20,origin[1]+28),text,font=font,fill=(15,68,65,90),stroke_width=8,stroke_fill=(15,68,65,70))
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(13)))
    draw=ImageDraw.Draw(image)
    for offset in range(18,0,-1):
        draw.text((origin[0]+offset,origin[1]+offset),text,font=font,fill='#2B7973',stroke_width=7,stroke_fill='#1D5F5A')
    draw.text(origin,text,font=font,fill='#FFF0B1',stroke_width=5,stroke_fill='#C6A75D')
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists():raise FileExistsError('Use a new versioned asset name')
    image.save(output)
    return {'id':output.stem,'path':str(output.relative_to(clinic.ROOT)),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
        'subject':'Dimensional numeral '+text,'source':'Original code-rendered typography using licensed Clinic Montserrat ExtraBold',
        'prompt':'Exact numeral '+text+'; ivory face, champagne edge and restrained teal depth; transparent background',
        'dimensions':list(image.size),'alpha_extrema':list(image.getchannel('A').getextrema()),'git_storage':'lfs',
        'visual_review':'Verify glyph shape and behind-person placement in encoded output'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('text');p.add_argument('output',type=Path);a=p.parse_args()
    print(json.dumps(build(a.text,a.output.resolve()),indent=2))
