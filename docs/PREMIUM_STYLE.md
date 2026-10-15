# Active art direction — light editorial, v3

User preference: the white editorial scenes work; NioLearn's dark chrome/glass scenes were rejected. Active NioLearn and ATFRO showcase compositions are therefore fully light. Rejected dark explorations are retained locally in Git-ignored `design-explorations/`, not mixed into the default asset library.

## Active scenes

- `Premium-paper-possibilities`: student, book and compass, a fine teal path and a bold curved paper line. Staged entries connect the individual to more than one option.
- `Premium-paper-pathways`: diagonal composition with compass → book → student. Three independently timed objects and editable labels; no glass dashboard cards.
- `Premium-paper-crowd`: layered people at three depths, low-contrast background, one clear foreground subject, a drawn selection ring and soft contact shadows.
- `Premium-paper-partnership`: monochrome handshake in the foreground, people and dotted guide field behind, oversized cropped paper stars, a narrow typographic callout.

`PremiumNiolearnV3` and `PremiumAtfroV3` are 23-second showcases, with 6-second scenes overlapping by 10 frames. Sources are in `src/premium/PaperScene.tsx` and `PaperShowcase.tsx`.

NioLearn uses off-white `#F2F3EF`, navy `#0B1320`, a small teal `#10A995` accent, Sora headings and Inter labels. ATFRO retains the paper/ink direction with a restrained lime accent. Large clean typography, genuine negative space and timed visual metaphors take priority over decorative UI, saturated gradients or a sound on every word.

All scene movement is calculated from video frames: blur-to-sharp type entrances, object settling, drawing paths, slight parallax and a restrained camera push. Frame timing and labels remain editable. The original reference artwork was not cut out or redistributed.

## Reusable assets

Original generated transparent cutouts are bundled under `public/assets/premium/cutouts/`: paper student, editorial business figure, handshake, open book and compass. The generated files are copied into this workspace; setup never calls ImageGen to recreate them. Prompt specifications and generation provenance are stored in `PREMIUM_ASSET_PROMPTS.json`.

Use `tools/export_premium.py` to render the four scenes for both brands as full-resolution transparent WebM layers. These live in `public/assets/broll/*-premium-paper-*-v3.webm`. The scene backgrounds are omitted in the alpha versions; use the composition itself for the complete off-white scene.

Example B-roll cue in a reel props file:

```json
{"from":300,"duration":180,"kind":"paper-pathways","labels":["Discover","Prepare","Progress"],"transparent":false}
```

Frame offsets refer to the final edited recording, not the estimated scriptbook time. Captions automatically use navy on opaque paper scenes and white on presenter footage. Adjust cue/caption placement during the actual edit to prevent text or object collisions.

The basic icon pack and first-generation scenes remain available as utility elements. `npm run render:demo` and the catalogue lead with the active paper direction.
