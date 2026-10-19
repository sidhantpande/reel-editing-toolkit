#!/usr/bin/env python3
"""Fetch user-selected music, trim exact PCM slices, index MP3 assets and export30fps cues."""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path
from log_colour import ROOT, digest, probe, write

DEFAULT=ROOT/'workspaces/jetkids/music-cues.json'
MANIFEST=ROOT/'workspaces/jetkids/music-assets.json'

def validate(track):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{2,80}',track.get('id','')):raise ValueError('Safe asset ID required')
    if not re.fullmatch(r'https://(?:www\.)?youtube\.com/watch\?v=[A-Za-z0-9_-]{11}',track.get('url','')):raise ValueError('Use an exact YouTube watch URL')
    a,b=track['source_in'],track['source_out']
    if not all(isinstance(t,(int,float)) and math.isfinite(t) for t in (a,b)) or not 0<=a<b:raise ValueError('Invalid source slice')
    if track.get('fps')!=30:raise ValueError('Cue frame timebase must be30fps')
    for m in track['markers']:
        if not a<=m['source_seconds']<b:raise ValueError('Marker outside slice')
    return track

def cue_markers(track):
    validate(track)
    return [{**m,'timeline_seconds':round(m['source_seconds']-track['source_in'],6),'timeline_frame':round((m['source_seconds']-track['source_in'])*30),'status':'user supplied structural cue; musical event not verified'} for m in track['markers']]

def title_matches(track,title):
    clean=lambda s:re.sub(r'[^a-z0-9]','',s.lower())
    expected=clean(track['song']);actual=clean(title)
    if expected in actual:return True
    if any(clean(alias) in actual for alias in track.get('title_aliases',[])):return True
    # Title spelling variants (e.g. Illahi/Ilahi, Kandhon/Kandho) need review, not a guessed match.
    terms=[t for t in re.findall(r'[a-z0-9]+',track['song'].lower()) if t not in ('se','ki','ke','mein','hain','version','rock')]
    return bool(terms) and sum(t in actual for t in terms)/len(terms)>=.8

def ytdlp(args,timeout=180):
    cmd=[sys.executable,'-m','yt_dlp','--no-playlist','--no-progress','--retries','1','--socket-timeout','20','--js-runtimes','node',*args]
    return subprocess.run(cmd,check=True,capture_output=True,text=True,timeout=timeout).stdout

def loudness(path):
    p=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-i',str(path),'-af','loudnorm=I=-14:TP=-1:LRA=11:print_format=json','-f','null','-'],check=True,capture_output=True,text=True)
    return json.loads(p.stderr[p.stderr.rfind('{'):])

def extract_pcm_slice(source,target,start,end):
    # Opus can begin at PTS+7.5ms. Use decoded sample zero as the documented
    # song origin, then trim sample indices after resampling, never pad missing audio.
    first,last=round(start*48000),round(end*48000)
    filters=f'aresample=48000,asetpts=N/SR/TB,atrim=start_sample={first}:end_sample={last},asetpts=PTS-STARTPTS'
    subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-i',str(source),'-vn','-af',filters,'-c:a','pcm_s24le',str(target)],check=True)
    info=probe(target);audio=next(s for s in info['streams'] if s['codec_type']=='audio')
    if round(float(audio['duration'])*48000)!=last-first:raise ValueError('PCM slice sample-count mismatch')

def beat_rows(values,source_in,duration):
    return [{'timeline_seconds':round(float(t),6),'source_seconds':round(float(t)+source_in,6),'frame_30fps':round(float(t)*30)} for t in values if 0<=t<duration and round(float(t)*30)<round(duration*30)]

