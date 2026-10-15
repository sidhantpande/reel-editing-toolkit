import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile} from 'remotion';
import {TransitionSeries,linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {PremiumScene,PremiumKind} from './PremiumScene';
import {Brand} from '../types';
export const PremiumShowcase:React.FC<{brand:Brand}>=({brand})=>{
 const kinds:PremiumKind[]=brand==='niolearn'?['glass-mentor','glass-paths','crowd-focus','editorial-trust']:['editorial-trust','crowd-focus','glass-mentor','glass-paths'];
 return <AbsoluteFill><TransitionSeries>{kinds.map((kind,i)=><React.Fragment key={kind}><TransitionSeries.Sequence durationInFrames={180}><PremiumScene brand={brand} kind={kind}/></TransitionSeries.Sequence>{i<3&&<TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames:10})}/>}</React.Fragment>)}</TransitionSeries>
 <Audio src={staticFile(`assets/music/${brand==='niolearn'?'calm-focus':'soft-momentum'}.wav`)} volume={.5}/>
 {[15,185,355,525].map(f=><Sequence key={f} from={f}><Audio src={staticFile('assets/sfx/transition-air.wav')} volume={.22}/></Sequence>)}
 </AbsoluteFill>;
};
