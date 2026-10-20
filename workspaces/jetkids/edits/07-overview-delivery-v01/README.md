# Event overview — delivery revision01

86.5 seconds,30fps;1920×1080 landscape and1080×1920 portrait. These are review exports, not user-approved masters.

Story: guest cars and greetings → student-led welcome/band/tilak → diya → ribbon → court visit and guest play → student sports → teachers → awards and original crest. Portrait uses independent native portrait ceremony angles and reviewed subject paths. No event photos or separate evening-event content.

The two user-supplied reference soundtracks are reused as supplied mixes. Entry audio is pitch-preservingly brought from approximately120 to92BPM, then hands over near the diya to the continuation mix. Source provenance and sample counts are retained. No song-name or lyric transcription is asserted.

`native-speed-audit.json` records original/master timing checks; `styles/event-cinematic.json` at workspace level stores future settings. Native100p clips retain100p in the colour masters;30fps delivery uses selected slow motion. The shot plans are authoritative for source-in, speed, crop and transition handles.

Run from repository root after activating `.cache/setup/activate.sh`:

```sh
python3 workspaces/jetkids/edits/07-overview-delivery-v01/render-recipe.py --preflight
python3 workspaces/jetkids/edits/07-overview-delivery-v01/render-recipe.py
```

Local exports live at `exports/jetkids-overview-delivery-v01/`. Render caches and supplied media stay outside Git. The renderer reuses the previous arrival-flow cache and invalidates segments by source/shot/filter signature. Do not run two recipes concurrently against that shared cache.

After this overview: fully review and transcribe daytime interviews across JKIS and mounted volumes, then create source-grounded talking-head stories with relevant B-roll. The191-entry new-root survey is sampled screening, including five existing Nikon aliases; it is not full interview analysis.
