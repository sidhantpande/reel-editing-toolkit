# CLI workflow for an AI editor

## Restore

```sh
git clone https://github.com/sidhantpande/atfro-niolearn-reel-studio.git
cd atfro-niolearn-reel-studio
git lfs pull
bash tools/bootstrap.sh
python3 tools/reelctl.py doctor
```

The repository contains the original reusable asset library, transparent B-roll, sound effects, music, fonts/licences, brand marks, native animation/caption sources, dependency locks, transition tooling and reviewed edit examples. It intentionally contains no raw recordings, supplied reference reels or rendered client/final videos. The owner authorized deletion of those local files on 16 October 2026. A historical edit can only be rendered again if its original footage is supplied separately.

## Start the next reel

```sh
python3 tools/reelctl.py init --brand niolearn --id niolearn-next-topic \
  --source /absolute/path/main.mov --source /absolute/path/pickup.mov
python3 tools/reelctl.py assets --query "review" --kind transparent-video
python3 tools/reelctl.py scenes --query "interview"
```

Intake preserves original bytes in ignored `media/raw/BRAND/ID`, records hashes and source metadata, and creates an explicit planning scaffold. It refuses an existing project, duplicate source names and invalid IDs. It never invents cuts or captions.

After analysing the full sources, fill the frame cut list and corrected source words. Use `templates/ai-edit/` for the JSON structure and existing reviewed projects for real examples. Replace the planning TODO with specific source/gaze/cut/B-roll decisions.

```sh
python3 tools/reelctl.py preflight projects/niolearn/niolearn-next-topic
python3 tools/reelctl.py render projects/niolearn/niolearn-next-topic
```

Rendering assembles source frames, source-maps word captions, prepares short cut blends and an exact final-frame hold, renders, finishes audio, scans the encoded video, exports alpha scenes and rebuilds the machine-readable asset catalog. Output defaults to ignored `exports/ID-FINAL.mp4`. Source language transcription is available through Faster Whisper; draft ASR must be corrected against the recording before it becomes caption data.

Inspect encoded caption and boundary contacts plus speech, motion and alpha reports. Then record the measured result:

```sh
python3 tools/reelctl.py record projects/niolearn/niolearn-next-topic \
  --video exports/niolearn-next-topic-FINAL.mp4 \
  --visual-reviewed --dialogue-reviewed
```

The flags attest to review already performed by the editor; they are not a request for user permission and do not replace viewing/listening. The result remains ready for the user's review.

## Export one reusable animation

```sh
python3 tools/reelctl.py scene nio-study-choice --seconds 4 --transparent \
  --output exports/study-choice.webm
```

`--beats 60 110` supplies internal relative scene frames. `--labels SCENE_ID ...` supplies the ordered sub-scenes for a service story. Exporting a new asset into `public/assets/projects/PROJECT/` makes it available to later edits after `python3 tools/catalog.py` and the asset build/validation step.

`catalog/assets.json` is the checksum inventory. `catalog/motion-scenes.json` is the editable scene registry. `catalog/transitions.json` and `catalog/ffmpeg-xfade.txt` describe transition support. `catalog/ASSET_INDEX.md` is a plain text index. No dashboard/server is needed. Remotion Studio remains an optional composition preview, not the editing workflow.

## Meaningful checks

```sh
python3 -m unittest discover -s tests
npm run check
python3 tools/git_audit.py
```

Portable checks validate code, asset checksums, timeline bounds and script references without requiring old footage. Per-project preflight requires the exact footage for that render. Old batch QA/export records are historical evidence, not a promise that deleted raw/final media can be recovered from this assets-only repository.
