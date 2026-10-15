import {SchoolBroll,SchoolKind} from './projects/SchoolBroll';
import {ComparisonBroll,ComparisonKind} from './projects/ComparisonBroll';
import {ProjectBroll,ProjectKind} from './projects/ProjectBroll';
import {StudyBroll,StudyKind} from './projects/StudyBroll';
import {Nio07Broll,Nio07Kind} from './projects/Nio07Broll';
import {Nio04Broll,Nio04Kind} from './projects/Nio04Broll';
import React from 'react';
import {Composition} from 'remotion';
import {Atfro01Broll,Atfro01Kind} from './projects/Atfro01Broll';
import {StyleLab} from './StyleLab';
import {PaperScene,PaperKind} from './premium/PaperScene';
import {PaperShowcase} from './premium/PaperShowcase';
import {TransitionLab} from './Transitions';
import {Broll} from './Broll';
import {Reel} from './Reel';
import {ReelProps,BrollKind} from './types';
const defaults:ReelProps={brand:'niolearn',durationInFrames:300,clips:[],captions:[],broll:[],endCard:true};
export const Root:React.FC=()=> <>
 {(['atfro-school-film','atfro-school-plan','atfro-school-workflow'] as SchoolKind[]).map(kind=><Composition key={kind} id={'School-'+kind} component={SchoolBroll} defaultProps={{kind,transparent:false,duration:240}} width={1080} height={1920} fps={30} durationInFrames={240} calculateMetadata={({props})=>({durationInFrames:props.duration})}/>)}
 {(['nio-story-comparison','nio-compare-board','nio-brand-services','nio-access-calendar'] as ComparisonKind[]).map(kind=><Composition key={kind} id={'Compare-'+kind} component={ComparisonBroll} defaultProps={{kind,transparent:false,duration:600,beats:[] as number[],labels:[] as string[]}} width={1080} height={1920} fps={30} durationInFrames={600} calculateMetadata={({props})=>({durationInFrames:props.duration})}/>)}
 {(['nio-project-phone','nio-project-structure','nio-project-attendance'] as ProjectKind[]).map(kind=><Composition key={kind} id={'Project-'+kind} component={ProjectBroll} defaultProps={{kind,transparent:false,duration:240}} width={1080} height={1920} fps={30} durationInFrames={240} calculateMetadata={({props})=>({durationInFrames:props.duration})}/>)}
 {(['nio-study-choice','nio-study-logic','nio-intro-problem','nio-intro-project','nio-intro-curiosity','nio-mock-read','nio-mock-eliminate','nio-story-profile','nio-story-mock'] as StudyKind[]).map(kind=>{const duration=kind==='nio-story-mock'?688:kind==='nio-story-profile'?239:180;return <Composition key={kind} id={'Study-'+kind} component={StudyBroll} defaultProps={{kind,transparent:false,duration}} width={1080} height={1920} fps={30} durationInFrames={duration} calculateMetadata={({props})=>({durationInFrames:props.duration})}/>})}
 {(['nio-system-diagnostic','nio-system-prep','nio-system-review','nio-system-interview','nio-system-path'] as Nio07Kind[]).map(kind=><Composition key={kind} id={'Nio07-'+kind} component={Nio07Broll} defaultProps={{kind,transparent:false,duration:180}} width={1080} height={1920} fps={30} durationInFrames={180} calculateMetadata={({props})=>({durationInFrames:props.duration})}/>)}
 {(['nio-parents-authority','nio-parents-credential','nio-parents-fees','nio-parents-outcomes','nio-parents-conversation','nio-parents-credential-fees'] as Nio04Kind[]).map(kind=><Composition key={kind} id={'Nio04-'+kind} component={Nio04Broll} defaultProps={{kind,transparent:false,duration:180,beats:[150]}} width={1080} height={1920} fps={30} durationInFrames={180} calculateMetadata={({props})=>({durationInFrames:props.duration})}/>)}
 {(['atfro-work','atfro-process'] as Atfro01Kind[]).map(kind=><Composition key={kind} id={'Atfro01-'+kind} component={Atfro01Broll} defaultProps={{kind,transparent:false,duration:180}} width={1080} height={1920} fps={30} durationInFrames={180} calculateMetadata={({props})=>({durationInFrames:props.duration})}/>)}
 <Composition id="PremiumNiolearnV3" component={PaperShowcase} defaultProps={{brand:'niolearn' as const}} width={1080} height={1920} fps={30} durationInFrames={690}/>
 <Composition id="PremiumAtfroV3" component={PaperShowcase} defaultProps={{brand:'atfro' as const}} width={1080} height={1920} fps={30} durationInFrames={690}/>
 {(['paper-possibilities','paper-pathways','paper-crowd','paper-partnership'] as PaperKind[]).map(kind=><Composition key={kind} id={`Premium-${kind}`} component={PaperScene} defaultProps={{brand:'niolearn' as const,kind,transparent:false,duration:180}} width={1080} height={1920} fps={30} durationInFrames={180} calculateMetadata={({props})=>({durationInFrames:props.duration??180})}/>)}
 <Composition id="StyleLab" component={StyleLab} defaultProps={{brand:'niolearn' as const}} width={1080} height={1920} fps={30} durationInFrames={1080}/>
 <Composition id="AtfroStyleLab" component={StyleLab} defaultProps={{brand:'atfro' as const}} width={1080} height={1920} fps={30} durationInFrames={1080}/>
 <Composition id="TransitionLab" component={TransitionLab} width={1080} height={1920} fps={30} durationInFrames={540}/>
 <Composition id="Reel" component={Reel} defaultProps={defaults} width={1080} height={1920} fps={30} durationInFrames={300} calculateMetadata={({props})=>({durationInFrames:props.durationInFrames})}/>
 {(['crowd','pathways','lead-flow','timeline','compare','countdown'] as BrollKind[]).map(kind=><Composition key={kind} id={`Broll-${kind}`} component={Broll} defaultProps={{brand:'niolearn' as const,kind,transparent:true,duration:180}} width={1080} height={1920} fps={30} durationInFrames={180} calculateMetadata={({props})=>({durationInFrames:props.duration??180})}/>)}
 </>;
