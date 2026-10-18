#!/usr/bin/env python3
"""Pinned full-band neural cleanup, conservative attenuation and exact PCM timing."""
import hashlib,json,os,platform,subprocess,urllib.request
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy import signal
import clinic
R=clinic.ROOT;FF=clinic.FF
BINARY_URL='https://github.com/Rikorose/DeepFilterNet/releases/download/v0.5.6/deep-filter-0.5.6-aarch64-apple-darwin'
MODEL_URL='https://raw.githubusercontent.com/Rikorose/DeepFilterNet/v0.5.6/models/DeepFilterNet3_onnx.tar.gz'
BINARY_SHA='4601e7f4e4c03e59a4c5b5000216ef3add3e808799cfccd95e14e83ea4611081'
MODEL_SHA='c94d91f70911001c946e0fabb4aa9adc37045f45a03b56008cb0c8244cb63616'

def digest(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def run(args):
 p=subprocess.run([str(s) for s in args],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr[-5000:])
 return p

def install():
 binary=R/'.cache/bin/deep-filter-0.5.6-arm64';model=R/'.cache/models/deepfilternet3/DeepFilterNet3_onnx.tar.gz'
 if platform.system()!='Darwin' or platform.machine()!='arm64':raise RuntimeError('This pinned executable targets Apple Silicon macOS; configure a supported DeepFilterNet binary for this host.')
 for path,url in [(binary,BINARY_URL),(model,MODEL_URL)]:
  if not path.exists():
   path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_suffix(path.suffix+'.partial')
   try:urllib.request.urlretrieve(url,temp);temp.replace(path)
   finally:temp.unlink(missing_ok=True)
 binary.chmod(0o755)
 if digest(binary)!=BINARY_SHA:raise RuntimeError('DeepFilterNet executable checksum mismatch')
 if digest(model)!=MODEL_SHA:raise RuntimeError('DeepFilterNet model checksum mismatch')
 return binary,model

def normalize(source,target,samples,target_i=-16):
 # Both input and measurement are stereo; no post-normalization channel boost.
 prefix='highpass=f=70'
 test=run([FF,'-v','info','-i',source,'-af',f'{prefix},loudnorm=I={target_i}:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
 start=test.stderr.rfind('{');stats=json.loads(test.stderr[start:test.stderr.rfind('}')+1])
 filt=(f'{prefix},loudnorm=I={target_i}:TP=-1.5:LRA=11:measured_I={stats["input_i"]}:measured_TP={stats["input_tp"]}:'
       f'measured_LRA={stats["input_lra"]}:measured_thresh={stats["input_thresh"]}:offset={stats["target_offset"]}:linear=true,'
       f'aresample=48000,apad,atrim=end_sample={samples}')
 run([FF,'-v','error','-y','-i',source,'-af',filt,'-c:a','pcm_f32le',target])
 return stats

def enhance(source,cache,attenuation=6):
 cache=Path(cache);cache.mkdir(parents=True,exist_ok=True);source=Path(source)
 binary,model=install();sr,a=wavfile.read(source)
 if sr!=48000:raise ValueError('Enhancement requires the original 48 kHz dialogue assembly')
 if np.issubdtype(a.dtype,np.integer):a=a.astype(np.float32)/np.iinfo(a.dtype).max
 a=a.astype(np.float32);mono=a.mean(axis=1) if a.ndim==2 else a
 gain=min(10**(-23/20)/max(1e-12,float(np.sqrt(np.mean(mono**2)))),.92/max(1e-12,float(np.max(abs(mono)))))
 # The compensated Rust output is 1440 samples shorter. Extra tail context
 # preserves the final phoneme; only then crop to the exact edit duration.
 model_input=cache/'model-input-padded.wav';samples=len(mono)
 wavfile.write(model_input,48000,np.round(np.clip(np.pad(mono*gain,(0,4800)),-1,1)*32767).astype(np.int16))
 target_dir=cache/'neural';target_dir.mkdir(exist_ok=True)
 run([binary,'-m',model,'-D','-a',attenuation,'-o',target_dir,model_input])
 rate,wet=wavfile.read(target_dir/model_input.name)
 if rate!=48000 or len(wet)<samples:raise RuntimeError('Enhanced output is too short after context padding')
 wet=wet[:samples].astype(np.float32)/32768
 raw_stereo=cache/'enhanced-stereo.wav';wavfile.write(raw_stereo,48000,np.stack([wet,wet],axis=1))
 mastered=cache/'dialogue-enhanced-master.wav';normalization=normalize(raw_stereo,mastered,samples)
 span=min(samples,480000);dry=mono[:span]*gain;candidate=wet[:span]
 corr=signal.correlate(candidate,dry,method='fft');lags=signal.correlation_lags(len(candidate),len(dry));mask=abs(lags)<=2400
 lag=int(lags[mask][np.argmax(corr[mask])])
 if abs(lag)>48:raise RuntimeError(f'Unexpected enhancement lag: {lag} samples')
 count=samples//960;frame_dry=np.sqrt(np.mean((mono[:count*960]*gain).reshape(-1,960)**2,axis=1));frame_wet=np.sqrt(np.mean(wet[:count*960].reshape(-1,960)**2,axis=1));quiet=(frame_dry>np.percentile(frame_dry,5))&(frame_dry<np.percentile(frame_dry,20));voice=frame_dry>np.percentile(frame_dry,60)
 report={'engine':'DeepFilterNet3','release':'v0.5.6','attenuation_limit_db':attenuation,'model_sha256':digest(model),'binary_sha256':digest(binary),'binary_source':BINARY_URL,'model_source':MODEL_URL,'input':str(source),'input_sha256':digest(source),'samples':samples,'output_samples':samples,'sample_rate':48000,'gain_before_model':gain,'tail_context_samples':4800,'measured_lag_samples':lag,'quiet_frame_reduction_db':float(np.median(20*np.log10((frame_dry[quiet]+1e-10)/(frame_wet[quiet]+1e-10)))),'voiced_frame_level_change_db_before_mastering':float(np.median(20*np.log10((frame_wet[voice]+1e-10)/(frame_dry[voice]+1e-10)))),'normalization':normalization,'output':str(mastered),'pitch_or_time_modification':False,'human_listening_available':False,'interpretation':'Quiet/voiced frame energy proxies and delay checks; these are not subjective sound-quality or clinical intelligibility scores.'}
 (cache/'enhancement-report.json').write_text(json.dumps(report,indent=2)+'\n')
 return mastered,report
