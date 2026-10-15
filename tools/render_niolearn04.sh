#!/usr/bin/env bash
set -euo pipefail
# First recorded NioLearn reel (calendar item 04), using the approved editing pattern.
.venv/bin/python tools/assemble_reel.py projects/niolearn/niolearn-04
python3 tools/build_niolearn04_timeline.py
python3 tools/prepare_reel_finish.py projects/niolearn/niolearn-04
python3 tools/build_niolearn04_timeline.py
npm run check
node tools/render.mjs Reel exports/niolearn-first-master-v2.mp4 --props=projects/niolearn/niolearn-04/reel.json --crf=16 --pixel-format=yuv420p
python3 tools/audio_finish.py exports/niolearn-first-master-v2.mp4 deliverables/niolearn/NIOLEARN_01_Parent_Questions_v2.mp4
python3 tools/export_niolearn04.py
.venv/bin/python tools/build_assets.py
.venv/bin/python tools/catalog.py
.venv/bin/python tools/qa_reel.py projects/niolearn/niolearn-04 deliverables/niolearn/NIOLEARN_01_Parent_Questions_v2.mp4 --output=.cache/analysis/niolearn-first/final-qa
