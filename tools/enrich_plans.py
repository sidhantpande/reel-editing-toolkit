#!/usr/bin/env python3
"""Store editorial planning, without inventing frame-accurate cues."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
briefs={
'niolearn-04':(['5 questions','Degree / recognition','Credential','Total fees','Outcomes','Talk to students'],[('On each numbered question','compare'),('On outcomes data','timeline')],'Keep a calm pace. One short card per question; do not show fictional university credentials.'),
'niolearn-07':(['One preparation system','Diagnostic','Focused prep','Mocks + review','Interview'],[('When the sequence of preparation steps starts','pathways')],'Extend the paths to four steps in source code when needed; the supplied three-path scene is a reusable starting point, not the final four-step diagram.'),
'niolearn-09':(['Choose questions','Understand the logic','Review every mock'],[('When all questions are treated equally','timeline'),('When reasoning is contrasted with formulas','compare')],'Use one selected keyword per beat; maintain spoken Hinglish.'),
'niolearn-11':(['Weak intro','Show proof','Why this school','Next goal'],[('When the resume-style answer becomes a stronger structure','compare')],'Use IMG_5966 as main. Keep IMG_5965 as an archived false start.'),
'niolearn-12':(['Problem','Project','Curiosity'],[('As each opener is demonstrated','pathways')],'Three simple text cards are enough. Do not confuse with the longer script 11.'),
'niolearn-15':(['Beyond marks','Problem solving','Communication','Projects + curiosity'],[('When the three qualities are listed','pathways'),('At the idea of an individual profile','crowd')],'Keep the caveat that every college weighs criteria differently. No invented scoring weights.'),
'niolearn-16':(['Question choice','Read carefully','Time leaks','Blind guessing'],[('On time being lost','countdown'),('On elimination versus blind guessing','compare')],'Join IMG_5961 then IMG_5962. Set the actual timer duration to the spoken context, not a default 5-second countdown.'),
'niolearn-19':(['Problem','Approach','Decision','Outcome'],[('When weak and stronger answers are contrasted','compare'),('On a more efficient school workflow','lead-flow')],'Any app demo is illustrative. Avoid presenting the example timing as a verified student outcome.'),
'niolearn-20':(['Recognition','Total cost','Selection','Curriculum','Mentors','Outcomes'],[('When comparison criteria are introduced','compare')],'Use a structured checklist. Include IMG_5971 only as a replacement CTA, not a second closing.'),
'niolearn-recorded-brand-intro':(['Beyond one exam','Discover opportunities','Understand pathways','Prepare with confidence'],[('When multiple pathways are mentioned','pathways'),('When students’ individual futures are discussed','crowd')],'Three recorded parts in order. Keep English captions for this English recording.'),
'niolearn-recorded-early-access':(['Different entrances','One preparation system','Early access'],[('When different preparation routes are described','pathways')],'Two parts in order. Confirm the October 22 offer/date before creating final CTA typography.'),
'niolearn-recorded-admissions':(['2027 pathways','First cohort','Live classes + mentorship','Register'],[('When services are listed','pathways')],'Resolve the repeated line around 26–35 s, verify the cohort offer, and keep English captions.'),
'atfro-01':(['Why we went quiet','Client work','A growth partner','We are back'],[('When school, doctor content and systems are mentioned','lead-flow')],'Stay on the founder for the hook. Prefer actual approved work footage over generic graphics. Review the late pickup ending in IMG_6001.'),
'atfro-04':(['Parents need a story','Learning + values','One clear goal','DM SCHOOL'],[('When an event dump is contrasted with a learning story','timeline'),('At the difference between a clip stack and a purposeful story','compare')],'Use restrained comparisons. Never insert stock identifiable students. IMG_5996 is the replacement CTA.')}
for p in sorted((R/'projects').glob('*/*/edit-plan.json')):
 plan=json.loads(p.read_text());sid=plan['id'];brand=plan['brand']
 if sid not in briefs:continue
 beats,cues,note=briefs[sid];plan['captionBeats']=beats;plan['suggestedBroll']=[{'spokenAnchor':anchor,'composition':'Broll-'+kind,'asset':f'public/assets/broll/{brand}-{kind}.webm','timingStatus':'Resolve against edited recording; no frame cue assigned'} for anchor,kind in cues];plan['soundDirection']={'music':'calm-focus' if brand=='niolearn' else 'soft-momentum','voicePriority':True,'sfx':['soft-whoosh at a major graphic reveal','soft-tick only for a real timer'],'avoid':'A sound effect on every caption word'};plan['creativeNote']=note
 p.write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n')
 lines=[f'# {sid} — edit brief','',note,'','## Caption beats','']+[f'- {b}' for b in beats]+['','## Suggested graphic cues','']+[f'- {anchor}: `{kind}`; reusable alpha file `public/assets/broll/{brand}-{kind}.webm`.' for anchor,kind in cues]+['','These cues are planning suggestions. Set timings after dialogue cuts; keep the actual scripted counts and labels. Pre-rendered graphics are starter examples and can be re-labelled in `src/Broll.tsx`.','', 'Keep speech clear, bed quiet and graphic sounds sparse. See the edit-plan JSON for clip roles, review notes and available takes.']
 (p.parent/'edit-brief.md').write_text('\n'.join(lines)+'\n')
print('Added 14 per-reel edit briefs with spoken anchors, caption beats and reusable B-roll suggestions.')