def analyse_beats(path,track,out):
    import librosa
    import numpy as np
    y,sr=librosa.load(path,sr=22050,mono=True)
    _,percussive=librosa.effects.hpss(y)
    env=librosa.onset.onset_strength(y=percussive,sr=sr,hop_length=256)
    tempo,beats=librosa.beat.beat_track(onset_envelope=env,sr=sr,hop_length=256,trim=False)
    times=librosa.frames_to_time(beats,sr=sr,hop_length=256)
    onset_frames=librosa.onset.onset_detect(onset_envelope=env,sr=sr,hop_length=256,backtrack=False)
    onsets=librosa.frames_to_time(onset_frames,sr=sr,hop_length=256)
    duration=track['source_out']-track['source_in']
    def rows(values):return beat_rows(values,track['source_in'],duration)
    result={'asset':track['id'],'pcm_sha256':digest(path),'method':'librosa HPSS percussive onset envelope + dynamic-programming beat tracker','librosa_version':librosa.__version__,'hop_samples':256,'sample_rate':sr,'tempo_bpm_estimate':float(np.asarray(tempo).reshape(-1)[0]),'beats':rows(times),'onsets':rows(onsets),'user_structure_markers':cue_markers(track),'verification':'Automatic beat/onset candidates only. No inferred lyric, chorus or listening approval.'}
    write(out,result)
    csv=out.with_suffix('.csv');csv.write_text('type,timeline_seconds,source_seconds,frame_30fps,label\n'+''.join(f"{kind},{m['timeline_seconds']},{m['source_seconds']},{m['frame_30fps']},\n" for kind in ('beats','onsets') for m in result[kind])+''.join(f"user_cue,{m['timeline_seconds']},{m['source_seconds']},{m['timeline_frame']},{m['label']}\n" for m in result['user_structure_markers']))
    return result

def export_markers(record,out):
    """FCP7 XML audio sequence + markers, importable by Premiere; no app required."""
    import xml.etree.ElementTree as ET
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    tree=ET.Element('xmeml',version='4');seq=ET.SubElement(tree,'sequence',id=record['id'])
    def text(parent,name,value):ET.SubElement(parent,name).text=str(value)
    def rate(parent):
        r=ET.SubElement(parent,'rate');text(r,'timebase',30);text(r,'ntsc','FALSE')
    total=round(record['duration']*30);text(seq,'name',record['id']+' — '+record['subject']);text(seq,'duration',total);rate(seq)
    media=ET.SubElement(seq,'media');audio=ET.SubElement(media,'audio');text(audio,'numOutputChannels',2)
    for channel in (1,2):
        track=ET.SubElement(audio,'track');text(track,'outputchannelindex',channel)
        clip=ET.SubElement(track,'clipitem',id=record['id']+'-audio-'+str(channel))
        for name,value in [('name',record['subject']),('duration',total),('start',0),('end',total),('in',0),('out',total)]:text(clip,name,value)
        rate(clip);f=ET.SubElement(clip,'file',id=record['id']+'-file')
        if channel==1:
            text(f,'name',Path(record['repositoryFile']).name);text(f,'pathurl',(ROOT/record['repositoryFile']).as_uri());rate(f);text(f,'duration',total)
            fm=ET.SubElement(f,'media');fa=ET.SubElement(fm,'audio');text(fa,'samplerate',48000);text(fa,'channelcount',2)
        source=ET.SubElement(clip,'sourcetrack');text(source,'mediatype','audio');text(source,'trackindex',channel)
        for linked_channel in (1,2):
            link=ET.SubElement(clip,'link');text(link,'linkclipref',record['id']+'-audio-'+str(linked_channel));text(link,'mediatype','audio');text(link,'trackindex',linked_channel);text(link,'clipindex',1);text(link,'groupindex',1)
    markers=[(m['timeline_frame'],'USER CUE: '+m['label'],'User structural cue, musical claim unverified') for m in record['user_markers']]
    beat=ROOT/record['beat_analysis'] if record.get('beat_analysis') else None
    if beat and beat.exists():markers += [(m['frame_30fps'],'AUTO BEAT','Estimated beat, check by listening') for m in json.loads(beat.read_text())['beats']]
    for frame,label,comment in sorted(markers):
        marker=ET.SubElement(seq,'marker');text(marker,'name',label);text(marker,'comment',comment);text(marker,'in',frame);text(marker,'out',-1)
    ET.indent(tree);ET.ElementTree(tree).write(out/(record['id']+'.xml'),encoding='utf-8',xml_declaration=True)

