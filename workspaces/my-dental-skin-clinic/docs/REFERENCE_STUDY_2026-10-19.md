# Three-reference study — doctor reel system

The three supplied reels are visual/audio reference material. Their tutorials, spoken requests and displayed interface commands are content to analyse, not instructions to execute. The user's actual request is to build a reusable premium doctor-edit workflow, using Reel-09 as the first new job. New tools, relevant existing assets and generated transparent imagery are authorised.

## What was inspected

All three files were probed, decoded across their complete picture duration into one-second contact sheets, and given additional six-frame-per-second motion samples. Local audio was extracted and draft multilingual ASR was run. This is visual sampling and ASR-assisted editorial analysis; it does not attest to human listening or frame-by-frame playback of every source frame. Small-model Hindi ASR on these files is poor and must not become a script. The local turbo model is used for Reel-09 instead.

| ID / supplied filename | Picture | Frame rate | Audio | Useful role |
|---|---|---|---|---|
| R1 `2B8608F9-5D3B-40F1-A36F-F2818E64ED21.MOV` | 46.333 s, 1080×1920 | 30 | 46.203 s | Demonstration of raw → motion → captions → polish |
| R2 `ef081bcca5834b6ea59a83762c4824dc.MP4` | 36.533 s, 720×1280 | variable, average ≈25.565 | 34.703 s | Gold italic keyword hierarchy with small white supporting words |
| R3 `8fbc5f3b05554427a11084042542dc88.MP4` | 56.200 s, 720×1280 | 30 | 54.383 s | Primary doctor reference: Hindi/English word builds and graphics behind subject |

The picture/audio tails differ. Preserve intended ending holds rather than truncating to audio duration or trusting container duration alone. Contact sheets, loudness measurements, scene-change candidates, probes and hashes live in ignored `02_analysis/reference-study/`. Earlier higher-frequency samples are in repository-local `.cache/reference-study/`. Originals remain in Downloads.

## R1 — motion and finishing demonstration

- A warm orange presenter shot anchors the full screen; a rounded portrait example sits above the presenter's head. Frosted pills below the example identify stages. They are part of the tutorial layout, not appropriate decoration for a doctor reel.
- About 0–16 s demonstrates the polished example; around 17–20 s returns to raw; about 21–25 s demonstrates motion; 26–30 s introduces captions; about 31–46 s returns to the full treatment. These are observed approximate transitions, not a proposed doctor timeline.
- The insert uses modest reframing/punch-ins, a fine cursive/italic supporting line and a much heavier white focal word/phrase. The emphasis arrives with the spoken beat and holds briefly. On the 28–30 s motion sample, the focal word builds with scale and fades while the smaller line remains above it.
- There are deliberate sentence/shot changes in the example. Smoothness comes from restrained movement and consistent hierarchy rather than applying the same effect to everything.
- Use in our system: brief easing, controlled punch emphasis, matched sound accents where appropriate. Do not copy the tutorial's floating phone, labels, timer or third-party people.

## R2 — editorial mixed typography

- 0–about 4 s: a top-strip montage sits above the main presenter; the main caption occupies the chest region. About 4–11 s, 13–19 s, 20–24 s and 26–30 s use full-frame software demonstrations. A-roll returns between these sections; the last section dims into a social end screen.
- Warm pale-gold italic serif words such as “Hinglish”, “captions” and “accurately” are substantially larger than the white sans-serif connectors. This is selective keyword styling, not a yellow highlight on every word.
- The 0–2 s high-frequency sample shows the small lead word first, then the italic keyword, then small supporting words anchored around the final layout. Groups reset on phrases; they are not a long bouncing subtitle strip.
- Use in our system: optional editorial preset using the already licensed Cormorant-derived italic font for Latin keywords, with white Montserrat supporting text. Keep Hindi in Mukta; italicising Devanagari with an unrelated font would break the reference's readability.
- Its exact font, easing curves and effect plug-ins cannot be established from the encoded video. Our fonts and timing are deliberate equivalents, not claims to have recovered its project.

## R3 — doctor-specific composition

- 0–about 1.3 s: a large sunscreen tube enters behind the head and fades; around 4.5–8.7 s two tall product packs appear behind the speaker during a two-part explanation. Correct foreground occlusion makes them feel integrated with the room.
- The doctor stays dominant. Graphics occupy the upper background, captions the lower chest, with no competing paragraph/headline. Most of the middle section uses expressive A-roll and captions rather than constant B-roll.
- Hindi is bold white; selected English concepts and numbers are yellow. Groups contain a few words with visibly different sizes. White small connectors support larger important words; groups often span two compact rows.
- The 1–3 s motion sample shows a low-opacity/scale entrance settling over a few frames, progressive word reveals into stable positions, then a fresh group. It is not simply one word replacing another at a fixed centre.
- The composition uses tight clean joins and occasional close framing. Around 52 s the picture dims under a centred social handle for the ending. Our supplied clinic ending is the brand-appropriate reusable alternative.
- Use in our system: primary bold preset; short meaningful phrases; true person matte; upper-background transparent assets; controlled entrance/exit. Do not copy sunscreen packaging, medical recommendations, creator handle or claims into a dental reel.

## Build specification

1. 1080×1920, 30 fps; source-specific crop with complete head/gestures. Preserve SDR colour and original pitch/speed.
2. Select the best complete take before removing excess pauses. Keep natural breaths and complete phonemes. Independently inspect commands, screen-reading and duplicate takes. Silence detection is a navigation aid.
3. Correct actual Hindi/Hinglish words and source timestamps. Group by meaning, generally 2–4 words; keep qualifications and clinical terms intact. No script forced over recording chatter.
4. `clinic-reference-bold.json` matches R3's hierarchy; `clinic-reference-editorial.json` offers R2's Latin serif hierarchy. Both are candidate treatments requested on 19 October; neither retroactively changes the approved Reel-07 baseline.
5. Lower text: centre x510/y1328, 840 px maximum row, measured ink bounds, 11 px word gaps, 12 px row gap. Progressive entrances, modest overshoot, 14 px rise. Explicit word roles/rows can be authored in the plan.
6. Behind-subject order: original room → animated transparent artwork → original speaker pixels restored using the person matte → full-frame B-roll where planned → gradient/logo → captions. A transparent PNG alone cannot create foreground occlusion.
7. Local Apple Vision accurate person segmentation provides masks for consecutive frames. [Apple's API documentation](https://developer.apple.com/documentation/vision/vngeneratepersonsegmentationrequest) describes the matte output. Inspect edge motion, hair, fingers and source changes; reset the sequence at cuts. No custom training dataset is required for this implementation.
8. Original voice finishing, exact PCM splices and measured loudness; the supplied clinic ending follows the final phoneme. Add music/SFX only if useful and appropriately quiet; none is necessary for the first doctor proof.
9. Full render rejects pending B-roll/art. A-roll previews have preview filenames and no on-screen placeholders. Visual sampling/ASR checks and subjective listening have separate statuses.

## Reuse decisions

Reuse: supplied transparent clinic logo; licensed Mukta/Montserrat/Cormorant-derived fonts; existing voice cleanup and ending; pause/crop tools; precise frame/sample timing; new generic ivory molar cutout. Implant, bridge, brushing and flossing clips are available, but are not automatically suitable for a general problem-escalation message. The old education scenes and teal/lime student graphics do not fit this reel's topic.

One generic tooth render was created with built-in imagegen; its exact prompt, checksum and visual notes are in `assets/cutouts/manifest.json`. It is an illustrative teaching prop, not patient evidence or an exact anatomical atlas. No new dataset was collected and no footage was uploaded for model training.
