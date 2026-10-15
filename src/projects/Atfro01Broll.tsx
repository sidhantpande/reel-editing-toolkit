import React from 'react';
import {AbsoluteFill,Img,interpolate,Easing,staticFile,useCurrentFrame} from 'remotion';
import {Fonts} from '../Fonts';
import {Atfro01Canvas} from './Atfro01Canvas';
export type Atfro01Kind='atfro-work'|'atfro-process';
const clamp={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
const rise=(f:number,start:number,d=18)=>interpolate(f,[start,start+d],[0,1],{...clamp,easing:Easing.bezier(.16,.8,.22,1)});
const premium=(name:string)=>staticFile(`assets/premium/cutouts/${name}.png`);
const project=(name:string)=>staticFile(`assets/projects/atfro-01/${name}`);
/** One visual at a time. Artwork is clipped above y=1220; captions live below y=1340. */
export const Atfro01Broll:React.FC<{kind:Atfro01Kind;beats?:number[];transparent?:boolean;duration?:number}>=({kind,beats,transparent=false})=>{
 const f=useCurrentFrame();const work=kind==='atfro-work';const entries=beats??(work?[0,83,139]:[0,40,112]);
 const objects=work?[
  {src:premium('open-book'),width:800,height:800,top:390,rotation:-6},
  {src:project('stethoscope.png'),width:670,height:670,top:430,rotation:8},
  {src:project('software-window.svg'),width:850,height:700,top:430,rotation:-4},
 ]:[
  {src:premium('compass'),width:690,height:690,top:430,rotation:-10},
  {src:project('software-window.svg'),width:850,height:700,top:430,rotation:-3},
  {src:premium('handshake'),width:1050,height:525,top:550,rotation:-4},
 ];
 // Start the first object with the scene. Subsequent objects replace it on the noun.
 const starts=[0,entries[1],entries[2]];
 return <AbsoluteFill style={{background:transparent?'transparent':'#F1F0EB',color:'#111A20',fontFamily:'Inter',overflow:'hidden'}}><Fonts/>
 {!transparent&&<AbsoluteFill style={{opacity:.045,backgroundImage:`url("${staticFile('assets/premium/textures/grain.svg')}")`,mixBlendMode:'multiply'}}/>}
 <div style={{position:'absolute',left:130,right:130,top:380,height:800,overflow:'hidden'}}>
  <div style={{position:'absolute',width:640,height:640,border:'1px solid #15221a19',borderRadius:'50%',left:90,top:60,transform:`scale(${.94+rise(f,0,50)*.06})`}}/>
  <div style={{position:'absolute',width:520,height:520,border:'1px solid #15221a12',borderRadius:'50%',left:150,top:120}}/>
  <div style={{position:'absolute',left:30,right:30,top:0,bottom:0,opacity:.17,backgroundImage:'radial-gradient(#15221a 1px,transparent 1px)',backgroundSize:'27px 27px',maskImage:'radial-gradient(ellipse,#0009,transparent 68%)'}}/>
  <div style={{position:'absolute',left:570,top:140,width:100,height:140,borderRadius:50,background:'#A9C448',opacity:.24,transform:'rotate(30deg)'}}/>
 </div>
 <Atfro01Canvas work={work} starts={starts}/>
 <div style={{position:'absolute',left:0,right:0,top:0,height:1220,overflow:'hidden',perspective:1400}}>
 {objects.map((o,i)=>{const start=starts[i],next=starts[i+1];const enter=rise(f,start,16);const exit=next===undefined?0:interpolate(f,[next,next+8],[0,1],clamp);if(f<start||exit>=1)return null;return <Img key={o.src+i} src={o.src} style={{position:'absolute',left:(1080-o.width)/2,top:o.top,width:o.width,height:o.height,objectFit:'contain',opacity:enter*(1-exit),transform:`translateY(${(1-enter)*48-exit*22}px) rotate(${o.rotation+(1-enter)*3}deg) rotateY(${(1-enter)*-12}deg) scale(${.97+enter*.03-exit*.025})`,filter:`blur(${(1-enter)*4+exit*3}px) drop-shadow(10px 28px 22px #0b132023)`}}/>})}
 </div>
 {/* A clear, quiet lower third is reserved exclusively for spoken captions. */}
 {!transparent&&<div style={{position:'absolute',left:160,right:160,top:1260,height:1,background:'#111a2015'}}/>}
 </AbsoluteFill>;
};