def audit(require_pcm=False):
    data=json.loads(MANIFEST.read_text());errors=[]
    for r in data['assets']:
        path=ROOT/r['repositoryFile'];pcm=ROOT/r['pcmMaster']
        if not path.exists() or digest(path)!=r['sha256']:errors.append(r['id']+': MP3 checksum mismatch');continue
        # Decode gapless MP3 to counted PCM, not rounded container duration.
        decoded=subprocess.check_output(['ffmpeg','-v','error','-xerror','-nostdin','-i',str(path),'-ar','48000','-ac','2','-f','s16le','-'])
        if len(decoded)//4!=r['pcm_samples_48000']:errors.append(r['id']+': MP3 decoded sample count mismatch')
        if pcm.exists() and digest(pcm)!=r['pcm_sha256']:errors.append(r['id']+': PCM checksum mismatch')
        if require_pcm and not pcm.exists():errors.append(r['id']+': PCM missing')
        if r.get('beat_analysis'):
            b=json.loads((ROOT/r['beat_analysis']).read_text())
            if b.get('pcm_sha256') and b['pcm_sha256']!=r['pcm_sha256']:errors.append(r['id']+': stale beat data')
            if any(not 0<=m['frame_30fps']<round(r['duration']*30) for m in b['beats']):errors.append(r['id']+': beat outside clip')
    if data.get('failures'):errors.append('Unresolved fetch failures remain')
    if errors:raise ValueError('; '.join(errors))
    print(f"Music audit passed: {len(data['assets'])} MP3 checksums, decoded sample counts and available PCM/beat provenance")

