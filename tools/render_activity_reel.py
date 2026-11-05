#!/usr/bin/env python3
"""Render a reviewed, music-led portrait activity plan; keep plans/media local."""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

from event_transitions import assemble, transition
from log_colour import probe

ROOT = Path(__file__).resolve().parents[1]


def run(args):
    subprocess.run(args, check=True)


def render(plan_path, source_root, output, cache):
    from PIL import Image, ImageDraw, ImageFont
    plan = json.loads(plan_path.read_text())
    if output.exists():
        raise ValueError('Choose a new export filename')
    cache.mkdir(parents=True, exist_ok=True)
    cached_plan = cache / 'render-plan.json'
    if cached_plan.exists() and json.loads(cached_plan.read_text()) != plan:
        raise ValueError('Plan changed; choose a new versioned cache')
    cached_plan.write_text(json.dumps(plan, indent=2))
    for key in ('music', 'logo'):
        if not (ROOT / plan[key]).is_file():
            raise ValueError(f'Missing {key} asset')
    shots = plan['shots']
    if not shots or transition(shots[0])[1]:
        raise ValueError('Need shots; first shot cannot have an incoming transition')
    resolved = []
    for i, shot in enumerate(shots):
        path = (source_root / shot['source']).resolve()
        if not path.is_relative_to(source_root.resolve()):
            raise ValueError('Source escapes source root')
        info = probe(path)
        video = next(s for s in info['streams'] if s['codec_type'] == 'video')
        frames = shot['frames']
        speed = shot.get('speed', 1)
        start = shot['in']
        if isinstance(frames, bool) or not isinstance(frames, int) or frames <= 0:
            raise ValueError('Positive whole frames required')
        if not all(math.isfinite(x) for x in (start, speed)) or start < 0 or not .5 <= speed <= 1:
            raise ValueError('Invalid source timing')
        if float(video['r_frame_rate'].split('/')[0]) / float(video['r_frame_rate'].split('/')[1]) * speed < 30:
            raise ValueError('Insufficient source fps for slow motion')
        outgoing = transition(shots[i + 1])[1] if i + 1 < len(shots) else 0
        if start + (frames + outgoing) / 30 * speed > float(info['format']['duration']):
            raise ValueError('Shot exceeds source handles')
        if not shot.get('review_note'):
            raise ValueError('Shot needs visual review note')
        resolved.append((path, frames + outgoing, speed))
    cache.mkdir(parents=True, exist_ok=True)
    segments = []
    for i, (path, frames, speed) in enumerate(resolved):
        segment = cache / f'shot-{i:03d}.mp4'
        vf = f'trim=duration={frames / 30 * speed:.9f},setpts=(PTS-STARTPTS)/{speed},fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,eq=contrast=1.015:saturation=1.06:brightness=0.004,format=yuv420p'
        if not segment.exists():
            run(['ffmpeg', '-v', 'error', '-nostdin', '-n', '-threads', '2', '-filter_threads', '2', '-ss', str(shots[i]['in']), '-i', str(path), '-an', '-vf', vf, '-frames:v', str(frames), '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-threads', '2', str(segment)])
        segments.append(segment)
    pieces = assemble(segments, shots, cache)
    body_frames = sum(s['frames'] for s in shots)
    ending_frames = plan.get('ending_frames', 74)
    total = body_frames + ending_frames
    font = ROOT / 'public/assets/fonts/Sora.ttf'
    def text_center(draw, y, text, size, fill):
        f = ImageFont.truetype(str(font), size)
        draw.text((540, y), text, font=f, fill=fill, anchor='mt')
    title = Image.new('RGBA', (1080, 1920))
    shade = Image.new('RGBA', title.size)
    sd = ImageDraw.Draw(shade)
    for y in range(1180, 1920):
        sd.line((0, y, 1080, y), fill=(7, 18, 25, round(150 * (y - 1180) / 740)))
    title = Image.alpha_composite(title, shade)
    draw = ImageDraw.Draw(title)
    text_center(draw, 1470, 'DIWALI', 105, '#FFE4A4')
    text_center(draw, 1600, 'Little hands. Bright ideas.', 43, '#FFFFFF')
    title.save(cache / 'title.png')
    end = Image.new('RGB', (1080, 1920), '#FAF6EB')
    crest = Image.open(ROOT / plan['logo']).convert('RGBA')
    crest.thumbnail((470, 390))
    end.paste(crest, ((1080 - crest.width) // 2, 650), crest)
    draw = ImageDraw.Draw(end)
    text_center(draw, 1130, 'HAPPY DIWALI', 64, '#16354C')
    text_center(draw, 1225, 'Creativity lights up our world.', 33, '#6D6455')
    end.save(cache / 'ending.png')
    ending = cache / 'ending.mp4'
    if not ending.exists():
        run(['ffmpeg', '-v', 'error', '-n', '-loop', '1', '-i', str(cache / 'ending.png'), '-vf', 'fade=t=in:st=0:d=0.2,format=yuv420p', '-r', '30', '-frames:v', str(ending_frames), '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-threads', '2', str(ending)])
    pieces.append(ending)
    concat = cache / 'concat.txt'
    concat.write_text(''.join("file '" + str(p).replace("'", "'\\''") + "'\n" for p in pieces))
    silent = cache / 'silent.mp4'
    if not silent.exists():
        run(['ffmpeg', '-v', 'error', '-n', '-f', 'concat', '-safe', '0', '-i', str(concat), '-c', 'copy', str(silent)])
    duration = total / 30
    output.parent.mkdir(parents=True, exist_ok=True)
    filters = '[2:v]format=rgba,fade=t=in:st=0:d=0.25:alpha=1,fade=t=out:st=1.85:d=0.5:alpha=1[t];[0:v][t]overlay=enable=lt(t\\,2.4):shortest=1[v];' + f'[1:a]atrim=duration={duration},asetpts=PTS-STARTPTS,afade=t=in:d=0.18,afade=t=out:st={duration-1.3}:d=1.3,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[a]'
    run(['ffmpeg', '-v', 'error', '-nostdin', '-n', '-threads', '2', '-filter_complex_threads', '2', '-i', str(silent), '-i', str(ROOT / plan['music']), '-loop', '1', '-i', str(cache / 'title.png'), '-filter_complex', filters, '-map', '[v]', '-map', '[a]', '-frames:v', str(total), '-t', str(duration), '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-threads', '2', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-movflags', '+faststart', str(output)])
    actual = probe(output)
    video = next(s for s in actual['streams'] if s['codec_type'] == 'video')
    if int(video['nb_frames']) != total or (video['width'], video['height']) != (1080, 1920):
        raise ValueError('Encoded output frame count/dimensions differ')
    run(['ffmpeg', '-v', 'error', '-xerror', '-nostdin', '-i', str(output), '-f', 'null', '-'])
    (cache / 'qa.json').write_text(json.dumps({'frames': total, 'seconds': duration, 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'full_decode': 'passed', 'visual_review': 'pending', 'listening_review': 'not attested', 'audio': 'existing toolkit music; source chatter omitted'}, indent=2))
    print(output)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('plan', type=Path)
    p.add_argument('--source-root', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--cache', required=True, type=Path)
    a = p.parse_args()
    render(a.plan.resolve(), a.source_root.resolve(), a.output.resolve(), a.cache.resolve())
