import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Img,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Fonts} from '../Fonts';
export type Nio04Kind='nio-parents-credential-fees'|'nio-parents-authority'|'nio-parents-credential'|'nio-parents-fees'|'nio-parents-outcomes'|'nio-parents-conversation';
const clamp=(n:number)=>Math.max(0,Math.min(1,n));const ease=(n:number)=>1-Math.pow(1-clamp(n),3);
const NioArt:React.FC<{kind:Nio04Kind}>=({kind})=>{const f=useCurrentFrame();const ref=useRef<HTMLCanvasElement>(null);
 useLayoutEffect(()=>{const c=ref.current?.getContext('2d');if(!c)return;c.clearRect(0,0,1080,1220);const p=ease(f/24),teal='#10A995',ink='#10202A';
 const path=(pts:number[][],progress:number,color:string,width=2)=>{c.save();c.strokeStyle=color;c.lineWidth=width;c.lineCap='round';let len=0;for(let i=1;i<pts.length;i++)len+=Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]);let left=len*clamp(progress);c.beginPath();c.moveTo(pts[0][0],pts[0][1]);for(let i=1;i<pts.length&&left>0;i++){const a=pts[i-1],b=pts[i],d=Math.hypot(b[0]-a[0],b[1]-a[1]),q=Math.min(1,left/d);c.lineTo(a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q);left-=d;}c.stroke();c.restore();};
 c.globalAlpha=p;
 if(kind==='nio-parents-fees'||kind==='nio-parents-outcomes'){
  c.save();c.translate(540,785+(1-p)*40);c.rotate(-.055);c.shadowColor='#10202a22';c.shadowBlur=30;c.shadowOffsetY=24;
  c.fillStyle='#D9DED5';c.beginPath();c.roundRect(-304,-340,626,680,18);c.fill();c.fillStyle='#FBFCF6';c.beginPath();c.roundRect(-320,-356,626,680,18);c.fill();c.shadowColor='transparent';c.strokeStyle='#D6DDD0';c.lineWidth=1;c.stroke();
  if(kind==='nio-parents-fees'){
   c.save();c.translate(-190,-250);path([[0,0],[100,0]],p,teal,6);path([[0,24],[100,24]],p,teal,6);c.strokeStyle=teal;c.lineWidth=6;c.beginPath();c.moveTo(25,0);c.bezierCurveTo(105,0,100,85,8,85);c.lineTo(90,170);c.stroke();c.restore();
   for(let i=0;i<5;i++){const q=ease((f-12-i*9)/20);c.globalAlpha=p*q;c.fillStyle=i===4?'#10A995':'#C9D1C2';c.beginPath();c.roundRect(-225,-20+i*57,i===4?330:300-i%2*60,7,3);c.fill();c.beginPath();c.roundRect(160,-20+i*57,65,7,3);c.fill();}
   c.globalAlpha=p;c.strokeStyle='#8CA38155';c.lineWidth=1;c.beginPath();c.moveTo(-230,235);c.lineTo(230,235);c.stroke();
  }else{
   for(let row=0;row<3;row++)for(let col=0;col<5;col++){const q=ease((f-10-row*8-col*3)/17);c.globalAlpha=p*q;c.fillStyle=col===2?teal:'#40565C';c.beginPath();c.arc(-190+col*87,-170+row*110,14*q,0,Math.PI*2);c.fill();c.globalAlpha=p*q*.35;c.fillStyle='#83938A';c.beginPath();c.roundRect(-210+col*87,-142+row*110,40,5,2);c.fill();}
   c.globalAlpha=p;for(let i=0;i<3;i++){c.strokeStyle='#D0D8CB';c.lineWidth=2;c.beginPath();c.roundRect(-225+i*160,195,130,68,7);c.stroke();c.strokeStyle=teal;c.beginPath();c.moveTo(-190+i*160,195);c.lineTo(-190+i*160,179);c.lineTo(-135+i*160,179);c.lineTo(-135+i*160,195);c.stroke();}
  }c.restore();
  // Moving inspection lens: emphasizes checking the details, not a fabricated result.
  const t=ease((f-24)/55),x=kind==='nio-parents-fees'?740-70*t:650+60*Math.sin(t*1.4),y=kind==='nio-parents-fees'?800+120*t:720+100*t;
  c.save();c.globalAlpha=ease((f-22)/22);c.strokeStyle=ink;c.lineWidth=8;c.shadowColor='#10202a22';c.shadowBlur=20;c.shadowOffsetY=12;c.beginPath();c.arc(x,y,100,0,Math.PI*2);c.stroke();c.shadowColor='transparent';c.strokeStyle=teal;c.lineWidth=2;c.beginPath();c.arc(x,y,86,0,Math.PI*2);c.stroke();path([[x+72,y+72],[x+160,y+160]],1,ink,18);c.restore();
 }else if(kind==='nio-parents-conversation'){
  for(let i=0;i<2;i++){const q=ease((f-i*9)/24);c.save();c.globalAlpha=q;c.translate(270+i*510,470+(1-q)*24);c.rotate(i===0?-.07:.07);c.fillStyle='#FCFCF7';c.shadowColor='#10202a20';c.shadowBlur=20;c.shadowOffsetY=14;c.beginPath();c.roundRect(-125,-60,250,120,18);c.fill();c.beginPath();c.moveTo(-20,60);c.lineTo(-30,90);c.lineTo(25,60);c.closePath();c.fill();c.shadowColor='transparent';for(let j=0;j<2;j++)path([[-80,-18+j*28],[75-j*40,-18+j*28]],ease((f-15-i*12)/24),j===0?teal:'#B4BFB0',4);c.restore();}
  path([[430,875],[540,850],[650,875]],ease((f-30)/35),'#10A99555',2);
 }else{
  c.strokeStyle='#10A99535';c.lineWidth=2;c.beginPath();c.ellipse(540,825,390,280,-.15,-Math.PI/2,-Math.PI/2+Math.PI*2*p);c.stroke();const a=-1.5+f*.012;c.fillStyle=teal;c.beginPath();c.arc(540+390*Math.cos(a),825+280*Math.sin(a),7,0,Math.PI*2);c.fill();
  if(kind==='nio-parents-credential')path([[210,1115],[420,1115],[540,1080]],ease((f-24)/40),'#10A99555',2);
 }
 },[f,kind]);return <canvas ref={ref} width={1080} height={1220} style={{position:'absolute',left:0,top:0,width:1080,height:1220}}/>;};
