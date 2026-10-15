#!/usr/bin/env python3
"""Rebuild prepared recorded reels in order; visual QA remains explicit per finished export."""
from pathlib import Path
import argparse,json,subprocess
R=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('--from-id');ap.add_argument('--only',nargs='*');ap.add_argument('--include-completed',action='store_true');a=ap.parse_args();queue=json.loads((R/'projects/batch-queue.json').read_text());started=not a.from_id
for item in queue['reels']:
 if item['id']==a.from_id:started=True
 if not started or (a.only and item['id'] not in a.only):continue
 if item['status']=='approved' or item['status']=='completed' and not a.include_completed:continue
 if not item.get('output'):continue
 P=R/item['project'];needed=['cut-list.json','source-words.json','editorial.json','colour-grade.json','production-plan.md','assets-provenance.json']
 missing=[n for n in needed if not(P/n).is_file()]
 if missing:raise RuntimeError(f'{item["id"]}: still needs editorial preparation: {missing}')
 print('Rendering',item['id'],'→',item['output'],flush=True)
 subprocess.run(['bash','tools/render_reviewed_reel.sh',item['project'],item['output']],cwd=R,check=True)
 print('Encoded checks complete; inspect contacts, dialogue and motion before recording finished:',item['id'],flush=True)
