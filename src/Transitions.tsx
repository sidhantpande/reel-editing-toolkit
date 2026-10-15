import {Fonts} from './Fonts';
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {TransitionSeries,linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {slide} from '@remotion/transitions/slide';
import {wipe} from '@remotion/transitions/wipe';
import {flip} from '@remotion/transitions/flip';
import {clockWipe} from '@remotion/transitions/clock-wipe';
import {brands,fontCSS} from './brand';
export const transitionPresets={fade:()=>fade(),slideLeft:()=>slide({direction:'from-right'}),slideUp:()=>slide({direction:'from-bottom'}),wipeLeft:()=>wipe({direction:'from-right'}),flip:()=>flip(),clock:()=>clockWipe({width:1080,height:1920})};
export const TransitionLab:React.FC=()=>{
 const entries=Object.entries(transitionPresets);
 return <TransitionSeries>{Array.from({length:7},(_,i)=><React.Fragment key={i}><TransitionSeries.Sequence durationInFrames={90}><AbsoluteFill style={{background:i%2?'#F7F9FA':'#0B1320',color:i%2?'#0B1320':'#F7F9FA',justifyContent:'center',padding:100,fontFamily:'Sora',gap:35}}><Fonts/><div style={{fontSize:24,letterSpacing:5,color:i%2?'#10B39B':'#34D1C6'}}>TRANSITION LIBRARY / {String(i+1).padStart(2,'0')}</div><div style={{fontSize:90,fontWeight:800,lineHeight:1.1}}>{i===0?'Cut with purpose.':entries[i-1][0]}</div><div style={{fontSize:32,opacity:.6}}>Choose motion that supports the thought.</div></AbsoluteFill></TransitionSeries.Sequence>{i<6&&<TransitionSeries.Transition<any> presentation={entries[i][1]()} timing={linearTiming({durationInFrames:15})}/>}</React.Fragment>)}</TransitionSeries>;
};
