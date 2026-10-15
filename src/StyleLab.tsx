import {Fonts} from './Fonts';
import React from 'react';
import {AbsoluteFill,Sequence,Audio,staticFile,useCurrentFrame} from 'remotion';
import {Broll} from './Broll';
import {Captions} from './Captions';
import {brands,fontCSS} from './brand';
import {BrollKind,Page,Brand} from './types';
export const StyleLab:React.FC<{brand:Brand}>=({brand})=>{
 const f=useCurrentFrame(),b=brands[brand];
 const text=['A clearer path','starts with one','better question.'];
 const pages:Page[]=text.map((s,i)=>({startMs:i*1700,endMs:(i+1)*1700,words:s.split(' ').map((w,j)=>({text:w,startMs:i*1700+j*290,endMs:i*1700+(j+1)*290,emphasis:j===2}))}));
 return <AbsoluteFill style={{background:b.bg,color:b.light,fontFamily:b.font}}><Fonts/>
 <Sequence durationInFrames={180}><Broll brand={brand} kind="crowd" title="Make the words move."/><Captions brand={brand} pages={pages} preset="editorial"/></Sequence>
 {(['pathways','lead-flow','timeline','compare','countdown'] as BrollKind[]).map((kind,i)=><Sequence key={kind} from={180+i*180} durationInFrames={180}><Broll brand={brand} kind={kind} title={{pathways:'More options. Better paths.','lead-flow':'Give every next step an owner.',timeline:'Three moments. One clear story.',compare:'Build a base. Adapt the plan.',countdown:'Pause. Think it through.'}[kind as 'pathways'|'lead-flow'|'timeline'|'compare'|'countdown']}/></Sequence>)}
 <div style={{position:'absolute',left:90,top:140,fontSize:24,letterSpacing:6,color:b.highlight}}>MOTION LIBRARY / {b.name.toUpperCase()}</div>
 <div style={{position:'absolute',left:90,right:130,top:1610,fontSize:23,opacity:.6}}>STYLE TEST • ORIGINAL REUSABLE GRAPHICS</div>
 <div style={{position:'absolute',left:90,bottom:200,width:870,height:3,background:'#ffffff18'}}><div style={{height:3,width:`${f/1080*100}%`,background:b.accent}}/></div>
 <Audio src={staticFile('assets/music/calm-focus.wav')} loop volume={.6}/>
 {[0,180,360,540,720,900].map(n=><Sequence key={n} from={n}><Audio src={staticFile('assets/sfx/soft-whoosh.wav')} volume={.35}/></Sequence>)}
 </AbsoluteFill>;
};
