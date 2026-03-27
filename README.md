# autolab-rig

Public operator repository for running Autolab experiments with Hugging Face
Jobs and, optionally, Gas Town.

This repository contains:

- the benchmark surface at repo root
- hosted-backend refresh and submission clients under `scripts/`
- local experiment memory under `research/`
- Gas Town rig assets under `gastown/`

It does **not** bundle the Autolab backend itself. The default workflow assumes
you have access to a hosted Autolab service plus Hugging Face Jobs.

## What This Repo Is

- `train.py`
  The working experiment surface. Most benchmark runs should edit this file
  only.
- `train_orig.py`
  The current hosted benchmark master after a refresh.
- `prepare.py`
  Read-only benchmark setup and evaluation logic.
- `scripts/refresh_master.py`
  Pull current benchmark truth from the hosted Autolab service into local files.
- `scripts/hf_job.py`
  Preflight, render, launch, inspect, and tail managed Hugging Face Jobs runs.
- `scripts/parse_metric.py`
  Parse the final metric block from a completed run log.
- `scripts/submit_patch.py`
  Submit a winning unified diff back to the hosted Autolab service.
- `scripts/trackio_reporter.py`
  Build a local Trackio experiment board from Hugging Face Jobs activity.
- `scripts/install-rig-assets.sh`
  Install the checked-in Gas Town rig assets into `~/gt/<rig>/`.
- `gastown/`
  Planner, polecat, reporter, and taxonomy assets for the live rig.
- `research/`
  Durable notebook files, idea backlog, and reference snapshots.

## What You Need

- Python 3.10 or newer
- `uv`
- `hf` CLI
- a Hugging Face account with Jobs access
- a hosted Autolab account, endpoint, and API key
- optional: Gas Town if you want planner/polecat orchestration

## Quick Start

1. Install dependencies:

```bash
uv sync
```

2. Create local credentials from the checked-in template:

```bash
mkdir -p ~/.autolab
cp .autolab.credentials.example ~/.autolab/credentials
$EDITOR ~/.autolab/credentials
. ~/.autolab/credentials
```

3. Validate your local operator setup:

```bash
bash scripts/bootstrap_public.sh
```

4. Warm the shared HF cache once:

```bash
python3 scripts/hf_job.py launch --mode prepare
```

5. Refresh current benchmark master:

```bash
python3 scripts/refresh_master.py --fetch-dag
```

This rewrites `train.py`, `train_orig.py`, and `research/live/*`. Treat those
files as the benchmark source of truth. Do **not** use repo git history such as
`main` or `origin/main` as benchmark truth.

6. Launch one managed experiment:

```bash
python3 scripts/hf_job.py preflight
python3 scripts/hf_job.py launch --mode experiment
python3 scripts/hf_job.py logs <JOB_ID> --follow --output /tmp/autolab-run.log
python3 scripts/parse_metric.py /tmp/autolab-run.log
```

7. Submit only if the observed `val_bpb` beats current master:

```bash
python3 scripts/submit_patch.py --comment "one-sentence hypothesis and observed val_bpb"
```

8. Optional: start the local Trackio dashboard:

```bash
uv run scripts/trackio_reporter.py sync --project "${AUTOLAB_TRACKIO_PROJECT:-autolab}"
uv run scripts/trackio_reporter.py dashboard --project "${AUTOLAB_TRACKIO_PROJECT:-autolab}" --mcp-server --no-footer
```

## Stable Public Entrypoints

These scripts are the operator-facing interface of the repo:

- `scripts/refresh_master.py`
- `scripts/hf_job.py`
- `scripts/parse_metric.py`
- `scripts/submit_patch.py`
- `scripts/trackio_reporter.py`

See [docs/script-reference.md](docs/script-reference.md) for inputs,
environment variables, outputs, and external dependencies.

## Supported Modes

### Direct Operator Mode

Use the scripts directly from this checkout. This is the simplest path for a
new operator and does not require Gas Town.

### Gas Town Mode

Install the rig assets and use planner, polecat, researcher, and reporter
workers:

```bash
gt rig add autolab <repo-url>
./scripts/install-rig-assets.sh ~/gt/autolab
./scripts/install-rig-assets.sh --check ~/gt/autolab
```

Then continue with [docs/gastown.md](docs/gastown.md).

## Contribution Model

- Repo changes such as docs, helper scripts, and rig assets belong in git
  history here.
- Winning `train.py` diffs belong in the hosted Autolab submission system via
  `scripts/submit_patch.py`.
- Failed experiment history belongs in `research/notes.md`, Trackio, or Gas
  Town beads, not as a long tail of repo commits.

## Docs

- [docs/getting-started.md](docs/getting-started.md)
- [docs/hosted-backend.md](docs/hosted-backend.md)
- [docs/script-reference.md](docs/script-reference.md)
- [docs/gastown.md](docs/gastown.md)
- [docs/troubleshooting.md](docs/troubleshooting.md)
- [docs/gastown-codex-guide.md](docs/gastown-codex-guide.md)

## License

This repository is released under the [MIT License](LICENSE).
