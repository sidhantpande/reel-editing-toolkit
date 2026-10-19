"""Quiet original toolkit music, speech ducking and sparse transition air."""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np
from scipy.io import wavfile
import clinic
from audio_enhance import normalize

def digest(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def read(path):
    sr,a=wavfile.read(path)
    if sr!=48000:raise ValueError('Music assets must be 48kHz')
    if np.issubdtype(a.dtype,np.integer):a=a.astype(np.float32)/np.iinfo(a.dtype).max
    if a.ndim==1:a=np.stack([a,a],axis=1)
    return a.astype(np.float32)

def mix(plan,voice,folder):
    config=plan['music'];source=Path(config['path']);sfx=Path(config['transition_sfx'])
    if digest(source)!=config['sha256'] or digest(sfx)!=config['sfx_sha256']:raise ValueError('Music/SFX asset checksum changed')
    folder.mkdir(parents=True,exist_ok=True);samples=round(plan['duration_seconds']*48000)
    bed=read(source);continuous=np.zeros((samples,2),np.float32)
    # The original composition already has matching two-second entrance/exit ramps.
    step=len(bed)-96000
    if step<=0:raise ValueError('Music too short to join')
    for start in range(0,samples,step):
        n=min(len(bed),samples-start);continuous[start:start+n]+=bed[:n]
    ramp=min(48000,samples//2);continuous[:ramp]*=np.linspace(0,1,ramp)[:,None];continuous[-ramp:]*=np.linspace(1,0,ramp)[:,None]
    rawbed=folder/'continuous-bed.wav';wavfile.write(rawbed,48000,continuous)
    levelled=folder/'bed-levelled.wav';normalize(rawbed,levelled,samples,target_i=config.get('bed_lufs',-31))
    air=np.zeros((samples,2),np.float32);effect=read(sfx)*config.get('sfx_gain',.05)
    for slot in plan['broll_slots']:
        for t in [slot['timeline_in'],slot['timeline_out']]:
            start=max(0,round((t-.08)*48000));n=min(samples-start,len(effect));air[start:start+n]+=effect[:n]
    airpath=folder/'transition-air.wav';wavfile.write(airpath,48000,air)
    raw=folder/'mix-before-master.wav'
    graph='[0:a]asplit=2[lead][key];[1:a]highpass=f=160,lowpass=f=6500[bed];[bed][key]sidechaincompress=threshold=0.08:ratio=2.2:attack=35:release=550:makeup=1[duck];[lead][duck][2:a]amix=inputs=3:duration=first:normalize=0[out]'
    clinic.run([clinic.FF,'-v','error','-y','-i',voice,'-i',levelled,'-i',airpath,'-filter_complex',graph,'-map','[out]','-c:a','pcm_f32le','-ar','48000',raw])
    output=folder/'dialogue-music-master.wav';stats=normalize(raw,output,samples)
    report={'source':str(source),'source_sha256':digest(source),'rights':'Original deterministic toolkit composition; tools/build_assets.py','bed_target_lufs_before_duck':config.get('bed_lufs',-31),'sidechain':{'threshold':.08,'ratio':2.2,'attack_ms':35,'release_ms':550},'sfx':str(sfx),'sfx_gain':config.get('sfx_gain',.05),'samples':samples,'sample_rate':48000,'voice_source':str(voice),'voice_sha256':digest(voice),'normalization':stats,'output':str(output),'human_listening_available':False}
    (folder/'mix-report.json').write_text(json.dumps(report,indent=2)+'\n')
    return output