export const Nio04Broll:React.FC<{kind:Nio04Kind;transparent?:boolean;duration?:number;beats?:number[]}>=({kind,transparent=false,duration=180,beats})=>{
 const f=useCurrentFrame(),p=ease(f/23);if(kind==='nio-parents-credential-fees'){const split=beats?.[0]??150;const t=ease((f-split)/12);return <AbsoluteFill style={{background:transparent?'transparent':'#F2F3EF'}}><AbsoluteFill style={{opacity:1-t}}><Nio04Broll kind="nio-parents-credential" transparent/></AbsoluteFill><Sequence from={split} durationInFrames={duration-split}><AbsoluteFill style={{opacity:t}}><Nio04Broll kind="nio-parents-fees" transparent/></AbsoluteFill></Sequence></AbsoluteFill>;}return <AbsoluteFill style={{background:transparent?'transparent':'#F2F3EF',overflow:'hidden'}}><Fonts/>
 {!transparent&&<AbsoluteFill style={{opacity:.045,backgroundImage:`url("${staticFile('assets/premium/textures/grain.svg')}")`,mixBlendMode:'multiply'}}/>}
 <div style={{position:'absolute',left:180,right:180,top:370,height:800,opacity:.13,backgroundImage:'radial-gradient(#16322D 1px,transparent 1px)',backgroundSize:'27px 27px',maskImage:'radial-gradient(ellipse,#0009,transparent 67%)'}}/>
 <NioArt kind={kind}/>
 <div style={{position:'absolute',left:0,right:0,top:0,height:1220,overflow:'hidden',perspective:1500}}>
 {(kind==='nio-parents-authority'||kind==='nio-parents-credential')&&<Img src={staticFile(`assets/projects/niolearn-04/${kind==='nio-parents-authority'?'campus':'credential'}.png`)} style={{position:'absolute',left:kind==='nio-parents-authority'?160:130,top:kind==='nio-parents-authority'?410:390,width:kind==='nio-parents-authority'?760:820,height:kind==='nio-parents-authority'?760:820,objectFit:'contain',opacity:p,transform:`translateY(${(1-p)*45}px) rotate(${kind==='nio-parents-authority'?-2:5}deg) rotateY(${(1-p)*-10}deg) scale(${.98+.02*p+Math.min(f,180)*.00006})`,filter:`blur(${(1-p)*4}px) drop-shadow(10px 27px 20px #10202a24)`}}/>}
 {kind==='nio-parents-conversation'&&[0,1].map(i=>{const q=ease((f-i*8)/23);return <Img key={i} src={staticFile('assets/premium/cutouts/paper-student.png')} style={{position:'absolute',left:140+i*420,top:570,width:380,height:620,objectFit:'contain',opacity:q,transform:`translateY(${(1-q)*40}px) scaleX(${i===0?1:-1}) rotate(${i===0?-4:4}deg)`,filter:'drop-shadow(10px 25px 18px #10202a20)'}}/>})}
 </div>
 {!transparent&&<div style={{position:'absolute',left:160,right:160,top:1260,height:1,background:'#10202a15'}}/>}
 </AbsoluteFill>;
};
