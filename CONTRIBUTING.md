# Contributing

This repository has two different contribution paths:

1. Repo changes
   - Docs, helper scripts, rig assets, and reporting improvements belong in git
     history here.
2. Benchmark improvements
   - Winning `train.py` diffs belong in the hosted Autolab submission system via
     `python3 scripts/submit_patch.py`, not as a long tail of experiment commits
     in this repo.

## Before You Start

- Install dependencies with `uv sync`.
- Copy `.autolab.credentials.example` to `~/.autolab/credentials`, fill in your
  values, and load it with `. ~/.autolab/credentials`.
- Run `bash scripts/bootstrap_public.sh` to validate your local operator setup.

## Benchmark Rules

These rules are the contribution contract for any timed benchmark run:

- Refresh from current hosted master with `python3 scripts/refresh_master.py --fetch-dag`.
- Treat `research/live/master.json`, `research/live/master_detail.json`, and
  `train_orig.py` as the benchmark source of truth.
- Edit `train.py` only unless the task explicitly says otherwise.
- Never modify `prepare.py`.
- Make exactly one hypothesis change per run.
- Launch one managed HF Jobs benchmark run per hypothesis.
- Submit only if observed `val_bpb` beats current master.
- Keep machine-local compatibility shims out of submitted diffs.

## What To Open As A Pull Request

Use pull requests for changes such as:

- public docs and setup improvements
- helper script fixes
- Trackio and reporting improvements
- rig asset updates under `gastown/`
- non-benchmark tooling changes

When you change a public command or workflow, update the docs in the same pull
request.

## What Not To Commit

Do not commit:

- `~/.autolab/credentials` or any other secret material
- local runtime state under `.runtime/`, `.beads/`, `.logs/`, or `.codex/`
- generated `research/live/*` snapshots
- ad hoc failed experiment history that belongs in Autolab or `research/notes.md`

## Useful Checks

Run the checks that match your change:

```bash
uv sync
bash -n scripts/bootstrap_public.sh
python3 scripts/hf_job.py preflight
python3 scripts/refresh_master.py --help
python3 scripts/submit_patch.py --help
uv run scripts/trackio_reporter.py summary --max-jobs 5
```

For docs-only changes, verify that all referenced files and commands exist.
