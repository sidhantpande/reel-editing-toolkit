import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Nio04Broll,Nio04Kind} from './Nio04Broll';
import {Nio07Broll,Nio07Kind} from './Nio07Broll';
import {StudyBroll,StudyKind} from './StudyBroll';
export type ComparisonKind='nio-story-comparison'|'nio-compare-board'|'nio-brand-services'|'nio-access-calendar';
const clamp=(x:number)=>Math.max(0,Math.min(1,x));const ease=(x:number)=>1-Math.pow(1-clamp(x),3);
const Board:React.FC<{calendar?:boolean}>=({calendar=false})=>{const f=useCurrentFrame(),ref=useRef<HTMLCanvasElement>(null);
 useLayoutEffect(()=>{const c=ref.current?.getContext('2d');if(!c)return;c.clearRect(0,0,1080,1220);c.save();c.beginPath();c.rect(0,0,1080,1210);c.clip();const p=ease(f/24),teal='#10A995',ink='#173239',paper='#FCFCF6';c.translate(540+Math.sin(f/60)*8,770+(1-p)*45-f*.055);c.rotate(-.045+Math.sin(f/100)*.007);c.scale(1+Math.min(f,300)*.00012,1+Math.min(f,300)*.00012);c.globalAlpha=p;
 const box=(x:number,y:number,w:number,h:number,color:string,r=8)=>{c.fillStyle=color;c.beginPath();c.roundRect(x,y,w,h,r);c.fill();};
 const line=(x:number,y:number,x2:number,y2:number,color:string,width=2)=>{c.strokeStyle=color;c.lineWidth=width;c.lineCap='round';c.beginPath();c.moveTo(x,y);c.lineTo(x2,y2);c.stroke();};
 c.shadowColor='#17323928';c.shadowBlur=30;c.shadowOffsetY=24;box(-310+14,-330+16,620,660,'#D8E2CE',16);box(-310,-330,620,660,paper,16);c.shadowColor='transparent';
 if(calendar){
  box(-310,-330,620,105,'#E0E8D9',16);box(-310,-274,620,49,'#E0E8D9',0);for(const x of [-195,195]){box(x-10,-365,20,72,ink,8);}c.font='600 37px Arial';c.textAlign='center';c.fillStyle=ink;c.fillText('OCT',0,-265);
  for(let i=0;i<35;i++){const x=-245+i%7*81,y=-155+Math.floor(i/7)*91,q=ease((f-10-Math.floor(i/7)*7)/20);c.globalAlpha=p*q;box(x-24,y-20,47,39,'#D9E3D0',5);}
  const q=ease((f-35)/28);c.globalAlpha=p*q;const x=-245,y=-155+3*91;box(x-33,y-28,65,55,teal,8);c.font='700 33px Arial';c.fillStyle=paper;c.fillText('22',x,y+10);
  const pulse=(Math.sin(f/20)+1)/2;c.strokeStyle=teal;c.lineWidth=3;c.globalAlpha=p*q*(1-pulse)*.7;c.beginPath();c.arc(x,y,42+pulse*20,0,Math.PI*2);c.stroke();
  c.globalAlpha=p;c.strokeStyle='#173239';c.lineWidth=3;c.beginPath();c.moveTo(70+Math.sin(f/42)*18,215+Math.cos(f/50)*10);c.lineTo(105+Math.sin(f/42)*18,250+Math.cos(f/50)*10);c.lineTo(86+Math.sin(f/42)*18,252+Math.cos(f/50)*10);c.lineTo(78+Math.sin(f/42)*18,275+Math.cos(f/50)*10);c.closePath();c.stroke();
 }else{
  c.font='600 32px Arial';c.textAlign='center';c.fillStyle=ink;c.fillText('A',20,-245);c.fillText('B',190,-245);line(-240,-207,250,-207,'#C0D0B4');line(-75,-285,-75,245,'#D5DFCC');line(105,-285,105,245,'#D5DFCC');
  const row=Math.floor(Math.max(0,f-35)/28)%6,column=Math.floor(Math.max(0,f-35)/168)%2;
  for(let i=0;i<6;i++){const q=ease((f-10-i*7)/24),y=-150+i*67;c.globalAlpha=p*q;line(-225,y,-110,y,'#B8C9AB',5);for(let j=0;j<2;j++){box(-45+j*175,y-20,125,38,'#EDF0E7',6);for(let k=0;k<5;k++){c.fillStyle='#C0CFB5';c.beginPath();c.arc(-27+j*175+k*22,y,3,0,Math.PI*2);c.fill();}}}
  c.globalAlpha=p;const x=-45+column*175,y=-150+row*67;c.strokeStyle=teal;c.lineWidth=3;c.beginPath();c.roundRect(x-7,y-26,139,50,8);c.stroke();const a=(f%28)/28;const px=x+93+Math.sin(f/40)*5,py=y+18+Math.sin(a*Math.PI)*7;c.fillStyle=ink;c.beginPath();c.moveTo(px,py);c.lineTo(px+21,py+27);c.lineTo(px+8,py+24);c.lineTo(px+4,py+35);c.closePath();c.fill();
  c.font='400 22px Arial';c.fillStyle='#8DA17D';c.fillText('Sample',0,290);
 }
 c.restore();},[f,calendar]);return <canvas ref={ref} width={1080} height={1220} style={{position:'absolute',top:0,left:0,width:1080,height:1220}}/>;};
export const ComparisonBroll:React.FC<{kind:ComparisonKind;transparent?:boolean;duration?:number;beats?:number[];labels?:string[]}>=({kind,transparent=false,duration=240,beats,labels})=>{const f=useCurrentFrame();const scenes=kind==='nio-story-comparison'?['nio-parents-credential','nio-parents-fees','nio-system-interview','nio-system-prep','nio-parents-conversation','nio-parents-outcomes','nio-compare-board']:labels?.length?labels:['nio-system-prep','nio-system-interview','nio-system-review'];const times=[0,...(beats?.length?beats:scenes.slice(1).map((_,i)=>Math.round((i+1)*duration/scenes.length)))];
 return <AbsoluteFill style={{background:transparent?'transparent':'#F2F3EF',overflow:'hidden'}}>
 {!transparent&&<AbsoluteFill style={{opacity:.045,backgroundImage:`url("${staticFile('assets/premium/textures/grain.svg')}")`,mixBlendMode:'multiply'}}/>}
 {kind==='nio-compare-board'||kind==='nio-access-calendar'?<Board calendar={kind==='nio-access-calendar'}/>:scenes.map((scene,i)=>{const from=times[i],next=times[i+1],alpha=(i?ease((f-from)/12):1)*(next===undefined?1:1-ease((f-next)/12));return <Sequence key={i} from={from} durationInFrames={Math.min(duration,next===undefined?duration:next+12)-from}><AbsoluteFill style={{opacity:alpha}}><div style={{position:'absolute',inset:0,height:1220,overflow:'hidden'}}><AbsoluteFill style={{transform:`translate(${Math.sin(f/65)*8}px,${-f*.025}px) scale(${1+Math.min(f,900)*.000025})`,transformOrigin:'540px 760px'}}>{scene.startsWith('nio-parents-')?<Nio04Broll kind={scene as Nio04Kind} transparent duration={duration}/>:scene.startsWith('nio-system-')?<Nio07Broll kind={scene as Nio07Kind} transparent duration={duration}/>:scene==='nio-compare-board'?<Board/>:<StudyBroll kind={scene as StudyKind} transparent duration={duration}/>}</AbsoluteFill></div></AbsoluteFill></Sequence>})}
 </AbsoluteFill>;
};
