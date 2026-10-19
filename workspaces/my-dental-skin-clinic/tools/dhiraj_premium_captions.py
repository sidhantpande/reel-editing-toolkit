#!/usr/bin/env python3
"""Clean reference-led captions with semantic hierarchy and paper-aware contrast."""
import hashlib,json,re,subprocess
from collections import defaultdict
from PIL import Image,ImageColor,ImageDraw,ImageFilter,ImageFont
import render_reel07_v04 as shared

R=shared.R;CACHE=None;OUT=None;STYLE={};FONTS={}
def prepare_fonts():
    shared.prepare_fonts()
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont
    source=R/'assets/fonts/cormorantgaramond/CormorantGaramond-Italic[wght].ttf'
    target=R/'assets/fonts/ready/ClinicSerif-BoldItalic.ttf'
    if not target.exists():
        font=instantiateVariableFont(TTFont(source),{'wght':700},inplace=False)
        for key,value in {1:'Clinic Serif',2:'Bold Italic',3:'ClinicSerif-BoldItalic',4:'Clinic Serif Bold Italic',6:'ClinicSerif-BoldItalic',16:'Clinic Serif',17:'Bold Italic'}.items():
            font['name'].removeNames(nameID=key);font['name'].setName(value,key,3,1,0x409)
        font.recalcTimestamp=False;font.save(target)
    provenance={'file':str(target.relative_to(R)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source':str(source.relative_to(R)),'weight':700,'licence':'assets/fonts/cormorantgaramond/OFL.txt','tool':'fontTools static instancing; renamed Clinic Serif'}
    (target.parent/'dhiraj-serif-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')

def ease(t):return 1-(1-max(0,min(1,t)))**3

def glyph(text,font_path,size,colour,paper=False):
    key=(font_path,size)
    if key not in FONTS:FONTS[key]=ImageFont.truetype(str(R/font_path),size)
    font=FONTS[key];box=font.getbbox(text,anchor='ls');pad=20
    image=Image.new('RGBA',(box[2]-box[0]+pad*2,box[3]-box[1]+pad*2))
    xy=(pad-box[0],pad-box[1])
    if not paper:
        shadow=Image.new('RGBA',image.size);d=ImageDraw.Draw(shadow)
        d.text((xy[0],xy[1]+4),text,font=font,anchor='ls',fill=(0,0,0,160),stroke_width=1,stroke_fill=(0,0,0,70))
        image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(4)))
    d=ImageDraw.Draw(image);d.text(xy,text,font=font,anchor='ls',fill=ImageColor.getrgb(colour)+(255,))
    return dict(image=image,width=box[2]-box[0],ascent=-box[1],descent=box[3],box=box,pad=pad,font=font_path,size=size)

