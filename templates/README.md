# Reusable templates

The active premium direction is `src/premium/PaperScene.tsx`: off-white paper scenes, original dimensional cutouts, restrained teal/navy typography and staged motion. See `docs/PREMIUM_STYLE.md`. Dark chrome explorations were rejected and are not default templates.

- `src/Captions.tsx`: kinetic white, clean partner, active pill, editorial size contrast. Reuse by supplying reviewed, explicit word timings.
- `src/Broll.tsx`: crowd depth, three preparation paths, connected lead workflow, 30-to-3 timeline, common-base comparison, 5-second timer. Both brand palettes; optional transparent background.
- `src/Reel.tsx`: source clip sequences, independent B-roll, captions, quiet music with A-roll ducking, timed SFX and 2-second end card.
- `src/Transitions.tsx`: six common previews; the installed transition package and FFmpeg make additional transitions available, listed in `catalog/transitions.json`.
- Each `projects/BRAND/ID/` stores its source script, edit plan and, when matched, footage mapping. The starter does not pretend source script timings equal the actual recorded take.

Render a transparent scene:

```sh
node tools/render.mjs Broll-pathways public/assets/broll/custom-pathways.webm --codec=vp9 --pixel-format=yuva420p --image-format=png
```

Render a project after preparing its props:

```sh
node tools/render.mjs Reel exports/my-reel-review.mp4 --props=projects/BRAND/ID/reel.json
python3 tools/audio_finish.py exports/my-reel-review.mp4 exports/my-reel-final.mp4
```

For editors that cannot reliably read WebM alpha, render ProRes 4444 MOV locally with `--codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png`. These exports can be large; keep them in `exports/` unless deliberately adding an approved reusable asset via LFS.
