#!/usr/bin/env python3
"""Add an authored, airy question opening to an unchanged portrait interview.

Project opening-question.json stays local with the transcript. Recompose from
the original silent picture and lossless mix, never from a prefixed export.
"""
from __future__ import annotations
import argparse
import array
import hashlib
import json
import math
import os
import shutil
import subprocess
from pathlib import Path
from PIL import Image
import interview_edit as kit


def opening_timing(plan, question):
    frames = question.get('durationFrames')
    transition = question.get('transitionFrames')
    if type(frames) is not int or not 90 <= frames <= 180:
        raise ValueError('Question needs 3–6 seconds of integer edit frames')
    if type(transition) is not int or not 3 <= transition <= 12:
        raise ValueError('Question dissolve needs 3–12 integer edit frames')
    if transition > plan.get('leadFrames', 0):
        raise ValueError('Question overlap must not fade the first spoken phoneme')
    offset = frames - transition
    total = plan['dialogueFrames'] + plan['logoFrames'] + offset
    if total > 1500:
        raise ValueError('Question plus complete answer exceeds 50 seconds; split editorially')
    return dict(cardFrames=frames, transitionFrames=transition,
                bodyOffsetFrames=offset, totalFrames=total)


def validate_question(plan, question):
    timing = opening_timing(plan, question)
    lines = question.get('lines', [])
    if not 2 <= len(lines) <= 4 or any(not isinstance(x, str) or not x.strip() for x in lines):
        raise ValueError('Author two to four short question lines')
    if ' '.join(lines) != question.get('question'):
        raise ValueError('Question line layout must preserve the complete authored question')
    english = question.get('englishLines', [])
    if not 1 <= len(english) <= 3 or ' '.join(english) != question.get('englishQuestion'):
        raise ValueError('English line layout must preserve the complete translated question')
    if any(c in question['question']+question['englishQuestion'] for c in '{}\\\n\r'):
        raise ValueError('Question must contain plain text, not ASS commands')
    if question.get('partLabel') and (type(question.get('partNumber')) is not int or not 1 <= question['partNumber'] <= 99 or
            question['partLabel'] != f"भाग {question['partNumber']} / Part {question['partNumber']}"):
        raise ValueError('Use matching Hindi and English part numbers')
    if question.get('wording') != 'condensed question, not a verbatim quotation':
        raise ValueError('Record the question wording provenance')
    source = question.get('sourceQuestion', {})
    if source.get('source_id') not in plan['sources'] or not 0 <= source.get('start', -1) < source.get('end', -1):
        raise ValueError('Record the original interviewer question range')
    return timing


def body_signature(plan, words):
    return hashlib.sha256(json.dumps(dict(plan=plan, words=words), sort_keys=True).encode()).hexdigest()


def assert_cached_body(cache, signature):
    if not (cache/'signature').is_file() or (cache/'signature').read_text() != signature:
        raise ValueError('Changed edit plan: question opening requires the unchanged cached body')
    for path in [cache/'portrait/silent.mp4', cache/'mixed-normalized.wav', cache/'mix.wav']:
        if not path.is_file():
            raise ValueError('Missing original body dependency: '+str(path))


def question_ass(question, fontdir, path):
    """Light native typography; complex shaping preserves Devanagari matras."""
    size = 110
    duration = question['durationFrames']/30
    end = kit.ass_time(duration)
    header = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,Noto Sans Devanagari,78,&H004D3F17,&H004D3F17,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    rows = [header]
    def line(text, y, family, size, color, spacing=0, delay=.12):
        tags = rf'{{\an5\fn{family}\b0\fs{size}\fsp{spacing}\bord0\shad0\c&H00{color}&\move(540,{y+12},540,{y},0,360)\fad(340,0)}}'
        rows.append(f'Dialogue: 1,{kit.ass_time(delay)},{end},Main,,0,0,0,,{tags}{text}\n')
    first = 860-(len(question['lines'])-2)*60
    line('DR AMOL MALPANI', first-144, 'Montserrat', 26, '86745D', 2.5)
    # An understated gold hairline separates the eyebrow from the question.
    rows.append(f'Dialogue: 0,0:00:00.12,{end},Main,,0,0,0,,'+r'{\an7\pos(504,'+str(first-87)+r')\p1\c&H007FAAAB&\bord0\shad0\fad(340,0)}m 0 0 l 72 0 l 72 2 l 0 2'+'\n')
    for i, text in enumerate(question['lines']):
        line(text, first+i*118, 'Noto Sans Devanagari', size, '4D3F17', delay=.18)
    english_start = first+(len(question['lines'])-1)*118+172
    for i, text in enumerate(question['englishLines']):
        line(text, english_start+i*66, 'Montserrat', 46, '756959', delay=.24)
    if question.get('partLabel'):
        line(question['partLabel'], english_start+(len(question['englishLines'])-1)*66+110,
             'Noto Sans Devanagari', 60, '86745D', delay=.3)
    path.write_text(''.join(rows))


def pcm_energy(path, duration=.14):
    samples = array.array('f', subprocess.check_output([
        'ffmpeg','-v','error','-i',str(path),'-t',str(duration),'-vn',
        '-ar','48000','-ac','1','-f','f32le','-']))
    return math.sqrt(sum(x*x for x in samples)/max(1, len(samples)))


