#!/usr/bin/env python3
"""Verify the latest recorded exports against reviewed QA and publish a local index."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--require-complete', action='store_true')
args = parser.parse_args()
queue = json.loads((ROOT / 'projects/batch-queue.json').read_text())
results, pending = [], []
for reel in queue['reels']:
    if reel['status'] not in ('approved', 'completed'):
        pending.append(reel['id'])
        continue
    project = ROOT / reel['project']
    qa = json.loads((project / 'analysis/final-qa.json').read_text())
    video = ROOT / reel['output']
    assert qa['export'] == reel['output'], f'Stale QA: {reel["id"]}'
    digest = hashlib.file_digest(video.open('rb'), 'sha256').hexdigest()
    assert digest == qa['sha256'], f'Export changed after review: {video}'
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,r_frame_rate,nb_frames',
        '-of', 'json', str(video)]))['streams'][0]
    assert (probe['width'], probe['height'], probe['r_frame_rate']) == (1080, 1920, '30/1')
    assert int(probe['nb_frames']) == qa['frames']
    assert qa['fullDecode'] == 'passed' and not qa['blackFramesDetected']
    assert abs(qa['audioLUFS'] + 14) < 1 and qa['audioTruePeakDBTP'] <= -1
    if reel['status'] == 'completed':
        tile = json.loads((ROOT / '.cache/batch' / reel['id'] / 'tile-scan/tile-scan.json').read_text())
        assert not tile['suspectedTiles']
        assert tile['firstClosingFrameBrightnessRatio'] > .8
        alpha = json.loads((project / 'analysis/alpha-all-frames.json').read_text())
        assert all(not asset['unexpectedEmptyFrames'] for asset in alpha)
        motion = json.loads((project / 'analysis/motion-review.json').read_text())
        assert all(not cue['lateFramePairs'] or len(cue['staticLatePairs']) < len(cue['lateFramePairs']) for cue in motion)
        editorial = json.loads((project / 'editorial.json').read_text())
        props = json.loads((project / 'reel.json').read_text())
        for entry in editorial.get('alphaExports', []):
            spec = entry if isinstance(entry, dict) else {'kind': entry}
            cue = next((c for c in props['broll'] if c['kind'] == spec['kind']), {})
            filename = f'{spec["kind"]}-v{editorial.get("assetVersion", 1)}-props.json'
            exported = json.loads((ROOT / 'public/assets/projects' / reel['id'] / filename).read_text())
            assert exported['transparent'] is True
            assert exported['duration'] == spec.get('duration', cue.get('duration'))
            for key in ('beats', 'labels'):
                expected = spec.get(key, cue.get(key))
                if expected is not None:
                    assert exported.get(key) == expected, f'Alpha {key} differs from the reel: {filename}'
    results.append(dict(brand=project.parent.name, number=reel['number'],
                        title=reel['workingName'].replace('_', ' '),
                        file=reel['output'], durationSeconds=qa['durationSeconds'],
                        sha256=digest, status=reel['status'],
                        finalQA=str((project / 'analysis/final-qa.json').relative_to(ROOT))))
report = dict(totalRecorded=len(queue['reels']), verified=len(results),
              pending=pending, reels=results)
(ROOT / 'catalog/RECORDED_EXPORTS.json').write_text(json.dumps(report, indent=2) + '\n')
lines = ['# Recorded reel exports', '',
         f'{len(results)} of {len(queue["reels"])} latest exports verified. Completed means checked locally and ready for user review.', '',
         '| Brand | Reel | Title | Duration | Video | QA |',
         '|---|---|---|---|---|---|']
for item in results:
    lines.append(f'| {item["brand"]} | {item["number"]} | {item["title"]} | {item["durationSeconds"]:.2f}s | [MP4](../{item["file"]}) | [Report](../{item["finalQA"]}) |')
if pending:
    lines.extend(['', 'Pending: ' + ', '.join(pending)])
(ROOT / 'catalog/RECORDED_EXPORTS.md').write_text('\n'.join(lines) + '\n')
print(f'Verified {len(results)}/{len(queue["reels"])} latest recorded exports.')
if args.require_complete:
    assert not pending, 'Recorded exports still pending: ' + ', '.join(pending)
