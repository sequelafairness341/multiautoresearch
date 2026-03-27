# Getting Started

This repo is a public operator checkout for Autolab. It assumes a hosted
Autolab backend plus Hugging Face Jobs access.

## Prerequisites

- Python 3.10 or newer
- `uv`
- `hf` CLI
- a Hugging Face account with Jobs access
- an Autolab account, API endpoint, and API key

## 1. Clone And Install

```bash
git clone <repo-url>
cd <repo-dir>
uv sync
```

## 2. Create Local Credentials

```bash
mkdir -p ~/.autolab
cp .autolab.credentials.example ~/.autolab/credentials
$EDITOR ~/.autolab/credentials
. ~/.autolab/credentials
```

The credentials file stays in your home directory, not in the repo.

## 3. Validate Your Operator Setup

```bash
bash scripts/bootstrap_public.sh
```

This checks:

- `python3`, `uv`, and `hf`
- Python version compatibility
- local Hugging Face auth with `hf auth whoami`
- required Autolab and HF environment variables
- shared HF cache bucket creation

It prints the next commands without starting paid jobs.

## 4. Warm The Shared HF Cache Once

```bash
python3 scripts/hf_job.py launch --mode prepare
```

This prime step keeps tokenizer and data bootstrap out of your paid experiment
loop.

## 5. Refresh To Current Benchmark Master

```bash
python3 scripts/refresh_master.py --fetch-dag
```

This rewrites:

- `train.py`
- `train_orig.py`
- `research/live/master.json`
- `research/live/master_detail.json`
- `research/live/dag.json`

Do not use repo git history as benchmark truth. Use the refreshed files above.

## 6. Run One Managed Experiment

Edit `train.py`, then run:

```bash
python3 scripts/hf_job.py preflight
python3 scripts/hf_job.py launch --mode experiment
python3 scripts/hf_job.py logs <JOB_ID> --follow --output /tmp/autolab-run.log
python3 scripts/parse_metric.py /tmp/autolab-run.log
```

Rules:

- one hypothesis change only
- `train.py` only unless explicitly authorized otherwise
- do not modify `prepare.py`

## 7. Submit If You Win

If the observed `val_bpb` beats current master:

```bash
python3 scripts/submit_patch.py --comment "one-sentence hypothesis and observed val_bpb"
```

## 8. Optional: Local Trackio Dashboard

```bash
uv run scripts/trackio_reporter.py sync --project "${AUTOLAB_TRACKIO_PROJECT:-autolab}"
uv run scripts/trackio_reporter.py dashboard --project "${AUTOLAB_TRACKIO_PROJECT:-autolab}" --mcp-server --no-footer
```

Use the reporter summary before launching more work:

```bash
uv run scripts/trackio_reporter.py summary --max-jobs 25
```

## 9. Optional: Gas Town Mode

If you want planner, polecat, researcher, and reporter workers:

```bash
gt rig add autolab <repo-url>
./scripts/install-rig-assets.sh ~/gt/autolab
./scripts/install-rig-assets.sh --check ~/gt/autolab
```

Then continue with [gastown.md](gastown.md) and the more detailed
[gastown-codex-guide.md](gastown-codex-guide.md).
