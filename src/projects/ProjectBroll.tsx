import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,staticFile,useCurrentFrame} from 'remotion';
export type ProjectKind='nio-project-phone'|'nio-project-structure'|'nio-project-attendance';
const clamp=(x:number)=>Math.max(0,Math.min(1,x));const ease=(x:number)=>1-Math.pow(1-clamp(x),3);
export const ProjectBroll:React.FC<{kind:ProjectKind;transparent?:boolean;duration?:number}>=({kind,transparent=false,duration=180})=>{const f=useCurrentFrame(),ref=useRef<HTMLCanvasElement>(null);
 useLayoutEffect(()=>{const c=ref.current?.getContext('2d');if(!c)return;c.clearRect(0,0,1080,1220);c.save();c.beginPath();c.rect(0,0,1080,1210);c.clip();const p=ease(f/24),teal='#10A995',ink='#173239',ivory='#FCFCF6';const drift=Math.min(1,f/300);c.translate(540+Math.sin(f/65)*8,760-drift*15);c.scale(1+drift*.045,1+drift*.045);c.translate(-540,-760);
 const rect=(x:number,y:number,w:number,h:number,color:string,r=10)=>{c.fillStyle=color;c.beginPath();c.roundRect(x,y,w,h,r);c.fill();};
 const line=(a:number[][],q=1,color=teal,w=4)=>{c.save();c.strokeStyle=color;c.lineWidth=w;c.lineCap='round';let len=0;for(let i=1;i<a.length;i++)len+=Math.hypot(a[i][0]-a[i-1][0],a[i][1]-a[i-1][1]);let left=len*clamp(q);c.beginPath();c.moveTo(a[0][0],a[0][1]);for(let i=1;i<a.length&&left>0;i++){const x=a[i-1],y=a[i],d=Math.hypot(y[0]-x[0],y[1]-x[1]),t=Math.min(1,left/d);c.lineTo(x[0]+(y[0]-x[0])*t,x[1]+(y[1]-x[1])*t);left-=d;}c.stroke();c.restore();};
 const dot=(x:number,y:number,r:number,color:string)=>{c.fillStyle=color;c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.fill();};
 const shadow=()=>{c.shadowColor='#17323928';c.shadowBlur=25;c.shadowOffsetY=22;};
 const phone=(x:number,y:number,q:number,checked:boolean)=>{c.save();c.globalAlpha=q;c.translate(x,y+(1-q)*35);c.rotate(.045);shadow();rect(-150,-265,300,530,'#D8E0CE',32);rect(-141,-256,282,512,ivory,26);c.shadowColor='transparent';rect(-50,-238,100,13,'#BCCBB0',6);for(let i=0;i<4;i++){const a=ease((f-25-i*8)/25),yy=-125+i*80;c.globalAlpha=q*a;dot(-82,yy,18,'#D4DECA');line([[-45,yy-8],[80,yy-8]],1,'#BCCBB0',5);line([[-45,yy+11],[35,yy+11]],1,'#D2DCC7',4);if(checked&&i<Math.floor(Math.max(0,f-65)/16)%5){line([[68,yy+14],[78,yy+23],[94,yy+5]],1,teal,4);}}
 c.globalAlpha=q;const pulse=(Math.sin(f/15)+1)/2;rect(-90,195,180,35,teal,8);if(checked){c.strokeStyle='#10A995';c.globalAlpha=q*.5*(1-pulse);c.lineWidth=2;c.beginPath();c.arc(0,210,25+pulse*40,0,Math.PI*2);c.stroke();}c.restore();};
 if(kind==='nio-project-phone'){phone(540,785,p,false);c.save();c.globalAlpha=p;for(let i=0;i<3;i++){const q=ease((f-20-i*9)/24),x=260+i*280,y=1060+Math.sin(f/45+i)*8;shadow();rect(x-85,y-45,170,90,ivory,12);c.shadowColor='transparent';line([[x-45,y],[x+45,y]],q,i===1?teal:'#B7C9AC',5);}c.restore();}
 else if(kind==='nio-project-structure'){
  const xs=[230,435,640,845],ys=[930,810,690,570];line(xs.map((x,i)=>[x,ys[i]]),ease((f-10)/55),'#B3C8A6',3);const prog=clamp((f-30)/Math.max(1,duration-45))*3;const index=Math.min(2,Math.floor(prog)),t=prog-index;dot(xs[index]+(xs[index+1]-xs[index])*t,ys[index]+(ys[index+1]-ys[index])*t,8,teal);
  for(let i=0;i<4;i++){const q=ease((f-i*10)/24);c.save();c.globalAlpha=q;c.translate(xs[i],ys[i]+(1-q)*35);shadow();dot(0,0,83,ivory);c.shadowColor='transparent';if(i===0){for(const r of [20,40]){c.strokeStyle=teal;c.lineWidth=3;c.beginPath();c.arc(0,0,r,0,Math.PI*2);c.stroke();}line([[0,0],[43,-43]],q,ink,4);}if(i===1)line([[-42,33],[-12,0],[12,15],[43,-33]],q,teal,5);if(i===2){line([[0,43],[0,8],[-35,-27]],q,teal,4);line([[0,8],[35,-27]],q,teal,4);dot(-35,-27,7,teal);dot(35,-27,7,teal);}if(i===3){line([[-40,20],[-10,42],[43,-33]],q,teal,6);}c.restore();}
 }else{
  const split=Math.round(duration*.43),t=ease((f-split)/24);
  c.save();c.globalAlpha=p*(1-t);c.translate(450,770+(1-p)*40);c.rotate(-.065);shadow();rect(-250,-280,500,580,ivory,13);c.shadowColor='transparent';line([[-180,-210],[-40,-210]],p,teal,7);const highlight=Math.floor(Math.max(0,f-30)/22)%5;
  for(let i=0;i<5;i++){const y=-100+i*70;c.globalAlpha=p*(1-t)*ease((f-12-i*8)/25);dot(-165,y,11,'#A9BD98');line([[-125,y],[120,y]],1,i===highlight?teal:'#C6D3BA',5);line([[145,y-10],[170,y+10]],1,'#ABBDA0',3);}c.restore();
  const angle=.8+f*.024;c.save();c.globalAlpha=p*(1-t);c.translate(785,715);shadow();dot(0,0,120,ivory);c.shadowColor='transparent';c.strokeStyle='#B4C6A4';c.lineWidth=3;c.beginPath();c.arc(0,0,108,0,Math.PI*2);c.stroke();line([[0,0],[Math.sin(angle)*83,-Math.cos(angle)*83]],1,teal,4);dot(0,0,6,teal);c.restore();
  if(f>=split){phone(540,775,t,true);const q=ease((f-split-20)/24);c.save();c.globalAlpha=q;c.translate(790,995+Math.sin(f/40)*8);shadow();dot(0,0,90,ivory);c.shadowColor='transparent';line([[-40,0],[-10,28],[44,-35]],q,teal,6);c.restore();}
 }
 c.restore();},[f,kind,duration]);
 return <AbsoluteFill style={{background:transparent?'transparent':'#F2F3EF'}}>{!transparent&&<AbsoluteFill style={{opacity:.045,backgroundImage:`url("${staticFile('assets/premium/textures/grain.svg')}")`,mixBlendMode:'multiply'}}/>}<canvas ref={ref} width={1080} height={1220} style={{position:'absolute',top:0,left:0,width:1080,height:1220}}/></AbsoluteFill>;
};
