import React from 'react';
import {AbsoluteFill,Img,interpolate,staticFile,useCurrentFrame,useVideoConfig,Easing} from 'remotion';
import {Fonts} from '../Fonts';
import {Brand} from '../types';
export type PremiumKind='glass-mentor'|'crowd-focus'|'editorial-trust'|'glass-paths';
export type PremiumProps={brand:Brand;kind:PremiumKind;transparent?:boolean;title?:string;labels?:string[]};
const clamp={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
const ease=Easing.bezier(.18,.8,.22,1);
const asset=(name:string)=>staticFile(`assets/premium/v2/${name}.png`);
const reveal=(f:number,start=0,duration=26)=>interpolate(f,[start,start+duration],[0,1],{...clamp,easing:ease});
const PaperStar:React.FC<{x:number;y:number;size:number;rotate:number}>=({x,y,size,rotate})=><svg width={size} height={size} viewBox="0 0 100 100" style={{position:'absolute',left:x,top:y,transform:`rotate(${rotate}deg)`,filter:'drop-shadow(0 18px 13px #0004)'}}><path d="M49 0C51 39 61 47 100 49C61 51 51 61 49 100C47 61 39 51 0 49C39 47 47 39 49 0Z" fill="#101111"/></svg>;
const Atmosphere:React.FC<{light:boolean;accent:string}>=({light,accent})=><>
 <AbsoluteFill style={{background:light?'#F0EFEB':'#080D15'}}/>
 {!light&&<AbsoluteFill style={{background:`radial-gradient(ellipse at 50% -4%,${accent}35,transparent 54%),radial-gradient(ellipse at 84% 56%,#5765841a,transparent 48%),linear-gradient(180deg,transparent,#04070dcc)`}}/>}
 <AbsoluteFill style={{opacity:light?.055:.065,backgroundImage:`url("${staticFile('assets/premium/v2/grain.svg')}")`,mixBlendMode:light?'multiply':'screen'}}/>
 {light&&<AbsoluteFill style={{background:'radial-gradient(ellipse at 50% 32%,#ffffffa8,transparent 62%)'}}/>}
</>;
const Heading:React.FC<{top:number;children:React.ReactNode;light?:boolean;opacity?:number}>=({top,children,light=false,opacity=1})=><div style={{position:'absolute',left:112,right:112,top,color:light?'#171918':'#F7F9FA',fontSize:76,lineHeight:1.08,fontWeight:520,letterSpacing:-3.7,textAlign:'center',opacity}}>{children}</div>;
export const PremiumScene:React.FC<PremiumProps>=({brand,kind,transparent=false,title,labels})=>{
 const f=useCurrentFrame(),{fps}=useVideoConfig();const accent=brand==='niolearn'?'#32CFBE':'#CBE957';const light=kind==='editorial-trust'||kind==='crowd-focus';
 const camera=1+interpolate(f,[0,180],[0,.035],clamp);
 return <AbsoluteFill style={{fontFamily:'Inter',overflow:'hidden',color:light?'#171918':'#F7F9FA',background:'transparent'}}><Fonts/>
 {!transparent&&<Atmosphere light={light} accent={accent}/>}
 <AbsoluteFill style={{transform:`scale(${camera})`,transformOrigin:'50% 60%'}}>
 {kind==='glass-mentor'&&<>
  {!transparent&&<div style={{position:'absolute',left:180,top:500,width:720,height:900,background:`radial-gradient(ellipse,${accent}12,transparent 70%)`,filter:'blur(42px)'}}/>}
  {Array.from({length:9},(_,i)=>{const distance=Math.abs(i-4);const depth=(4-distance)/4;const x=60+i*110;return <Img key={i} src={asset('glass-person')} style={{position:'absolute',left:x-96,top:760-distance*24,width:230+depth*20,opacity:reveal(f,8+i*2,35)*(.13+depth*.09)*(1-reveal(f,58,35)*.45),filter:`blur(${2+distance*.45}px) saturate(.35)`,transform:`translateY(${(1-reveal(f,8+i*2,35))*65}px)`}}/>})}
  <div style={{position:'absolute',left:130,top:680,width:820,height:730,opacity:.3,background:'radial-gradient(ellipse at 50% 75%,#82b7b018,transparent 65%)'}}/>
  <Img src={asset('glass-person')} style={{position:'absolute',width:770,left:155,top:600,opacity:reveal(f,24,38),transform:`translateY(${(1-reveal(f,24,38))*100+Math.sin(f/60)*5}px) scale(${.78+.22*reveal(f,32,45)})`,filter:`blur(${(1-reveal(f,25,30))*12}px) drop-shadow(0 35px 55px #0008)`}}/>
  <Img src={asset('open-book')} style={{position:'absolute',left:628-120*reveal(f,72,40),top:934+Math.sin(f/35)*13,width:320,opacity:reveal(f,68,30),transform:`translateY(${(1-reveal(f,68,36))*45}px) rotate(${-12+reveal(f,70,42)*8}deg)`,filter:'drop-shadow(0 28px 30px #0008)'}}/>
  <Heading top={310} opacity={reveal(f,4,24)}>{title??<>Every student.<br/><span style={{color:accent}}>A different possibility.</span></>}</Heading>
  <div style={{position:'absolute',left:200,right:200,top:1470,textAlign:'center',fontSize:30,fontWeight:400,lineHeight:1.4,letterSpacing:-.6,opacity:reveal(f,95,24)*.6}}>Clarity. Preparation. A way forward.</div>
 </>}
 {kind==='crowd-focus'&&<>
  {!transparent&&<div style={{position:'absolute',left:0,right:0,top:880,height:800,background:'linear-gradient(180deg,transparent,#dedfda44,transparent)'}}/>}
  {Array.from({length:21},(_,i)=>{const row=i%3;const col=Math.floor(i/3);const size=145+row*70;const x=col*173-30+(row%2)*55;const y=755+row*65;return <div key={i} style={{position:'absolute',left:x,top:y,width:size,height:size*1.5,opacity:(.16+row*.08)*reveal(f,i%7*2,28),filter:`blur(${(2-row)*1.2}px) grayscale(1)`,transform:`translateX(${Math.sin(i*3.7)*18+f*(row-1)*.14}px)`}}><div style={{position:'absolute',left:'20%',bottom:'-8%',width:'70%',height:'8%',background:'#2224',borderRadius:'50%',filter:'blur(9px)',transform:'skewX(-35deg)'}}/><Img src={asset('editorial-person')} style={{width:'100%',height:'100%',objectFit:'contain'}}/></div>})}
  <div style={{position:'absolute',left:335,top:1355,width:430,height:80,borderRadius:'50%',background:'#1719182c',filter:'blur(22px)',opacity:reveal(f,40,35)}}/>
  <Img src={asset('editorial-person')} style={{position:'absolute',width:490,left:295,top:640,opacity:reveal(f,28,35),filter:'drop-shadow(18px 22px 11px #0002)',transform:`translateY(${(1-reveal(f,28,35))*70}px) scale(${.85+.15*reveal(f,35,45)})`}}/>
  <svg width="1080" height="1920" style={{position:'absolute',opacity:reveal(f,78,30)}}><ellipse cx="544" cy="1380" rx="220" ry="48" fill="none" stroke={accent} strokeWidth="3" strokeDasharray="9 10"/><path d="M765 1370C945 1300 913 1080 838 1040" fill="none" stroke="#1b2525" strokeWidth="2"/><circle cx="838" cy="1040" r="6" fill={accent}/></svg>
  <Heading top={305} light opacity={reveal(f,3,22)}>{title??<>You are more<br/>than a <span style={{fontWeight:760}}>number.</span></>}</Heading>
  <div style={{position:'absolute',top:1525,left:140,right:140,textAlign:'center',fontSize:26,letterSpacing:-.5,opacity:reveal(f,98,25)*.6}}>Make room for your own direction.</div>
 </>}
 {kind==='editorial-trust'&&<>
  {!transparent&&<div style={{position:'absolute',left:140,right:140,top:620,height:770,opacity:.25,backgroundImage:'radial-gradient(#121c1a 1px,transparent 1px)',backgroundSize:'23px 23px',maskImage:'radial-gradient(ellipse,#0009,transparent 73%)'}}/>}
  <PaperStar x={-230} y={90} size={430} rotate={12+f*.04}/><PaperStar x={875} y={1375} size={380} rotate={-8-f*.04}/>
  <svg width="1080" height="1920" style={{position:'absolute',opacity:.95}}><path d="M-170 1230C190 950 530 1570 1250 1040" fill="none" stroke="#121615" strokeWidth="14"/><path d="M-180 1244C190 965 530 1585 1250 1055" fill="none" stroke="#121615" strokeWidth="3" opacity=".2"/></svg>
  <Img src={asset('editorial-person')} style={{position:'absolute',left:100,top:625,width:310,opacity:reveal(f,8,35)*.35,transform:`translateY(${(1-reveal(f,8,35))*55}px) rotate(-6deg)`,filter:'blur(.8px) grayscale(1)'}}/>
  <Img src={asset('editorial-person')} style={{position:'absolute',right:110,top:680,width:340,opacity:reveal(f,18,35)*.35,transform:`scaleX(-1) translateY(${(1-reveal(f,18,35))*55}px) rotate(-6deg)`,filter:'blur(.8px) grayscale(1)'}}/>
  <Img src={asset('handshake')} style={{position:'absolute',left:-92+reveal(f,42,40)*65,top:865,width:1130,opacity:reveal(f,42,27),transform:`translateY(${(1-reveal(f,42,40))*130}px) rotate(${-5+3*reveal(f,50,55)}deg)`,filter:`blur(${(1-reveal(f,42,25))*7}px) drop-shadow(0 35px 30px #0002)`}}/>
  <Heading top={320} light opacity={reveal(f,2,25)}>{title??<>Good work becomes<br/><span style={{fontWeight:780}}>shared progress.</span></>}</Heading>
  <div style={{position:'absolute',left:300,top:1450,width:480,height:88,border:'1.5px dashed #17191880',display:'flex',alignItems:'center',justifyContent:'center',fontSize:31,fontWeight:500,letterSpacing:-.8,opacity:reveal(f,91,26),transform:`translateY(${(1-reveal(f,91,26))*18}px)`}}>{brand==='atfro'?'Built together.':'Guidance that goes further.'}<svg width="55" height="65" viewBox="0 0 55 65" style={{position:'absolute',right:-35,bottom:-35,transform:'rotate(-12deg)'}}><path d="M6 2V51L21 37L33 62L44 56L32 32L53 30Z" fill="#111" stroke="#F0EFEB" strokeWidth="3"/></svg></div>
 </>}
 {kind==='glass-paths'&&<>
  {!transparent&&<div style={{position:'absolute',left:120,top:730,width:850,height:620,borderRadius:'50%',background:`radial-gradient(ellipse,${accent}0e,transparent 65%)`,filter:'blur(35px)'}}/>}
  <svg width="1080" height="1920" style={{position:'absolute'}}><defs><linearGradient id="route-v2" x1="0" y1="1" x2="1" y2="0"><stop stopColor={accent} stopOpacity=".05"/><stop offset=".7" stopColor={accent} stopOpacity=".8"/><stop offset="1" stopColor="#ffffff" stopOpacity=".7"/></linearGradient></defs>{[270,540,810].map((x,i)=><g key={x}><path d={`M540 1240C540 1000 ${x} 1000 ${x} 770`} fill="none" stroke="url(#route-v2)" strokeWidth="2" pathLength="1" strokeDasharray="1" strokeDashoffset={1-reveal(f,26+i*8,54)}/><circle cx={x} cy="782" r="4" fill={accent} opacity={reveal(f,48+i*8,15)}/></g>)}</svg>
  {(labels?.length?labels.slice(0,3):['Discover','Prepare','Progress']).map((label,i)=>{const p=reveal(f,12+i*12,40);return <div key={i} style={{position:'absolute',left:108+i*300,top:710+(i%2)*34,width:260,height:295,borderRadius:24,background:'linear-gradient(140deg,#ffffff14,#ffffff02)',border:'1px solid #ffffff35',boxShadow:'inset 0 1px 1px #fff3,inset 0 -1px 0 #0008,0 35px 50px #0006',transform:`perspective(1200px) translateY(${(1-p)*90}px) rotateY(${(i-1)*-13}deg) rotateX(8deg)`,opacity:p}}><div style={{position:'absolute',top:22,left:26,fontSize:18,color:accent,letterSpacing:2}}>0{i+1}</div><Img src={asset('open-book')} style={{position:'absolute',width:180,left:40,top:48,filter:'drop-shadow(0 12px 10px #0005)'}}/><div style={{position:'absolute',bottom:27,width:'100%',textAlign:'center',fontSize:30,fontWeight:500,letterSpacing:-1}}>{label}</div></div>})}
  <div style={{position:'absolute',left:385,top:1170,width:310,height:80,borderRadius:'50%',border:`1px solid ${accent}40`,boxShadow:`0 0 65px ${accent}10,inset 0 0 40px ${accent}0c`,transform:`rotateX(55deg) scale(${reveal(f,30,60)})`}}/>
  <Img src={asset('glass-person')} style={{position:'absolute',left:348,top:1070,width:385,opacity:reveal(f,39,35),transform:`translateY(${(1-reveal(f,39,35))*55}px)`,filter:'drop-shadow(0 20px 30px #0005)'}}/>
  <Heading top={310} opacity={reveal(f,3,24)}>{title??<>One ambition.<br/><span style={{color:accent}}>More ways forward.</span></>}</Heading>
 </>}
 </AbsoluteFill>
 </AbsoluteFill>;
};
