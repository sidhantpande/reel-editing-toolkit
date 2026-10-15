import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile} from 'remotion';
import {TransitionSeries,linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {PaperScene,PaperKind} from './PaperScene';
import {Brand} from '../types';
export const PaperShowcase:React.FC<{brand:Brand}>=({brand})=>{
 const kinds:PaperKind[]=brand==='niolearn'?['paper-possibilities','paper-pathways','paper-crowd','paper-partnership']:['paper-partnership','paper-crowd','paper-pathways','paper-possibilities'];
 return <AbsoluteFill><TransitionSeries>{kinds.map((kind,i)=><React.Fragment key={kind}><TransitionSeries.Sequence durationInFrames={180}><PaperScene brand={brand} kind={kind}/></TransitionSeries.Sequence>{i<3&&<TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames:10})}/>}</React.Fragment>)}</TransitionSeries>
 <Audio src={staticFile(`assets/music/${brand==='niolearn'?'calm-focus':'soft-momentum'}.wav`)} volume={.5}/>
 {[22,192,362,532].map(f=><Sequence key={f} from={f}><Audio src={staticFile('assets/sfx/transition-air.wav')} volume={.2}/></Sequence>)}
 </AbsoluteFill>;
};
