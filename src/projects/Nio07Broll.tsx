import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Img,staticFile,useCurrentFrame} from 'remotion';
export type Nio07Kind='nio-system-diagnostic'|'nio-system-prep'|'nio-system-review'|'nio-system-interview'|'nio-system-path';
const clamp=(x:number)=>Math.max(0,Math.min(1,x));const ease=(x:number)=>1-Math.pow(1-clamp(x),3);
const teal='#10A995',ink='#173239',paper='#FCFCF6';
const MotionArt:React.FC<{kind:Nio07Kind}>=({kind})=>{const f=useCurrentFrame(),ref=useRef<HTMLCanvasElement>(null);
 useLayoutEffect(()=>{const c=ref.current?.getContext('2d');if(!c)return;c.clearRect(0,0,1080,1220);c.save();c.beginPath();c.rect(0,0,1080,1210);c.clip();const drift=Math.min(f,360)/360;c.translate(540+Math.sin(f/60)*7,760-drift*12);c.scale(1+drift*.035,1+drift*.035);c.translate(-540,-760);const p=ease(f/25);
 const line=(pts:number[][],progress:number,color:string,width=3)=>{c.save();c.strokeStyle=color;c.lineWidth=width;c.lineCap='round';let len=0;for(let i=1;i<pts.length;i++)len+=Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]);let left=len*clamp(progress);c.beginPath();c.moveTo(pts[0][0],pts[0][1]);for(let i=1;i<pts.length&&left>0;i++){const a=pts[i-1],b=pts[i],d=Math.hypot(b[0]-a[0],b[1]-a[1]),q=Math.min(1,left/d);c.lineTo(a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q);left-=d;}c.stroke();c.restore();};
 const sheet=(x:number,y:number,w:number,h:number,r:number)=>{c.translate(x,y+(1-p)*45);c.rotate(r);c.globalAlpha=p;c.shadowColor='#17323926';c.shadowBlur=28;c.shadowOffsetY=25;c.fillStyle='#DDE2D7';c.beginPath();c.roundRect(-w/2+13,-h/2+16,w,h,14);c.fill();c.fillStyle=paper;c.beginPath();c.roundRect(-w/2,-h/2,w,h,14);c.fill();c.shadowColor='transparent';c.strokeStyle='#D6DDCE';c.lineWidth=1;c.stroke();};
 const circle=(x:number,y:number,r:number,fill:string)=>{c.fillStyle=fill;c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.fill();};
 if(kind==='nio-system-diagnostic'){
  c.save();sheet(505,785,560,620,-.07);line([[-200,-235],[-65,-235]],p,teal,8);line([[-200,-203],[100,-203]],p,'#C5CEC0',5);
  // Abstract diagnostic, no fabricated scores or student results.
  const center=[0,35],rad=175;c.strokeStyle='#D6DED0';c.lineWidth=2;
  for(const scale of [.33,.66,1]){c.beginPath();for(let i=0;i<6;i++){const a=-Math.PI/2+i*Math.PI/3,x=center[0]+Math.cos(a)*rad*scale,y=center[1]+Math.sin(a)*rad*scale;i?c.lineTo(x,y):c.moveTo(x,y);}c.closePath();c.stroke();}
  const q=ease((f-15)/40),values=[.82,.57,.74,.43,.7,.52];c.beginPath();for(let i=0;i<6;i++){const a=-Math.PI/2+i*Math.PI/3,x=Math.cos(a)*rad*values[i]*q,y=35+Math.sin(a)*rad*values[i]*q;i?c.lineTo(x,y):c.moveTo(x,y);}c.closePath();c.fillStyle='#10A99524';c.fill();c.strokeStyle=teal;c.lineWidth=4;c.stroke();
  for(let i=0;i<6;i++){const a=-Math.PI/2+i*Math.PI/3;circle(Math.cos(a)*rad*values[i]*q,35+Math.sin(a)*rad*values[i]*q,5,teal);}c.restore();
  c.save();c.globalAlpha=ease((f-25)/25);c.translate(780,1010+(1-ease((f-25)/25))*40);c.rotate(-.1);c.shadowColor='#17323935';c.shadowBlur=18;c.shadowOffsetY=15;circle(0,0,102,paper);c.shadowColor='transparent';c.strokeStyle='#BFCBB9';c.lineWidth=2;c.beginPath();c.arc(0,0,90,0,Math.PI*2);c.stroke();c.rotate(.35+Math.sin(f/40)*.08);c.fillStyle=teal;c.beginPath();c.moveTo(0,-65);c.lineTo(24,40);c.lineTo(0,25);c.lineTo(-24,40);c.closePath();c.fill();circle(0,0,7,ink);c.restore();
 }else if(kind==='nio-system-prep'){
  c.save();sheet(620,705,520,490,.075);line([[-185,-170],[-30,-170]],p,teal,7);
  for(let row=0;row<3;row++)for(let col=0;col<4;col++){const q=ease((f-10-row*7-col*5)/22),x=-180+col*105,y=-75+row*95;c.globalAlpha=p*q;c.fillStyle=row===1&&col===2?'#10A995':'#E6EADD';c.beginPath();c.roundRect(x,y,78,68,7);c.fill();if(row===1&&col===2)line([[x+18,y+34],[x+32,y+47],[x+59,y+20]],q,'#FFFFFF',4);}c.restore();
  c.globalAlpha=ease((f-30)/25);c.strokeStyle=teal;c.lineWidth=3;c.beginPath();c.ellipse(700,780,185,130,.13,-1.3,-1.3+Math.PI*2*ease((f-30)/35));c.stroke();
 }else if(kind==='nio-system-review'){
  c.save();sheet(450,790,500,620,-.09);line([[-175,-230],[-20,-230]],p,teal,7);
  for(let i=0;i<4;i++){const q=ease((f-9-i*11)/20),y=-120+i*100;c.globalAlpha=p*q;line([[-115,y],[145-(i%2)*50,y]],q,'#BDC8B7',6);c.strokeStyle=i===2?teal:'#B8C3B2';c.lineWidth=2;c.beginPath();c.roundRect(-180,y-16,32,32,4);c.stroke();line([[-174,y],[-165,y+8],[-153,y-9]],q,teal,3);}
  c.globalAlpha=p;c.strokeStyle='#10A99580';c.lineWidth=3;c.beginPath();c.ellipse(10,80,196,42,0,0,Math.PI*2*ease((f-45)/25));c.stroke();c.restore();
  c.save();const q=ease((f-18)/27);c.globalAlpha=q;c.translate(785,705+(1-q)*50);c.shadowColor='#17323930';c.shadowBlur=24;c.shadowOffsetY=22;circle(0,0,145,paper);c.shadowColor='transparent';c.strokeStyle='#BEC9B6';c.lineWidth=5;c.beginPath();c.arc(0,0,133,0,Math.PI*2);c.stroke();c.strokeStyle=teal;c.lineWidth=7;c.lineCap='round';c.beginPath();c.arc(0,0,120,-Math.PI/2,-Math.PI/2+Math.PI*1.4*ease((f-30)/55));c.stroke();for(let i=0;i<12;i++){const a=i*Math.PI/6;line([[Math.sin(a)*104,-Math.cos(a)*104],[Math.sin(a)*112,-Math.cos(a)*112]],1,'#A5B49A',2);}const a=.8+Math.max(0,f-18)*.019;line([[0,0],[Math.sin(a)*85,-Math.cos(a)*85]],1,ink,4);line([[0,0],[-30,-40]],1,ink,5);circle(0,0,7,teal);c.fillStyle=paper;c.beginPath();c.roundRect(-30,-172,60,25,5);c.fill();c.strokeStyle='#BEC9B6';c.stroke();c.restore();
 }else if(kind==='nio-system-interview'){
  for(let i=0;i<2;i++){const q=ease((f-i*10)/24);c.save();c.globalAlpha=q;c.translate(290+i*475+Math.sin(f/55+i)*9,460+(1-q)*35+Math.sin(f/40+i)*5);c.rotate(i===0?-.05:.06);c.fillStyle=paper;c.shadowColor='#17323925';c.shadowBlur=24;c.shadowOffsetY=18;c.beginPath();c.roundRect(-130,-55,260,120,18);c.fill();c.beginPath();c.moveTo(-20,65);c.lineTo(-30,95);c.lineTo(20,65);c.fill();c.shadowColor='transparent';for(let j=0;j<2;j++)line([[-85,-15+j*30],[80-j*40,-15+j*30]],ease((f-12-i*10)/25),j===0?teal:'#C0CBB8',4);for(let j=0;j<3;j++){c.globalAlpha=q*(.35+.65*(.5+.5*Math.sin(f/8-j*1.1-i*2)));circle(-30+j*30,32,4,teal);}c.restore();}line([[395,1050],[540,1080],[685,1050]],ease((f-30)/35),'#10A99566',3);
 }else{
  // Four tactile checkpoints resolve into one continuous route.
  const xs=[240,440,640,840],ys=[930,810,690,570];line(xs.map((x,i)=>[x,ys[i]]),ease((f-8)/55),'#10A99566',4);
  for(let i=0;i<4;i++){const q=ease((f-i*11)/26);c.save();c.globalAlpha=q;c.translate(xs[i],ys[i]+(1-q)*35);c.shadowColor='#1732392b';c.shadowBlur=20;c.shadowOffsetY=16;circle(0,0,88,paper);c.shadowColor='transparent';c.strokeStyle='#CED7C6';c.lineWidth=1;c.beginPath();c.arc(0,0,87,0,Math.PI*2);c.stroke();
   if(i===0){c.strokeStyle=teal;c.lineWidth=3;for(const r of [19,39,56]){c.beginPath();c.arc(0,0,r,0,Math.PI*2);c.stroke();}line([[0,0],[47,-46]],q,ink,4);}
   if(i===1){line([[-45,-38],[-3,-25],[-3,43],[-45,30],[-45,-38],[0,-25],[45,-38],[45,30],[0,43]],q,teal,4);}
   if(i===2){c.strokeStyle=teal;c.lineWidth=4;c.beginPath();c.arc(0,3,45,0,Math.PI*2);c.stroke();line([[0,-42],[0,-56],[-14,-56],[14,-56]],q,teal,4);line([[0,3],[0,-24],[20,-24]],q,ink,4);}
   if(i===3){c.strokeStyle=teal;c.lineWidth=4;c.beginPath();c.roundRect(-45,-34,90,58,9);c.stroke();line([[-20,24],[-27,44],[5,24]],q,teal,4);for(let j=0;j<3;j++)circle(-20+j*20,-5,4,teal);}
   c.restore();}
 }
 c.restore();},[f,kind]);return <canvas ref={ref} width={1080} height={1220} style={{position:'absolute',left:0,top:0,width:1080,height:1220}}/>;};