def layout(plan):
    groups=defaultdict(list)
    for w in plan['words']:groups[w['phrase_id']].append(w)
    groups=list(groups.values());assets=[];records=[];config=STYLE['caption']
    for k,group in enumerate(groups):
        ident=group[0]['phrase_id'];scene=plan.get('caption_scenes',{}).get(ident,{})
        main=set(scene.get('main',[]));accent=set(scene.get('accent',[]));serif=set(scene.get('serif',[]));gs=[]
        for i,word in enumerate(group):
            text=word['text'];latin=bool(re.search('[A-Za-z0-9]',text));is_main=i in main
            font=config['english_font' if latin else 'hindi_font']
            if i in serif:font=config['serif_font']
            size=(132 if i in serif else 114 if latin else 119) if is_main else (84 if latin else 88)
            if main and not is_main:size=74 if latin else 77
            if scene.get('hero') and is_main:size=158
            size=round(size*scene.get('size_scale',1))
            upper=scene.get('uppercase',False) and is_main and latin and i not in serif
            display=text.upper() if upper else text
            colour='#FFE29A' if i in accent else '#FFFFFF'
            g=glyph(display,font,size,colour);g['paper']=glyph(display,font,size,'#955719' if i in accent else '#16312D',True)['image']
            g['display']=display;g['accent']=i in accent;gs.append(g)
        gap=14;limit=828
        width=lambda row:sum(gs[i]['width'] for i in row)+gap*max(0,len(row)-1)
        rows=scene.get('rows')
        if rows is None:
            rows=[list(range(len(group)))]
            if width(rows[0])>limit:
                options=[(list(range(j)),list(range(j,len(group)))) for j in range(1,len(group))]
                rows=min(options,key=lambda pair:max(width(pair[0]),width(pair[1]))+.14*abs(width(pair[0])-width(pair[1])))
        if sorted(i for row in rows for i in row)!=list(range(len(group))):raise ValueError('Caption rows omit/duplicate words: '+ident)
        scales=[min(1,limit/width(row)) for row in rows]
        dims=[(max(gs[i]['ascent'] for i in row)*scale,max(gs[i]['descent'] for i in row)*scale) for row,scale in zip(rows,scales)]
        linegap=13;total=sum(a+d for a,d in dims)+linegap*(len(rows)-1)
        cy=scene.get('centre_y',1325)-1100;top=cy-total/2
        start=min(w['start'] for w in group);next_start=groups[k+1][0]['start'] if k+1<len(groups) else plan['duration_seconds']
        end=min(plan['duration_seconds'],max(max(w['end'] for w in group)+.12,group[-1]['start']+.20),next_start-.012)
        reveals=[max(start,w['start']-.012) for w in group]
        for i in range(len(reveals)-1,-1,-1):reveals[i]=max(start,min(reveals[i],end-.12 if i==len(reveals)-1 else reveals[i+1]-.045))
        for row,(asc,desc),scale in zip(rows,dims,scales):
            x=510-width(row)*scale/2;baseline=top+asc
            for i in row:
                g=gs[i];light=g['image'];dark=g['paper']
                if scale<1:
                    size=(round(light.width*scale),round(light.height*scale));light=light.resize(size,Image.Resampling.LANCZOS);dark=dark.resize(size,Image.Resampling.LANCZOS)
                assets.append(dict(light=light,paper=dark,x=x-g['pad']*scale,y=baseline+g['box'][1]*scale-g['pad']*scale,start=reveals[i],end=end,hero=scene.get('hero',False),blur_light=[light.filter(ImageFilter.GaussianBlur(s)) for s in [2.4,1.1]],blur_paper=[dark.filter(ImageFilter.GaussianBlur(s)) for s in [2.4,1.1]]))
                records.append(dict(word=group[i]['text'],display=g['display'],phrase=ident,start=reveals[i],end=end,font=g['font'],point_size=g['size'],ink_width=g['width']*scale,x=x,baseline=baseline+1100,main=i in main,accent=g['accent'],space_pixels=gap*scale))
                x+=(g['width']+gap)*scale
            top=baseline+desc+linegap
    return assets,records

def frame_at(plan,assets,t):
    paper=any(s['timeline_in']+.15<=t<s['timeline_out']-.10 for s in plan['broll_slots'])
    canvas=Image.new('RGBA',(1080,620))
    for asset in assets:
        if not asset['start']<=t<asset['end']:continue
        age=t-asset['start'];tail=asset['end']-t;key='paper' if paper else 'light'
        img=asset[key]
        if age<.045:img=asset['blur_'+key][0]
        elif age<.085:img=asset['blur_'+key][1]
        factor=.975+.025*ease(age/.22) if asset['hero'] else 1
        if factor!=1:img=img.resize((round(img.width*factor),round(img.height*factor)),Image.Resampling.LANCZOS)
        op=min(1,age/.055,tail/.055)
        if op<1:img=img.copy();img.putalpha(img.getchannel('A').point(lambda p:round(p*op)))
        rise=10*(1-ease(age/.19))
        canvas.alpha_composite(img,(round(asset['x']+(asset[key].width-img.width)/2),round(asset['y']+(asset[key].height-img.height)/2+rise)))
    return canvas

def captions(plan):
    assets,records=layout(plan);target=CACHE/'premium-word-captions.mov';partial=target.with_name(target.stem+'.partial.mov')
    process=subprocess.Popen([shared.FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgba','-s','1080x620','-r','30','-i','-','-an','-c:v','qtrle','-pix_fmt','argb',str(partial)],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for frame in range(round(plan['duration_seconds']*30)):
            process.stdin.write(frame_at(plan,assets,frame/30).tobytes())
            if frame%300==0:print('Premium captions',frame/30,'/',plan['duration_seconds'],flush=True)
        process.stdin.close();error=process.stderr.read();code=process.wait()
        if code:raise RuntimeError(error.decode()[-3000:])
        partial.replace(target)
    except BaseException:process.kill();partial.unlink(missing_ok=True);raise
    (OUT/'caption-layout.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    return target
