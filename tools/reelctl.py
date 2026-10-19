#!/usr/bin/env python3
"""Filesystem-first intake, asset discovery, preflight and measured reel workflow."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def run(args):
    subprocess.run(args, cwd=ROOT, check=True)


def probe(path):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))


def project_path(value):
    p = (ROOT / value).resolve()
    p.relative_to(ROOT / 'projects')
    return p


def init_project(brand, project_id, sources, script=None):
    if not re.fullmatch(r'[a-z][a-z0-9-]{2,79}', project_id) or not project_id.startswith(brand + '-'):
        raise ValueError('Project ID must start with the brand and contain only lowercase letters, numbers and hyphens.')
    p = ROOT / 'projects' / brand / project_id
    if p.exists():
        raise ValueError('Project already exists; intake never overwrites an edit.')
    inputs = [Path(s).expanduser().resolve(strict=True) for s in sources]
    if len({s.name.casefold() for s in inputs}) != len(inputs):
        raise ValueError('Duplicate source filenames; rename the takes explicitly first.')
    if not inputs or any(s.suffix.lower() not in {'.mov', '.mp4', '.m4v', '.mkv'} for s in inputs):
        raise ValueError('Supply at least one source video.')
    # Inspect every input before creating a project or copying any bytes.
    info = [(s, probe(s)) for s in inputs]
    for source, meta in info:
        if not any(s['codec_type'] == 'video' for s in meta['streams']):
            raise ValueError(f'No video stream: {source}')
    records = []
    for source, meta in info:
        target = ROOT / 'media/raw' / brand / project_id / source.name
        if target.exists():
            raise ValueError(f'Unregistered source destination already exists: {target}')
    p.mkdir(parents=True)
    for source, meta in info:
        target = ROOT / 'media/raw' / brand / project_id / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        sha = digest(source)
        if digest(target) != sha:
            raise ValueError(f'Copy verification failed: {target}')
        records.append(dict(source=str(target.relative_to(ROOT)), sourceId=target.stem,
                            bytes=target.stat().st_size, sha256=sha, probe=meta))
    write(p / 'intake.json', dict(id=project_id, brand=brand, editFps=30, sources=records))
    write(p / 'edit-plan.json', dict(id=project_id, brand=brand, format='RECORDED_REEL',
          status='awaiting-source-analysis', sourceClips=[r['source'] for r in records], broll=[]))
    write(p / 'editorial.json', dict(phrases=[], accentWords=[], broll=[], alphaExports=[], notes=[]))
    write(p / 'colour-grade.json', dict(filter='eq=contrast=1.035:saturation=0.97:gamma=1.012:brightness=-0.005'))
    write(p / 'assets-provenance.json', dict(project=project_id, creation='Record new assets and reused sources here.'))
    (p / 'production-plan.md').write_text('# ' + project_id + '\n\nTODO: analyse the complete sources; document take roles, gaze, complete speech cuts, crop calibration, caption corrections and per-point B-roll plan before rendering.\n')
    (p / 'script.md').write_text(Path(script).read_text() if script else '# Source brief\n\nTranscribe the actual recording; add the current user brief here.\n')
    return p


def check_project(p):
    needed = ['cut-list.json', 'source-words.json', 'editorial.json', 'colour-grade.json',
              'production-plan.md', 'assets-provenance.json']
    missing = [name for name in needed if not (p / name).is_file()]
    if missing:
        raise ValueError('Missing reviewed edit inputs: ' + ', '.join(missing))
    plan = (p / 'production-plan.md').read_text()
    if len(plan.strip()) < 80 or 'TODO:' in plan:
        raise ValueError('Complete the per-source editorial/gaze/B-roll plan first.')
    cuts = read(p / 'cut-list.json')
    if cuts.get('id') != p.name or cuts.get('fps') != 30 or not cuts.get('cuts'):
        raise ValueError('Expected a nonempty 30fps cut list matching the project ID.')
    offset, checked, sources = 0, {}, set()
    for c in cuts['cuts']:
        if not all(type(c.get(k)) is int for k in ['inFrame', 'outFrame', 'duration', 'timelineFrom']):
            raise ValueError('All cut frames must be integers.')
        if c['inFrame'] < 0 or c['outFrame'] <= c['inFrame'] or c['duration'] != c['outFrame'] - c['inFrame'] or c['timelineFrom'] != offset:
            raise ValueError('Discontinuous timeline or inconsistent source cut frames.')
        source = (ROOT / c['source']).resolve(strict=True)
        source.relative_to(ROOT / 'media/raw')
        if source not in checked:
            checked[source] = float(probe(source)['format']['duration'])
        if c['outFrame'] > math.ceil(checked[source] * 30) + 1:
            raise ValueError(f'Cut exceeds actual source duration: {source.name}')
        if not 1 <= c.get('zoom', 1) <= 4 or any(not 0 <= c.get(k, .5) <= 1 for k in ['cropX', 'cropY']):
            raise ValueError('Invalid crop/zoom values.')
        offset += c['duration']
        sources.add(c['source'])
    if cuts.get('dialogueFrames') != offset or cuts.get('totalFrames') != offset + cuts.get('endHoldFrames', 45):
        raise ValueError('Dialogue/end-card totals differ from the actual cut durations.')
    words = read(p / 'source-words.json').get('words', [])
    if not words or any(not isinstance(w.get('text'), str) or not w['text'].strip() or not 0 <= w['start'] < w['end'] for w in words):
        raise ValueError('Supply corrected source-language word text and valid second timings.')
    if len(sources) > 1 and any(not w.get('source') for w in words):
        raise ValueError('Every word in a multi-source edit needs its source ID.')
    valid_sources = sources | {Path(s).name for s in sources} | {Path(s).stem for s in sources}
    if any(w.get('source') and w['source'] not in valid_sources for w in words):
        raise ValueError('Unknown word source ID; it must identify a selected take.')
    editorial = read(p / 'editorial.json')
    if not editorial.get('phrases') or not isinstance(editorial.get('broll'), list):
        raise ValueError('Supply curated caption phrases and the reviewed B-roll cue list.')
    intake = p / 'intake.json'
    if intake.exists():
        for entry in read(intake)['sources']:
            if digest(ROOT / entry['source']) != entry['sha256']:
                raise ValueError('Source bytes changed after intake: ' + entry['source'])
    return dict(project=str(p.relative_to(ROOT)), fps=30, dialogueFrames=offset,
                totalFrames=cuts['totalFrames'], sourceFiles=len(sources), sourceWords=len(words))


def record(p, video):
    cut = read(p / 'cut-list.json'); props = read(p / 'reel.json')
    base = ROOT / '.cache/batch' / p.name
    finish = read(base / 'finish/finish-measurements.json')
    tile = read(base / 'tile-scan/tile-scan.json')
    captions = read(base / 'captions/encoded-caption-check.json')
    if Path(finish['video']).resolve() != video or finish['fullDecode'] != 'passed' or finish['frames'] != cut['totalFrames']:
        raise ValueError('Missing or stale encoded-video evidence.')
    if finish['dimensions'] != [1080, 1920] or finish['fps'] != '30/1' or finish['blackIntervals'] or abs(finish['audioLUFS'] + 14) > 1 or finish['audioTruePeakDBTP'] > -1:
        raise ValueError('Video geometry, black-frame or audio finish check failed.')
    if tile['suspectedTiles'] or tile['firstClosingFrameBrightnessRatio'] <= .8 or len(captions['captions']) != len(props['captions']):
        raise ValueError('Caption/capture/end-hold verification failed.')
    for item in read(p / 'analysis/alpha-all-frames.json'):
        if item['unexpectedEmptyFrames']:
            raise ValueError('Unexpected blank alpha frames: ' + item['asset'])
    for cue in read(p / 'analysis/motion-review.json'):
        if cue['lateFramePairs'] and len(cue['staticLatePairs']) == len(cue['lateFramePairs']):
            raise ValueError('Frozen late B-roll: ' + cue['kind'])
    out = dict(export=str(video.relative_to(ROOT)), sha256=digest(video),
               status='ready-for-user-review', encodedVisualsReviewed=True, dialogueReviewed=True,
               resolution=[1080, 1920], fps=30, frames=finish['frames'],
               audioLUFS=finish['audioLUFS'], audioTruePeakDBTP=finish['audioTruePeakDBTP'],
               fullDecode='passed', captionGroups=len(props['captions']))
    write(p / 'analysis/final-qa.json', out)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor')
    for name in ['assets', 'scenes']:
        p = sub.add_parser(name); p.add_argument('--query', default='');p.add_argument('--brand', choices=['atfro', 'niolearn', 'clinic']);p.add_argument('--kind');p.add_argument('--limit', type=int, default=30)
    p = sub.add_parser('init');p.add_argument('--brand', required=True, choices=['atfro', 'niolearn']);p.add_argument('--id', required=True);p.add_argument('--source', action='append', required=True);p.add_argument('--script')
    for name in ['preflight', 'render', 'record']:
        p = sub.add_parser(name);p.add_argument('project')
        if name == 'render':p.add_argument('--output')
        if name == 'record':
            p.add_argument('--video', required=True);p.add_argument('--visual-reviewed', action='store_true', required=True);p.add_argument('--dialogue-reviewed', action='store_true', required=True)
    p = sub.add_parser('scene');p.add_argument('kind');p.add_argument('--seconds', type=float, default=4);p.add_argument('--transparent', action='store_true');p.add_argument('--output', required=True);p.add_argument('--beats', nargs='*', type=int);p.add_argument('--labels', nargs='*')
    args = parser.parse_args()
    if args.command == 'doctor':run(['python3', 'tools/doctor.py']);return
    if args.command in ['assets', 'scenes']:
        items = read(ROOT / 'catalog' / ('assets.json' if args.command == 'assets' else 'motion-scenes.json'))
        clinic_assets=ROOT/'catalog/clinic-assets.json'
        if args.command=='assets' and clinic_assets.is_file():items=items+read(clinic_assets)
        tokens = args.query.casefold().split();out = []
        if args.brand:items=sorted(items,key=lambda item:item.get('brand')!=args.brand)
        for item in items:
            hay = json.dumps(item, ensure_ascii=False).casefold()
            asset_brand = item.get('brand') or ('atfro' if 'atfro' in hay else 'niolearn' if 'niolearn' in hay else 'shared')
            if args.brand and asset_brand not in [args.brand, 'shared']:continue
            if args.kind and item.get('kind') != args.kind:continue
            if all(t in hay for t in tokens):out.append(item)
        print(json.dumps(out[:max(1, args.limit)], indent=2));return
    if args.command == 'init':print(init_project(args.brand, args.id, args.source, args.script).relative_to(ROOT));return
    if args.command == 'scene':
        matches = [x for x in read(ROOT / 'catalog/motion-scenes.json') if x['kind'] == args.kind]
        if len(matches) != 1 or not .5 <= args.seconds <= 120:raise ValueError('Unknown scene or invalid duration (.5–120 seconds).')
        frames = round(args.seconds * 30)
        if args.beats and (args.beats != sorted(set(args.beats)) or any(b <= 0 or b >= frames for b in args.beats)):raise ValueError('Scene beats must be unique ascending interior frame positions.')
        props = dict(kind=args.kind, duration=frames, transparent=args.transparent)
        if args.beats:props['beats'] = args.beats
        if args.labels:props['labels'] = args.labels
        path = ROOT / '.cache/scene-props' / (args.kind + '.json');write(path, props)
        output = (ROOT / args.output).resolve();output.relative_to(ROOT);output.parent.mkdir(parents=True, exist_ok=True)
        if output.suffix.lower() != ('.webm' if args.transparent else '.mp4'):raise ValueError('Transparent scenes need .webm; opaque previews need .mp4.')
        flags = ['--codec=vp9', '--pixel-format=yuva420p', '--crf=22'] if args.transparent else ['--crf=18']
        run(['node', 'tools/render.mjs', matches[0]['composition'], str(output), '--props=' + str(path), *flags]);return
    p = project_path(args.project)
    if args.command == 'record':
        video = (ROOT / args.video).resolve(strict=True);video.relative_to(ROOT)
        print(json.dumps(record(p, video), indent=2));return
    report = check_project(p);print(json.dumps(report, indent=2))
    if args.command == 'render':
        output = (ROOT / (args.output or f'exports/{p.name}-FINAL.mp4')).resolve();output.relative_to(ROOT);output.parent.mkdir(parents=True, exist_ok=True)
        run(['bash', 'tools/render_reviewed_reel.sh', str(p.relative_to(ROOT)), str(output.relative_to(ROOT))])


if __name__ == '__main__':
    try:
        main()
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
