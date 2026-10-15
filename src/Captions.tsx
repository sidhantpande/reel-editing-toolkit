import React,{useEffect,useLayoutEffect,useRef,useState} from 'react';
import {continueRender,delayRender,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import {Brand,Page} from './types';
import {brands} from './brand';
const clamp=(n:number)=>Math.max(0,Math.min(1,n));
/** Canvas text avoids intermittent Chrome compositing loss of transformed HTML spans. */
export const Captions:React.FC<{pages:Page[];brand:Brand;preset?:'kinetic'|'clean'|'pill'|'editorial'|'reference';tone?:'white'|'ink'}>=({pages,brand,preset='reference',tone='white'})=>{
 const frame=useCurrentFrame(),{fps,width,height}=useVideoConfig();const ref=useRef<HTMLCanvasElement>(null);
 const [handle]=useState(()=>delayRender('Loading caption typeface'));const [ready,setReady]=useState(false);const released=useRef(false);
 useEffect(()=>{let live=true;const font=new FontFace('ReelCaption',`url(${staticFile('assets/fonts/Inter.ttf')})`,{weight:'100 900'});font.load().then(loaded=>{(document.fonts as FontFaceSet & {add:(font:FontFace)=>FontFaceSet}).add(loaded);if(live)setReady(true);}).catch(()=>{if(live)setReady(true);});return()=>{live=false;if(!released.current){released.current=true;continueRender(handle);}};},[handle]);
 useLayoutEffect(()=>{
  if(!ready)return;const c=ref.current?.getContext('2d');if(!c)return;c.clearRect(0,0,width,height);
  const page=pages.find(p=>frame>=Math.round(p.startMs/1000*fps)&&frame<Math.round(p.endMs/1000*fps));
  if(page){
   const base=page.fontSize??65,gap=preset==='reference'?15:14,maxWidth=920,center=540;
   const items=page.words.map(w=>{const size=base*(w.emphasis&&preset==='reference'?1.12:1);const font=`${w.emphasis?850:780} ${size}px ReelCaption, Inter, sans-serif`;c.font=font;return {w,size,font,width:c.measureText(w.text).width};});
   const lines:typeof items[]=[];let line:typeof items=[];let used=0;
   for(const item of items){if(line.length&&used+gap+item.width>maxWidth){lines.push(line);line=[];used=0;}used+=(line.length?gap:0)+item.width;line.push(item);}if(line.length)lines.push(line);
   let y=page.top??1230;const pageFade=1-clamp((frame/fps*1000-(page.endMs-75))/75)*.8;
   for(const row of lines){const rowWidth=row.reduce((n,item)=>n+item.width,0)+gap*(row.length-1);let x=center-rowWidth/2;const rowHeight=Math.max(...row.map(item=>item.size))*1.16;
    for(const item of row){const {w,size,font}=item;const elapsed=frame-Math.round(w.startMs/1000*fps);const visible=preset==='clean'||elapsed>=0;
     if(visible){const p=clamp(elapsed/8);const ease=1-Math.pow(1-p,3);const alpha=preset==='clean'?1:clamp(elapsed/3);const active=frame<Math.round(w.endMs/1000*fps);const scale=active?1.018:1;
      c.save();c.globalAlpha=alpha*pageFade;c.translate(x+item.width/2,y+(preset==='clean'?0:(1-ease)*23));c.scale(scale,scale);c.font=font;c.textAlign='left';c.textBaseline='top';
      if(preset==='pill'&&active){c.fillStyle=brands[brand].accent;c.beginPath();c.roundRect(-item.width/2-10,-5,item.width+20,size*1.2,12);c.fill();}
      c.fillStyle=w.accent?(brand==='niolearn'?(tone==='ink'?'#087F70':'#46DECA'):(tone==='ink'?'#586A12':'#D8F477')):(tone==='ink'?'#0B1320':'#FFFFFF');c.shadowColor=tone==='ink'?'#111a201a':'#000000b0';c.shadowBlur=tone==='ink'?9:13;c.shadowOffsetY=tone==='ink'?2:5;c.fillText(w.text,-item.width/2,0);c.restore();
     }x+=item.width+gap;
    }y+=rowHeight;
   }
  }
  if(!released.current){released.current=true;continueRender(handle);}
 },[ready,frame,fps,width,height,pages,brand,preset,tone,handle]);
 return <canvas ref={ref} width={width} height={height} style={{position:'absolute',left:0,top:0,width,height,zIndex:20,pointerEvents:'none'}}/>;
};