export const Nio07Broll:React.FC<{kind:Nio07Kind;transparent?:boolean;duration?:number}>=({kind,transparent=false})=>{const f=useCurrentFrame(),p=ease(f/25);return <AbsoluteFill style={{background:transparent?'transparent':'#F2F3EF',overflow:'hidden'}}>
 {!transparent&&<AbsoluteFill style={{opacity:.045,backgroundImage:`url("${staticFile('assets/premium/textures/grain.svg')}")`,mixBlendMode:'multiply'}}/>}
 <div style={{position:'absolute',left:100,right:100,top:350,height:850,opacity:.12,backgroundImage:'radial-gradient(#173239 1px,transparent 1px)',backgroundSize:'28px 28px',maskImage:'radial-gradient(ellipse,#000a,transparent 67%)'}}/>
 <MotionArt kind={kind}/>
 <div style={{position:'absolute',top:0,left:0,right:0,height:1220,overflow:'hidden'}}>
 {kind==='nio-system-prep'&&<Img src={staticFile('assets/premium/cutouts/open-book.png')} style={{position:'absolute',left:80,top:740,width:570,height:460,objectFit:'contain',opacity:p,transform:`translateY(${(1-p)*50}px) rotate(-8deg)`,filter:'drop-shadow(10px 24px 20px #17323929)'}}/>}
 {kind==='nio-system-interview'&&[0,1].map(i=><Img key={i} src={staticFile(`assets/premium/cutouts/${i?'paper-student':'editorial-person'}.png`)} style={{position:'absolute',left:110+i*470,top:565,width:400,height:630,objectFit:'contain',opacity:ease((f-i*8)/25),transform:`translateY(${(1-ease((f-i*8)/25))*45+Math.sin(f/42+i)*6}px) rotate(${(i?3:-3)+Math.sin(f/65+i)*.6}deg) scaleX(${i?-1:1})`,filter:'drop-shadow(10px 22px 18px #17323925)'}}/>)}
 </div>
 </AbsoluteFill>;};
