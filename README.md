# autolab-rig

Public operator repository for running Autolab experiments with Gas Town and
Hugging Face Jobs.

This repo does **not** bundle the Autolab backend itself. You need access to a
hosted Autolab service plus Hugging Face Jobs.

## What You Need

- Python 3.10 or newer
- `uv`
- `hf` CLI
- a Hugging Face account with Jobs access
- a hosted Autolab account, endpoint, and API key
- Gas Town

## Quick Start

This is the canonical setup path for the repo.

### 1. Clone And Install

```bash
git clone https://github.com/burtenshaw/autolab-gastown.git
cd autolab-gastown
uv sync
```

### 2. Create Local Credentials

```bash
mkdir -p ~/.autolab
cp .autolab.credentials.example ~/.autolab/credentials
$EDITOR ~/.autolab/credentials
```

Your credentials file stays in your home directory, not in the repo.

### 3. Log In To Hugging Face Once

```bash
hf auth login
```

### 4. Validate Your Setup

```bash
. ~/.autolab/credentials
bash scripts/bootstrap_public.sh
```

This verifies:

- `python3`, `uv`, and `hf`
- your local Hugging Face login
- required Autolab and HF environment variables
- shared HF bucket access

If this step fails, start with [docs/troubleshooting.md](docs/troubleshooting.md).

### 5. Create The Gas Town Rig

```bash
gt rig add autolab https://github.com/burtenshaw/autolab-gastown.git
./scripts/install-rig-assets.sh ~/gt/autolab
./scripts/install-rig-assets.sh --check ~/gt/autolab
```

### 6. Add The Control-Plane Workers

```bash
cd ~/gt/autolab
gt crew add researcher --rig autolab
gt crew add reporter --rig autolab
```

### 7. Warm The Shared Cache And Refresh Master

```bash
cd ~/gt/autolab/crew/planner
. ~/.autolab/credentials
python3 scripts/hf_job.py launch --mode prepare
python3 scripts/refresh_master.py --fetch-dag
```

This rewrites `train.py`, `train_orig.py`, and `research/live/*`. Treat those
files as the benchmark source of truth. Do **not** use repo git history such as
`main` or `origin/main` as benchmark truth.

### 8. Create And Dispatch Your First Bead

```bash
bd create --title "optimizer: first autolab experiment" --type=task --priority=1
# note the bead id from the output, then:
gt convoy create "optimizer: first autolab run" <BEAD_ID>
gt sling <BEAD_ID> autolab --agent codex
```

At that point the planner and polecats own the benchmark loop. For the full
role split and daily workflow, continue with [docs/gastown.md](docs/gastown.md),
[docs/gastown-investigation.md](docs/gastown-investigation.md), and
[docs/gastown-codex-guide.md](docs/gastown-codex-guide.md).

## First Run Rules

- Refresh from hosted master before every fresh experiment.
- Use `train.py`, `train_orig.py`, and `research/live/master.json` as benchmark
  truth.
- Make exactly one hypothesis change per run.
- Do not modify `prepare.py`.
- Submit only if observed `val_bpb` beats current master.

## Optional: Local Trackio Dashboard

```bash
uv run scripts/trackio_reporter.py sync --project "${AUTOLAB_TRACKIO_PROJECT:-autolab}"
uv run scripts/trackio_reporter.py dashboard --project "${AUTOLAB_TRACKIO_PROJECT:-autolab}" --mcp-server --no-footer
```

## Script-Only Path

If you want to use the benchmark scripts directly without Gas Town, see
[docs/getting-started.md](docs/getting-started.md).

## Stable Public Entrypoints

These scripts are the operator-facing interface of the repo:

- `scripts/refresh_master.py`
- `scripts/hf_job.py`
- `scripts/parse_metric.py`
- `scripts/submit_patch.py`
- `scripts/trackio_reporter.py`

See [docs/script-reference.md](docs/script-reference.md) for inputs,
environment variables, outputs, and external dependencies.

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
- [docs/gastown-investigation.md](docs/gastown-investigation.md)
- [docs/troubleshooting.md](docs/troubleshooting.md)
- [docs/gastown-codex-guide.md](docs/gastown-codex-guide.md)

## License

This repository is released under the [MIT License](LICENSE).
