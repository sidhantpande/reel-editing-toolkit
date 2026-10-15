import React,{useEffect,useLayoutEffect,useRef,useState} from 'react';
import {continueRender,delayRender,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
/** Decode and paint the complete still before capture; avoid partial first-frame JPEG compositing. */
export const StillBlend:React.FC<{src:string;duration?:number}>=({src,duration})=>{
 const frame=useCurrentFrame(),{width,height}=useVideoConfig();const ref=useRef<HTMLCanvasElement>(null);
 const [handle]=useState(()=>delayRender('Decoding cut-transition still'));const [picture,setPicture]=useState<HTMLImageElement|null>(null);const released=useRef(false);
 useEffect(()=>{let live=true;const picture=new window.Image();picture.src=staticFile(src);picture.decode().then(()=>{if(live)setPicture(picture);}).catch(error=>{console.error(error);if(!released.current){released.current=true;continueRender(handle);}});return()=>{live=false;if(!released.current){released.current=true;continueRender(handle);}};},[src,handle]);
 useLayoutEffect(()=>{if(!picture)return;const c=ref.current?.getContext('2d');if(!c)return;c.clearRect(0,0,width,height);c.globalAlpha=duration?Math.pow(Math.max(0,1-(frame+1)/(duration+1)),1.5):1;c.drawImage(picture,0,0,width,height);if(!released.current){released.current=true;continueRender(handle);}},[picture,frame,duration,width,height,handle]);
 return <canvas ref={ref} width={width} height={height} style={{position:'absolute',left:0,top:0,width,height}}/>;
};
