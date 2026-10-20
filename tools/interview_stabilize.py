#!/usr/bin/env python3
import cv2,numpy as np,json,subprocess,argparse,hashlib
from pathlib import Path
cv2.setNumThreads(2)
parser=argparse.ArgumentParser(description='Rigid camera stabilization using editor-selected background; preserves native cadence. Requires OpenCV and FFmpeg.')
parser.add_argument('source',type=Path);parser.add_argument('output',type=Path);parser.add_argument('--analysis',type=Path,required=True)
parser.add_argument('--exclude',type=float,nargs=4,required=True,metavar=('X0','Y0','X1','Y1'),help='Normalized speaker rectangle to exclude; calibrate to actual footage')
args=parser.parse_args();src=args.source;out=args.output
if out.exists():raise ValueError('Output exists; use a new version')
x0,y0,x1,y1=args.exclude
if not (0<=x0<x1<=1 and 0<=y0<y1<=1):raise ValueError('Invalid speaker exclusion rectangle')
if src.resolve()==out.resolve():raise ValueError('Original must remain untouched')
out.parent.mkdir(parents=True,exist_ok=True);args.analysis.parent.mkdir(parents=True,exist_ok=True)
partial=out.with_name(out.stem+'.partial.mp4')
if partial.exists():raise ValueError('Interrupted partial exists; inspect it before retrying')
cap=cv2.VideoCapture(str(src));fps=cap.get(cv2.CAP_PROP_FPS);old=None;steps=[];n=0;sw=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH));sh=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT));ww=540;hh=round(sh/max(1,sw)*ww)
if sw<=0 or sh<=0 or fps<=0:raise ValueError('Unreadable source video')
while True:
 ok,f=cap.read()
 if not ok:break
 g=cv2.cvtColor(cv2.resize(f,(ww,hh)),cv2.COLOR_BGR2GRAY)
 if old is not None:
  mask=np.full_like(old,255);mask[round(y0*hh):round(y1*hh),round(x0*ww):round(x1*ww)]=0
  p=cv2.goodFeaturesToTrack(old,300,.003,8,mask=mask)
  step=np.zeros(3)
  if p is not None and len(p)>6:
   q,st,err=cv2.calcOpticalFlowPyrLK(old,g,p,None,winSize=(31,31),maxLevel=4)
   a=p[st.ravel()==1];b=q[st.ravel()==1]
   if len(a)>6:
    mat,inside=cv2.estimateAffinePartial2D(a,b,method=cv2.RANSAC,ransacReprojThreshold=1.25)
    if mat is not None:step=np.array([mat[0,2],mat[1,2],np.arctan2(mat[1,0],mat[0,0])])
  steps.append(step)
 old=g;n+=1
cap.release()
if n<2:raise ValueError('At least two frames required')
steps=np.vstack([np.zeros(3),np.array(steps)]);path=np.cumsum(steps,axis=0)
# Symmetric Gaussian camera path. Translation/rotation only; no face or body deformation.
x=np.arange(-36,37);weights=np.exp(-.5*(x/13)**2);weights/=weights.sum()
smooth=np.vstack([np.convolve(np.pad(path[:,j],(36,36),mode='edge'),weights,'valid') for j in range(3)]).T
correction=smooth-path
args.analysis.write_text(json.dumps(dict(engine='OpenCV LK background features + RANSAC rigid camera motion',fps=fps,frames=n,mask=args.exclude,source=str(src.resolve()),output=str(out.resolve()),source_sha256=hashlib.file_digest(src.open('rb'),'sha256').hexdigest(),smoothing_frames=73,sigma_frames=13,max_correction=abs(correction).max(axis=0).tolist(),camera_path=path.tolist(),correction=correction.tolist()),indent=2))
cap=cv2.VideoCapture(str(src))
p=subprocess.Popen(['ffmpeg','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{sw}x{sh}','-r',str(fps),'-i','-','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-y',str(partial)],stdin=subprocess.PIPE)
for i,delta in enumerate(correction):
 ok,f=cap.read()
 if not ok:raise RuntimeError('Missing input frame')
 dx,dy,angle=delta;angle=np.clip(angle,-.025,.025)
 mat=np.array([[np.cos(angle),-np.sin(angle),dx*sw/ww],[np.sin(angle),np.cos(angle),dy*sh/hh]],dtype=np.float32)
 fixed=cv2.warpAffine(f,mat,(sw,sh),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT_101)
 p.stdin.write(fixed.tobytes())
 if i%200==0:print(i,flush=True)
p.stdin.close();assert p.wait()==0;cap.release()
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(partial)]));v=next(t for t in info['streams'] if t['codec_type']=='video')
if int(v['nb_frames'])!=n or (v['width'],v['height'])!=(sw,sh):raise RuntimeError('Derivative frame/dimension mismatch')
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(partial),'-f','null','-'],check=True)
partial.replace(out)
report=json.loads(args.analysis.read_text());report.update(status='Encoded full decode and frame count passed; visual review pending',output_sha256=hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),audio='Silent picture derivative; use unchanged original source dialogue')
args.analysis.write_text(json.dumps(report,indent=2)+'\n');print(out,flush=True)
