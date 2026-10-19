#!/usr/bin/env python3
"""Original source-derived transparent type cards, using bundled OFL fonts."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import clinic
ROOT=clinic.ROOT;OUT=ROOT/'assets/cutouts/dhiraj'
CARDS={'native-shopping-questions':['ज़रूरत है?','पहले से है?','Suit करेगा?'],
       'native-skin-types':['OILY','DRY','SENSITIVE'],
       'native-hair-terms':['HAIR FALL','BREAKAGE','THINNING'],
       'native-trust-knowledge':['TRUST','TECHNICAL KNOWLEDGE'],
       'native-price-pair':['₹1,700','₹1,000']}
def main():
    manifest=json.loads((OUT/'manifest.json').read_text());master=json.loads((ROOT/'assets/cutouts/manifest.json').read_text())
    for slug,lines in CARDS.items():
        image=Image.new('RGBA',(1000,840),(0,0,0,0));draw=ImageDraw.Draw(image)
        for index,line in enumerate(lines):
            y=40+index*230;draw.rounded_rectangle((32,y,968,y+190),radius=40,fill='#F7F3EA',outline='#C5B48E',width=4)
            draw.rounded_rectangle((52,y+20,68,y+170),radius=8,fill='#518278')
            filename='Mukta-ExtraBold.ttf' if any(ord(c)>127 for c in line) else 'ClinicMontserrat-ExtraBold.ttf'
            size=90
            while True:
                font=ImageFont.truetype(str(ROOT/'assets/fonts/ready'/filename),size)
                box=draw.textbbox((0,0),line,font=font)
                if box[2]-box[0]<=820:break
                size-=1
            draw.text((500-(box[2]-box[0])/2,y+95-(box[3]-box[1])/2-box[1]),line,font=font,fill='#162D36')
        path=OUT/(slug+'-v01.png');image.save(path);digest=hashlib.sha256(path.read_bytes()).hexdigest()
        record=next(r for r in manifest if r['id']==slug);record.update(sha256=digest,visual_reviewed=False)
        record['text']=lines;record['builder']='tools/build_dhiraj_elements.py'
        item=next(r for r in master['assets'] if r['path']==str(path.relative_to(ROOT)));item['sha256']=digest;item['visual_review']='Pending current native-card contact inspection'
    clinic.save(OUT/'manifest.json',manifest);clinic.save(ROOT/'assets/cutouts/manifest.json',master)
if __name__=='__main__':main()
