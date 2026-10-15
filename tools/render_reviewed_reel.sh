#!/usr/bin/env bash
set -euo pipefail
project="$1"
output="$2"
reel_id="$(basename "$project")"
.venv/bin/python tools/assemble_reel.py "$project"
python3 tools/build_reviewed_timeline.py "$project"
python3 tools/prepare_reel_finish.py "$project"
python3 tools/build_reviewed_timeline.py "$project"
npm run typecheck
node tools/render.mjs Reel "exports/${reel_id}-master-v1.mp4" "--props=${project}/reel.json" --crf=16 --pixel-format=yuv420p
bash tools/finish_reviewed_reel.sh "$project" "$output"
