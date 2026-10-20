# Optional neural beat analysis

The arrival-led Jet Kids revision uses [Beat This! v1.1.0](https://github.com/CPJKU/beat_this/tree/v1.1.0), with its `final0` model and CPU inference. It estimates beats and downbeats; these remain suggestions for matching complete source actions and musical phrases. It does not transcribe lyrics, certify emotional meaning, or approve listening quality. The MIT licence is preserved in `licenses/Beat-This-LICENSE.txt`.

Install in a separate local environment so Torch dependencies do not alter the rendering environment:

```sh
source .cache/setup/activate.sh
python3 -m venv .cache/beat-env
.cache/beat-env/bin/python -m pip install -r tools/requirements-beats.lock
.cache/beat-env/bin/python tools/neural_beats.py /absolute/music.wav --out /absolute/estimated-beats.json
```

First inference downloads the official checkpoint into `.cache/models/beat-this`. Models, environments and analysed media stay out of Git. The wrapper records the exact audio hash, validates bounded increasing timestamps and writes source-relative seconds plus30fps frame suggestions. Offset these when placing a slice into a timeline. Different-tempo reference tracks should not be forced onto one grid by stretching them; place a deliberate handover between phrases instead.
