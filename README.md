# ATFRO × NioLearn — AI editing kit

Reusable, filesystem-first editing environment for an AI agent. Start with [AGENTS.md](AGENTS.md) and [the CLI workflow](docs/AI_WORKFLOW.md). No dashboard/server is needed.

```sh
git lfs pull
bash tools/bootstrap.sh
python3 tools/reelctl.py doctor
python3 tools/reelctl.py assets --query "clock"
python3 tools/reelctl.py scenes --query "interview"
```

The kit contains 156 checksum-indexed assets, 42 native motion scene kinds, transparent B-roll clips, original music/SFX, fonts/licences, logos, caption/transition code, dependency locks and reviewed edit decisions. See [the asset index](catalog/ASSET_INDEX.md), [approved style](docs/PREMIUM_STYLE.md) and [reference analysis](docs/REFERENCE_ANALYSIS.md).

```sh
python3 tools/reelctl.py init --brand niolearn --id niolearn-next-topic --source /absolute/main.mov
# Analyse the complete source, then fill the reviewed cut/word/editorial JSON.
python3 tools/reelctl.py preflight projects/niolearn/niolearn-next-topic
python3 tools/reelctl.py render projects/niolearn/niolearn-next-topic
```

[Templates](templates/ai-edit/) document the edit contract. Historical `projects/` retain real reviewed cuts, source word timings, scripts, provenance and QA for reuse. New recordings must be supplied each time. Raw recordings, supplied reference videos and all rendered final/client videos are excluded from Git and were authorized for local removal by the owner on 16 October 2026. Historical export/footage indexes describe the earlier batch, not files included in this repository.

```sh
npm test
npm run check
python3 tools/git_audit.py
```

Portable checks run without old camera files. `npm run check:media` additionally requires every historical source recording. Rendering a specific project always checks that project's source media. Remotion Studio is an optional composition preview via `npm run studio`.

Current reliable renderer: 1080×1920 / 30 fps, serial PNG capture, software GL and separate encoding. Preserve these settings unless encoded frames have been verified after a change. The runtime, model caches and virtual environments install locally; they are restored from version locks rather than stored in Git.

Repository: private [sidhantpande/atfro-niolearn-reel-studio](https://github.com/sidhantpande/atfro-niolearn-reel-studio). Binary original assets use Git LFS. Third-party code/fonts retain attribution and licences; Remotion use is subject to its [included licence](docs/licenses/Remotion-LICENSE.md).
