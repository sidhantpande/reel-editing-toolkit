import React from 'react';
import {AbsoluteFill,Img,interpolate,Easing,staticFile,useCurrentFrame} from 'remotion';
import {Fonts} from '../Fonts';
import {Brand} from '../types';
export type PaperKind='paper-possibilities'|'paper-pathways'|'paper-crowd'|'paper-partnership';
export type PaperProps={duration?:number;brand:Brand;kind:PaperKind;transparent?:boolean;title?:string;labels?:string[]};
const clamp={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
const ease=Easing.bezier(.16,.82,.2,1);
const r=(f:number,start=0,length=28)=>interpolate(f,[start,start+length],[0,1],{...clamp,easing:ease});
const a=(name:string)=>staticFile(`assets/premium/cutouts/${name}.png`);
const Star:React.FC<{x:number;y:number;size:number;rotation?:number}>=({x,y,size,rotation=0})=><svg width={size} height={size} viewBox="0 0 100 100" style={{position:'absolute',left:x,top:y,transform:`rotate(${rotation}deg)`,filter:'drop-shadow(0 15px 13px #0B13201f)'}}><path d="M49 0C51 39 61 47 100 49C61 51 51 61 49 100C47 61 39 51 0 49C39 47 47 39 49 0Z" fill="#111A23"/></svg>;
const Phrase:React.FC<{text:string;frame:number;from?:number;size?:number;weight?:number;color?:string}>=({text,frame,from=0,size=76,weight=600,color='#0B1320'})=><span style={{display:'inline-block',fontSize:size,fontWeight:weight,color,opacity:r(frame,from,15),filter:`blur(${(1-r(frame,from,18))*8}px)`,transform:`translateY(${(1-r(frame,from,25))*20}px)`}}>{text}</span>;
export const PaperScene:React.FC<PaperProps>=({brand,kind,transparent=false,title,labels})=>{
 const f=useCurrentFrame(),accent=brand==='niolearn'?'#10A995':'#A3BD40',ink='#0B1320';const person=brand==='niolearn'?'paper-student':'editorial-person';
 const caption=(text:string,x:number,y:number,from:number,width=340)=><div style={{position:'absolute',left:x,top:y,width,padding:'18px 20px',border:'1.5px dashed #0b13205c',fontSize:28,lineHeight:1.2,letterSpacing:-.8,textAlign:'center',color:ink,opacity:r(f,from,25),transform:`translateY(${(1-r(f,from,25))*14}px)`}}>{text}</div>;
 const heading=(first:string,second:string,secondColor=ink)=><div style={{position:'absolute',left:105,right:105,top:305,textAlign:'center',lineHeight:1.08,letterSpacing:-3.6,fontFamily:brand==='niolearn'?'Sora':'Inter'}}><Phrase text={title??first} frame={f} from={1} size={70} weight={500}/><br/>{!title&&<Phrase text={second} frame={f} from={14} size={76} weight={750} color={secondColor}/>}</div>;
 return <AbsoluteFill style={{overflow:'hidden',color:ink,fontFamily:'Inter'}}><Fonts/>
 {!transparent&&<><AbsoluteFill style={{background:brand==='niolearn'?'#F2F3EF':'#F1F0EB'}}/><AbsoluteFill style={{background:'radial-gradient(ellipse at 48% 32%,#fff9,transparent 70%)'}}/><AbsoluteFill style={{opacity:.07,backgroundImage:`url("${staticFile('assets/premium/textures/grain.svg')}")`,mixBlendMode:'multiply'}}/></>}
 <AbsoluteFill style={{transform:`scale(${1+f*.00012})`,transformOrigin:'50% 60%'}}>
 {kind==='paper-possibilities'&&<>
  {heading('One exam.','More possibilities.')}
  {!transparent&&<div style={{position:'absolute',left:150,right:150,top:600,height:800,opacity:.18,backgroundImage:'radial-gradient(#142b28 1px,transparent 1px)',backgroundSize:'25px 25px',maskImage:'radial-gradient(ellipse,#0009,transparent 70%)'}}/>}
  <Star x={-170} y={1180} size={350} rotation={f*.03-12}/>
  <svg width="1080" height="1920" style={{position:'absolute'}}><path d="M-150 1320C120 1550 310 1430 540 1350S940 1230 1190 1440" fill="none" stroke={ink} strokeWidth="9" pathLength="1" strokeDasharray="1" strokeDashoffset={1-r(f,35,70)}/><path d="M180 1000C260 700 740 720 870 1030" fill="none" stroke={accent} strokeWidth="2" strokeDasharray="5 12" opacity={r(f,55,40)*.75}/></svg>
  <div style={{position:'absolute',left:327,top:1360,width:410,height:45,borderRadius:'50%',background:'#0b132026',filter:'blur(18px)',opacity:r(f,38,35)}}/>
  <Img src={a(person)} style={{position:'absolute',left:280,top:640,width:515,opacity:r(f,24,35),transform:`translateY(${(1-r(f,24,35))*75}px) rotate(-2deg)`,filter:`blur(${(1-r(f,25,25))*8}px) drop-shadow(12px 25px 15px #0b132016)`}}/>
  <Img src={a('compass')} style={{position:'absolute',left:725,top:879+Math.sin(f/44)*7,width:260,opacity:r(f,58,30),transform:`translateX(${(1-r(f,58,35))*70}px) rotate(${8-4*r(f,60,45)}deg)`,filter:'drop-shadow(10px 24px 17px #0b13201c)'}}/>
  <Img src={a('open-book')} style={{position:'absolute',left:66,top:1100+Math.sin(f/48)*6,width:305,opacity:r(f,72,28),transform:`translateX(${(1-r(f,72,35))*-65}px) rotate(-13deg)`,filter:'drop-shadow(8px 22px 16px #0b132025)'}}/>
  {caption('Your next chapter.',585,1470,98,330)}
 </>}
 {kind==='paper-pathways'&&<>
  {heading('Find your direction.','Build your own path.')}
  <Star x={945} y={65} size={330} rotation={12+f*.03}/>
  <svg width="1080" height="1920" style={{position:'absolute'}}><path d="M240 830C700 710 250 1260 780 1190" fill="none" stroke="#0B132018" strokeWidth="2"/><path d="M240 830C700 710 250 1260 780 1190" fill="none" stroke={ink} strokeWidth="2.5" pathLength="1" strokeDasharray="1" strokeDashoffset={1-r(f,35,85)}/>{[[235,810],[520,1030],[800,1200]].map(([x,y],i)=><g key={i} opacity={r(f,24+i*28,20)}><circle cx={x} cy={y} r="15" fill="#F2F3EF" stroke={accent} strokeWidth="2"/><circle cx={x} cy={y} r="4" fill={accent}/></g>)}</svg>
  <Img src={a('compass')} style={{position:'absolute',left:100,top:610,width:295,opacity:r(f,14,32),transform:`translateY(${(1-r(f,14,32))*35}px) rotate(-13deg)`,filter:'drop-shadow(13px 28px 16px #0b132021)'}}/>
  <Img src={a('open-book')} style={{position:'absolute',left:350,top:870,width:330,opacity:r(f,43,32),transform:`translateY(${(1-r(f,43,32))*45}px) rotate(8deg)`,filter:'drop-shadow(14px 28px 18px #0b132026)'}}/>
  <Img src={a(person)} style={{position:'absolute',left:660,top:940,width:330,opacity:r(f,71,35),transform:`translateY(${(1-r(f,71,35))*40}px)`,filter:'drop-shadow(10px 20px 15px #0b13201a)'}}/>
  {caption(labels?.[0]??'Discover',113,929,27,230)}{caption(labels?.[1]??'Prepare',402,1215,58,230)}{caption(labels?.[2]??'Progress',710,1460,95,230)}
 </>}
 {kind==='paper-crowd'&&<>
  {heading(brand==='niolearn'?'You are more':'Behind every goal,',brand==='niolearn'?'than a number.':'there are people.')}
  {Array.from({length:18},(_,i)=>{const row=i%3,col=Math.floor(i/3),size=145+row*65;return <div key={i} style={{position:'absolute',left:col*188-5+(row%2)*46,top:745+row*82,width:size,height:size*1.5,opacity:(.13+row*.08)*r(f,i%6*2,30),filter:`blur(${(2-row)*1.1}px) grayscale(1)`,transform:`translateX(${f*(row-1)*.1}px)`}}><div style={{position:'absolute',left:'25%',bottom:'-4%',width:'60%',height:'5%',background:'#0b13203b',borderRadius:'50%',filter:'blur(8px)'}}/><Img src={a(person)} style={{width:'100%',height:'100%',objectFit:'contain'}}/></div>})}
  <div style={{position:'absolute',left:350,top:1325,width:370,height:45,background:'#0b132022',filter:'blur(16px)',borderRadius:'50%',opacity:r(f,30,35)}}/>
  <Img src={a(person)} style={{position:'absolute',left:302,top:640,width:475,opacity:r(f,25,35),transform:`translateY(${(1-r(f,25,35))*70}px) scale(${.88+.12*r(f,30,42)})`,filter:'drop-shadow(11px 20px 13px #0b132015)'}}/>
  <svg width="1080" height="1920" style={{position:'absolute',opacity:r(f,74,27)}}><ellipse cx="540" cy="1375" rx="205" ry="42" fill="none" stroke={accent} strokeWidth="2.5" strokeDasharray="8 11"/><path d="M748 1373C942 1330 941 1160 862 1120" fill="none" stroke={ink} strokeWidth="1.8"/><circle cx="862" cy="1120" r="5" fill={accent}/></svg>
  <div style={{position:'absolute',left:160,right:160,top:1490,textAlign:'center',fontSize:28,letterSpacing:-.7,opacity:r(f,94,25)*.65}}>{brand==='niolearn'?'A path that makes room for you.':'Progress starts with understanding.'}</div>
 </>}
 {kind==='paper-partnership'&&<>
  {heading(brand==='niolearn'?'With the right guidance,':'Good work becomes',brand==='niolearn'?'move with clarity.':'shared progress.')}
  <Star x={-260} y={90} size={400} rotation={12+f*.035}/><Star x={880} y={1410} size={370} rotation={-8-f*.035}/>
  {!transparent&&<div style={{position:'absolute',left:150,right:150,top:650,height:700,opacity:.22,backgroundImage:'radial-gradient(#0b1320 1px,transparent 1px)',backgroundSize:'24px 24px',maskImage:'radial-gradient(ellipse,#0008,transparent 75%)'}}/>}
  <svg width="1080" height="1920" style={{position:'absolute'}}><path d="M-150 1230C190 950 530 1570 1250 1040" fill="none" stroke={ink} strokeWidth="12"/></svg>
  <Img src={a(person)} style={{position:'absolute',left:95,top:650,width:310,opacity:r(f,10,35)*.4,transform:`translateY(${(1-r(f,10,35))*55}px) rotate(-5deg)`,filter:'blur(.7px) grayscale(.5)'}}/>
  <Img src={a('editorial-person')} style={{position:'absolute',right:100,top:680,width:325,opacity:r(f,20,35)*.4,transform:`scaleX(-1) translateY(${(1-r(f,20,35))*55}px) rotate(-5deg)`,filter:'blur(.7px) grayscale(.5)'}}/>
  <Img src={a('handshake')} style={{position:'absolute',left:-90+r(f,43,38)*65,top:870,width:1130,opacity:r(f,43,27),transform:`translateY(${(1-r(f,43,38))*120}px) rotate(${-5+3*r(f,50,50)}deg)`,filter:`blur(${(1-r(f,43,24))*7}px) drop-shadow(0 32px 24px #0b13201f)`}}/>
  {caption(brand==='niolearn'?'Navigate more possibilities.':'Built together.',298,1455,94,485)}
  <svg width="50" height="60" viewBox="0 0 55 65" style={{position:'absolute',left:778,top:1520,opacity:r(f,104,20),transform:'rotate(-12deg)'}}><path d="M6 2V51L21 37L33 62L44 56L32 32L53 30Z" fill={ink} stroke="#F2F3EF" strokeWidth="3"/></svg>
 </>}
 </AbsoluteFill>
 </AbsoluteFill>;
};
