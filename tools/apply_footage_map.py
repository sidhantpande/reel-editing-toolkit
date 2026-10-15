#!/usr/bin/env python3
"""Apply the reviewed content-level mapping; camera originals retain names and bytes."""
from pathlib import Path
import json,shutil
R=Path(__file__).resolve().parents[1]
# ID, file stem, role, confidence, content evidence and editorial caution.
rows=[
('niolearn-04','IMG_5941','main','high','Fee before paying; five parent questions: recognition, credential, fees, outcomes, students.','Longer than estimated script. Preserve all five points; tighten naturally.'),
('niolearn-07','IMG_5947','main','high','Diagnostic, focused preparation, mocks/review, interview preparation; NioLearn system.','ASR misspells brand; use approved NioLearn spelling.'),
('niolearn-09','IMG_5952','main','high','Three entrance mistakes: attempting everything, formula-only study, mocks without analysis.','Recorded dialogue differs from the exact script; caption the take.'),
('niolearn-12','IMG_5956','main','high','Three better intro openers: problem, project, curiosity.','Version B openers, not the longer My name is interview scene.'),
('niolearn-15','IMG_5960','main','high','Marks do not guarantee selection; problem-solving, communication, projects and curiosity.','Selection criteria are contextual; keep the spoken verify-each-college qualification.'),
('niolearn-16','IMG_5961','part-1','high','Mock mistakes: tough questions, missing NOT/EXCEPT, time on easy questions; stops at fourth item.','Continues in IMG_5962. Do not treat as a complete reel.'),
('niolearn-16','IMG_5962','part-2','high','Blind guessing, elimination method, closing CTA.','Continuation of IMG_5961. Match the fourth-item lead-in at the cut.'),
('niolearn-19','IMG_5963','main','high','Weak app answer lists login/database/buttons; better problem, approach, decision, outcome; school register example.','Same broad theme also appears in script 46; this take matches script 19 scene details.'),
('niolearn-11','IMG_5965','false-start','medium','Short aborted My name opening immediately preceding complete interview intro take.','Probable pickup/false start based on opening and adjacent take. Keep for audit; use IMG_5966 as main.'),
('niolearn-11','IMG_5966','main','high','My name, Pune, 87 percent; resume-reading critique; proof, school choice and next goal.','Recorded formula is phrased differently from the written four-step structure.'),
('niolearn-20','IMG_5967','main','high','Brochures look alike; compare recognition, total fee, selection, curriculum, mentors/exposure and outcomes.','Review end against replacement CTA in IMG_5971.'),
('niolearn-20','IMG_5971','cta-pickup','high','Comment SHEET for college comparison cheat sheet; NioLearn CTA.','Replacement ending for IMG_5967, not a separate reel.'),
('niolearn-recorded-brand-intro','IMG_5974','part-1','high','What if JEE were not your only option; new generation tech colleges and different entrance routes.','Recorded English brand introduction, outside this calendar scriptbook.'),
('niolearn-recorded-brand-intro','IMG_5976','part-2','high','That is exactly why we started NioLearn; discover, understand and prepare for opportunities.','Short bridge after IMG_5974 and before IMG_5978.'),
('niolearn-recorded-brand-intro','IMG_5978','part-3','high','Modern tech admissions platform; live classes, mocks, interviews, feedback, mentorship; Navigate More Possibilities.','Complete the introduction with the three ordered parts; verify product claims before publication.'),
('niolearn-recorded-early-access','IMG_5980','part-1','high','Planning for new generation tech colleges; structured live classes, mentorship, personalized interviews.','Recorded English promotional opener, not an exact calendar-script match.'),
('niolearn-recorded-early-access','IMG_5987','part-2','high','Early access and waitlist by October 22; website CTA.','Time-sensitive October 22 claim. Confirm intended year, offer and live waitlist before editing a release.'),
('niolearn-recorded-admissions','IMG_5990','main','high','First cohort targeting 2027 admissions; live classes, mentorship, mocks and guidance; registration CTA.','Contains repeated Don’t wait line around 26–35 s. Confirm admissions-open/cohort claims.'),
('atfro-04','IMG_5995','main','high','School event reel vs the story parents need; culture, values, growth partner, one learning story.','CTA wording stumbles; compare replacement CTA in IMG_5996.'),
('atfro-04','IMG_5996','cta-pickup','high','If you lead a school, DM SCHOOL with one communication bottleneck.','Replacement ending for IMG_5995.'),
('atfro-01','IMG_5999','false-start','high','Three months of silence from ATFRO; relaunch opening; stops on strategy/skill wording.','Opening false start. Use IMG_6001 as the main source.'),
('atfro-01','IMG_6001','main-with-pickups','high','ATFRO silence, client work, schools/doctor content/software, growth partner, return to sharing work.','90.48 s contains repeated sentences and pauses. Approx candidate main 0–27 s plus later 67–88 s ending; these are draft review ranges, not applied edits.'),
]
extras={
'niolearn-recorded-brand-intro':('Brand introduction — more pathways beyond one exam','''# Recorded NioLearn brand introduction\n\nReconstructed editorial outline from recorded English dialogue; not a verbatim approved transcript.\n\n1. IMG_5974: “What if JEE wasn’t your only option?” Introduce the different examination and interview routes at new generation technology colleges.\n2. IMG_5976: Explain why NioLearn was started: help students discover, understand and prepare for these opportunities.\n3. IMG_5978: Describe the recorded offer — structured live classes, mocks, interviews, feedback and mentorship — and close with “One exam shouldn’t define your future. NioLearn. Navigate More Possibilities.”\n\nUse pathway motion and a short comparison graphic, then return to the presenter. Verify current service availability. No invented college/exam facts or metrics. Caption the actual English recording after manual review.\n'''),
'niolearn-recorded-early-access':('Early access / waitlist promo','''# Recorded NioLearn early-access promo\n\nReconstructed editorial outline from recorded English dialogue; not a verbatim approved transcript.\n\n1. IMG_5980: Planning for a new generation tech college? Explain that multiple examinations and interviews can be confusing; position the recorded preparation offer.\n2. IMG_5987: Early-access CTA refers to a waitlist deadline of October 22.\n\nCheck the intended year, actual deadline, early-access offer and URL before final copy or release. Do not silently update a spoken date. If it is no longer valid, omit the dated pickup and record a current CTA. Motion: live-class, mentor, interview cards; one end card.\n'''),
'niolearn-recorded-admissions':('First cohort / 2027 admissions announcement','''# Recorded NioLearn admissions announcement\n\nReconstructed editorial outline from recorded English dialogue; not a verbatim approved transcript.\n\nIMG_5990: Open with students planning for the 2027 admissions cycle. Announce the first cohort, outline live classes, mentorship, mocks/interviews and guidance, and end with website registration.\n\nThe take contains a repeated “Don’t wait” thought around 26–35 seconds. Choose the clean delivery during editing. Confirm cohort availability, admissions-open status, eligibility and live website before using the claims. Motion: preparation cards, calendar, subtle CTA reveal. No invented deadline or results.\n''')}
index=json.loads((R/'catalog/scripts.json').read_text())
for sid,(title,body) in extras.items():
 folder=R/'projects/niolearn'/sid;folder.mkdir(parents=True,exist_ok=True);(folder/'script.md').write_text(body)
 if not any(s['id']==sid for s in index):index.append({'id':sid,'brand':'niolearn','format':'RECORDED_REEL','title':title,'script_date':'Unscheduled recorded extra','script':str((folder/'script.md').relative_to(R)),'source':'Reconstructed editorial outline from recordings; requires dialogue review'})
 p=folder/'edit-plan.json'
 if not p.exists():p.write_text(json.dumps({'id':sid,'brand':'niolearn','status':'mapped-recorded-extra','sourceClips':[],'format':'RECORDED_REEL','captionPreset':'kinetic-white','broll':[],'notes':[]},indent=2)+'\n')
