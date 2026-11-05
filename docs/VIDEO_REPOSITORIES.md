# Video source repositories

The toolkit includes pinned Git submodules under `vendor/repos/`. They retain upstream history, authorship and licences. The root toolkit does not copy their binary test fixtures or install their dependencies.

| Checkout | Upstream | Purpose |
|---|---|---|
| `hyperframes` | https://github.com/heygen-com/hyperframes | HTML video renderer, composition catalog and video skills |
| `remotion` | https://github.com/remotion-dev/remotion | Source for the toolkit's existing React video engine |
| `motion-canvas` | https://github.com/motion-canvas/motion-canvas | Programmatic animation and motion scenes |
| `gl-transitions` | https://github.com/gl-transitions/gl-transitions | Full transition source library; selected existing shaders remain in `vendor/gl-transitions` |
| `editly` | https://github.com/mifi/editly | Declarative video editing, transition integration and examples |
| `muses` | https://github.com/fiehrfly/muses | Music-source index with licence and platform notes; contains links rather than a licensed audio collection |

Restore exactly the pinned revisions, without downloading upstream LFS test footage:

```sh
GIT_LFS_SKIP_SMUDGE=1 git submodule update --init --depth 1
git submodule status
```

The parent repository's gitlinks are the revision lock. Update those deliberately after reviewing upstream changes. Read each upstream's own licence before using its code or assets; installation here does not change those terms. Source checkouts are available for reuse; this does not attest that all four engines have been built or tested. HyperFrames's upstream currently reports some tracked test files as non-pointers despite its LFS attributes; source checkout succeeds without fetching fixture media.

## Portrait activity reel

`tools/render_activity_reel.py` adds a simple footage-led path using the existing serial source-handle transition helper. It needs FFmpeg and Pillow (`.venv/bin/python -m pip install Pillow==13.0.0`); it does not require the optional speech/ML audio environment. The full bootstrap currently encounters a Python 3.11 conflict with the pinned `scipy==1.18.1`; that unrelated dependency is not changed by this workflow.

Keep the reviewed JSON plan in ignored `media/edit-projects/`, containing `shots` with `source`, `in` (seconds), `frames` (30 fps), `speed` (0.5–1), `review_note`, and optional `transitionIn` matching `event_transitions.py`. It also contains root-relative `music` and `logo` asset paths and `ending_frames`. Use a fresh output and cache for every revision.

```sh
.venv/bin/python tools/render_activity_reel.py media/edit-projects/diwali/plan-v01.json \
  --source-root /absolute/footage-folder \
  --output exports/Diwali-Reel-v01.mp4 --cache .cache/diwali-v01
```

The November Diwali workspace uses only the four supplied portrait camera clips. After the user requested a complete restart, the new action-led cut uses the `natural-festive` look: source-specific modest crops, natural colour, clean cuts, two short chapter dissolves and a short school closing card. Latest audio direction is smooth background music that attracts very little attention, using the original toolkit Soft Momentum bed at approximately−24LUFS. Earlier festive/blur/slide treatments and prominent soundtracks are superseded. Exact source plans and client exports remain local; current and historical music selections are in [MUSIC_SOURCES.md](MUSIC_SOURCES.md).

Set `look` to `festive` for the original gold/serif Diwali artwork, warm natural grade, controlled close-up pushes, amber edge bokeh and three optional light sweeps (`light_cues`, in seconds). The transparent school crest is176px wide at44,64 throughout the footage. The closing card uses one larger centered crest. Chapters use the existing source-handle transition engine's `hblur`, `zoomin`, `smoothleft`, `smoothright` and `fade`; no new GL renderer is required. `tools/activity_design.py` makes the original artwork locally using the included Sora and OFL Cormorant Garamond fonts. Cormorant's existing font/licence files remain under the clinic fonts directory; no clinic identity is applied to the school.

`--picture-only` allows picture approval before music selection. Otherwise `music_in` selects source seconds at native speed and pitch; it defaults to0. Festive picture is encoded once and the selected music is muxed without re-encoding it. Source chatter is omitted; no spoken captions or event claims are invented. Camera footage, source plans, review images and final reels stay local. Encoded frame count, dimensions and full decode are measured; visual and subjective listening review are tracked separately in local QA. The downloaded repositories are available for future use; their addition is not a claim that Editly or every shader was built or used in this export.

For `natural-festive`, `crop_factor` (1–1.3) and normalized `crop_x`/`crop_y` (0–1) allow reviewed shot-specific framing. This look omits synthetic pushes, light sweeps and edge particles. A compact title fades over the opening and the original transparent logo remains top-left. The quiet-background audio finishing recipe is recorded separately in the local `audio_finish` plan/QA metadata; the renderer's default music mix remains−14LUFS unless the project is finished separately.
