#!/usr/bin/env bash
set -euo pipefail
# Second recorded NioLearn reel: calendar 07, the preparation system.
.venv/bin/python tools/assemble_reel.py projects/niolearn/niolearn-07
python3 tools/build_niolearn07_timeline.py
python3 tools/prepare_reel_finish.py projects/niolearn/niolearn-07
python3 tools/build_niolearn07_timeline.py
npm run check
node tools/render.mjs Reel exports/niolearn-second-master-v1.mp4 --props=projects/niolearn/niolearn-07/reel.json --crf=16 --pixel-format=yuv420p
python3 tools/audio_finish.py exports/niolearn-second-master-v1.mp4 deliverables/niolearn/NIOLEARN_02_Preparation_System_v1.mp4
python3 tools/export_niolearn07.py
.venv/bin/python tools/build_assets.py
.venv/bin/python tools/catalog.py
.venv/bin/python tools/qa_reel.py projects/niolearn/niolearn-07 deliverables/niolearn/NIOLEARN_02_Preparation_System_v1.mp4 --output=.cache/analysis/niolearn-second/final-qa

.venv/bin/python tools/inspect_reel_finish.py projects/niolearn/niolearn-07 deliverables/niolearn/NIOLEARN_02_Preparation_System_v1.mp4 --output=.cache/analysis/niolearn-second/final-finish