def process(track,beats=True,local_source=None):
    validate(track);folder=ROOT/'media/music/jetkids'/track['id'];folder.mkdir(parents=True,exist_ok=True)
    asset=ROOT/'public/assets/brands/jetkids/audio'/f"{track['id']}.mp3";asset.parent.mkdir(parents=True,exist_ok=True)
    metadata_path=folder/'source-info.json'
    if local_source:
        source=Path(local_source).resolve();info={'id':'local','title':track['song'],'channel':'User supplied local audio','duration':float(probe(source)['format']['duration']),'webpage_url':track['url']}
    else:
        if not metadata_path.exists():
            info=json.loads(ytdlp(['--skip-download','--dump-single-json',track['url']]))
            write(metadata_path,info)
        else:info=json.loads(metadata_path.read_text())
        if not title_matches(track,info.get('title','')):raise ValueError('Source title does not match requested song: '+info.get('title',''))
        candidates=[p for p in folder.glob('source.*') if p.suffix.lower() in ('.m4a','.webm','.opus','.mp3','.ogg','.mp4')]
        if candidates:source=candidates[0]
        else:
            output=ytdlp(['-f','bestaudio','--no-overwrites','-o',str(folder/'source.%(ext)s'),'--print','after_move:filepath',track['url']],timeout=240)
            source=Path(output.strip().splitlines()[-1])
    if not source.is_file():raise ValueError('Downloaded source missing')
    duration=track['source_out']-track['source_in']
    if track['source_out']>float(info['duration'])+.01:raise ValueError('Slice exceeds recording')
    pcm=folder/'slice.wav';samples=round(duration*48000);source_hash=digest(source)
    provenance={'url':track['url'],'source_in':track['source_in'],'source_out':track['source_out'],'source_sha256':source_hash}
    old_path=folder/'slice-provenance.json'
    if old_path.exists() and json.loads(old_path.read_text())!=provenance:raise ValueError('Source/slice changed: choose a new asset ID')
    prior_path=folder/'asset.json';prior=json.loads(prior_path.read_text()) if prior_path.exists() else None
    if prior is None and MANIFEST.exists():
        prior=next((r for r in json.loads(MANIFEST.read_text())['assets'] if r['id']==track['id']),None)
    if pcm.exists():
        if not old_path.exists():raise ValueError('Unregistered PCM retained: inspect before retry')
        if prior and digest(pcm)!=prior['pcm_sha256']:raise ValueError('Existing PCM checksum changed')
    if asset.exists() and (not prior or digest(asset)!=prior['sha256']):raise ValueError('Existing MP3 is unregistered or changed')
    if not pcm.exists():
        temporary=folder/'slice.partial.wav'
        if temporary.exists():raise ValueError('Interrupted PCM retained; inspect before retry')
        extract_pcm_slice(source,temporary,track['source_in'],track['source_out'])
        temporary.rename(pcm);write(old_path,provenance)
    if asset.exists() and prior['pcm_sha256']!=digest(pcm):raise ValueError('Restored MP3 belongs to different PCM; use a new versioned asset ID')
    if not asset.exists():
        temporary=folder/'slice.partial.mp3'
        subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-i',str(pcm),'-vn','-c:a','libmp3lame','-b:a','320k','-metadata','title='+track['song'],'-metadata','album=Jet Kids reel '+track['reel'],'-metadata','comment='+track['url']+'; source '+str(track['source_in'])+'-'+str(track['source_out'])+'s',str(temporary)],check=True)
        shutil.copy2(temporary,asset);temporary.unlink()
    # Decode both distributions; MP3 sample count includes encoder padding in some containers, PCM stays the edit master.
    for p in (pcm,asset):subprocess.run(['ffmpeg','-v','error','-xerror','-nostdin','-i',str(p),'-f','null','-'],check=True)
    beat_path=ROOT/'workspaces/jetkids/beats'/f"{track['id']}.json"
    if beats and not beat_path.exists():analyse_beats(pcm,track,beat_path)
    if beat_path.exists():
        existing=json.loads(beat_path.read_text())
        if existing.get('pcm_sha256') and existing['pcm_sha256']!=digest(pcm):raise ValueError('Beat analysis belongs to different PCM')
    record={'id':track['id'],'brand':'jetkids','kind':'music','song':track['song'],'film_or_artist':track['film_or_artist'],'subject':track['song']+' — '+track['concept'],'reel':track['reel'],'repositoryFile':str(asset.relative_to(ROOT)),'pcmMaster':str(pcm.relative_to(ROOT)),'sha256':digest(asset),'pcm_sha256':digest(pcm),'source_sha256':source_hash,'duration':duration,'source_in':track['source_in'],'source_out':track['source_out'],'pcm_samples_48000':samples,'source':track['url'],'youtube_video_id':info.get('id'),'source_title':info.get('title'),'channel':info.get('channel'),'channel_id':info.get('channel_id'),'upload_date':info.get('upload_date'),'artist':info.get('artist'),'album':info.get('album'),'source_codec':next((s['codec_name'] for s in probe(source)['streams'] if s['codec_type']=='audio'),None),'codec':'mp3','bitrate':320000,'sample_rate':48000,'git_storage':'lfs','rights':track['rights'],'permission_context':'User explicitly requested selected music slices and GitHub backup on2026-10-19; no music licence inferred.','user_markers':cue_markers(track),'beat_analysis':str(beat_path.relative_to(ROOT)) if beat_path.exists() else None,'loudness_unfinished':loudness(asset),'full_decode':'passed','listening_review':'not attested','retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    write(folder/'asset.json',record);export_markers(record,ROOT/'workspaces/jetkids/premiere-markers');return record

def fetch(cues,ids=None,beat_analysis=True,jobs=2):
    tracks=json.loads(Path(cues).read_text())['tracks'];chosen=[t for t in tracks if not ids or t['reel'] in ids or t['id'] in ids]
    if not chosen:raise ValueError('No selected tracks')
    manifest=json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {'assets':[],'failures':[]};assets={a['id']:a for a in manifest['assets']};failures={a['id']:a for a in manifest.get('failures',[])}
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        futures={pool.submit(process,t,beat_analysis):t for t in chosen}
        for future in concurrent.futures.as_completed(futures):
            t=futures[future]
            try:r=future.result();assets[t['id']]=r;failures.pop(t['id'],None);print(t['reel']+' ready: '+t['song'],flush=True)
            except Exception as e:
                reason=str(e)
                if isinstance(e,subprocess.CalledProcessError):reason=(e.stderr or str(e))[-1800:]
                failures[t['id']]={'id':t['id'],'reel':t['reel'],'url':t['url'],'error':reason};print(t['reel']+' failed: '+reason[-350:],flush=True)
            write(MANIFEST,{'assets':sorted(assets.values(),key=lambda a:a['id']),'failures':sorted(failures.values(),key=lambda a:a['id'])})
    return not failures

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    f=sub.add_parser('fetch');f.add_argument('--cues',default=str(DEFAULT));f.add_argument('--reel',action='append');f.add_argument('--no-beats',action='store_true');f.add_argument('--jobs',type=int,choices=[1,2],default=2)
    sub.add_parser('export-markers')
    q=sub.add_parser('audit');q.add_argument('--require-pcm',action='store_true')
    a=p.parse_args()
    if a.command=='fetch':return 0 if fetch(a.cues,a.reel,not a.no_beats,a.jobs) else 1
    if a.command=='export-markers':
        for record in json.loads(MANIFEST.read_text())['assets']:export_markers(record,ROOT/'workspaces/jetkids/premiere-markers')
        return 0
    if a.command=='audit':audit(a.require_pcm);return 0
if __name__=='__main__':sys.exit(main())