(R/'catalog/scripts.json').write_text(json.dumps(index,indent=2,ensure_ascii=False)+'\n')
mapped=[]
for sid,stem,role,confidence,evidence,note in rows:
 brand=sid.split('-')[0];target=R/f'media/raw/{brand}/{sid}/{stem}.mov';target.parent.mkdir(parents=True,exist_ok=True)
 candidates=list((R/'media/raw').rglob(stem+'.mov'))
 if len(candidates)!=1:raise RuntimeError(f'Expected one original: {stem}: {candidates}')
 if candidates[0]!=target:candidates[0].rename(target)
 mapped.append({'project':sid,'brand':brand,'file':stem+'.mov','path':str(target.relative_to(R)),'role':role,'confidence':confidence,'evidence':evidence,'edit_note':note,'asr_draft':f'.cache/transcripts-en/{stem}.json'})
for sid in sorted({r['project'] for r in mapped}):
 folder=R/'projects'/sid.split('-')[0]/sid;p=folder/'edit-plan.json';plan=json.loads(p.read_text());clips=[r for r in mapped if r['project']==sid]
 plan.update({'status':'mapped-awaiting-edit','sourceClips':[r['path'] for r in clips],'takes':clips,'notes':list(dict.fromkeys(plan.get('notes',[])+[r['edit_note'] for r in clips]))})
 if sid.startswith('niolearn-recorded'):plan['captionLanguage']='English recording; review exact words'
 (folder/'edit-plan.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n')
 # Preserve machine drafts beside the project for future offline matching, labelled explicitly.
 draftdir=folder/'transcripts-draft';draftdir.mkdir(exist_ok=True)
 for row in clips:
  for ext in ['json','txt']:
   src=R/'.cache/transcripts-en'/Path(row['file']).with_suffix('.'+ext).name
   if src.exists():shutil.copy2(src,draftdir/src.name)
(R/'catalog/footage-map.json').write_text(json.dumps(mapped,indent=2,ensure_ascii=False)+'\n')
media=json.loads((R/'catalog/media-originals.json').read_text())
for m in media:
 for row in mapped:
  if m['original_name']==row['file']:m['path']=row['path']
(R/'catalog/media-originals.json').write_text(json.dumps(media,indent=2)+'\n')
lines=['# Footage map','', '22 camera originals: 18 NioLearn and 4 ATFRO. Content-level matches were checked against both scriptbooks using draft local ASR. Drafts paraphrase/misspell some words; they are not final captions. One 3.33 s false start has a medium-confidence association.','', '| Project | File | Role | Confidence | Editing note |','|---|---|---|---|---|']
for row in mapped:lines.append(f"| {row['project']} | {row['file']} | {row['role']} | {row['confidence']} | {row['edit_note']} |")
lines+=['','All original names and bytes are preserved. Source scripts without matching recordings remain `awaiting-footage-match`; footage has not been invented for them. Three English NioLearn recorded projects are stored separately because they are not exact calendar-script matches.','', 'Reel folders contain source scripts, edit plans and labelled draft transcripts. Original reference videos remain local in `media/reference/`; original reusable B-roll is in `public/assets/broll/`.']
(R/'catalog/FOOTAGE_MAP.md').write_text('\n'.join(lines)+'\n')
print(f'Mapped {len(mapped)} clips to {len(set(r["project"] for r in mapped))} reel projects. All originals preserved.')
