#!/usr/bin/env python3
"""Package clean-cut review links, all B-roll requests, assets and source accounting."""
import csv,hashlib,json,shutil,zipfile
from pathlib import Path
import clinic
ROOT=clinic.ROOT;BATCH=ROOT/'03_reels/dhiraj';DELIVERY=Path('/Users/sidhant/Desktop/Video-Editing/Dhiraj-Edits')
EXCLUDED={9775:('reel-03','failed opening, superseded by 9776'),9777:('reel-03','false start and spoken cut command'),9779:('reel-03','incomplete alternate ending, superseded by 9782'),9780:('reel-03','rehearsal/setup and interrupted close'),9781:('reel-03','accidental 2.3-second camera clip'),9787:('reel-05','incomplete alternate hook'),9790:('reel-05','concise alternate closing; main complete take 9788 retained'),9791:('reel-07','setup / aborted interviewer intro'),9792:('reel-07','aborted interviewer intro'),9793:('reel-07','optional question, followed by setup; doctor explainer works without it'),9797:('reel-08','aborted opening, replaced by 9798'),9799:('reel-08','accidental 1.27-second tail')}
COMMON='Generate a 10-second silent vertical 9:16 video, 1080×1920, 30fps, photoreal/editorial or refined realistic 3D as specified. Stable geometry and consistent lighting, soft ivory background, muted sage/teal accents, restrained champagne highlights. Keep the lower 20% visually quiet for later captions. Use purposeful continuous motion, not random shaking or a static image hold. No text, captions, watermark, logo, recognizable app/brand, treatment promises, skin-whitening, before/after, patient outcome or copied face. No soundtrack; original doctor narration will continue over this insert.'

def timeline_anchor(plan,clip,t):
    matches=[s for s in plan['segments'] if Path(s['source']).stem==clip and s['source_in']<=t<s['source_out']]
    if not matches:raise ValueError(f'B-roll anchor not retained: {clip} {t}')
    s=matches[0];return round((s['timeline_in']+t-s['source_in'])*30)/30

