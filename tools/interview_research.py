"""Compile local ASR research without treating it as approved dialogue or cut data.

Native whisper.cpp JSON and full-source faster-whisper research are supported.
Raw camera files and transcripts belong in ignored local folders.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


def checked_manifest(rows):
    seen = set()
    for row in rows:
        sid = row['id']
        if not isinstance(sid, str) or not re.fullmatch(r'[A-Z]\d{3,}', sid):
            raise ValueError(f'Invalid stable source ID: {sid!r}')
        if sid in seen:
            raise ValueError(f'Duplicate source ID: {sid}')
        seen.add(sid)
        duration = float(row['duration'])
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError(f'Invalid duration: {sid}')
        if row.get('audio_duration') is not None:
            if abs(float(row['audio_duration']) - duration) > .2:
                raise ValueError(f'Incomplete or mismatched extracted audio: {sid}')
    return rows


def timed_segment(sid, text, start, end, duration, **extra):
    start, end = float(start), float(end)
    if not math.isfinite(start) or not math.isfinite(end):
        raise ValueError(f'Non-finite ASR timing: {sid}')
    issues = []
    if start < 0 or end > duration or end < start:
        issues.append('ASR timing outside physical source bounds')
    bounded_start = min(duration, max(0., start))
    bounded_end = min(duration, max(0., end))
    if bounded_end <= bounded_start:
        issues.append('No positive source interval; do not use as a cut')
    if '\ufffd' in text:
        issues.append('Segment text contains an undecodable character')
    return dict(source_id=sid, text=text.strip(), start=bounded_start,
                end=bounded_end, original_asr_start=start, original_asr_end=end,
                timing_issues=issues, cut_approved=False, **extra)


def native_research(raw, row):
    decoded = raw.decode('utf-8', errors='replace')
    doc = json.loads(decoded)
    segments = []
    for s in doc['transcription']:
        times = s['offsets']
        segments.append(timed_segment(
            row['id'], s['text'], times['from'] / 1000,
            times['to'] / 1000, float(row['duration']),
            native_token_count=len(s.get('tokens', []))))
    return dict(engine='whisper.cpp', language=doc.get('result', {}).get('language'),
                model=doc.get('params', {}).get('model'), segments=segments,
                invalid_utf8_replacements=decoded.count('\ufffd'),
                note='Token byte fragments can make native JSON invalid UTF-8. '
                     'Replacements are recorded; token evidence is not word-aligned captions.')


def fallback_research(doc, row):
    segments = []
    for chunk in doc.get('chunks', []):
        for s in chunk['segments']:
            # This input format already uses absolute source-relative seconds.
            words = [dict(w, source_id=row['id']) for w in s.get('words', [])]
            segments.append(timed_segment(
                row['id'], s['text'], s['start'], s['end'],
                float(row['duration']), words=words,
                chunk_start=chunk['source_start'],
                language=chunk.get('language')))
    return dict(engine='faster-whisper', model=doc.get('model'), segments=segments,
                language=sorted({c.get('language') or 'unknown' for c in doc.get('chunks', [])}),
                note='Overlapping chunks are retained as research evidence. '
                     'Repeated text is not an editorial instruction or a verified repeated utterance.')


def compile_one(row, native_dir, fallback_dir):
    sid = row['id']
    if row.get('audio_status') == 'silent' and row.get('peak') == 0:
        return dict(id=sid, source=row['path'], event=row.get('event'),
                    source_duration=float(row['duration']), audio_duration=row.get('audio_duration'),
                    audio_sha256=row.get('audio_sha256'), status='Measured digital silence; no dialogue to transcribe',
                    engine='measured-silence', segments=[], dialogue_approved=False,
                    captions_approved=False, editor_listening_attestation=False,
                    input_errors=[]), []
    native = native_dir / (sid + '.json')
    fallback = fallback_dir / (sid + '.json')
    errors = []
    research = None
    if native.exists():
        try:
            research = native_research(native.read_bytes(), row)
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f'Native output incomplete or invalid: {exc}')
    if research is None and fallback.exists():
        try:
            doc = json.loads(fallback.read_text())
            if 'chunks' in doc and 'partial' not in doc.get('status', '').lower():
                research = fallback_research(doc, row)
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f'Fallback output incomplete or invalid: {exc}')
    if research is None:
        return None, errors
    return dict(id=sid, source=row['path'], event=row.get('event'),
                source_duration=float(row['duration']), audio_duration=row.get('audio_duration'),
                audio_sha256=row.get('audio_sha256'),
                status='Full-source ASR research attempt; transcript completeness not verified',
                dialogue_approved=False, captions_approved=False,
                editor_listening_attestation=False,
                review_requirements=['Correct selected wording against original audio',
                                     'Confirm speaker identity and role',
                                     'Review complete sentences and actual cut boundaries'],
                input_errors=errors, **research), errors


def stamp(seconds):
    return f'{int(seconds // 60):02}:{seconds % 60:05.2f}'


def write_research(manifest, native_dir, fallback_dir, output):
    checked_manifest(manifest)
    output.mkdir(parents=True, exist_ok=True)
    processed, pending, failures = [], [], {}
    for row in manifest:
        result, errors = compile_one(row, native_dir, fallback_dir)
        if errors:
            failures[row['id']] = errors
        if result is None:
            pending.append(row['id'])
            continue
        sid = row['id']
        (output / (sid + '.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        lines = [f'# {sid} — ASR research draft', '',
                 'Original-language research. Wording, role and cut timings need review before publication.', '',
                 f"Source: {result['source']}", f"Duration: {result['source_duration']:.3f}s", '',
                 'Token/segment timestamps are not approved caption or edit timings.', '']
        for seg in result['segments']:
            lines.append(f"**{stamp(seg['start'])}–{stamp(seg['end'])}** {seg['text']}")
            if seg['timing_issues']:
                lines.append('Timing review: ' + '; '.join(seg['timing_issues']))
            lines.append('')
        (output / (sid + '.md')).write_text('\n'.join(lines))
        processed.append(sid)
    silent = [r['id'] for r in manifest if r['id'] in processed and r.get('audio_status') == 'silent' and r.get('peak') == 0]
    summary = dict(registered_candidates=len(manifest), full_source_asr_attempts=len(processed) - len(silent),
                   accounted_sources=len(processed), measured_silent_sources=silent,
                   processed=processed, pending=pending, input_errors=failures,
                   candidate_duration_seconds=sum(float(r['duration']) for r in manifest),
                   processed_duration_seconds=sum(float(r['duration']) for r in manifest if r['id'] in processed),
                   final_caption_or_listening_approval=False)
    (output / 'coverage.json').write_text(json.dumps(summary, indent=2) + '\n')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--native-dir', type=Path, required=True)
    parser.add_argument('--fallback-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--require-complete', action='store_true', help='Fail if any registered source lacks completed ASR research or measured-silence evidence')
    args = parser.parse_args()
    summary = write_research(json.loads(args.manifest.read_text()), args.native_dir, args.fallback_dir, args.out)
    print(json.dumps({k: v for k, v in summary.items() if k not in {'processed', 'pending'}}, indent=2))
    print(f"Pending: {len(summary['pending'])}")
    return 1 if args.require_complete and summary['pending'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
