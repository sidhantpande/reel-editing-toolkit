#!/usr/bin/env python3
"""Add supplied clinic end-card and neural-cleaned original narration to a base edit."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from scipy.io import wavfile
import clinic
from audio_enhance import enhance,normalize,run,digest
from finish_timing import finish_timing,validate_video_frames
R=clinic.ROOT;FF=clinic.FF

def finish(base,dialogue,output,qa_dir,attenuation=6):
 base=Path(base);dialogue=Path(dialogue);output=Path(output);qa_dir=Path(qa_dir);qa_dir.mkdir(parents=True,exist_ok=True)
 settings=json.loads((R/'styles/clinic-approved.json').read_text()).get('ending',{})
 asset=R/settings.get('asset','assets/brand/endcards/my-dental-reference-outro.mp4');manifest=json.loads(asset.with_name('manifest.json').read_text())
 if digest(asset)!=manifest['sha256']:raise RuntimeError('End-card asset was changed')
 asset_probe=clinic.probe(asset);validate_video_frames(next(s for s in asset_probe['streams'] if s['codec_type']=='video'),manifest['frames'])
 probe=clinic.probe(base);video=next(s for s in probe['streams'] if s['codec_type']=='video')
 if (video['width'],video['height'],video['avg_frame_rate'])!=(1080,1920,'30/1'):raise ValueError('Base must be the 1080×1920 / 30 fps clinic edit')
 frames=int(video['nb_frames']);timing=finish_timing(frames,manifest['frames'],settings.get('dissolve_frames',8),settings.get('spoken_signature_gap_frames',4));samples=frames*1600
 sr,dry=wavfile.read(dialogue)
 if sr!=48000 or len(dry)!=samples:raise ValueError('Base and original dialogue duration differ')
 cache=R/'.cache/finishing'/output.stem;cache.mkdir(parents=True,exist_ok=True)
 mastered,report=enhance(dialogue,cache/'voice',attenuation)
 outro_raw=cache/'outro-raw.wav'
 run([FF,'-v','error','-y','-i',asset,'-vn','-ac','2','-ar','48000','-af',f'apad,atrim=end_sample={timing["outro_frames"]*1600}','-c:a','pcm_f32le',outro_raw])
 outro_master=cache/'outro-matched.wav';outro_measure=normalize(outro_raw,outro_master,timing['outro_frames']*1600,target_i=settings.get('ending_loudness_lufs',-18))
 _,voice=wavfile.read(mastered);_,outro=wavfile.read(outro_master)
 # Keep the entire narration at full level. The supplied spoken signature begins
 # after a four-frame gap, independently of the earlier visual dissolve.
 total_samples=timing['total_frames']*1600;full=np.zeros((total_samples,2),dtype=np.float32);full[:samples]=voice
 offset=timing['audio_outro_start_frame']*1600
 fade_in=384;fade_out=1920;outro[:fade_in]*=np.linspace(0,1,fade_in)[:,None];outro[-fade_out:]*=np.linspace(1,0,fade_out)[:,None]
 full[offset:offset+len(outro)]+=outro
 audio=cache/'complete-audio.wav';wavfile.write(audio,48000,full)
 d=timing['dissolve_frames']/30;start=timing['video_outro_start_frame']/30;hold=timing['outro_hold_extra_frames']/30
 graph=f'[0:v]settb=AVTB,setpts=PTS-STARTPTS,format=yuv420p[base];[1:v]fps=30,scale=1080:1920,setsar=1,settb=AVTB,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={hold},format=yuv420p[end];[base][end]xfade=transition=fade:duration={d}:offset={start},fps=30,format=yuv420p[v]'
 output.parent.mkdir(parents=True,exist_ok=True)
 run([FF,'-v','error','-nostdin','-y','-filter_complex_threads','2','-i',base,'-i',asset,'-i',audio,'-filter_complex',graph,'-map','[v]','-map','2:a:0','-frames:v',timing['total_frames'],'-t',timing['total_frames']/30,'-c:v','libx264','-threads','4','-preset','fast','-crf','18','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',output])
 encoded=clinic.probe(output);validate_video_frames(next(s for s in encoded['streams'] if s['codec_type']=='video'),timing['total_frames'])
 encoded_audio=next(s for s in encoded['streams'] if s['codec_type']=='audio')
 if abs(float(encoded_audio['duration'])-timing['total_frames']/30)>.022:raise RuntimeError('Encoded audio is shorter than the complete finishing timeline')
 note={'base':str(base),'base_sha256':digest(base),'original_dialogue':str(dialogue),'outro':str(asset),'outro_sha256':digest(asset),'timing':timing,'enhancement':report,'outro_loudness_target_lufs':-18,'outro_measurement':outro_measure,'output':str(output),'output_sha256':digest(output),'status':'Review export; original speech retained; supplied ending inserted; human listening unavailable','future_broll': 'Reel-08 remains an A-roll preview until requested clips return' if 'aroll' in base.name else None}
 (qa_dir/'finish-plan.json').write_text(json.dumps(note,indent=2)+'\n');print('Finished',output,flush=True)
 return output

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--dialogue',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--qa-dir',type=Path,required=True);p.add_argument('--attenuation',type=float,default=6);a=p.parse_args();finish(a.base,a.dialogue,a.output,a.qa_dir,a.attenuation)
if __name__=='__main__':main()
