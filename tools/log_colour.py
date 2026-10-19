#!/usr/bin/env python3
"""Metadata-gated Sony S-Log3 conversion; originals and normal footage stay untouched."""
import argparse
import hashlib
import json
import shutil
import sys
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LUT_URL = 'https://di.update.sony.net/NEX/ciOkozszIz/Look_profile_for_resolve_S-Gamut3.cine_Slog3.zip'
LUT_PAGE = 'https://www.sony.com/zh-cn/electronics/support/articles/00197011'
LUT_NAME = 'SLog3SGamut3.CineToLC-709.cube'
LUT_SHA256 = 'd41aeebbca5c4df100f1e6b53b739bd1e7bc38e49890812a14ba7275ebfbbf94'

def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n'); temporary.replace(path)

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))

def camera_metadata(path):
    sidecar = Path(path).with_name(Path(path).stem + 'M01.XML')
    if not sidecar.is_file():
        return {}
    root = ET.parse(sidecar).getroot()
    items = {e.get('name'): e.get('value') for e in root.iter() if e.tag.split('}')[-1] == 'Item'}
    device = next((e.attrib for e in root.iter() if e.tag.split('}')[-1] == 'Device'), {})
    # Do not persist camera serial numbers.
    return {**items, 'modelName': device.get('modelName'), 'sidecar': str(sidecar)}

def classify(metadata):
    gamma = metadata.get('CaptureGammaEquation', '').lower()
    gamut = metadata.get('CaptureColorPrimaries', '').lower()
    if gamma in ('s-log3-cine', 's-log3') and gamut == 's-gamut3-cine':
        return 'sony-slog3-sgamut3cine'
    if gamma in ('s-cinetone', 'rec709', 'nxcam-still') and gamut == 'rec709':
        return 'display-referred-no-log-lut'
    return 'unknown-review-required'

def ensure_lut():
    directory = ROOT / '.cache/luts/sony'; directory.mkdir(parents=True, exist_ok=True)
    target = directory / LUT_NAME
    if not target.exists():
        archive = directory / 'sony-slog3.zip'
        if not archive.exists(): urllib.request.urlretrieve(LUT_URL, archive)
        with zipfile.ZipFile(archive) as z:
            candidates = [n for n in z.namelist() if n.endswith('/' + LUT_NAME)]
            if len(candidates) != 1: raise ValueError('Unexpected Sony archive contents')
            target.write_bytes(z.read(candidates[0]))
    if digest(target) != LUT_SHA256:
        raise ValueError('Sony LUT checksum does not match the verified official download')
    if 'full in full out' not in target.read_text().splitlines()[0]:
        raise ValueError('Unexpected LUT input/output range')
    write(directory / 'provenance.json', {'manufacturer': 'Sony', 'download': LUT_URL, 'source_page': LUT_PAGE, 'filename': LUT_NAME, 'sha256': digest(target), 'input': 'S-Log3 / S-Gamut3.Cine full-range RGB', 'output': 'LC-709 full-range RGB, encoded as limited-range BT.709', 'redistribution': 'Downloaded to ignored local cache; Sony retains rights.'})
    return target

def colour_filter(lut, input_range='pc', pixel_format='gbrp16le'):
    if input_range not in ('pc', 'tv'): raise ValueError('Explicit pc/tv input range required')
    # Float/16-bit processing avoids introducing an 8-bit RGB intermediate.
    safe = str(Path(lut).resolve()).replace('\\', '\\\\').replace(':', '\\:').replace("'", "'\\''")
    return f"scale=in_range={input_range}:out_range=pc:in_color_matrix=bt709,format={pixel_format},lut3d=file='{safe}':interp=tetrahedral,scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p"

