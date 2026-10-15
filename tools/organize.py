#!/usr/bin/env python3
"""Idempotent initial intake; moves originals without re-encoding."""
from pathlib import Path
import json,re,hashlib,shutil
R=Path(__file__).resolve().parents[1]
def move(p,d):
 d=R/d;d.parent.mkdir(parents=True,exist_ok=True)
 if p.exists() and not d.exists():p.rename(d)
move(R/'ATFRO _ Growth Partner Edition _ Complete 30-Day Content Scripts _ V2.md',Path('scripts/source/atfro-scriptbook.md'))
move(R/'NioLearn_Instagram_Scripts.docx.md',Path('scripts/source/niolearn-scriptbook.md'))
move(R/'NioLearn_Instagram_Scripts.docx',Path('scripts/source/niolearn-original.docx'))
move(R/'Minimal-Mark.png',Path('public/assets/brands/niolearn/original-mark.png'))
move(R/'OffwhiteBg.png',Path('public/assets/brands/atfro/original-wordmark.png'))
for p in list(R.glob('*.mp4')):
 if not (p.name.startswith('SaveClip') or p.stem in ['ac7a4e6616e5def4306e0468754568a9_720w','e767a28b8bc3f20d77f51ce85a760346_720w','505d87e62e77b841a0b0b52721168c31_720w']):
  move(p,Path('media/raw/unassigned')/p.name);continue
 typ='ideal-captions' if '6b25' in p.name else 'secondary-reel' if p.name.startswith('SaveClip') else 'animated-broll'
 move(p,Path('media/reference')/typ/p.name)
# Raw footage will be assigned by reviewed transcript mapping, never by appearance alone.
for p in R.glob('IMG*.mov'):move(p,Path('media/raw/unassigned')/p.name)
entries=[]
for brand in ['atfro','niolearn']:
 text=(R/f'scripts/source/{brand}-scriptbook.md').read_text()
 if brand=='atfro':
  text=text.split('# PART II')[0]
  matches=list(re.finditer(r'^## DAY (\d+) — (.+?) \| (.+)$',text,re.M))[:14]
 else:matches=list(re.finditer(r'^## \*\*(\d+) · (REEL|STATIC|CAROUSEL) · (.+?)\*\*$',text,re.M))
 for i,m in enumerate(matches):
  end=matches[i+1].start() if i+1<len(matches) else len(text)
  block=text[m.start():end]
  if brand=='atfro': fmt='REEL';title=m[3];date=m[2]
  else:
   fmt=m[2];date=m[3];title=re.search(r'\n\n\*\*(.+?)\*\*',block)[1]
  sid=f'{brand}-{int(m[1]):02d}';folder=R/f'projects/{brand}/{sid}'
  folder.mkdir(parents=True,exist_ok=True);(folder/'script.md').write_text(block.strip()+'\n')
  entry={'id':sid,'brand':brand,'format':fmt,'title':title,'script_date':date,'script':str((folder/'script.md').relative_to(R))}
  entries.append(entry)
  plan=folder/'edit-plan.json'
  if not plan.exists():plan.write_text(json.dumps({'id':sid,'brand':brand,'status':'awaiting-footage-match','sourceClips':[],'format':fmt,'captionPreset':'kinetic-white' if brand=='niolearn' else 'clean-partner','broll':[],'notes':['Source script timings are estimates. Match recorded dialogue before final captions.','Review all fact placeholders before final export.']},indent=2)+'\n')
prior=R/'catalog/scripts.json'
if prior.exists():entries.extend(e for e in json.loads(prior.read_text()) if e.get('format')=='RECORDED_REEL')
(R/'catalog/scripts.json').write_text(json.dumps(entries,indent=2,ensure_ascii=False)+'\n')
media=[]
for p in sorted((R/'media').rglob('*')):
 if p.is_file():
  h=hashlib.sha256()
  with p.open('rb') as f:
   for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
  media.append({'original_name':p.name,'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':h.hexdigest()})
(R/'catalog/media-originals.json').write_text(json.dumps(media,indent=2)+'\n')
print(f'Indexed {len(entries)} scripts and {len(media)} original videos.')
