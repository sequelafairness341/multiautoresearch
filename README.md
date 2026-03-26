# autolab-rig

Concrete repository for running autolab with Gas Town and Codex CLI.

This repo is the source of truth for:

- the live benchmark harness at repo root
- local research notes and seeded hub snapshots under `research/`
- Gas Town rig assets under `gastown/`

It is intentionally separate from the Gas Town source repo. Keep reusable
orchestration code in `autoresearch-gastown`. Keep live autolab work here.

## Layout

- `train.py`
  Working experiment file. This is the only file most experiments should edit.
- `train_orig.py`
  Local copy of the current hub master used as the diff base.
- `prepare.py`
  Read-only benchmark setup and evaluation logic.
- `run-local.sh`
  Canonical timed local run wrapper.
- `sitecustomize.py`
  Machine-local compatibility shim for local runs. Keep local hacks here, not in
  submitted diffs.
- `scripts/refresh_master.py`
  Refresh `train.py`, `train_orig.py`, and live hub snapshots from the autolab
  API.
- `scripts/submit_patch.py`
  Generate a unified diff and submit it to the autolab API.
- `scripts/parse_metric.py`
  Parse the final metric block from a local run log.
- `scripts/install-rig-assets.sh`
  Copy the checked-in Gas Town rig assets into a live `~/gt/<rig>/` layout.
- `gastown/`
  Rig directives, overlays, templates, and operating docs for the live Gas Town
  rig.
- `research/`
  Seed snapshots, local notes, archived diffs, and git-tracked experiment memory.

## Quick Start

1. Load credentials:

```bash
. ~/.autolab/credentials
```

2. Refresh to current hub master:

```bash
python3 scripts/refresh_master.py --fetch-dag
```

3. Run a local benchmark:

```bash
CUDA_VISIBLE_DEVICES=0 ./run-local.sh /tmp/autolab-run.log
python3 scripts/parse_metric.py /tmp/autolab-run.log
```

4. If the result beats current master, submit it:

```bash
python3 scripts/submit_patch.py --comment "one-sentence hypothesis and result"
```

## Gas Town Setup

After creating a live rig from this repo:

```bash
gt rig add autolab <repo-url>
./scripts/install-rig-assets.sh ~/gt/autolab
```

That installs the checked-in planner and polecat directives plus the autolab
formula overlay into the rig container where Gas Town expects them.

## Push Policy

- Push harness changes, notes, helper scripts, and rig assets to this repo.
- Submit winning `train.py` diffs to the autolab hub via the API.
- Do not treat failed experiments as merge-worthy code history. Keep most of that
  memory in `research/` and in beads when using Gas Town.

## Current Seeds

The repo is bootstrapped with the existing local work from `autolab/`:

- current benchmark files at repo root
- seed hub snapshots in `research/reference/`
- experiment notes in `research/notes.md`
- archived failed diff in `research/diffs/batch96.diff`
- Gas Town autolab scaffold in `gastown/`

## See Also

- `docs/gastown-codex-guide.md`
- `gastown/day-1-checklist.md`
- `gastown/templates/experiment-bead.md`
