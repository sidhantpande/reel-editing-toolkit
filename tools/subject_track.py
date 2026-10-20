#!/usr/bin/env python3
"""Track an editor-selected subject with OpenCV CSRT; emit a smoothed crop path."""
import argparse
import hashlib
import json
import math
import statistics
import subprocess
from pathlib import Path


def crop_expression(points):
    if not points:
        raise ValueError('Crop path is empty')
    previous = -1
    for t, centre in points:
        if not math.isfinite(t) or t < 0 or t <= previous or not math.isfinite(centre) or not .158 <= centre <= .842:
            raise ValueError('Crop times must increase and centres must stay inside a full-height9:16 crop')
        previous = t
    expression = f'{points[-1][1]:.7f}'
    for (a, x), (b, y) in reversed(list(zip(points, points[1:]))):
        expression = f'if(lt(t,{b:.7f}),({x:.7f}+({y-x:.7f})*max(0,t-{a:.7f})/{b-a:.7f}),{expression})'
    return expression


def smooth(values):
    if not values or any(not math.isfinite(x) for x in values):
        raise ValueError('Finite tracked centres required')
    medians = [statistics.median(values[max(0, i-1):i+2]) for i in range(len(values))]
    weights = [1, 4, 6, 4, 1]
    return [sum(weight * medians[min(len(values)-1, max(0, i+j-2))] for j, weight in enumerate(weights))/16 for i in range(len(values))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--start', required=True, type=float)
    parser.add_argument('--seconds', required=True, type=float)
    parser.add_argument('--speed', type=float, default=1)
    parser.add_argument('--bbox', required=True, nargs=4, type=float, metavar=('X', 'Y', 'W', 'H'))
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    x, y, w, h = args.bbox
    if args.start < 0 or args.seconds <= 0 or args.speed <= 0 or not (0 <= x < x+w <= 1 and 0 <= y < y+h <= 1):
        parser.error('Valid source window, speed and normalized subject rectangle required')
    if args.source.resolve() == args.out.resolve():
        parser.error('Output must not overwrite source media')
    import cv2
    import numpy as np
    cv2.setNumThreads(2)
    q = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(args.source)]))
    video = next(s for s in q['streams'] if s['codec_type'] == 'video')
    rotation = int(video.get('tags', {}).get('rotate', 0))
    for item in video.get('side_data_list', []):
        rotation = int(item.get('rotation', rotation))
    if rotation % 360 or abs(video['width']/video['height'] - 16/9) > .01:
        raise ValueError('Tracking crop requires an already oriented16:9 source; use native portrait directly')
    width = 960
    height = round(video['height'] / video['width'] * width / 2) * 2
    process = subprocess.Popen(['ffmpeg', '-v', 'error', '-nostdin', '-threads', '2', '-ss', str(args.start), '-i', str(args.source), '-t', str(args.seconds), '-vf', f'fps=15,scale={width}:{height}', '-pix_fmt', 'bgr24', '-f', 'rawvideo', '-'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    tracker = cv2.TrackerCSRT_create()
    rows, views = [], []
    box = tuple(round(v) for v in (x*width, y*height, w*width, h*height))
    while True:
        raw = process.stdout.read(width*height*3)
        if not raw:
            break
        if len(raw) != width*height*3:
            raise ValueError('Incomplete tracking frame')
        frame = np.frombuffer(raw, np.uint8).reshape(height, width, 3).copy()
        if not rows:
            tracker.init(frame, box)
            ok = True
        else:
            ok, candidate = tracker.update(frame)
            if ok:
                box = candidate
        bx, by, bw, bh = box
        rows.append({'source_seconds': args.start + len(rows)/15, 'output_seconds': len(rows)/15/args.speed, 'tracker_ok': bool(ok), 'bbox': [bx/width, by/height, bw/width, bh/height], 'centre': (bx+bw/2)/width})
        # First/middle/last frames are saved after tracking, without identity inference.
        views.append((frame, box))
    error = process.stderr.read().decode()
    if process.wait() or not rows:
        raise RuntimeError(error or 'No frames decoded')
    centres = smooth([r['centre'] for r in rows])
    path = [[r['output_seconds'], min(.842, max(.158, centre))] for r, centre in zip(rows, centres)]
    crop_expression(path)
    result = {'source': str(args.source.resolve()), 'source_sha256': hashlib.file_digest(args.source.open('rb'), 'sha256').hexdigest(), 'tool': 'OpenCV CSRT', 'opencv_version': cv2.__version__, 'initial_bbox': args.bbox, 'source_in': args.start, 'source_seconds': args.seconds, 'speed': args.speed, 'analysis_fps': 15, 'failed_frames': sum(not r['tracker_ok'] for r in rows), 'tracked_frames': rows, 'crop_path': path, 'status': 'Editor-selected target; automatic trajectory, median/binomial smoothing. Identity and framing require visual review.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2))
    for index in sorted({0, len(views)//2, len(views)-1}):
        frame, box = views[index]
        bx, by, bw, bh = (round(v) for v in box)
        cv2.rectangle(frame, (bx, by), (bx+bw, by+bh), (0, 0, 255), 2)
        centre = path[index][1]*width
        half = height*9/16/2
        cv2.rectangle(frame, (round(centre-half), 0), (round(centre+half), height-1), (0, 220, 0), 2)
        cv2.imwrite(str(args.out.with_suffix(f'.frame-{index:03}.jpg')), frame)
    print(f'{args.out}: {len(rows)} tracked samples, {result["failed_frames"]} tracking failures')


if __name__ == '__main__':
    main()
