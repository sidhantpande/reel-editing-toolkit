# Private backup and portability

The private repository `sidhantpande/atfro-niolearn-reel-studio` stores reusable source, templates, edit decisions, scripts, fonts/licences, brand logos, original image/vector assets, transparent animated B-roll, music and sound effects. Original binary assets use Git LFS.

Raw camera files, supplied reference reels, final rendered client videos, previews, caches, models, virtual environments and node_modules are excluded. The owner explicitly authorized removal of local raw AND final media on 16 October 2026, after verification of the reusable private backup. These excluded videos cannot be restored by cloning this repository. Historical QA/manifests retain hashes and editing decisions only.

```sh
git clone https://github.com/sidhantpande/atfro-niolearn-reel-studio.git
cd atfro-niolearn-reel-studio
git lfs pull
bash tools/bootstrap.sh
npm test
npm run check
```

Then supply new footage with `python3 tools/reelctl.py init`. See `docs/AI_WORKFLOW.md`. No dashboard, account keys or service subscription is needed for local editing. Commercial Remotion eligibility remains subject to its licence.

Before future pushes run `npm test`, `npm run check`, and `python3 tools/git_audit.py`. Do not upload raw/final client media or credentials. New changes use the owner's configured Git identity; third-party history and attribution must remain intact.
