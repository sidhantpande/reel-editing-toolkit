# Jet Kids delivery organization — 28 October 2026

The current local export set is arranged in `Jet Kids - Organized` beside the editing repository on the Desktop. Media remains local; this public repository contains tooling and workflow notes.

| Folder | Contents |
| --- | --- |
| 01 Final Reels | 49 current portrait interview/story reels, grouped into nine speaker/topic folders; descriptive filenames and a CSV index |
| 02 Morning Event / Approved Overview | Locked overview in both approved formats |
| 02 Morning Event / YouTube - For Review | Existing 7m45s landscape film, still awaiting user approval |
| 03 Night Event - Source Collection | 124 linked source entries, 75 separate proxy links, private clip index, incoming folder and provisional YouTube/reel planning folders |
| 90 Superseded Excerpts - Not Final | One older Amol excerpt, separate from the current six-part set |

“Final Reels” identifies the current encoded delivery set. Existing per-item review status is preserved in the local index, including pending user review. No new listening or frame-review attestation is implied by organizing files.

The 49 current reels, two overview files and one YouTube film were verified against their registered SHA-256 hashes before relocation. The older excerpt received a pre-move hash. All 53 files were verified again after relocation. Old export paths remain compatibility symlinks so approval locks, source provenance and existing projects continue to resolve. No file was re-encoded.

## Executable relocation verification

`tools/organize_deliveries.py` accepts a private JSON manifest with `destination_root` and `files`. Each row has absolute `source`, `destination`, `sha256`, and optional `bytes`. The default is read-only batch preflight. `--apply` checks the entire batch before moving files on the same filesystem and creates old-path compatibility links. It refuses overwritten destinations, unrelated source symlinks, duplicate paths, paths outside the destination root and changed bytes. `--verify` rechecks hashes, byte counts and compatibility links. These links preserve project references; they are not independent backups.

```sh
python3 tools/organize_deliveries.py media/edit-projects/jetkids/organization-2026-10-28.local.json --verify
python3 tools/approved_delivery.py workspaces/jetkids/edits/09-reference-led-overview-v01/approval-lock.json
python3 tools/approved_delivery.py workspaces/jetkids/edits/interview-g1-approved-v06/approval-lock.json
```

The manifest and delivered media must remain outside Git. Tests cover batch verification before mutation, destination conflicts, path escape, changed bytes, preserved legacy links and repeat execution.

## Cache policy for this sorting task

The task-specific cleanup inventory is local at `media/edit-projects/jetkids/cache-cleanup-2026-10-28.local.json`. It selects known derived interview/aftermovie audio and video intermediates. Active project references, stabilized/prepared sources, silent pictures and lossless mixes are promoted to `media/working/jetkids` with SHA-256 verification and compatibility links. Potential original/rescue bytes are retained, including an incomplete older copy. Camera originals are never cleanup candidates.

Completed cleanup removed 1,452 derived files totaling 12,341,048,772 bytes (12.34 GB / 11.49 GiB). Before deletion, 233 active working files totaling 9,203,300,957 bytes were relocated and verified. The source-owned masters remain private local files; compatibility links preserve active project paths. Deletion candidates and current exports were hash-checked before cleanup.

Canonical transcripts, source registries, contact sheets, encoded QA evidence, working models, environments, LUTs and reusable dependencies remain available. This is disposal of unnecessary render intermediates, not removal of all editing dependencies. The local cleanup record distinguishes planned and completed deletion and lists every selected file, size and hash.

## Evening-event scope

More footage is expected. The current request is sorting and preparation for one landscape YouTube film and roughly 2–4 portrait reels. Exact stories and count depend on full source review. Preserve the separation from the morning sports inauguration. Additional-camera content labels, camera-clock synchronization and cross-camera duplicates remain future review work; the collection does not present those as completed editorial analysis.