def main():
    specs=json.loads((BATCH/'editorial-specs.json').read_text());broll=json.loads((BATCH/'broll-specs.json').read_text())
    active=json.loads((BATCH/'active-plans.json').read_text()) if (BATCH/'active-plans.json').exists() else {}
    finishes=json.loads((BATCH/'finishing-plans.json').read_text()) if (BATCH/'finishing-plans.json').exists() else {}
    assets=json.loads((ROOT/'assets/cutouts/dhiraj/manifest.json').read_text())
    assets_out=DELIVERY/'visual-elements';assets_out.mkdir(parents=True,exist_ok=True)
    for a in assets:shutil.copy2(ROOT/a['path'],assets_out/Path(a['path']).name)
    for name in ['manifest.json','prompts.json','extra-prompts.json']:shutil.copy2(ROOT/'assets/cutouts/dhiraj'/name,assets_out/name)
    master=['# Dhiraj — complete B-roll request pack\n','24 planned clips: 2 per edited reel. Received and inserted assets are marked per shot below.\n','For pending prompts generate 10 seconds, keep all sound muted, and return the exact filename. Times change if dialogue cuts are revised.\n']
    plans={};flat=[];index=['# Dhiraj — reel review\n','12 separate 1080×1920 / 30fps clean cuts. Setup, failed retakes and long silences removed; source-specific crops, dialogue joins and two-person speaker cuts included. Finished review versions are linked separately when captions, returned B-rolls and supplied branding are available.\n','[All B-roll prompts](BROLL-PROMPTS.md) · [Source accounting](SOURCE-ACCOUNTING.md) · [Visual elements](visual-elements/)\n','| Reel | Topic | Duration | Play clean edit | B-roll |\n|---|---|---:|---|---|\n']
    for spec in specs:
        name=spec['id'];folder=BATCH/name;p=ROOT/active[name] if name in active else folder/'04_timeline/v01/plan.json';plan=json.loads(p.read_text());plans[name]=plan
        video=Path(plan.get('delivery_export',plan['clean_export']));deliver=DELIVERY/name
        finished=json.loads((ROOT/finishes[name]).read_text()) if name in finishes else None
        finished_video=Path(finished['finished_export']) if finished else None
        clinic.save(deliver/'timeline.json',plan)
        play=f'[Clean]({name}/{video.name})'
        if finished_video and finished_video.is_file():play+=f' · [Finished review]({name}/{finished_video.name})'
        index.append(f'| {name} | {spec["title"]} | {plan["duration_seconds"]:.2f}s | {play} | [Prompts]({name}/broll-prompts.md) |\n')
        lines=[f'# {name} — {spec["title"]}\n',f'Clean-cut reference: {video.name}\n',f'Script match: {spec.get("script_ref","Supplied Reel "+name[-2:])}\n']
        requests=[]
        for cue in [r for r in broll if r['reel']==name]:
            start=timeline_anchor(plan,cue['clip'],cue['source_anchor']);end=min(start+cue['seconds'],plan['duration_seconds']);filename=f'dhiraj_{name}_{cue["id"]}.mp4'
            req={**cue,'timeline_in':start,'timeline_out':end,'delivery_filename':filename,'status':'REQUESTED / awaiting returned video','media_in':.5,'full_prompt':COMMON+'\n\nScene: '+cue['prompt']};requests.append(req);flat.append(req)
            received=[s for s in finished.get('broll_slots',[]) if s.get('request_id',s['id'])==cue['id']] if finished else []
            if received:
                first=received[0]
                req.update(status='RECEIVED / inserted in finished review',timeline_in=first['timeline_in'],timeline_out=first['timeline_out'],media_in=first['media_in'],received_path=first['path'],sha256=first['sha256'],selected_ranges=[{k:s[k] for k in ['timeline_in','timeline_out','media_in']} for s in received])
                start,end=req['timeline_in'],req['timeline_out']
            lines.extend([f'\n## {cue["id"]} — {filename}\n',f'- Spoken anchor: **{cue["spoken_anchor"]}**\n',f'- Source: {cue["clip"]}.MP4 at {cue["source_anchor"]:.2f}s\n',f'- Clean-edit placement: **{start:.3f}–{end:.3f}s** ({end-start:.2f}s), narration continues, B-roll muted.\n',f'- Companion element: `{cue["element"]}-v01.png`\n',f'\n{req["full_prompt"]}\n'])
            lines.append(f'\nStatus: **{req["status"]}**\n')
            if len(received)>1:
                lines.append('\nFinished insert windows: '+', '.join(f'{s["timeline_in"]:.3f}–{s["timeline_out"]:.3f}s (source {s["media_in"]:.3f}s onward)' for s in received)+'.\n')
        lines.append('\n## Element use\n\nUse the companion PNG as a short meaningful insert, separate from captions. Solo-presenter illustrations may sit behind the real subject only after shot-local person-matte review. On two-person scenes use a full-frame insert or a safe standalone card; the single-presenter matte must not select the wrong speaker. Clean MP4s contain none of these planned layers yet.\n')
        text='\n'.join(lines);(deliver/'broll-prompts.md').write_text(text);(folder/'broll-prompts.md').write_text(text);clinic.save(deliver/'planned-broll.json',requests);clinic.save(folder/'planned-broll.json',requests)
        master.append(text)
    (DELIVERY/'BROLL-PROMPTS.md').write_text('\n\n'.join(master));(BATCH/'BROLL-PROMPTS.md').write_text('\n\n'.join(master));clinic.save(BATCH/'broll-requests.json',flat)
    with (DELIVERY/'BROLL-SHOTLIST.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['reel','id','delivery_filename','spoken_anchor','clip','source_anchor','timeline_in','timeline_out','element']);writer.writeheader()
        for row in flat:writer.writerow({k:row[k] for k in writer.fieldnames})
    accounting=[]
    for r in clinic.sources():
        if not any('/Dhiraj/' in p for p in r['paths']):continue
        n=int(Path(r['filename']).stem[-4:]);uses=[{'reel':name,'source_in':s['source_in'],'source_out':s['source_out']} for name,plan in plans.items() for s in plan['segments'] if s['source_id']==r['id']]
        if uses:status='selected';reel=uses[0]['reel'];reason='Explicit selected source ranges; discarded portions remain in original'
        else:reel,reason=EXCLUDED[n];status='alternate / excluded from current cut'
        accounting.append({'filename':r['filename'],'id':r['id'],'sha256':r['sha256'],'duration':r['duration'],'reel':reel,'decision':status,'reason':reason,'selected_ranges':uses})
        dest=DELIVERY/reel/('source-links' if uses else 'alternate-source-links');dest.mkdir(exist_ok=True);link=dest/r['filename']
        if not link.exists():link.symlink_to(r['paths'][0])
    assert len(accounting)==32
    clinic.save(BATCH/'source-accounting.json',accounting)
    text='# Complete source accounting\n\n32 camera clips, all preserved. Links below point to originals; no source media was moved or deleted.\n\n| Clip | Reel | Decision | Reason |\n|---|---|---|---|\n'+''.join(f'| {r["filename"]} | {r["reel"]} | {r["decision"]} | {r["reason"]} |\n' for r in accounting)
    text+='\nSupplied script topics with no matching recording in this folder: **script 07 hair oil / hair-loss causes, script 08 pigmentation, script 09 oily skin and moisturizer**. They are preserved under the toolkit batch’s supplied-scripts folder. Output reel numbers follow this edited batch, not the original script numbering.\n\n17 JPG photos were inspected as cover/reference candidates; they are not counted as recorded reels.\n'
    (DELIVERY/'SOURCE-ACCOUNTING.md').write_text(text);(BATCH/'SOURCE-ACCOUNTING.md').write_text(text)
    index.append('\nOutput reel numbering is independent from supplied script numbering. Supplied scripts 07–09 have no matching recordings in this folder. See source accounting for all 32 clip decisions.\n\nEight AI-generated transparent object illustrations and five native typography cards are in visual-elements, with saved prompts and checksums. B-roll delivery status is recorded per reel. Reel-01 caption styling is user approved; finished exports carry their individual review notes and listening limits.\n')
    (DELIVERY/'START-HERE.md').write_text(''.join(index))
    repo_index=''.join(index)
    for name,plan in plans.items():
        video=Path(plan.get('delivery_export',plan['clean_export']))
        repo_index=repo_index.replace(f']({name}/{video.name})',f']({video})')
    for name,path in finishes.items():
        finished=json.loads((ROOT/path).read_text());video=Path(finished['finished_export'])
        repo_index=repo_index.replace(f']({name}/{video.name})',f']({video})')
    repo_index=repo_index.replace('](visual-elements/)','](../../assets/cutouts/dhiraj/)')
    (BATCH/'README.md').write_text(repo_index)
    transition_out=DELIVERY/'transition-presets';transition_out.mkdir(exist_ok=True)
    for path in (ROOT/'assets/transitions/ffmpeg-n9.0').iterdir():
        if path.is_file():shutil.copy2(path,transition_out/path.name)
    # Preserve prior human notes when filling newly ingested clip rows.
    review=ROOT/'01_catalog/review.csv'
    with review.open(newline='') as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
    byid={r['id']:r for r in accounting}
    for row in rows:
        if row['id'] not in byid:continue
        r=byid[row['id']];note='Dhiraj batch: '+r['reel']+' / '+r['reason']
        if note not in row.get('notes',''):row['notes']=(row.get('notes','')+' | '+note).strip(' |')
        for key,value in {'category':'Dhiraj shoot','topic':plans[r['reel']]['title'],'decision':r['decision']}.items():
            if not row.get(key):row[key]=value
    with review.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    print('Packaged 12 reels / 24 B-roll requests / 13 elements / 32 source decisions')

if __name__=='__main__':main()
