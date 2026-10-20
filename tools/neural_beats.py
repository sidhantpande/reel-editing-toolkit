#!/usr/bin/env python3
"""Estimate beats/downbeats with the optional, isolated Beat This! runtime."""
import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path


def checked_times(values, duration):
    result = [float(value) for value in values]
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('Positive finite audio duration required')
    if any(not math.isfinite(t) or t < 0 or t > duration for t in result):
        raise ValueError('Beat timestamps must lie inside the source audio')
    if any(b <= a for a, b in zip(result, result[1:])):
        raise ValueError('Beat timestamps must be strictly increasing')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('audio', type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--model', default='final0')
    parser.add_argument('--torch-home', type=Path, default=Path('.cache/models/beat-this'))
    args = parser.parse_args()
    if args.audio.resolve() == args.out.resolve():
        parser.error('Output must not overwrite source audio')
    os.environ['TORCH_HOME'] = str(args.torch_home.resolve())
    # Keep the primary rendering environment free of these optional dependencies.
    import soundfile as sf
    import torch
    from beat_this.inference import File2Beats
    torch.set_num_threads(2)
    duration = sf.info(args.audio).duration
    model = File2Beats(checkpoint_path=args.model, device='cpu', dbn=False)
    beats, downbeats = model(str(args.audio))
    beats = checked_times(beats, duration)
    downbeats = checked_times(downbeats, duration)
    if any(not beats or min(abs(t - b) for b in beats) > .04 for t in downbeats):
        raise ValueError('Downbeat does not correspond to a predicted beat')
    result = {
        'source': str(args.audio.resolve()),
        'source_sha256': hashlib.file_digest(args.audio.open('rb'), 'sha256').hexdigest(),
        'duration_seconds': duration,
        'tool': 'beat-this',
        'version': importlib.metadata.version('beat-this'),
        'checkpoint': args.model,
        'beats': beats,
        'downbeats': downbeats,
        'beat_frames_30fps': [round(t * 30) for t in beats],
        'status': 'Model estimates; action and musical phrase review still required. No listening attestation.',
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.out.with_suffix(args.out.suffix + '.tmp')
    temporary.write_text(json.dumps(result, indent=2) + '\n')
    temporary.replace(args.out)
    print(f'{len(beats)} beats, {len(downbeats)} downbeats -> {args.out}')


if __name__ == '__main__':
    main()
