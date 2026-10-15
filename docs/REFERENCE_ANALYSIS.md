# Reference analysis and editing direction

Analysed the supplied local videos with FFprobe and sampled frames. Reference media stays in `media/reference/` for private study; no permission to redistribute it is assumed.

## Ideal: SaveClip ending 6b25 (22.38 s, 720 × 1280, 30 fps)

The warm talking-head scene is the anchor. White bold sans-serif captions occupy the middle/lower chest region, with short phrases and substantial negative space. Captions change size and line placement: a large lead word sits above or beside smaller supporting words. Sampled frames around 9 s show “Then” large with “a hard light” smaller, around 13.4 s show “third”, and around 17.9 s show “3 lights”. Product detail B-roll interrupts the presenter around 4.5 s. A denser frame pass from 8.00–10.72 s confirms individual word groups blur in and out: “Then” enters blurred at 8.32 s, is sharp by 8.48 s, “a hard light” appears below/right around 8.80–9.12 s, and the outgoing leading word blurs around 9.28 s. The cut to a light stand is visible by 9.60 s.

Translate the visual grammar, not the exact artwork: short word groups, staggered entrances, quick blur-to-sharp settling, selected large keywords, restrained spring overshoot, and cuts on relevant spoken nouns. Keep faces visible. The library provides kinetic, editorial, pill and clean caption variants with explicit word timestamps. Script timing is never treated as word alignment.

The starter is a reusable interpretation of these techniques, not a frame-exact replica of the original animation. Final word timing and typography need a pass against each recording.

## Secondary reel (44.86 s)

Seated speaker, bold white compact multi-line captions, headers such as “REMOVE THE DEAD SPACE”, visual inserts, and tighter changes of scale. Useful for thought-level jump cuts, small explanatory graphics, and maintaining pace while the presenter remains the visual anchor.

## Animated B-roll

- `ac7…` (14.04 s): translucent rounded people, a softly lit dark background, foreground/background scale differences, a highlighted central person, and book icons. Reusable layers: glass person, crowd layout, icon, shadow and glow.
- `e767…` (20 s): crowd silhouettes at different depths on a white field, perspective movement and blue highlighted people. Reusable layers: person silhouettes, depth offsets, scale/blur and a selected accent subject.
- `505…` (83.03 s): monochrome editorial layouts, dotted grids, fine outline boxes, cursor, abstract business figures and briefcase/handshake metaphors. Text carries the story while objects slide and scale around it. Build original scene geometry; do not cut out or redistribute the supplied creator’s artwork.

## Brand applications

NioLearn: source scriptbook navy `#0B1320`, teal `#10B39B`, aqua `#34D1C6`, Sora headlines, Inter body. Portrait master 1080 × 1920 / 30 fps. Safe text region: x=110…940, y=250…1540. Caption defaults around y=1230 with compact groups. Original NioLearn mark preserved; place it on a light plate because a reverse logo was not supplied. Never recolour it to fake a reverse logo.

ATFRO: supplied wordmark has a lime gradient. The starter uses charcoal + lime as an inferred working palette, not an official brand book. Use clean captions and quieter motion. Preserve the original PNG. The source scripts often request documentary cuts and noun-matched B-roll; stronger transitions are options, not a default.

## Sound direction

Presenter voice leads. Use one quiet instrumental bed; duck it during dialogue. Use short whooshes at major visual reveals, light ticks for timers, and occasional low impacts. Avoid a sound for every word. Original synthesized SFX and two 32-second instrumental sketches are bundled; recorded presenter remains the final narration. `guide_voice.py` can create local scratch narration using an installed macOS voice.

## Finishing targets

1080 × 1920, 30 fps, H.264 + AAC, 48 kHz audio, Rec.709. Target approximately -14 LUFS integrated and ≤ -1 dBTP, then measure the final encode. Captions must be corrected to Roman Hinglish and checked by ear before release. Cut filler and false starts manually from the recording; automatic silence removal is not run on the originals. Puzzle thinking pauses should remain intentional.

## Motion re-study — batch revision

The user requested movement after the opening reveal. Re-sampled the supplied white crowd reference at 0.5-second intervals from 3–11 s and the editorial reference from 12–20 s. The crowd shot moves its viewpoint continuously: foreground figures cross faster than distant silhouettes, with scale/depth changes even between text beats. The editorial shot advances the explanation: cursor/check interaction becomes a large shadow/person composition, then new hands/figures replace it. Objects continue to travel while words enter. A single reveal followed by a five-second hold misses both patterns.

Apply the motion grammar to original art: a slow controlled camera push with foreground/background separation; ongoing functional motion such as a searching lens, clock hand, travelling highlight or cursor; and a new action/focus every 1–2 seconds where the speech changes. Longer inserts become several linked compositions on one ivory background. Keep captions anchored outside the art area and avoid arbitrary shaking or continuous spinning. Source contact sheets remain private in `.cache/batch/reference-motion/`.
