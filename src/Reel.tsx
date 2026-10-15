import {Fonts} from './Fonts';
import {StillBlend} from './StillBlend';
import React from 'react';
import {AbsoluteFill,Audio,Img,OffthreadVideo,Sequence,staticFile,interpolate,useCurrentFrame,useVideoConfig} from 'remotion';
import {brands} from './brand';
import {Captions} from './Captions';
import {Broll} from './Broll';
import {ReelProps,Brand,BrollCue} from './types';
export const EndCard:React.FC<{brand:Brand}>=({brand})=>{const b=brands[brand];return brand==='atfro'?<AbsoluteFill style={{background:'#F1F0EB',alignItems:'center'}}><div style={{position:'absolute',top:820,width:860,height:280,overflow:'hidden'}}><Img src={staticFile(b.logo)} style={{position:'absolute',width:860,height:860,left:0,top:-290}}/></div></AbsoluteFill>:<AbsoluteFill style={{background:'#F2F3EF',alignItems:'center',justifyContent:'center'}}><Img src={staticFile(b.logo)} style={{width:850,height:850,objectFit:'contain'}}/></AbsoluteFill>};
const cueOpacity=(f:number,cue:BrollCue)=>{const fade=cue.fadeFrames??0;return fade?interpolate(f,[0,fade,cue.duration-fade,cue.duration],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}):1;};
const ClosingLayer:React.FC<{brand:Brand;fade:number}>=({brand,fade})=>{const f=useCurrentFrame();const t=fade?Math.min(1,f/fade):1;return <AbsoluteFill style={{opacity:t*t*(3-2*t)}}><EndCard brand={brand}/></AbsoluteFill>;};
const BrollLayer:React.FC<{cue:BrollCue;brand:Brand}>=({cue,brand})=>{const f=useCurrentFrame();const opacity=cueOpacity(f,cue);return <AbsoluteFill style={{opacity}}><Broll {...cue} brand={brand}/></AbsoluteFill>};
export const Reel:React.FC<ReelProps>=(p)=>{
 const {fps}=useVideoConfig(),frame=useCurrentFrame();const current=p.broll.find(c=>frame>=c.from&&frame<c.from+c.duration);const endCardFrom=p.endCardFrom??p.durationInFrames-2*fps;const endCardActive=!!p.endCard&&frame>=endCardFrom;const ink=(current&&!current.transparent&&cueOpacity(frame-current.from,current)>.55&&(current.kind.startsWith('paper-')||current.kind.startsWith('atfro-')||current.kind.startsWith('nio-parents-')||current.kind.startsWith('nio-system-')||current.kind.startsWith('nio-study-')||current.kind.startsWith('nio-intro-')||current.kind.startsWith('nio-mock-')||current.kind.startsWith('nio-story-')||current.kind.startsWith('nio-project-')||current.kind.startsWith('nio-compare-')||current.kind.startsWith('nio-brand-')||current.kind.startsWith('nio-access-')))||(endCardActive&&p.brand==='atfro');
 const duck=(f:number)=>{const fadeIn=p.smoothMusic?36:20,fadeOut=p.smoothMusic?65:30;const a=Math.min(1,Math.max(0,f/fadeIn)),z=Math.min(1,Math.max(0,(p.durationInFrames-f)/fadeOut));const envelope=p.smoothMusic?(a*a*(3-2*a))*(z*z*(3-2*z)):a*z;return (p.musicVolume??.12)*(p.smoothMusic?.35:p.clips.some(c=>f>=c.from&&f<c.from+c.duration)?.35:1)*envelope;};
 return <AbsoluteFill style={{background:brands[p.brand].bg}}><Fonts/>
 {p.clips.map((c,i)=><Sequence key={i} from={c.from} durationInFrames={c.duration}><OffthreadVideo src={staticFile(c.src)} trimBefore={c.trimBefore??0} volume={p.dialogueAudio?0:c.volume??1} style={{width:'100%',height:'100%',objectFit:'cover'}}/></Sequence>)}
 {p.cutBlends?.map((c,i)=><Sequence key={'blend'+i} from={c.from} durationInFrames={c.duration}><StillBlend src={c.src} duration={c.duration}/></Sequence>)}
 {p.endHoldImage&&p.endCard&&<Sequence from={endCardFrom} durationInFrames={p.durationInFrames-endCardFrom}><StillBlend src={p.endHoldImage}/></Sequence>}
 {p.bottomShade&&<AbsoluteFill style={{pointerEvents:'none',opacity:interpolate(frame,[0,18],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}}><div style={{position:'absolute',left:0,right:0,bottom:0,height:1220,background:'linear-gradient(to top, rgba(0,0,0,.90) 0%, rgba(0,0,0,.54) 35%, rgba(0,0,0,.16) 72%, rgba(0,0,0,0) 100%)',transform:`translateY(${interpolate(frame,[0,18],[50,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'})}px)`}}/></AbsoluteFill>}
 {p.broll.map((c,i)=><Sequence key={i} from={c.from} durationInFrames={c.duration}><BrollLayer cue={c} brand={p.brand}/></Sequence>)}
 {p.dips?.map((d,i)=>{const phase=(frame-d.from)/d.duration;return phase>=0&&phase<=1?<AbsoluteFill key={i} style={{background:'#030504',opacity:Math.sin(phase*Math.PI)*(d.strength??.6)}}/>:null})}
 {p.endCard&&<Sequence from={endCardFrom} durationInFrames={p.durationInFrames-endCardFrom}><ClosingLayer brand={p.brand} fade={p.endCardFadeFrames??0}/></Sequence>}
 <Captions pages={endCardActive?[]:p.captions} brand={p.brand} preset={p.captionPreset} tone={ink?'ink':'white'}/>
 {p.dialogueAudio&&<Audio src={staticFile(p.dialogueAudio)}/>}
 {p.music&&<Audio src={staticFile(p.music)} loop volume={duck}/>}
 {p.sfx?.map((s,i)=><Sequence key={i} from={s.from}><Audio src={staticFile(s.src)} volume={s.volume??.3}/></Sequence>)}
 </AbsoluteFill>;
};
