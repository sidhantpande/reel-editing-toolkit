# Video source repositories

The toolkit includes pinned Git submodules under `vendor/repos/`. They retain upstream history, authorship and licences. The root toolkit does not copy their binary test fixtures or install their dependencies.

| Checkout | Upstream | Purpose |
|---|---|---|
| `hyperframes` | https://github.com/heygen-com/hyperframes | HTML video renderer, composition catalog and video skills |
| `remotion` | https://github.com/remotion-dev/remotion | Source for the toolkit's existing React video engine |
| `motion-canvas` | https://github.com/motion-canvas/motion-canvas | Programmatic animation and motion scenes |
| `gl-transitions` | https://github.com/gl-transitions/gl-transitions | Full transition source library; selected existing shaders remain in `vendor/gl-transitions` |

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

The November Diwali edit uses only the four supplied portrait camera clips, a restrained natural grade, short chapter dissolves, a brief opening title, the existing school crest and the existing Shubhaarambh music excerpt at native speed. Classroom chatter is omitted; no spoken captions or event claims are invented. Music attribution and supplied-use context remain in `workspaces/jetkids/music-assets.json`. Raw footage, source plans, review images and the final reel stay local. Encoded frame count, dimensions and complete decode are measured; visual and subjective listening review are tracked separately in local QA.
