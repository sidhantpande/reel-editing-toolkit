#!/usr/bin/env python3
"""Record a verified export only after its encoded visuals and dialogue have been reviewed."""
from pathlib import Path
import argparse,json,hashlib,subprocess
R=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('project');ap.add_argument('--visual-reviewed',action='store_true',required=True);ap.add_argument('--dialogue-reviewed',action='store_true',required=True);a=ap.parse_args();P=R/a.project;name=P.name
queue=json.loads((R/'projects/batch-queue.json').read_text());item=next(x for x in queue['reels'] if x['id']==name);video=R/item['output'];props=json.loads((P/'reel.json').read_text());cut=json.loads((P/'cut-list.json').read_text());editor=json.loads((P/'editorial.json').read_text());finish=R/'.cache/batch'/name/'finish';captions=R/'.cache/batch'/name/'captions';m=json.loads((finish/'finish-measurements.json').read_text());ocr=json.loads((captions/'encoded-caption-check.json').read_text())
assert video.is_file() and m['fullDecode']=='passed';assert m['dimensions']==[1080,1920] and m['frames']==props['durationInFrames'];assert abs(m['audioLUFS']+14)<1 and m['audioTruePeakDBTP']<=-1;assert not m['blackIntervals'];tile=R/'.cache/batch'/name/'tile-scan/tile-scan.json';assert tile.is_file();tile_report=json.loads(tile.read_text());assert not tile_report['suspectedTiles'] and tile_report.get('firstClosingFrameBrightnessRatio',0)>.8;assert len(ocr['captions'])==len(props['captions'])
motion_path=P/'analysis/motion-review.json'
if props['broll']:
 assert motion_path.is_file(),'Missing encoded late-motion review'
 for cue in json.loads(motion_path.read_text()):assert not cue['lateFramePairs'] or len(cue['staticLatePairs'])<len(cue['lateFramePairs']),('Frozen late B-roll',cue['kind'])
alpha=[]
for entry in editor.get('alphaExports',[]):
 kind=entry['kind'] if isinstance(entry,dict) else entry
 p=R/'public/assets/projects'/name/(kind+f'-v{editor.get("assetVersion",1)}.webm');raw=subprocess.check_output(['ffmpeg','-v','error','-c:v','libvpx-vp9','-i',str(p),'-vf','alphaextract,scale=108:192','-f','rawvideo','-pix_fmt','gray','-']);assert min(raw)==0 and max(raw)==255
 alpha.append(dict(asset=str(p.relative_to(R)),alphaMin=0,alphaMax=255,dimensions=[1080,1920]))
(P/'analysis').mkdir(exist_ok=True);(P/'analysis/alpha-check.json').write_text(json.dumps(alpha,indent=2)+'\n')
report=dict(export=item['output'],title=item['workingName'],order=item['number'],sha256=hashlib.sha256(video.read_bytes()).hexdigest(),bytes=video.stat().st_size,resolution=m['dimensions'],fps=30,frames=m['frames'],durationSeconds=m['frames']/30,dialogueFrames=cut['dialogueFrames'],captions=dict(words=sum(len(x['words']) for x in props['captions']),groups=len(props['captions']),color=('Opt-in lime on camera and dark olive on ivory.' if P.parent.name=='atfro' else 'Opt-in bright teal on camera and darker teal on ivory.')+' One main keyword per phrase; brand/domain always colored.',visualReview='Every caption group and encoded transition-boundary contact inspected.',sourceAlignment='Reviewed source-language medium word transcript, manually corrected names/English terms and pause overhangs, mapped through exact 30fps source cuts.'),boundaryEvents=m['boundaryEvents'],audioLUFS=m['audioLUFS'],audioTruePeakDBTP=m['audioTruePeakDBTP'],fullDecode=m['fullDecode'],blackFramesDetected=False,reusableAlphaScenes=len(alpha),alphaCheck='analysis/alpha-check.json',ending='Original brand logo only on ivory; no additional text.',status='awaiting-user-review',rebuild=f'bash tools/render_reviewed_reel.sh {a.project} {item["output"]}')
(P/'analysis/final-qa.json').write_text(json.dumps(report,indent=2)+'\n')
plan=json.loads((P/'edit-plan.json').read_text());plan.update(status='edited-awaiting-user-review',captionPreset='reference',broll=props['broll'],output=item['output'],finalQA='analysis/final-qa.json');(P/'edit-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
item['status']='completed';item['finalQA']=str((P/'analysis/final-qa.json').relative_to(R));(R/'projects/batch-queue.json').write_text(json.dumps(queue,indent=2)+'\n')
lines=['# Recorded reel batch','',queue['objective'],'','| Reel | Project | Status | Export |','|---|---|---|---|']
for x in queue['reels']:lines.append(f'| {x["number"]} | {x["id"]} | {x["status"]} | {x.get("output") or "Previously approved export"} |')
(R/'projects/BATCH_PROGRESS.md').write_text('\n'.join(lines)+'\n');print('Recorded verified export:',name,report['durationSeconds'],'seconds')
