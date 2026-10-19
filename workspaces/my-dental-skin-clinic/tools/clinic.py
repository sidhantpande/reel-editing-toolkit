#!/usr/bin/env python3
"""Local, non-destructive media intake and review preparation."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'project.json').read_text())
FF = CONFIG['ffmpeg']
FP = CONFIG['ffprobe']
CAT = ROOT / '01_catalog'
MANIFEST = CAT / 'sources.json'
EXTS = {'.mp4', '.mov', '.m4v', '.mkv', '.avi', '.mts', '.m2ts', '.webm'}
FIELDS = ['id', 'filename', 'category', 'topic', 'take', 'usable_in', 'usable_out', 'decision', 'notes']


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)


def run(args):
    return subprocess.run([str(x) for x in args], check=True, capture_output=True, text=True).stdout


def ff(*args):
    # Keep interrupted encodes from looking like finished cached outputs.
    target = Path(args[-1])
    partial = target.with_name(target.stem + '.partial' + target.suffix)
    try:
        result = run([FF, '-hide_banner', '-loglevel', 'error', '-nostdin', '-y', *args[:-1], partial])
        partial.replace(target)
        return result
    finally:
        partial.unlink(missing_ok=True)


def sources():
    return json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []


def probe(path):
    return json.loads(run([FP, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path]))


def model_path(name='small'):
    repo = 'models--dropbox-dash--faster-whisper-large-v3-turbo' if name == 'turbo' else 'models--Systran--faster-whisper-small'
    candidates = list((ROOT / '.cache/models').glob(repo + '/snapshots/*'))
    return next((p for p in candidates if (p / 'model.bin').exists()), None)


def doctor(_):
    from PIL import Image, features
    import faster_whisper
    filters = run([FF, '-hide_banner', '-filters'])
    for name in ['zscale', 'tonemap', 'subtitles', 'loudnorm', 'silencedetect']:
        if not re.search(r'\b' + name + r'\b', filters):
            raise RuntimeError('Missing FFmpeg filter: ' + name)
    if not features.check('raqm'):
        raise RuntimeError('Pillow RAQM is required for measured Hindi captions')
    fonts = ['Mukta-ExtraBold.ttf', 'ClinicMontserrat-ExtraBold.ttf']
    for font in fonts:
        if not (ROOT/'assets/fonts/ready'/font).is_file():
            raise RuntimeError('Missing approved caption font: '+font)
    data = {
        'raqm': True, 'approved_fonts': fonts, 'approved_style': 'styles/clinic-approved.json',
        'turbo_model_path': str(model_path('turbo')) if model_path('turbo') else None,
        'checked_utc': datetime.now(timezone.utc).isoformat(),
        'python': sys.version, 'ffmpeg': run([FF, '-version']).splitlines()[0],
        'ffprobe': run([FP, '-version']).splitlines()[0],
        'packages': {p: importlib.metadata.version(p) for p in ['Pillow', 'faster-whisper', 'ctranslate2', 'numpy', 'fonttools']},
        'required_filters': 'available', 'model_path': str(model_path()) if model_path() else None,
        'free_gib': round(shutil.disk_usage(ROOT).free / 2**30, 2),
        'subject_matte': {'engine': 'Apple Vision / accurate', 'xcrun': shutil.which('xcrun'),
                          'source': str(ROOT/'tools/person_matte.swift'), 'required_for': 'behind-subject graphic slots'},
    }
    save(CAT / 'environment.json', data)
    print(json.dumps(data, indent=2))
    if not model_path():
        raise RuntimeError('Multilingual small model is not downloaded yet')
    preferred=CONFIG.get('transcription',{}).get('model','small')
    if not model_path(preferred):
        raise RuntimeError('Configured ASR model missing; run tools/fetch_model.py --model '+preferred)


def ingest(a):
    folder = Path(a.folder).expanduser().resolve()
    if not folder.is_dir():
        raise ValueError('Source folder does not exist: ' + str(folder))
    rows = sources()
    by_hash = {r['sha256']: r for r in rows}
    errors = []
    for path in sorted(folder.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in EXTS or path.name.startswith('._'):
            continue
        try:
            before = path.stat()
            h = hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
                    h.update(block)
            meta = probe(path)
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise ValueError('File changed during scan; wait for download completion')
            digest = h.hexdigest()
            if any(str(path) in row['paths'] and row['sha256'] != digest for row in rows):
                raise ValueError('Registered source was changed. Restore the original or register the new version at a different path')
            if digest in by_hash:
                r = by_hash[digest]
                if str(path) not in r['paths']:
                    r['paths'].append(str(path))
                r.setdefault('file_stats', {})[str(path)] = {'bytes': after.st_size, 'mtime_ns': after.st_mtime_ns}
                continue
            v = next(s for s in meta['streams'] if s['codec_type'] == 'video')
            duration = float(meta.get('format', {}).get('duration') or v.get('duration') or 0)
            if duration <= 0:
                raise ValueError('No usable duration')
            r = {'id': 'clip-' + digest[:16], 'filename': path.name, 'paths': [str(path)],
                 'sha256': digest, 'bytes': after.st_size, 'mtime_ns': after.st_mtime_ns,
                 'file_stats': {str(path): {'bytes': after.st_size, 'mtime_ns': after.st_mtime_ns}},
                 'duration': duration, 'width': v.get('width'), 'height': v.get('height'),
                 'fps': v.get('avg_frame_rate'), 'rotation': [s.get('rotation') for s in v.get('side_data_list', []) if 'rotation' in s],
                 'hdr': v.get('color_transfer') in ['smpte2084', 'arib-std-b67'],
                 'has_audio': any(s['codec_type'] == 'audio' for s in meta['streams']), 'probe': meta}
            rows.append(r)
            by_hash[digest] = r
            print('Registered', r['id'], path.name, flush=True)
        except (subprocess.CalledProcessError, ValueError, OSError, StopIteration) as e:
            errors.append({'path': str(path), 'error': str(e)})
    save(MANIFEST, rows)
    save(CAT / 'intake-errors.json', errors)
    review = CAT / 'review.csv'
    old = {}
    if review.exists():
        with review.open(newline='') as f:
            old = {r['id']: r for r in csv.DictReader(f)}
    with review.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow({**dict.fromkeys(FIELDS, ''), **old.get(r['id'], {}), 'id': r['id'], 'filename': r['filename']})
    print(f'{len(rows)} unique clips; {len(errors)} intake errors. Review 01_catalog/intake-errors.json.')
    if errors:
        raise RuntimeError('Some files could not be registered; see intake-errors.json')


def stamp(t):
    return f'{int(t // 60):02}:{t % 60:06.3f}'


def analyse(a):
    from PIL import Image, ImageDraw, ImageFont
    for r in sources():
        if a.source_folder and not any(Path(q).is_relative_to(Path(a.source_folder).expanduser().resolve()) for q in r['paths']):
            continue
        path = next((Path(p) for p in r['paths'] if Path(p).exists()), None)
        if path is None:
            raise FileNotFoundError('Missing source ' + r['id'])
        stat = path.stat()
        expected = r.get('file_stats', {}).get(str(path), r)
        if (stat.st_size, stat.st_mtime_ns) != (expected['bytes'], expected['mtime_ns']):
            raise RuntimeError('Source changed; ingest again before analysis: ' + str(path))
        out = ROOT / '02_analysis' / r['id']
        out.mkdir(parents=True, exist_ok=True)
        tone = 'zscale=t=linear:npl=100,format=gbrpf32le,tonemap=hable:desat=0,zscale=p=bt709:t=bt709:m=bt709:r=tv,' if r['hdr'] else ''
        if not (out / 'contact-sheet.jpg').exists():
            canvas = Image.new('RGB', (1280, 930), '#171717')
            draw = ImageDraw.Draw(canvas)
            font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 17)
            draw.text((12, 8), r['filename'][:100] + ' | ' + r['id'], fill='white', font=font)
            with tempfile.TemporaryDirectory(dir=ROOT / '.cache') as temp:
                for i in range(12):
                    # A sub-frame seek near EOF can yield no decoded image in
                    # very short accidental camera clips. Keep a decode margin.
                    t = min(r['duration'] * (i + 0.5) / 12, max(0, r['duration'] - .15))
                    frame = Path(temp) / f'{i}.png'
                    ff('-ss', t, '-i', path, '-frames:v', '1', '-vf', tone + 'scale=300:250:force_original_aspect_ratio=decrease,setsar=1', frame)
                    with Image.open(frame) as img:
                        x, y = (i % 4) * 320, 40 + (i // 4) * 290
                        canvas.paste(img, (x + (320-img.width)//2, y + (250-img.height)//2))
                        draw.text((x + 10, y + 254), stamp(t), fill='white', font=font)
            canvas.save(out / 'contact-sheet.jpg', quality=90)
        if r['has_audio'] and not (out / 'audio.wav').exists():
            ff('-i', path, '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', out / 'audio.wav')
        if r['has_audio'] and not (out / 'audio-check.txt').exists():
            result = subprocess.run([FF, '-hide_banner', '-nostdin', '-i', str(out / 'audio.wav'), '-af', 'silencedetect=n=-35dB:d=0.4,volumedetect', '-f', 'null', '-'], capture_output=True, text=True, check=True)
            (out / 'audio-check.txt').write_text(result.stderr)
        if a.proxy and not (out / 'proxy.mp4').exists():
            ff('-i', path, '-map', '0:v:0', '-map', '0:a:0?', '-vf', tone + 'scale=540:960:force_original_aspect_ratio=decrease:force_divisible_by=2,setsar=1,format=yuv420p', '-r', '30', '-c:v', 'libx264', '-preset', 'fast', '-crf', '24', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', '-metadata:s:v:0', 'rotate=0', out / 'proxy.mp4')
        print('Prepared', r['id'], flush=True)


def srt_time(t):
    ms = max(0, round(t * 1000))
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'


def transcribe(a):
    from faster_whisper import WhisperModel
    from faster_whisper.audio import decode_audio
    import numpy as np
    p = model_path(a.model)
    if not p:
        raise RuntimeError('Requested local transcription model missing: '+a.model)
    model = WhisperModel(str(p), device='cpu', compute_type='int8', cpu_threads=4)
    for r in sources():
        if a.source_folder and not any(Path(q).is_relative_to(Path(a.source_folder).expanduser().resolve()) for q in r['paths']):
            continue
        if not r['has_audio']:
            continue
        out = ROOT / '02_analysis' / r['id']
        if not (out / 'audio.wav').exists():
            raise RuntimeError('Run analyse first for ' + r['id'])
        if (out / 'transcript.json').exists() and not a.redo:
            continue
        audio=np.clip(decode_audio(str(out/'audio.wav'))*a.gain,-.98,.98)
        segments, info = model.transcribe(audio, language=None if a.language == 'auto' else a.language, word_timestamps=True, vad_filter=True, condition_on_previous_text=False, beam_size=5)
        items = [{'start': s.start, 'end': s.end, 'text': s.text, 'words': [{'start': w.start, 'end': w.end, 'text': w.word, 'probability': w.probability} for w in (s.words or [])]} for s in segments]
        save(out / 'transcript.json', {'status': 'DRAFT_REQUIRES_AUDIO_REVIEW', 'source_id': r['id'], 'model': a.model, 'requested_language': a.language, 'detected_language': info.language, 'language_probability': info.language_probability, 'segments': items})
        (out / 'transcript.txt').write_text('\n'.join(f"[{stamp(s['start'])}–{stamp(s['end'])}] {s['text']}" for s in items))
        (out / 'transcript.srt').write_text('\n\n'.join(f"{i}\n{srt_time(s['start'])} --> {srt_time(s['end'])}\n{s['text'].strip()}" for i, s in enumerate(items, 1)))
        print('Draft transcript', r['id'], flush=True)


def new_reel(a):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', a.id):
        raise ValueError('Use a lowercase reel ID with letters, numbers and hyphens')
    folder = ROOT / '03_reels' / a.id
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / 'brief.md').open('x') as f:
        f.write((ROOT / 'templates/reel-brief.md').read_text().replace('<reel-id>', a.id).replace('<ID>', a.id))
    print(folder / 'brief.md')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor').set_defaults(fn=doctor)
    p = sub.add_parser('ingest'); p.add_argument('folder'); p.set_defaults(fn=ingest)
    p = sub.add_parser('analyse'); p.add_argument('--proxy', action='store_true'); p.add_argument('--source-folder'); p.set_defaults(fn=analyse)
    p = sub.add_parser('transcribe'); p.add_argument('--language', choices=['auto', 'hi', 'en'], default='auto'); p.add_argument('--redo', action='store_true'); p.add_argument('--model', choices=['small','turbo'], default=CONFIG.get('transcription',{}).get('model','small')); p.add_argument('--gain', type=float, default=4); p.add_argument('--source-folder'); p.set_defaults(fn=transcribe)
    p = sub.add_parser('new-reel'); p.add_argument('id'); p.set_defaults(fn=new_reel)
    a = parser.parse_args()
    a.fn(a)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError) as error:
        print('ERROR:', error, file=sys.stderr)
        sys.exit(1)
