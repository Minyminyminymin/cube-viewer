# Cube trajectory viewer

Summer cube calibration (6/23–8/27), 8 participants (AA, AZ, EC, EM, IL, JP, MM, ZZ), all 558 trials (279 static + 279 rotating).

## Open

Double-click `cube_trajectory_viewer.html`. The data is embedded in the file and Plotly 2.35.2 is in `lib/`, so it works offline. Keep `lib/` next to the HTML when moving or sharing the viewer.

## Contents

| Path | What it is |
|---|---|
| `cube_trajectory_viewer.html` | The viewer, with the trial data embedded |
| `lib/plotly.min.js` | Plotly 2.35.2 (MIT license), used by the 3D view |
| `data/samples.csv.gz` | Every sample of the 558 trials with its rebuilt ground truth (made by `rebuild_gt.py`) |
| `scripts/rebuild_gt.py` | Raw `RotatingTrace_Calib_*.csv` → `samples.csv.gz` |
| `scripts/build_viewer_data.py` | `samples.csv.gz` → viewer JSON |
| `scripts/embed_viewer_data.py` | Puts the JSON into the viewer HTML |

`samples.csv.gz` columns: hx/hy/hz = hand position and gx/gy/gz = nearest point on the traced edges, both in metres in the cube's own frame (rotating trials rotated back by the fitted angle); seg = nearest edge (1–9); dist = recomputed distance; logged = DistanceToCurve from the CSV; phase = fitted start angle (deg, rotating only); session = calibration session number per participant.

## Ground truth

- Center (0, 1, 0.65) m, edge 0.24 m, traced edges 0-1-2-3-0-4-5-6-7-4, rotation about world z at +30°/s.
- The summer build did not log the rotation angle, so each rotating trial's start angle is fitted on all of its samples to match the logged DistanceToCurve.
- Check: median |recomputed − logged| = 0.028 mm over 1.13 M samples; no sample in any trial is off by more than 1 mm.

## Rebuild

Run from this folder (needs Python with numpy and pandas):

```bash
python3 -I scripts/rebuild_gt.py ../.. data/samples.csv.gz
python3 -I scripts/build_viewer_data.py data/samples.csv.gz viewer_data.json
python3 -I scripts/embed_viewer_data.py cube_trajectory_viewer.html viewer_data.json
```

`../..` is the folder with the raw `RotatingTrace_Calib_*.csv` files (`HMD_Verification_20261012_121503`), so if the folder is moved, give the raw-data path instead.

Session numbers count calibration sessions only. The Formatted folder (`format_tracing_data.py`) also counts days with only the main experiment, so ZZ's calibration sessions 17–22 appear there as 18, 19, 20, 23, 24, 25.
