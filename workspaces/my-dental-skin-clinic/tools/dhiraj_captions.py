#!/usr/bin/env python3
"""Phrase-directed typography: editorial, number, list, caution and advice beats."""
import copy, json, math, subprocess
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageDraw
import render_reel07_v04 as shared

R=shared.R;CACHE=None;OUT=None;STYLE={}
prepare_fonts=shared.prepare_fonts

def ease(t):return 1-(1-max(0,min(1,t)))**3

def captions(plan):
    groups=defaultdict(list)
    for word in plan['words']:groups[word['phrase_id']].append(word)
    groups=list(groups.values());assets=[];records=[];decor=[]
    for k,group in enumerate(groups):
        ident=group[0]['phrase_id'];scene=plan.get('caption_scenes',{}).get(ident,{})
        mode=scene.get('mode','editorial');config=copy.deepcopy(STYLE)
        config['caption']['accent_colour']=scene.get('accent','#E8C77A')
        # Most clauses stay quiet; selected beats get their own hierarchy.
        config['caption']['uppercase_keywords']=mode in ['number','stop','list','caution','advice','title']
        config['caption']['sizes']={'hindi':{'normal':83,'key':94,'emphasis':104,'connector':76},'english':{'normal':79,'key':90,'emphasis':108,'connector':76}}
        shared.STYLE=config;glyphs=[]
        for word in group:
            style=copy.deepcopy(config)
            scale=scene.get('size_scale',1)
            if mode=='number' and word['text'].isdigit():scale=1.95
            if mode in ['stop','advice']:scale*=1.14 if word.get('key') else 1
            for lang in style['caption']['sizes'].values():
                for role in lang:lang[role]=round(lang[role]*scale)
            shared.STYLE=style;glyphs.append(shared.glyph(word['text'],word))
        start=min(w['start'] for w in group);next_start=groups[k+1][0]['start'] if k+1<len(groups) else plan['duration_seconds']
        end=min(plan['duration_seconds'],max(w['end'] for w in group)+.13,next_start-.018)
        reveal=[max(start,w['start']-.018) for w in group]
        for j in range(len(reveal)-1,-1,-1):reveal[j]=max(start,min(reveal[j],end-.12 if j==len(reveal)-1 else reveal[j+1]-.04))
        gap=16;limit=840
        width=lambda row:sum(glyphs[i]['width'] for i in row)+gap*max(0,len(row)-1)
        rows=scene.get('rows')
        if rows is None:
            rows=[list(range(len(group)))]
            if width(rows[0])>limit:
                options=[(list(range(j)),list(range(j,len(group)))) for j in range(1,len(group))]
                rows=min(options,key=lambda pair:max(width(pair[0]),width(pair[1]))+.1*abs(width(pair[0])-width(pair[1])))
        assert sorted(i for row in rows for i in row)==list(range(len(group))),ident
        scales=[min(1,limit/width(row)) for row in rows]
        dims=[(max(glyphs[i]['ascent'] for i in row)*s,max(glyphs[i]['descent'] for i in row)*s) for row,s in zip(rows,scales)]
        linegap=18 if mode in ['list','caution','advice'] else 12
        total=sum(a+d for a,d in dims)+linegap*(len(rows)-1)
        cy=scene.get('centre_y',1360)-1100;top=cy-total/2
        fullwidth=max(width(row)*s for row,s in zip(rows,scales));left=510-fullwidth/2
        if mode in ['advice','stop']:
            decor.append(dict(mode=mode,start=start,end=end,left=left-28,top=top-22,width=fullwidth+56,height=total+44,accent=scene.get('accent','#E8C77A')))
        for row,(asc,desc),scale in zip(rows,dims,scales):
            rowwidth=width(row)*scale;x=(left if mode=='list' else 510-rowwidth/2);baseline=top+asc
            for i in row:
                g=glyphs[i];img=g['image']
                if scale<1:img=img.resize((round(img.width*scale),round(img.height*scale)),Image.Resampling.LANCZOS)
                a=dict(image=img,x=x-g['pad']*scale,y=baseline+g['box'][1]*scale-g['pad']*scale,start=reveal[i],end=end,mode=mode,entry=scene.get('entry','rise'),key=g['key'])
                assets.append(a);records.append(dict(word=group[i]['text'],display=g['display'],start=reveal[i],end=end,phrase=ident,mode=mode,font=g['font'],point_size=g['point'],ink_width=g['width']*scale,x=x,baseline=baseline+1100,space_pixels=gap*scale))
                if mode=='title' and g['key']:decor.append(dict(mode='underline',start=reveal[i]+.06,end=end,left=x,top=baseline+desc+8,width=g['width']*scale,height=4,accent=scene.get('accent','#E8C77A')))
                x+=(g['width']+gap)*scale
            top=baseline+desc+linegap
    target=CACHE/'editorial-word-captions.mov';partial=target.with_name(target.stem+'.partial.mov')
    cmd=[shared.FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1080x620','-r','30','-i','-','-an','-c:v','qtrle','-pix_fmt','argb',str(partial)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for frame in range(round(plan['duration_seconds']*30)):
            t=frame/30;canvas=Image.new('RGBA',(1080,620));draw=ImageDraw.Draw(canvas)
            for item in decor:
                if not item['start']<=t<item['end']:continue
                from PIL import ImageColor
                age=t-item['start'];op=min(1,age/.1,(item['end']-t)/.07);x=item['left'];y=item['top'];w=item['width'];h=item['height'];c=ImageColor.getrgb(item['accent'])
                if item['mode']=='underline':draw.rounded_rectangle((x,y,x+w*ease(age/.24),y+h),radius=2,fill=c+(round(220*op),))
                else:
                    draw.rounded_rectangle((x,y,x+w,y+h),radius=23,fill=(14,24,23,round(190*op)))
                    draw.rounded_rectangle((x,y+15,x+4,y+h-15),radius=2,fill=c+(round(255*op),))
            for asset in assets:
                if not asset['start']<=t<asset['end']:continue
                age=t-asset['start'];tail=asset['end']-t;img=asset['image'];factor=1;dx=0;dy=0
                if asset['mode'] in ['number','stop']:factor=.83+.17*ease(age/.19)
                elif asset['entry']=='slide':dx=-24*(1-ease(age/.22))
                elif asset['entry']=='settle':factor=1.035-.035*ease(age/.24)
                else:dy=13*(1-ease(age/.21))
                if factor!=1:img=img.resize((max(1,round(img.width*factor)),max(1,round(img.height*factor))),Image.Resampling.LANCZOS)
                op=min(1,age/.045,tail/.06)
                if op<1:img=img.copy();img.putalpha(img.getchannel('A').point(lambda p:round(p*op)))
                canvas.alpha_composite(img,(round(asset['x']+(asset['image'].width-img.width)/2+dx),round(asset['y']+(asset['image'].height-img.height)/2+dy)))
            proc.stdin.write(canvas.tobytes())
            if frame%300==0:print('Directed captions',frame/30,'/',plan['duration_seconds'],flush=True)
        proc.stdin.close();err=proc.stderr.read();code=proc.wait()
        if code:raise RuntimeError(err.decode()[-3000:])
        partial.replace(target)
    except BaseException:proc.kill();partial.unlink(missing_ok=True);raise
    (OUT/'caption-layout.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    return target