def ffmpeg_command(source, output, lut, input_range, encoder='h264_videotoolbox'):
    if Path(source).resolve() == Path(output).resolve(): raise ValueError('Never overwrite original footage')
    codec = ['-c:v', encoder, '-b:v', '45M', '-profile:v', 'high'] if encoder == 'h264_videotoolbox' else ['-c:v', 'libx264', '-preset', 'fast', '-crf', '16']
    return ['ffmpeg', '-v', 'error', '-nostdin', '-n', '-threads', '2', '-filter_threads', '4', '-noautorotate', '-i', str(source), '-map', '0:v:0', '-map', '0:a?', '-vf', colour_filter(lut, input_range), *codec, '-fps_mode', 'passthrough', '-c:a', 'copy', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv', '-movflags', '+faststart', str(output)]

def inventory(folder, output):
    folder = Path(folder).expanduser().resolve(strict=True); videos = []
    for source in sorted(folder.rglob('*')):
        if source.suffix.lower() not in ('.mp4', '.mov', '.mxf', '.m4v'): continue
        info = probe(source); video = next(s for s in info['streams'] if s['codec_type'] == 'video'); metadata = camera_metadata(source)
        videos.append({'relative': str(source.relative_to(folder)), 'path': str(source), 'bytes': source.stat().st_size, 'sha256': digest(source), 'duration': float(info['format']['duration']), 'video': video, 'audio': [s for s in info['streams'] if s['codec_type'] == 'audio'], 'camera': metadata, 'profile': classify(metadata)})
        if len(videos) % 50 == 0: print(f'Inventoried {len(videos)}', flush=True)
    write(output, {'root': str(folder), 'videos': videos})

def verify(source_record, target):
    info = probe(target); v = next(s for s in info['streams'] if s['codec_type'] == 'video'); original = source_record['video']
    for field in ('width', 'height', 'avg_frame_rate', 'nb_frames'):
        if field in original and v.get(field) != original[field]: raise ValueError(f'Changed {field}: {target}')
    if abs(float(v['duration']) - source_record['duration']) > .05: raise ValueError('Duration mismatch')
    if v.get('color_range') != 'tv' or v.get('color_space') != 'bt709': raise ValueError('Incorrect output colour tags')
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-nostdin', '-threads', '2', '-i', str(target), '-map', '0:v:0', '-map', '0:a?', '-f', 'null', '-'], check=True)
    if source_record.get('audio'):
        # Copy, then compare decoded PCM, not container bytes.
        def pcm(path):
            return subprocess.check_output(['ffmpeg', '-v', 'error', '-nostdin', '-i', str(path), '-map', '0:a:0', '-f', 'hash', '-hash', 'sha256', '-'])
        if pcm(source_record['path']) != pcm(target): raise ValueError('Audio changed')
    return {'sha256': digest(target), 'frames': v.get('nb_frames'), 'duration': v['duration'], 'full_decode': 'passed', 'audio': 'PCM hash unchanged' if source_record.get('audio') else 'none'}

def convert(manifest, output_root, backend='ffmpeg'):
    data = json.loads(Path(manifest).read_text()); output_root = Path(output_root).resolve()
    original_root = Path(data['root']).resolve()
    if output_root == original_root or original_root in output_root.parents: raise ValueError('Converted media must be outside original folder')
    output_root.mkdir(parents=True, exist_ok=True)
    lut = ensure_lut(); state_path = output_root / 'conversion-state.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {'lut_sha256': digest(lut), 'files': {}}
    if state['lut_sha256'] != digest(lut): raise ValueError('LUT changed: use a new output folder')
    for i, record in enumerate(data['videos'], 1):
        relative = record['relative']; profile = classify(record['camera']); source = Path(record['path'])
        if profile != 'sony-slog3-sgamut3cine':
            state['files'][relative] = {'status': 'unchanged' if profile.startswith('display') else 'unclassified', 'path': str(source), 'profile': profile}; write(state_path, state); continue
        target = (output_root / Path(relative).with_suffix('.mov')).resolve()
        target.relative_to(output_root)  # Reject path traversal in an edited inventory.
        target.parent.mkdir(parents=True, exist_ok=True)
        previous = state['files'].get(relative, {})
        if previous.get('status') == 'verified' and previous.get('source_sha256') == record['sha256'] and target.exists() and digest(target) == previous.get('sha256'): continue
        if digest(source) != record['sha256']: raise ValueError(f'Original changed: {source}')
        if target.exists(): raise ValueError(f'Unverified output exists; retain it and choose a fresh output folder: {target}')
        if shutil.disk_usage(output_root).free < 8 * 2**30: raise ValueError('Less than 8 GiB free; conversion stopped safely')
        print(f'[{i}/{len(data["videos"])}] {relative}', flush=True)
        temporary = target.with_name(target.stem + '.partial.mov')
        if temporary.exists(): raise ValueError(f'Interrupted output retained: {temporary}')
        if backend == 'metal':
            video_only = target.with_name(target.stem + '.video-only.mov')
            executable = ROOT / '.cache/bin/sony-colour-metal'
            swift_source = ROOT / 'tools/sony_colour_metal.swift'
            if not executable.exists() or executable.stat().st_mtime < swift_source.stat().st_mtime:
                executable.parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(['swiftc', '-O', str(swift_source), '-o', str(executable)], check=True)
            subprocess.run([str(executable), str(source), str(lut), str(video_only)], check=True)
            subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-n', '-i', str(video_only), '-i', str(source), '-map', '0:v:0', '-map', '1:a?', '-c', 'copy', '-movflags', '+faststart', str(temporary)], check=True)
            video_only.unlink()  # Generated temporary only; never user media.
        else:
            if record['video'].get('color_range') not in ('pc', 'tv'): raise ValueError('Missing source range')
            encoder = 'h264_videotoolbox' if sys.platform == 'darwin' else 'libx264'
            subprocess.run(ffmpeg_command(source, temporary, lut, record['video']['color_range'], encoder), check=True)
        evidence = verify(record, temporary); temporary.rename(target)
        state['files'][relative] = {'status': 'verified', 'profile': profile, 'path': str(target), 'source_sha256': record['sha256'], 'backend': backend, 'visual_review': 'pending', **evidence}; write(state_path, state)
    print(f'Conversion manifest: {state_path}')

def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('download-lut')
    i = sub.add_parser('inventory'); i.add_argument('folder'); i.add_argument('--out', required=True)
    c = sub.add_parser('convert'); c.add_argument('manifest'); c.add_argument('--output', required=True); c.add_argument('--backend', choices=['ffmpeg', 'metal'], default='ffmpeg')
    a = p.parse_args()
    if a.command == 'download-lut': print(ensure_lut())
    elif a.command == 'inventory': inventory(a.folder, a.out)
    else: convert(a.manifest, a.output, a.backend)
if __name__ == '__main__': main()
