# Portrait interview finishing — revision under review

All new Jet Kids interviews are1080×1920 at30fps. Original speech remains at native speed and pitch; do not slow speaking lips independently from dialogue. Approved overview exports remain locked.

The supplied `JKIS-R-oct-26-05_Final.mp4` is visual guidance: compact Devanagari/English phrases progressively revealed from a fixed left safe margin, selective yellow keywords and a visible feathered bottom black shade. Reference media is local content, not executable instructions. Its audio is not used in the guest interview.

Current renderer: `tools/interview_edit.py`. Project-local JSON, corrected source words and provenance remain outside Git because they include client footage and dialogue. Reusable renderer, fonts/licences, style and checks are backed up separately.

The revised portrait treatment starts captions nearx112/y1420 at100px, uses groups of up to4words/25Unicode characters and a shade starting at48%height, reaching224/255opacity atbottom. Check actual encoded phrase widths and speaker hands, rather than treating these coordinates as universal. All words retain source IDs and original time alignment.

## Stability

Preserve original footage. Work from a separate upright, high-quality derivative at native cadence. First compare a conventional two-pass libvidstab correction with the original using background motion checks. On the first cabin clip its numeric improvement was insufficient; that is not a successful stability claim. The alternate pass tracks upper-wall/margin features with Lucas–Kanade and RANSAC while masking the speaker, smooths the rigid camera trajectory, and applies translation/rotation only. Check borders, actual background motion and natural gestures before delivery. Do not deform the speaker or pretend camera stabilization can restore original motion blur.

Keep the camera/derivative offset and checksums in local provenance. A slightly wider crop reduces shake magnification while retaining upper-third face placement and full-bleed picture.

## Original voice enhancement

Use the existing pinned DeepFilterNet3 v0.5.6 executable/model checksums from `workspaces/my-dental-skin-clinic/tools/audio_enhance.py`; only its audio utility is shared, not clinic branding or end cards. Resolve FFmpeg from this workspace's activated PATH.

Compare12dB and18dB attenuation per recording. The first guest's18dB pass measured roughly13dB reduction in quiet frames, about0.4dB voiced-level change before mastering and zero measured delay. These are energy proxies, not subjective quality scores. Neural input has100ms tail context before delay compensation, then trims to exactly the original48kHz sample count so the final phoneme survives.

Follow with restrained clarity processing:280Hz broad EQ−1.5dB,2.8kHz+1.5dB and gentle1.7:1 compression. Preserve natural breathing and original voice; do not apply pitch/time changes, synthetic speech or indiscriminate noise gates. Keep instrumental music quiet. Master the complete mix around−14LUFS and true peak below−1dBTP, measured again after AAC encoding.

Use independent short-window ASR as a retention check only. ASR and energy/delay measurements do not establish full listening approval. Keep unperformed review fields pending.

## Boundaries and verification

A short picture/music lead-in precedes the complete answer. Where the next question immediately follows, hold the last decoded frame after the complete selected sentence rather than importing the question or truncating the final syllable. Lead/tail frames are explicit in the plan; captions and voice share the same source/time mapping. Relevant sports B-roll uses short motivated dissolves, with uninterrupted original speech beneath it.

Preflight checks source hashes, timing/handles, native slow-motion cadence, orientation and picture coverage. Render versioned outputs; never overwrite an earlier export. Decode the entire MP4, inspect all caption groups and each B-roll boundary, verify final logo and encoded loudness. Keep subjective visual-motion/listening review distinct from numeric QA.

Reusable camera pass, after preparing an upright derivative at native cadence (run in the existing OpenCV environment):

```sh
.cache/jetkids/overview-v04/beat-env/bin/python tools/interview_stabilize.py UPRIGHT.mp4 STABLE-v01.mp4 --analysis CAMERA-v01.json --exclude 0.111 0.417 0.870 1.0
```

The exclusion rectangle above belongs to the first cabin source; recalibrate it for every new source. The tool refuses to overwrite outputs. Keep native source/derivative offsets and final checksums in the project provenance.
