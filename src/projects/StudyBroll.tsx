import {Nio07Broll} from './Nio07Broll';
import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Sequence,Img,staticFile,useCurrentFrame} from 'remotion';
export type StudyKind='nio-mock-read'|'nio-mock-eliminate'|'nio-story-profile'|'nio-story-mock'|'nio-study-choice'|'nio-study-logic'|'nio-intro-problem'|'nio-intro-project'|'nio-intro-curiosity';
const clamp=(n:number)=>Math.max(0,Math.min(1,n));const ease=(n:number)=>1-Math.pow(1-clamp(n),3);
const Art:React.FC<{kind:StudyKind}>=({kind})=>{const f=useCurrentFrame(),ref=useRef<HTMLCanvasElement>(null);
 useLayoutEffect(()=>{const c=ref.current?.getContext('2d');if(!c)return;c.clearRect(0,0,1080,1220);c.save();c.beginPath();c.rect(0,0,1080,1210);c.clip();const drift=Math.min(f,360)/360;c.translate(540+Math.sin(f/65)*9,760-18*drift);c.scale(1+drift*.045,1+drift*.045);c.translate(-540,-760);const p=ease(f/24),teal='#10A995',ink='#173239',ivory='#FCFCF6';
 const stroke=(points:number[][],q:number,color=teal,width=4)=>{c.save();c.strokeStyle=color;c.lineWidth=width;c.lineCap='round';c.lineJoin='round';let length=0;for(let i=1;i<points.length;i++)length+=Math.hypot(points[i][0]-points[i-1][0],points[i][1]-points[i-1][1]);let left=length*clamp(q);c.beginPath();c.moveTo(points[0][0],points[0][1]);for(let i=1;i<points.length&&left>0;i++){const a=points[i-1],b=points[i],d=Math.hypot(b[0]-a[0],b[1]-a[1]),t=Math.min(1,left/d);c.lineTo(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t);left-=d;}c.stroke();c.restore();};
 const rect=(x:number,y:number,w:number,h:number,color:string,r=10)=>{c.fillStyle=color;c.beginPath();c.roundRect(x,y,w,h,r);c.fill();};
 const dot=(x:number,y:number,r:number,color:string)=>{c.fillStyle=color;c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.fill();};
 const shadow=()=>{c.shadowColor='#17323926';c.shadowBlur=28;c.shadowOffsetY=22;};
 const sheet=(x:number,y:number,w:number,h:number,rotate:number)=>{c.translate(x,y+(1-p)*40);c.rotate(rotate);c.globalAlpha=p;shadow();rect(-w/2+12,-h/2+15,w,h,'#DEE3D6',14);rect(-w/2,-h/2,w,h,ivory,14);c.shadowColor='transparent';c.strokeStyle='#D2DCC8';c.lineWidth=1;c.stroke();};
 if(kind==='nio-study-choice'){
  c.save();sheet(460,795,510,620,-.06);stroke([[-180,-235],[-40,-235]],p,teal,7);
  for(let i=0;i<4;i++){const q=ease((f-10-i*9)/24),y=-130+i*105;c.globalAlpha=p*q;c.strokeStyle=i===1||i===3?teal:'#BCC9B4';c.lineWidth=2;c.beginPath();c.arc(-160,y,18,0,Math.PI*2);c.stroke();stroke([[-110,y-7],[140-(i%2)*45,y-7]],q,'#BDC9B3',6);stroke([[-110,y+16],[60,y+16]],q,'#D4DCCD',4);if(i===1||i===3)stroke([[-170,y],[-162,y+7],[-149,y-9]],ease((f-40-i*8)/20),teal,4);}c.restore();
  const q=ease((f-20)/30);c.save();c.globalAlpha=q;c.translate(790,650+(1-q)*50);shadow();dot(0,0,130,ivory);c.shadowColor='transparent';c.strokeStyle='#C2CEB8';c.lineWidth=4;c.beginPath();c.arc(0,0,119,0,Math.PI*2);c.stroke();c.strokeStyle=teal;c.lineWidth=7;c.beginPath();c.arc(0,0,106,-Math.PI/2,-Math.PI/2+Math.PI*1.3*ease((f-30)/65));c.stroke();for(let i=0;i<12;i++){const a=i*Math.PI/6;stroke([[Math.sin(a)*87,-Math.cos(a)*87],[Math.sin(a)*96,-Math.cos(a)*96]],1,'#9EB28E',2);}const a=.5+Math.max(0,f-20)*.023;stroke([[0,0],[Math.sin(a)*72,-Math.cos(a)*72]],1,ink,4);dot(0,0,7,teal);c.restore();
 }else if(kind==='nio-study-logic'||kind==='nio-intro-problem'){
  // A missing tactile piece joins the pattern; no competing copy.
  const q=ease((f-20)/55);c.save();c.translate(540,790+(1-p)*35);c.rotate(-.055);c.globalAlpha=p;
  const piece=(x:number,y:number,color:string)=>{shadow();c.fillStyle=color;c.beginPath();c.moveTo(x,y);c.lineTo(x+87,y);c.bezierCurveTo(x+65,y-52,x+155,y-52,x+133,y);c.lineTo(x+220,y);c.lineTo(x+220,y+87);c.bezierCurveTo(x+168,y+65,x+168,y+155,x+220,y+133);c.lineTo(x+220,y+220);c.lineTo(x+133,y+220);c.bezierCurveTo(x+155,y+168,x+65,y+168,x+87,y+220);c.lineTo(x,y+220);c.lineTo(x,y+133);c.bezierCurveTo(x-52,y+155,x-52,y+65,x,y+87);c.closePath();c.fill();c.shadowColor='transparent';c.strokeStyle='#CAD6BE';c.lineWidth=1;c.stroke();};
  piece(-225,-225,ivory);piece(5,-225,ivory);piece(-225,5,ivory);c.save();c.translate((1-q)*150+Math.sin(f/38)*3,(1-q)*105+Math.cos(f/48)*3);c.rotate((1-q)*.12+Math.sin(f/70)*.009);piece(5,5,teal);c.restore();c.restore();
  if(kind==='nio-study-logic'){for(let i=0;i<2;i++){const a=p*(1-ease((f-45)/35))*.8;c.save();c.globalAlpha=a;c.translate(290+i*500,420+i*25);c.rotate(i?-.1:.07);shadow();rect(-90,-55,180,110,ivory);c.shadowColor='transparent';c.fillStyle='#8FA184';c.font='500 38px Georgia';c.textAlign='center';c.fillText(i?'x²':'a+b',0,12);c.restore();}}
  else{c.save();c.globalAlpha=ease((f-65)/25);stroke([[440,1100],[490,1135],[610,1060]],1,teal,5);c.restore();}
 }else if(kind==='nio-intro-project'){
  c.save();c.translate(540,780+(1-p)*45);c.rotate(-.04);c.globalAlpha=p;shadow();rect(-320,-260,640,440,'#DCE3D4',21);rect(-305,-245,610,405,ivory,13);c.shadowColor='transparent';rect(-275,-212,550,40,'#EDF0E7',6);for(let i=0;i<3;i++)dot(-247+i*19,-192,4,i===0?teal:'#BAC8B0');
  for(let i=0;i<5;i++){const q=ease((f-10-i*8)/25);c.globalAlpha=p*q;stroke([[-235+(i%2)*28,-105+i*44],[-40+(i%3)*70,-105+i*44]],q,i===2?teal:'#B9C6AE',7);}
  c.globalAlpha=p;const cursorY=-105+(Math.floor(Math.max(0,f-45)/23)%5)*44;stroke([[-246,cursorY-13],[-246,cursorY+9]],1,teal,3);c.save();c.globalAlpha=.12;rect(-248,cursorY-20,280,35,teal,4);c.restore();shadow();c.fillStyle='#E5E9DD';c.beginPath();c.moveTo(-320,180);c.lineTo(320,180);c.lineTo(405,260);c.quadraticCurveTo(410,280,380,282);c.lineTo(-380,282);c.quadraticCurveTo(-410,280,-405,260);c.closePath();c.fill();c.shadowColor='transparent';rect(-85,216,170,30,'#CDD8C1',6);c.restore();
  c.save();const q=ease((f-35)/25);c.globalAlpha=q;c.translate(815,1000+(1-q)*40);shadow();dot(0,0,80,ivory);c.shadowColor='transparent';stroke([[-37,2],[-10,28],[40,-30]],q,teal,7);c.restore();
 }else if(kind==='nio-mock-read'){
  c.save();sheet(500,785,560,650,-.05);stroke([[-200,-245],[-60,-245]],p,teal,7);stroke([[-200,-205],[165,-205]],p,'#C4CFB9',5);
  c.font='750 52px Arial';c.fillStyle=ink;c.fillText('NOT',-55,-115);stroke([[-195,-91],[-83,-91]],p,'#C3CEB8',6);stroke([[80,-91],[190,-91]],p,'#C3CEB8',6);stroke([[-62,-64],[65,-64]],ease((f-20)/25),teal,5);
  for(let i=0;i<3;i++){const q=ease((f-15-i*8)/22),y=20+i*78;c.globalAlpha=p*q;c.strokeStyle='#BFCBB5';c.lineWidth=2;c.beginPath();c.arc(-175,y,12,0,Math.PI*2);c.stroke();stroke([[-135,y],[135-(i%2)*50,y]],q,'#CBD4C2',6);}c.restore();
  const q=ease((f-25)/30);c.save();c.globalAlpha=q;c.translate(680-60*q+Math.sin(Math.max(0,f-60)/40)*42,675+(1-q)*40+Math.cos(Math.max(0,f-60)/50)*27);shadow();c.strokeStyle=ink;c.lineWidth=8;c.beginPath();c.arc(0,0,110,0,Math.PI*2);c.stroke();c.shadowColor='transparent';c.strokeStyle=teal;c.lineWidth=2;c.beginPath();c.arc(0,0,96,0,Math.PI*2);c.stroke();stroke([[77,77],[160,160]],1,ink,17);c.restore();
 }else if(kind==='nio-mock-eliminate'){
  for(let i=0;i<4;i++){const enter=ease((f-i*7)/25),remove=ease((f-40-i*4)/30),x=330+(i%2)*420,y=600+Math.floor(i/2)*300,keep=i%2===1;c.save();c.globalAlpha=enter*(keep?1:1-remove*.7);c.translate(x,y+(1-enter)*40);c.rotate(i%2?.035:-.035);shadow();rect(-145,-105,290,210,ivory,16);c.shadowColor='transparent';c.strokeStyle=keep?'#10A995':'#C8D3BE';c.lineWidth=keep?2:1;c.stroke();c.font='600 48px Georgia';c.textAlign='center';c.fillStyle=keep?teal:'#9EAF90';c.fillText('ABCD'[i],0,-15);for(let j=0;j<2;j++)stroke([[-80,30+j*25],[80-j*35,30+j*25]],enter,'#CFD8C5',5);if(!keep){stroke([[-100,-65],[100,65]],remove,'#A7B49C',4);stroke([[-100,65],[100,-65]],remove,'#A7B49C',4);}c.restore();}
  const q=ease((f-65)/30);c.save();c.globalAlpha=q*(.7+.3*Math.sin(f/24));c.strokeStyle=teal;c.lineWidth=3;c.beginPath();c.ellipse(750,750,205,330,0,-Math.PI/2,-Math.PI/2+Math.PI*2*q);c.stroke();c.restore();
 }else{
  c.save();c.globalAlpha=p;c.translate(540,760+(1-p)*45);c.rotate(-.04);shadow();dot(0,0,205,ivory);c.shadowColor='transparent';c.strokeStyle='#C9D5BD';c.lineWidth=2;c.beginPath();c.arc(0,0,185,0,Math.PI*2);c.stroke();
  // A drawn branching idea, then a lens reveals one route.
  const branches=[[[-110,70],[-30,0],[55,30],[120,-70]],[[-30,0],[-60,-95]],[[55,30],[70,110]]];for(let i=0;i<branches.length;i++)stroke(branches[i],ease((f-10-i*8)/35),i===0?teal:'#AABB9C',5);for(const [x,y] of [[-110,70],[-60,-95],[120,-70],[70,110]])dot(x,y,10,teal);c.restore();
  const q=ease((f-28)/28);c.save();c.globalAlpha=q;c.translate(740+Math.sin(Math.max(0,f-55)/36)*70,940+(1-q)*70+Math.cos(Math.max(0,f-55)/45)*35);c.rotate(-.15);shadow();c.strokeStyle=ink;c.lineWidth=9;c.beginPath();c.arc(0,0,110,0,Math.PI*2);c.stroke();c.shadowColor='transparent';stroke([[80,80],[172,172]],1,ink,19);c.strokeStyle=teal;c.lineWidth=2;c.beginPath();c.arc(0,0,96,0,Math.PI*2);c.stroke();c.restore();
 }
 c.restore();},[f,kind]);return <canvas ref={ref} width={1080} height={1220} style={{position:'absolute',left:0,top:0,width:1080,height:1220}}/>;};