def prepare_opening(plan, question, cache, work):
    folder = work/'question-opening'
    folder.mkdir(exist_ok=True)
    fonts = folder/'fonts'
    fonts.mkdir(exist_ok=True)
    # Isolate the two opening fonts: adding a lighter font must not affect
    # existing body captions' font selection on a graphics-only recompose.
    for name in ['NotoSansDevanagari-SemiBold.ttf','Montserrat-SemiBold.ttf']:
        shutil.copyfile(kit.ROOT/'.cache/jetkids/interview-edits/fonts'/name, fonts/name)
    ass = folder/'question.ass'
    question_ass(question, fonts, ass)
    card = folder/'card.mkv'
    duration = question['durationFrames']/30
    fc = f"[0:v]{kit.caption_filter(ass,fonts)}[type];[1:v]scale=176:-2,setsar=1[crest];[type][crest]overlay=44:64:shortest=1,format=yuv420p[v]"
    kit.run(['-threads','2','-filter_complex_threads','2','-f','lavfi','-i',
             f'color=c=0xf9f7f1:s=1080x1920:r=30:d={duration}',
             '-loop','1','-i',kit.corner_crest(),'-filter_complex',fc,'-map','[v]',
             '-an','-frames:v',question['durationFrames'],'-c:v','ffv1','-level','3',
             '-threads','2','-y',card])
    design = folder/'design.png'
    kit.run(['-ss','1','-i',card,'-frames:v','1','-y',design])
    # Measure the actual HarfBuzz-shaped render. Pillow without RAQM measures
    # Devanagari clusters incorrectly and cannot be the typography gate.
    with Image.open(design) as image:
        bounds = image.convert('RGB').crop((0,500,1080,1600)).getchannel('B').point(lambda x: 255 if x < 160 else 0).getbbox()
    if bounds is None or bounds[0] < 80 or bounds[2] > 1000:
        raise ValueError('Rendered question exceeds safe margins; curate its line breaks')
    kit.save(folder/'type-bounds.json',dict(centralInkBounds=list(bounds),
             measurement='Actual complex-shaped bilingual card raster, y500–1600; safe x80–1000'))
    # Reuse the same quiet instrumental; estimate its mastering gain from the
    # source-owned music-only lead, rather than guessing an unrelated volume.
    original_energy = pcm_energy(cache/'mix.wav')
    mastered_energy = pcm_energy(cache/'mixed-normalized.wav')
    if original_energy <= 0:
        raise ValueError('Cannot establish the existing music lead gain')
    gain = 1.1*mastered_energy/original_energy
    audio = folder/'music-prefix.wav'
    kit.run(['-stream_loop','-1','-i',plan['music'],'-t',duration,'-vn','-af',
             f'volume={gain},afade=t=in:d=0.35,afade=t=out:st={duration-.2}:d=0.2',
             '-ar','48000','-ac','2','-c:a','pcm_s24le','-y',audio])
    return dict(question, cardPath=str(card), audioPath=str(audio), musicGain=gain)


def render(project):
    project = Path(project).resolve()
    plan, words, checks = kit.preflight(project)
    question = kit.read(project/'opening-question.json')
    timing = validate_question(plan, question)
    cache = kit.ROOT/'.cache/jetkids/interview-edits'/plan['id']
    signature = body_signature(plan, words)
    assert_cached_body(cache, signature)
    work = cache/'portrait'
    dest = kit.ROOT/'exports/jetkids-interview-edits'/plan['id']/'portrait.mp4'
    if not dest.is_file():
        raise ValueError('A reviewed current body export is required before adding an opening')
    before = kit.digest(dest)
    oldqa = kit.read(work/'qa.json')
    prior = work/'question-opening/body-review.json'
    prior.parent.mkdir(exist_ok=True)
    if prior.exists():
        if kit.read(prior)['bodySignature'] != signature:
            raise ValueError('Question body provenance changed')
    else:
        kit.save(prior, dict(bodySignature=signature, originalExportSha256=before,
                            bodyQA=oldqa, silentSha256=kit.digest(work/'silent.mp4'),
                            losslessMixSha256=kit.digest(cache/'mixed-normalized.wav')))
    saved = kit.read(prior)
    if (kit.digest(work/'silent.mp4') != saved['silentSha256'] or
            kit.digest(cache/'mixed-normalized.wav') != saved['losslessMixSha256']):
        raise ValueError('Reviewed body picture/audio cache changed')
    prepared = prepare_opening(plan, question, cache, work)
    target = dest.with_name('portrait.pending.mp4')
    v, loudness, groups = kit.finish_picture(plan, words, 'portrait', work,
                                           cache/'mixed-normalized.wav', target,
                                           question=prepared)
    os.replace(target, dest)
    report = dict(question=question, **timing, bodySignature=signature,
                  originalBodyExportSha256=saved['originalExportSha256'],
                  silentSha256=saved['silentSha256'], losslessMixSha256=saved['losslessMixSha256'],
                  musicGain=prepared['musicGain'], pictureAndAudioOffsetIdentical=True,
                  unchangedBodyReview=saved['bodyQA'], cardVisualReview='Pending encoded opening inspection',
                  preservation='Full unchanged source cuts, caption groups, crop, voice speed and closing crest',
                  rerenderInput='Original silent picture and lossless mix; never a prefixed export')
    kit.save(work/'question-opening/report.json', report)
    kit.save(work/'qa.json',dict(path=str(dest),sha256=kit.digest(dest),frames=int(v['nb_frames']),
             full_decode='passed',loudness=loudness,captions=len(groups),
             cornerLogoSha256=kit.digest(kit.corner_crest()),openingQuestion=report,
             visual_review='Original body review inherited; new opening pending encoded review',
             listening_review=saved['bodyQA'].get('listening_review','Not attested'),
             status='Question opening review draft'))
    print('QUESTION_OPENING_EXPORTED', dest, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    render(parser.parse_args().project)
