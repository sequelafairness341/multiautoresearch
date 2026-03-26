# Agent Instructions

This repo is a live autolab experiment repo.

## Goal

Lower `val_bpb` on the autolab benchmark with disciplined, comparable
single-change experiments.

## Hard Rules

- Edit `train.py` only unless the task explicitly says otherwise.
- Never modify `prepare.py`.
- Start from current hub master, not stale local history.
- Make exactly one hypothesis change per run.
- Run the timed benchmark before claiming success.
- Submit only if local `val_bpb` beats current master.
- Keep machine-local compatibility shims out of submitted diffs.

## Standard Workflow

1. Refresh from the hub:
   - `python3 scripts/refresh_master.py --fetch-dag`
2. Edit `train.py`.
3. Run:
   - `CUDA_VISIBLE_DEVICES=0 ./run-local.sh /tmp/autolab-run.log`
4. Parse the result:
   - `python3 scripts/parse_metric.py /tmp/autolab-run.log`
5. Record the hypothesis and outcome in `research/notes.md`.
6. Submit if improved:
   - `python3 scripts/submit_patch.py --comment "..."`

## Repo Layout

- Root benchmark files are the experiment surface.
- `research/` is the durable experiment notebook.
- `gastown/` contains the rig assets that should be installed into a live
  `~/gt/<rig>/` container with `scripts/install-rig-assets.sh`.

## Local Compatibility

`run-local.sh` sets `AUTOLAB_FORCE_FA3_REDIRECT=1`, and `sitecustomize.py`
redirects the Hopper FA3 kernel lookup for hosts that cannot import the default
wheel locally. Do not bake that redirect into `train.py`.
