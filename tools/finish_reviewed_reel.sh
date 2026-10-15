#!/usr/bin/env bash
set -euo pipefail
project="$1"
output="$2"
reel_id="$(basename "$project")"
python3 tools/audio_finish.py "exports/${reel_id}-master-v1.mp4" "$output"
.venv/bin/python tools/qa_reel.py "$project" "$output" "--output=.cache/batch/${reel_id}/captions"
.venv/bin/python tools/inspect_reel_finish.py "$project" "$output" "--output=.cache/batch/${reel_id}/finish"
.venv/bin/python tools/scan_reel_frames.py "$project" "$output" "--output=.cache/batch/${reel_id}/tile-scan"
.venv/bin/python tools/inspect_motion.py "$project" "$output" "--output=${project}/analysis"
.venv/bin/python tools/export_reviewed_assets.py "$project"
.venv/bin/python tools/audit_alpha_assets.py "public/assets/projects/${reel_id}" "--output=${project}/analysis/alpha-all-frames.json"
.venv/bin/python tools/build_assets.py
.venv/bin/python tools/catalog.py
npm run check
