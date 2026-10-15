import React,{useEffect,useState} from 'react';
import {continueRender,delayRender,staticFile} from 'remotion';
export const Fonts:React.FC=()=>{
 const [handle]=useState(()=>delayRender('Loading local brand fonts'));
 useEffect(()=>{let cancelled=false;Promise.all(['Sora','Inter'].map(async name=>{const font=new FontFace(name,`url(${staticFile(`assets/fonts/${name}.ttf`)})`,{weight:'100 900'});await font.load();(document.fonts as FontFaceSet & {add:(font:FontFace)=>FontFaceSet}).add(font);})).then(()=>{if(!cancelled)continueRender(handle);}).catch(e=>{console.error(e);continueRender(handle);});return()=>{cancelled=true;};},[handle]);return null;
};
