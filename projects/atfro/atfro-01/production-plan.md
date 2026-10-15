# ATFRO 01 — revision 5

The rejected review used an off-camera reading take and allowed artwork and duplicate B-roll titles to compete with subtitles. This revision changes the edit decisions and the motion design.

## Footage

- Keep the usable introduction, accountability, client-work and business-question delivery from 0–27 seconds, removing filler and dead pauses.
- Exclude the growth sentence at 34.5–36.77 seconds: the presenter is looking toward his screen.
- Use the camera-facing growth-partner pickup at 68.07–71.47 seconds.
- Use the later process and closing pickup, removing the corrected “real / what is” false start and the pause between “people” and “work”.
- Keep the business question on the presenter. Keep the closing welcome on the presenter; show the logo card only after dialogue finishes.

## Motion design

Two purposeful B-roll passages, both with the approved ivory paper direction. Every passage shows one large hero visual at a time. No extra headlines or category labels compete with spoken captions.

1. School communication → open book and two animated paper communication cards. Doctor-led content → isolated stethoscope and drawn ECG line. Practical software → dimensional software window and component tiles.
2. Understand → compass and scanning orbit. Build → software window and assembling components. Grow with people → handshake and expanding connected nodes.

Canvas artwork is rendered deterministically from the timeline frame. SVG and transparent cutouts retain crisp edges; objects enter with eased perspective, subtle blur and soft shadows. Animation timing comes from the edited spoken nouns. Artwork is clipped above y=1220. The spoken-caption zone starts at y=1340 on an unobstructed ivory field. The business question uses normal presenter captions.

Reusable transparent WebM exports and their props are stored under `public/assets/projects/atfro-01/`. Original generated cutouts and source geometry remain editable. No Canva video export capability is exposed by the available connector, so the video is rendered locally using Canvas, SVG and Remotion.

## Finish and verification

30 fps, 1080 × 1920 H.264/AAC. Source-mapped word timing is checked against a fresh transcription of the edited dialogue, with brand spelling corrected. Review the actual encoded video across all B-roll transitions, caption groups, the replacement take and the end card. Two-pass audio normalization targets -14 LUFS with AAC peak headroom. Source files remain unchanged; the previous review decisions are preserved in `revisions/`.

## Requested finishing changes

Soft black gradient rises from the bottom over the first 18 frames and stays feathered beneath presenter shots. B-rolls retain their clean ivory field. Very light contrast/midtone correction is specified in `colour-grade.json`. Five-frame B-roll dissolves are checked with subtitle colour switching after the ivory background becomes dominant. Caption typography is painted to Canvas with gentle upward easing and a soft shadow; this avoids intermittent missing HTML text in encoded Chrome renders. Caption bounds use integer timeline frames.

## Revision 6 — finishing refinement

Preserve the accepted recording choices and all dialogue/word timings. Add 11 short three-frame video-only cut blends; extend the two B-roll dissolves from five to eight frames. Widen captions to a centered 920 px area, increase presenter type from 65 to 75 px, opening from 75 to 84 px and B-roll from 70 to 77 px. Presenter captions start at y=1240 and flow toward the lower chest. Increase the feathered bottom black field from 1050 to 1220 px. Retain the subtle colour grade.

The original music now has a four-second equal-power overlap instead of a 32-second restart, gentle low-pass filtering and a slightly quieter constant dialogue-level mix. Smooth intro/outro envelopes prevent an end-card volume jump. Close on only the original ATFRO wordmark, centered on ivory, with a ten-frame dissolve over the last approved presenter frame.
