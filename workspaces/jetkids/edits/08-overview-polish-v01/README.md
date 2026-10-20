# Overview polish01

86.5s,30fps, landscape1920×1080 and full-bleed portrait1080×1920. User considered delivery07 much better; this revision preserves that story and slow-video treatment, restores original-speed music and refines timing. No approval of this output is implied.

Greeting-to-car transition midpoint is on7.52s. Blend midpoints and hard cuts follow the mapped source beat estimates. Ribbon release41.78s and student bat contact58.74s are independently anchored. See `beat-edit-map.json`.

Both tracks play at100% native speed/pitch. An8s entry phrase repeats once to preserve visual duration; source ranges and amplitude/percussion handover are documented in `audio-mix.json`. Only continuation after the join. No atempo or time stretching. `mix-native-audio.py` uses the primary bootstrapped Python environment.

Run from repository root:

```sh
source .cache/setup/activate.sh
python3 workspaces/jetkids/edits/08-overview-polish-v01/mix-native-audio.py
python3 workspaces/jetkids/edits/08-overview-polish-v01/render-recipe.py
```

Outputs: `exports/jetkids-overview-polish-v01/`. Independent render cache: `.cache/jetkids/overview-polish-v01/`. Raw/reference/PCM/export/cache media stay local. Future settings: workspace `styles/event-cinematic.json`. Full interview-led work remains the next commissioned phase.
