#!/usr/bin/env bash
# Run from the repository root after tools/bootstrap.sh and restoring local raw media.
set -euo pipefail
python3 tools/assemble_atfro01.py
python3 tools/build_atfro01_timeline.py
python3 tools/prepare_atfro01_finish.py
python3 tools/build_atfro01_timeline.py
npm run check
node tools/render.mjs Reel exports/atfro-01-master-v7.mp4 --props=projects/atfro/atfro-01/reel.json --crf=16 --pixel-format=yuv420p
python3 tools/audio_finish.py exports/atfro-01-master-v7.mp4 deliverables/atfro/ATFRO_01_reedit_v7.mp4
python3 tools/export_atfro01.py
.venv/bin/python tools/build_assets.py
.venv/bin/python tools/catalog.py

.venv/bin/python tools/qa_atfro01.py deliverables/atfro/ATFRO_01_reedit_v7.mp4
