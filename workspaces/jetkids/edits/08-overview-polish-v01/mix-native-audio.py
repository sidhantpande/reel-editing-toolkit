"""Native-speed supplied-mix edit; all source playback ratios are exactly1."""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
import librosa
R=Path.cwd();P=R/'workspaces/jetkids/edits/08-overview-polish-v01';M=R/'media/music/jetkids/overview-user-tracks';SR=48000;DURATION=86.5;START=28.74

def frame(t):return round(t*SR)
def normalise(source,dest,target):
    result=subprocess.run(['ffmpeg','-hide_banner','-i',str(source),'-af',f'loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    m=json.loads(result.stderr[result.stderr.rfind('{'):]);f=f"loudnorm=I={target}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
    subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-i',str(source),'-af',f,'-ar',str(SR),'-c:a','pcm_s24le',str(dest)],check=True);return m
for role in ['entry','diya']:
    normalise(M/(role+'.wav'),M/(role+'-v03-level.wav'),-16)
a,sr=sf.read(M/'entry-v03-level.wav',dtype='float32',always_2d=True);assert sr==SR
b,sr=sf.read(M/'diya-v03-level.wav',dtype='float32',always_2d=True);assert sr==SR
# Native source sample slices, no change of playback rate or time stretching. Repeat exactly8s.
left=a[frame(.2):frame(16.22)].copy();right=a[frame(8.22):frame(24.2)].copy();n=frame(.005)
left[-n:]*=np.cos(np.linspace(0,np.pi/2,n))[:,None];right[:n]*=np.sin(np.linspace(0,np.pi/2,n))[:,None]
a=np.concatenate([left,right]);b=b[frame(.04):];start=frame(START);count=len(a)-start
shortfall=max(0,frame(DURATION)-start-len(b));assert shortfall<=frame(.1)
if shortfall:b=np.pad(b,((0,shortfall),(0,0)))

def harmonic(x):
    result=[]
    for channel in range(2):
        st=librosa.stft(x[:,channel],n_fft=2048,hop_length=512);h,_=librosa.decompose.hpss(st,kernel_size=31,margin=(2.,2.));result.append(librosa.istft(h,hop_length=512,length=len(x)))
    return np.stack(result,axis=1)
ae=a[start:];be=b[:count];ah=harmonic(ae);bh=harmonic(be);ap=ae-ah;bp=be-bh;t=np.arange(count)/SR
# The tempos differ naturally: exchange percussion rather than overlapping grids.
ah_gain=np.cos(np.pi/2*np.clip(t/.85,0,1))**2
bh_gain=np.sin(np.pi/2*np.clip((t-.95)/1.4,0,1))**2
ap_gain=np.cos(np.pi/2*np.clip((t-1.0)/.3,0,1))**2
bp_gain=np.sin(np.pi/2*np.clip((t-1.3)/.2,0,1))**2
bridge=ah*ah_gain[:,None]+bh*bh_gain[:,None]+ap*ap_gain[:,None]+bp*bp_gain[:,None]
mix=np.zeros((frame(DURATION),2),dtype='float32');mix[:start]=a[:start];mix[start:start+count]=bridge;mix[start+count:]=b[count:frame(DURATION)-start]
f=np.arange(len(mix));mix*=np.minimum(np.clip(f/frame(.06),0,1),np.clip((len(mix)-1-f)/frame(.85),0,1))[:,None]
sf.write(M/'v03-native-mixed.wav',mix,SR,subtype='PCM_24');measured=normalise(M/'v03-native-mixed.wav',M/'v03-native-normalised.wav',-14)
info=sf.info(M/'v03-native-normalised.wav');assert info.frames==frame(DURATION) and info.samplerate==SR
(P/'audio-mix.json').write_text(json.dumps({'duration':DURATION,'sample_rate':SR,'samples':info.frames,'entry_tempo_ratio':1,'continuation_tempo_ratio':1,'time_stretch':False,'pitch_change':False,'entry_edits':[{'timeline_in':0,'source_in':.2,'source_out':16.22,'speed':1},{'timeline_in':16.02,'source_in':8.22,'source_out':24.2,'speed':1}],'repeat_join_seconds':16.02,'anti_click_ms':5,'tail_padding_samples':shortfall,'tail_padding_note':'Only the final50.6ms of the0.85s ending fade requires zero padding; no tempo change.','continuation_source_in':.04,'continuation_timeline_in':START,'handover_seconds':count/SR,'percussion_pivot_seconds':30.04,'method':'Native-speed sample slices; one8s phrase repeat. HPSS short overlap: outgoing harmony fades0.85s; incoming harmony rises0.95–2.35s; outgoing percussion falls1.0–1.3s and incoming rises1.3–1.5s. Different tempos remain unchanged.','first_pass_loudness':measured,'mixed_pcm_sha256':hashlib.file_digest((M/'v03-native-normalised.wav').open('rb'),'sha256').hexdigest(),'listening_review':'not attested'},indent=2)+'\n');print('Native-speed mix complete',info.frames,flush=True)
