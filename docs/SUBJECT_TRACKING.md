# Subject tracking for portrait edits

`tools/subject_track.py` uses [OpenCV CSRT](https://docs.opencv.org/4.11.0/d2/da2/classcv_1_1TrackerCSRT.html) to follow an editor-selected subject in a short16:9 source window. The editor must select the correct guest/player in the first frame. This prevents a crowd detector from choosing an unrelated larger face. Native portrait coverage remains preferable for groups, ribbon cutting and interacting hands.

```sh
source .cache/setup/activate.sh
python3 -m venv .cache/tracking-env
.cache/tracking-env/bin/python -m pip install -r tools/requirements-tracking.lock
.cache/tracking-env/bin/python tools/subject_track.py /absolute/source.mov \
  --start 29.1 --seconds 1.5 --speed 0.75 \
  --bbox 0.52 0.29 0.10 0.50 --out /absolute/subject-path.json
```

The rectangle is normalized x/y/width/height. Analysis uses15fps960px frames. The source remains untouched; output records its hash, raw tracked boxes, tracking failures and a smoothed, bounded portrait crop path. Times in `crop_path` refer to output time after the specified constant speed. Median and binomial smoothing reduce crop jitter without simply joining two guessed centres. First/middle/last diagnostic images include the selected box and crop window.

Inspect diagnostic frames and the encoded output. A successful tracker flag does not prove it retained the intended person, and an occluded face can cause drift. Re-select the target or choose alternate coverage when needed. Do not use this script for native portrait or unoriented recordings; it rejects those inputs. OpenCV4.11.0 licence is preserved in `licenses/OpenCV-LICENSE.txt`.