export const StudyBroll:React.FC<{kind:StudyKind;transparent?:boolean;duration?:number;beats?:number[]}>=({kind,transparent=false,duration=180,beats})=>{
 const f=useCurrentFrame();
 if(kind==='nio-story-profile'||kind==='nio-story-mock'){
  const mock=kind==='nio-story-mock',starts=[0,...(beats??(mock?[169,332,483]:[110]))];
  const kinds=mock?['nio-study-choice','nio-mock-read','nio-system-review','nio-mock-eliminate']:['nio-intro-project','nio-intro-curiosity'];
  return <AbsoluteFill style={{background:transparent?'transparent':'#F2F3EF',overflow:'hidden'}}>
   {!transparent&&<AbsoluteFill style={{opacity:.045,backgroundImage:`url("${staticFile('assets/premium/textures/grain.svg')}")`,mixBlendMode:'multiply'}}/>}
   {kinds.map((scene,i)=>{const from=starts[i],next=starts[i+1],alpha=ease((f-from)/12)*(next===undefined?1:1-ease((f-next)/12));return <Sequence key={scene} from={from} durationInFrames={Math.min(duration,next===undefined?duration:next+12)-from}><AbsoluteFill style={{opacity:i===0&&f<12?1:alpha}}>{scene==='nio-system-review'?<Nio07Broll kind="nio-system-review" transparent/>:<StudyBroll kind={scene as StudyKind} transparent/>}</AbsoluteFill></Sequence>})}
  </AbsoluteFill>;
 }
 return <AbsoluteFill style={{background:transparent?'transparent':'#F2F3EF',overflow:'hidden'}}>
 {!transparent&&<AbsoluteFill style={{opacity:.045,backgroundImage:`url("${staticFile('assets/premium/textures/grain.svg')}")`,mixBlendMode:'multiply'}}/>}
 <Art kind={kind}/>
 </AbsoluteFill>;
};
