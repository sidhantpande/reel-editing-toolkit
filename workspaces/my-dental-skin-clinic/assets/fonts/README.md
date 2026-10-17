# Clinic font pack

Downloaded from the official [Google Fonts repository](https://github.com/google/fonts).
Each family folder contains the original font files and its SIL Open Font License 1.1.
`manifest.json` records source URLs, Git blob IDs, sizes and SHA256 digests.

| Original family | Intended use |
|---|---|
| Manrope | Clear bold dialogue captions; default dental direction |
| Plus Jakarta Sans | Smooth, restrained dialogue captions and labels |
| Barlow Condensed | Short bold hooks and emphasis |
| Cormorant Garamond | Short editorial skin-care headings; pair with a sans serif for dialogue |
| Noto Sans Devanagari | Hindi captions with proper shaping |

`ready/` contains private static instances with distinct internal family names:
Clinic Sans A (Manrope), Clinic Sans B (Plus Jakarta Sans), Clinic Hindi (Noto),
and Clinic Serif (Cormorant). Barlow Condensed Bold is copied unchanged.
The original licences and copyright metadata are retained. These static instances
avoid variable weight ambiguity in FFmpeg/libass; original fonts remain available
for other editors. No system font installation is required for this workflow.

Rebuild samples with `.venv/bin/python tools/build_caption_previews.py` from the project folder.
The rendered [style board](../../previews/captions/caption-style-board.png) and
[12-second motion sample](../../previews/captions/caption-styles.mp4) use illustrative text,
not reviewed reel scripts or actual footage.

Use `templates/captions/*.ass` as starting points. At render time pass this pack's
`ready` directory to the ASS filter's `fontsdir` option. Replace event timing and copy
from reviewed dialogue; adapt font size and placement to the face, framing and UI.
Presets favour 2–5 words per phrase, two lines maximum, and restrained emphasis.
Colours are temporary palette choices pending the supplied clinic logo/reference.
