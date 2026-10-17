#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Restore the runtime without upgrading system packages. Media/models stay local.
clinic_python="${CLINIC_PYTHON:-$(command -v python3.11 || command -v python3)}"
"$clinic_python" -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check -r requirements.lock
.venv/bin/python - <<'PY'
from pathlib import Path
import json,os,shutil
p=Path('project.json');d=json.loads(p.read_text())
for key in ('ffmpeg','ffprobe'):
 candidates=[os.environ.get(key.upper()),d.get(key),'/opt/homebrew/opt/ffmpeg-full/bin/'+key,shutil.which(key)]
 d[key]=next((s for s in candidates if s and Path(s).is_file()),None)
 if not d[key]:raise SystemExit('Install full FFmpeg first; set FFMPEG and FFPROBE if needed.')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
Path('.cache/models').mkdir(parents=True,exist_ok=True)
PY
if ! .venv/bin/python -c 'import sys;sys.path.insert(0,"tools");import clinic;assert clinic.model_path()'; then
 .venv/bin/python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download('Systran/faster-whisper-small',revision='536b0662742c02347bc0e980a01041f333bce120',cache_dir='.cache/models')
PY
fi
.venv/bin/python tools/clinic.py doctor
if [[ "${1:-}" == "--turbo" ]]; then
 .venv/bin/python tools/fetch_model.py --model turbo
fi
