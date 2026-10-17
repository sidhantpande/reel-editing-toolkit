#!/usr/bin/env python3
"""Restore pinned local ASR data without adding model weights to Git."""
import os
os.environ.setdefault('HF_HUB_DISABLE_XET','1')
import argparse,hashlib,json
from pathlib import Path
from huggingface_hub import snapshot_download
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--model',choices=['small','turbo'],default='small');a=p.parse_args()
repo,revision=('Systran/faster-whisper-small','536b0662742c02347bc0e980a01041f333bce120') if a.model=='small' else ('dropbox-dash/faster-whisper-large-v3-turbo','0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf')
folder=snapshot_download(repo,revision=revision,cache_dir=str(ROOT/'.cache/models'),allow_patterns=['model.bin','config.json','tokenizer.json','preprocessor_config.json','vocabulary.json'])
with (Path(folder)/'model.bin').open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
if a.model=='turbo' and digest!='e76620f83d5f5b69efd3d87e3dc180c1bd21df9fbebacfd4335e5e1efcc018da':raise RuntimeError('Model checksum mismatch')
print(json.dumps({'model':a.model,'repo':repo,'revision':revision,'path':folder,'sha256':digest},indent=2))
