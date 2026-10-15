import React,{useLayoutEffect,useRef} from 'react';
import {useCurrentFrame} from 'remotion';
const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const ease=(n:number)=>1-Math.pow(1-clamp(n),3);
/** Frame-deterministic Canvas artwork. No clocks, network assets or random particles. */
export const Atfro01Canvas:React.FC<{work:boolean;starts:number[]}>=({work,starts})=>{
 const ref=useRef<HTMLCanvasElement>(null);const f=useCurrentFrame();
 useLayoutEffect(()=>{
  const c=ref.current?.getContext('2d');if(!c)return;c.clearRect(0,0,1080,1220);
  const ink='#17221c',lime='#A9C448';
  const line=(points:number[][],progress:number,color=ink,width=2)=>{
   c.save();c.strokeStyle=color;c.lineWidth=width;c.lineCap='round';
   let length=0;for(let i=1;i<points.length;i++)length+=Math.hypot(points[i][0]-points[i-1][0],points[i][1]-points[i-1][1]);
   let left=length*clamp(progress);c.beginPath();c.moveTo(points[0][0],points[0][1]);
   for(let i=1;i<points.length&&left>0;i++){const a=points[i-1],b=points[i],d=Math.hypot(b[0]-a[0],b[1]-a[1]);const p=Math.min(1,left/d);c.lineTo(a[0]+(b[0]-a[0])*p,a[1]+(b[1]-a[1])*p);left-=d;}c.stroke();c.restore();
  };
  const card=(x:number,y:number,w:number,h:number,p:number,angle=0)=>{
   c.save();c.translate(x,y+(1-p)*30);c.rotate(angle);c.globalAlpha*=p;
   c.shadowColor='#111a201c';c.shadowBlur=22;c.shadowOffsetY=12;
   c.fillStyle='#FCFCF7';c.beginPath();c.roundRect(-w/2,-h/2,w,h,16);c.fill();c.shadowColor='transparent';
   c.strokeStyle='#D4D8CB';c.lineWidth=1;c.stroke();
   c.fillStyle=lime;c.beginPath();c.arc(-w/2+27,-h/2+28,6,0,Math.PI*2);c.fill();
   c.strokeStyle='#71806b';c.lineWidth=3;c.lineCap='round';c.beginPath();c.moveTo(-w/2+46,-h/2+28);c.lineTo(w/2-25,-h/2+28);c.stroke();
   c.strokeStyle='#C5CCBE';for(let k=0;k<2;k++){c.beginPath();c.moveTo(-w/2+25,-h/2+58+k*16);c.lineTo(w/2-25-k*25,-h/2+58+k*16);c.stroke();}c.restore();
  };
  for(let stage=0;stage<3;stage++){
   const local=f-starts[stage];if(local<0)continue;
   const exit=stage<2?1-ease((f-starts[stage+1])/9):1;if(exit<=0)continue;
   c.save();c.globalAlpha=exit;const p=ease(local/22);
   // Fine orbit lines draw on, rather than sitting as static decorative rings.
   c.strokeStyle='#17221c20';c.lineWidth=1.5;c.beginPath();c.ellipse(540,785,365,250,-.13,-Math.PI/2,-Math.PI/2+Math.PI*2*p);c.stroke();
   if(work&&stage===0){
    card(290,505,215,112,ease((local-4)/19),-.13);card(785,560,210,110,ease((local-12)/20),.13);
    line([[340,570],[385,610],[420,650]],ease((local-15)/26),'#17221c55');
    line([[740,615],[700,640],[665,660]],ease((local-23)/26),'#17221c55');
   }else if(work&&stage===1){
    const pts:number[][]=[];for(let i=0;i<=120;i++){const x=130+i*6.8;const pulse=Math.exp(-Math.pow((i-60)/12,2));const y=940+Math.sin(i*.55)*pulse*72;pts.push([x,y]);}
    line(pts,ease(local/33),'#829D36',3);
    for(let k=0;k<3;k++){c.fillStyle=lime;c.globalAlpha=exit*ease((local-k*5)/15)*.4;c.beginPath();c.arc(245+k*280,995,5,0,Math.PI*2);c.fill();}
   }else if((work&&stage===2)||(!work&&stage===1)){
    // Three component tiles assemble around the central software window.
    card(235,490,180,112,ease((local-2)/18),-.12);card(835,1010,195,120,ease((local-7)/22),.12);
    line([[295,545],[340,570],[390,605]],ease((local-13)/20),'#829D36',2);
    line([[765,970],[725,945],[690,910]],ease((local-20)/20),'#829D36',2);
   }else if(!work&&stage===0){
    c.strokeStyle='#829D3644';c.lineWidth=2;c.beginPath();c.arc(540,775,295,-Math.PI/2,-Math.PI/2+Math.PI*2*p);c.stroke();
    const a=-Math.PI/2+local*.016;c.fillStyle=lime;c.beginPath();c.arc(540+295*Math.cos(a),775+295*Math.sin(a),9,0,Math.PI*2);c.fill();
   }else{
    const nodes=[[270,505],[540,420],[810,505],[250,1055],[540,1140],[830,1055]];
    nodes.forEach(([x,y],i)=>{const q=ease((local-i*3)/22);line([[540,790],[x,y]],q,'#17221c32',1.5);c.save();c.globalAlpha*=q;c.fillStyle='#F9FAF3';c.strokeStyle='#7C8C6B';c.lineWidth=1.5;c.beginPath();c.arc(x,y,23*q,0,Math.PI*2);c.fill();c.stroke();c.fillStyle=lime;c.beginPath();c.arc(x,y,6*q,0,Math.PI*2);c.fill();c.restore();});
   }
   c.restore();
  }
 },[f,work,starts]);
 return <canvas ref={ref} width={1080} height={1220} style={{position:'absolute',left:0,top:0,width:1080,height:1220}}/>;
};
