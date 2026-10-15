#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v ffmpeg >/dev/null || ! command -v python3 >/dev/null; then
 if command -v brew >/dev/null; then brew bundle --file=Brewfile; else echo 'Install FFmpeg and Python 3.11+ first.'; exit 1; fi
fi
command -v node >/dev/null || { echo 'Install Node (version in .nvmrc), then rerun.'; exit 1; }
node -e 'if(Number(process.versions.node.split(".")[0])<22)process.exit(1)' || { echo 'Node 22+ required'; exit 1; }
if command -v brew >/dev/null && ! git lfs version >/dev/null 2>&1; then HOMEBREW_NO_AUTO_UPDATE=1 brew install git-lfs; fi
if git rev-parse --git-dir >/dev/null 2>&1 && git lfs version >/dev/null 2>&1; then git lfs install --local; fi
npm ci --no-fund
python3 -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check -r requirements.lock
.venv/bin/python tools/build_assets.py
.venv/bin/python tools/catalog.py
.venv/bin/python tools/link_media.py
# Renderer uses installed Chrome with serial software capture on this Mac.
# Download the compatible headless runtime only when no desktop Chrome is present.
if [ ! -x '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' ]; then npx remotion browser ensure; fi
.venv/bin/python tools/doctor.py
printf '\nReady: python3 tools/reelctl.py assets --query clock\nAI workflow: docs/AI_WORKFLOW.md\nRaw/final client media is excluded; supply new recordings with reelctl init.\n'
