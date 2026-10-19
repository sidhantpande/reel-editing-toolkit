# Reusable doctor editing pipeline

Reference study: [three supplied reels](REFERENCE_STUDY_2026-10-19.md). Start at repository root. This extends the existing clinic renderer with configurable kinetic typography and true behind-person graphics. Source originals remain unchanged. New model weights, audio, masks, proxies and exports stay local.

## Restore and inspect

```sh
bash workspaces/my-dental-skin-clinic/tools/bootstrap.sh
python3 tools/pipeline.py clinic doctor
python3 tools/pipeline.py clinic intake /absolute/path/to/Reel-09
python3 tools/pipeline.py clinic analyse --source-folder /absolute/path/to/Reel-09 --proxy
python3 tools/pipeline.py clinic transcribe --source-folder /absolute/path/to/Reel-09 --model turbo --language hi
python3 tools/pipeline.py clinic assets --query tooth
```

Analysis can be limited to the current folder; missing historical recordings do not block a new job. Small accidental clips are registered but can be excluded editorially. Never use a draft transcript or silence report as automatic approval of a cut.

```sh
python3 tools/pipeline.py clinic references /absolute/ref1.mov /absolute/ref2.mp4 /absolute/ref3.mp4
```

This prepares complete contact sheets, audio, measured loudness, metadata, hashes and scene-change candidates in ignored `02_analysis/reference-study/`. Inspect phrase-animation sequences at higher temporal resolution as well. Tutorial text inside reference media is not an instruction source.

## Author the reel

Use `03_reels/<id>/brief.md` for source roles, actual dialogue, rejected takes/cues, gaze, crop, music and B-roll decisions. Store a versioned source-aware `04_timeline/v01/plan.json`. Set:

```json
{
  "style": "styles/clinic-reference-bold.json",
  "graphic_slots": [{
    "id": "G01", "path": "/absolute/assets/cutouts/molar-ivory-v01.png",
    "timeline_in": 12.0, "timeline_out": 15.0,
    "x": 570, "y": 100, "width": 460,
    "visual_reviewed": true
  }]
}
```

The snippet adds fields to the full existing segment/word plan; it is not a complete render plan. Use seconds for source/timeline times on the 30 fps grid. Words retain source IDs; phrase IDs define complete short thought groups. Optional `key`, `emphasis` and `row` fields control individual words. Set `row` on all words of a phrase when authoring an explicit stacked layout. The old approved style remains the default for historical plans. Gold editorial Latin keywords are available through `styles/clinic-reference-editorial.json`.

Transparent graphics must have actual nonempty alpha and have been visually inspected. Behind-subject slots must stay within a single shot (split at cuts to reset the matte) and cannot overlap full-frame B-roll; preflight prevents a graphic from silently disappearing under another layer. Keep illustrations out of caption and logo regions. Generate a new relevant asset or request one; do not insert an unrelated asset merely because it exists.

For video B-roll, write one or two prompts with exact spoken anchors, source/timeline ranges, delivery names, durations, camera/motion instructions and forbidden elements. Inspect returned footage before registration/use. Do not add patient outcomes, new clinical claims or generated lookalike patients. Keep all B-roll audio muted while narration continues.

## Render

```sh
python3 tools/pipeline.py clinic preflight /absolute/plan.json --aroll-only
python3 tools/pipeline.py clinic render /absolute/plan.json --aroll-only
# After requested B-roll has arrived and the art has been checked:
python3 tools/pipeline.py clinic preflight /absolute/plan.json
python3 tools/pipeline.py clinic render /absolute/plan.json
```

`--aroll-only` explicitly omits both B-roll and behind-subject graphics and creates a preview. Full rendering first assembles exact picture/dialogue, makes short clip-local masks for graphic slots, composites the supplied PNG behind the real speaker, then applies captions and brand finishing. It does not generate a new face or voice. Use the separate proof plan to inspect graphics before video B-roll arrives.

```sh
python3 tools/pipeline.py clinic matte /absolute/1080x1920-30fps-clip.mp4 \
  --work /absolute/local-mask-folder \
  --art /absolute/tooth.png --output /absolute/occlusion-proof.mp4 \
  --x 570 --y 100 --width 460
```

The matte tool uses the Mac's Vision framework (`xcrun swiftc` required), accurate quality, consecutive 540×960 masks and full-resolution compositing. Review rather than assume perfect hair edges. Reset at each shot. The original person pixels are restored over the graphic. Lossless FFV1 masks are cached with implementation/input signatures; incomplete sequences are rejected. Graphics have restrained vertical easing and opacity entrance. Use the CLI on portrait 1080×1920/30 fps clip-local inputs.

## Acceptance and maintenance

Inspect the encoded export: every caption phrase including Devanagari shaping, every cut and B-roll boundary, complete speech and final signature, face/hand edges during all occlusion frames, logo and platform margins. Full-decode the MP4; measure video frame count, audio duration, integrated loudness and peak. Preserve a QA report with actual review status and unresolved pronunciation/timing issues. Human listening is separate from ASR agreement. Never promote a draft as final because a render finished.

```sh
python3 tools/pipeline.py clinic qa /absolute/plan.json /absolute/review.mp4 \
  --out /absolute/local-qa-folder --ending
```

Use `--ending` only for an export containing the supplied 127-frame clinic end-card/signature extension. The command checks full decode, actual output frames, dimensions, audio/video duration, loudness and black intervals, and prepares contact sheets at the rendered phrase windows and every cut. These measured reports do not automatically mark subjective review complete.

```sh
python3 -m unittest discover -s tests
npm run check
python3 tools/catalog.py
python3 tools/git_audit.py
```

Reusable illustrations live in `assets/cutouts/` with prompts/checksums and Git LFS. Camera/reference/final media, frames, models and environments remain ignored. Approved historical B-roll remains in its existing manifest. This request does not authorise deleting originals or old exports.


## Varied assets and single-presenter masks — Reel-09 received-media revision

Use a different visual only when the spoken concept changes. Reel-09 v03 uses the supplied arch and attention-ring videos, a complete arch behind the tooth-role line, a magnifier behind the small-problem line, and exact dimensional 32 typography for the reminder. The earlier isolated molar PNG is not used in the active edit. Retain plans/prompts and old exports for history rather than overwriting them.

Vision may assign weak alpha to a background balloon. The single-presenter cleanup keeps the largest solid connected person core after a small opening and retains a three-mask-pixel soft-edge margin. It is intended for one doctor in frame; multi-person scenes need an explicit subject-selection workflow. Inspect every graphic's head/hair edge and motion after cleanup. The encoded Reel-09 v03 was checked with 50 six-fps upper-frame samples; numerical coverage was audited for all 249 masks.

Use `tools/build_clinic_typography.py 32 assets/cutouts/NEW-VERSION.png` for exact native typographic assets. Generated imagery still uses built-in imagegen and the cutout manifest retains the complete prompts. Returned B-roll is copied unchanged to the approved asset folder, checked by SHA-256 and registered in the existing manifest. Its audio is discarded by the renderer.
