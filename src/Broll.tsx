import {SchoolBroll,SchoolKind} from './projects/SchoolBroll';
import {ComparisonBroll,ComparisonKind} from './projects/ComparisonBroll';
import {ProjectBroll,ProjectKind} from './projects/ProjectBroll';
import {StudyBroll,StudyKind} from './projects/StudyBroll';
import {Nio07Broll,Nio07Kind} from './projects/Nio07Broll';
import {Nio04Broll,Nio04Kind} from './projects/Nio04Broll';
import {Atfro01Broll,Atfro01Kind} from './projects/Atfro01Broll';
import {PaperScene,PaperKind} from './premium/PaperScene';
import {Fonts} from './Fonts';
import React from 'react';
import {AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {brands} from './brand';
import {Brand,BrollKind} from './types';
const clamp={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
const BasicBroll:React.FC<{brand:Brand;kind:BrollKind;title?:string;transparent?:boolean;labels?:string[];seconds?:number}> = ({brand,kind,title,transparent=false,labels,seconds=5})=>{
 const f=useCurrentFrame(),{fps}=useVideoConfig(),b=brands[brand],theme=brand==='niolearn'?'teal':'lime';
 const pathLabels=labels?.length?labels.slice(0,5):['Prep','Mocks','Interview'];const pathWidth=Math.min(250,880/pathLabels.length-24);const pathCenters=pathLabels.map((_,i)=>100+880/pathLabels.length*(i+.5));
 const enter=(delay=0)=>spring({frame:Math.max(0,f-delay),fps,config:{damping:19,stiffness:110}});
 const icon=(name:string,size=120)=><Img src={staticFile(`assets/elements/${name}-${theme}.svg`)} style={{width:size,height:size}}/>;
 const card=(text:string,i:number,x:number,y:number,w=250)=><div key={text} style={{position:'absolute',left:x,top:y,width:w,padding:'34px 20px',background:`linear-gradient(140deg,${b.light}20,${b.light}08)`,border:`2px solid ${b.accent}66`,borderRadius:28,backdropFilter:'blur(10px)',textAlign:'center',fontSize:32,fontWeight:700,opacity:enter(i*7),transform:`translateY(${(1-enter(i*7))*60}px)`}}>{text}</div>;
 return <AbsoluteFill style={{background:transparent?'transparent':`radial-gradient(ellipse at 50% 0%,${b.accent}25,transparent 65%),${b.bg}`,color:b.light,fontFamily:b.font,overflow:'hidden'}}>
 <Fonts/>{!transparent&&<div style={{position:'absolute',inset:0,opacity:.08,backgroundImage:'radial-gradient(#fff 1px, transparent 1px)',backgroundSize:'26px 26px'}}/>}
 {title&&<div style={{position:'absolute',left:100,right:130,top:300,fontSize:64,fontWeight:800,lineHeight:1.12,letterSpacing:-2,opacity:enter(),transform:`translateY(${(1-enter())*25}px)`}}>{title}</div>}
 {kind==='crowd'&&<>
  {[0,1,2,3,4,5,6].map((i)=><Img key={i} src={staticFile(`assets/elements/glass-person-${i===3?theme:'white'}.png`)} style={{position:'absolute',width:i===3?550:270,left:i===3?250:40+i*130,top:i===3?630:760+(i%2)*80,opacity:enter(i*4)*(i===3?1:.3),transform:`translateY(${(1-enter(i*4))*70+Math.sin(f/40+i)*8}px)`,filter:i===3?'none':'blur(2px)'}}/>)}
  <div style={{position:'absolute',top:1350,left:100,right:130,textAlign:'center',fontSize:36,color:b.highlight}}>One clear path starts with you.</div>
 </>}
 {kind==='pathways'&&<>
  <svg width="1080" height="1920" style={{position:'absolute'}}><g fill="none" stroke={b.accent} strokeWidth="5" strokeDasharray="12 12">{pathCenters.map((x,i)=><path key={i} d={`M540 1160 C540 900 ${x} 900 ${x} 740`} pathLength="1" strokeDasharray="1" strokeDashoffset={1-interpolate(f,[12,60],[0,1],clamp)}/>)}</g></svg>
  {pathLabels.map((v,i)=>card(v,i,pathCenters[i]-pathWidth/2,620,pathWidth))}
  <div style={{position:'absolute',left:440,top:1080,transform:`scale(${enter()})`}}>{icon('compass-route',200)}</div>
 </>}
 {kind==='lead-flow'&&<>{(labels?.length?labels.slice(0,4):['Enquiry','Owner','Follow-up','Review']).map((v,i)=><React.Fragment key={v}>{card(v,i,210,580+i*185,660)}{i<3&&<div style={{position:'absolute',left:495,top:710+i*185,transform:'rotate(90deg)',opacity:enter(i*7+10)}}>{icon('arrow-forward',70)}</div>}</React.Fragment>)}<div style={{position:'absolute',top:1420,width:'100%',textAlign:'center',opacity:.6,fontSize:24}}>ILLUSTRATIVE WORKFLOW</div></>}
 {kind==='timeline'&&<>
  {Array.from({length:30},(_,i)=>{const p=interpolate(f,[25,75],[0,1],clamp);const group=Math.floor(i/10);return <div key={i} style={{position:'absolute',left:100+i*28+(group*290+110-(100+i*28))*p,top:830+(group%2)*p*15,width:20+(220-20)*p,height:170,background:i%10===0?b.accent:'#899097',opacity:i%10===0?1:1-p,borderRadius:14}}/>})}
  {(labels?.length?labels.slice(0,3):['Beginning','Learning','Payoff']).map((v,i)=><div key={v} style={{position:'absolute',left:200+i*290,top:1060,fontSize:28,opacity:interpolate(f,[60,85],[0,1],clamp)}}>{v}</div>)}
 </>}
 {kind==='compare'&&<>{(labels?.length?labels.slice(0,2):['One common base','Test-specific prep']).map((v,i)=><React.Fragment key={v}>{card(v,i,110+i*440,700,400)}<div style={{position:'absolute',left:245+i*440,top:990,opacity:enter(i*8)}}>{icon(i?'check-ring':'book-open',130)}</div></React.Fragment>)}<div style={{position:'absolute',left:510,top:770,fontSize:55,color:b.highlight}}>+</div></>}
 {kind==='countdown'&&<>
  <svg style={{position:'absolute',left:240,top:650}} width="600" height="600"><circle cx="300" cy="300" r="260" fill="none" stroke={b.light+'20'} strokeWidth="12"/><circle cx="300" cy="300" r="260" fill="none" stroke={b.accent} strokeWidth="12" strokeLinecap="round" strokeDasharray={1634} strokeDashoffset={1634*interpolate(f,[0,seconds*fps],[0,1],clamp)} transform="rotate(-90 300 300)"/></svg>
  <div style={{position:'absolute',top:820,width:'100%',fontSize:180,textAlign:'center',fontWeight:800}}>{Math.max(0,seconds-Math.floor(f/fps))}</div>
 </>}
 </AbsoluteFill>
};

export const Broll:React.FC<{brand:Brand;kind:BrollKind;title?:string;transparent?:boolean;labels?:string[];seconds?:number;beats?:number[];duration?:number}>=(props)=>
 props.kind.startsWith('atfro-school-')?<SchoolBroll {...props} kind={props.kind as SchoolKind}/>:['nio-story-comparison','nio-compare-board','nio-brand-services','nio-access-calendar'].includes(props.kind)?<ComparisonBroll {...props} kind={props.kind as ComparisonKind}/>:props.kind.startsWith('nio-project-')?<ProjectBroll {...props} kind={props.kind as ProjectKind}/>:(props.kind.startsWith('nio-study-')||props.kind.startsWith('nio-intro-')||props.kind.startsWith('nio-mock-')||props.kind.startsWith('nio-story-'))?<StudyBroll {...props} kind={props.kind as StudyKind}/>:props.kind.startsWith('nio-system-')?<Nio07Broll {...props} kind={props.kind as Nio07Kind}/>:props.kind.startsWith('nio-parents-')?<Nio04Broll {...props} kind={props.kind as Nio04Kind}/>:['atfro-work','atfro-process'].includes(props.kind)?<Atfro01Broll {...props} kind={props.kind as Atfro01Kind}/>:['paper-possibilities','paper-pathways','paper-crowd','paper-partnership'].includes(props.kind)?<PaperScene {...props} kind={props.kind as PaperKind}/>:<BasicBroll {...props}/>;
