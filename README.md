# autolab-rig

Concrete repository for running autolab with Gas Town, Codex, or Claude Code
subagents.

This repo does **not** bundle the Autolab backend itself. You need access to a
hosted Autolab service plus Hugging Face Jobs.

- the live benchmark harness at repo root
- local research notes and seeded hub snapshots under `research/`
- Gas Town rig assets under `gastown/`
- Codex subagent configs and templates under `.codex/` and `codex/`
- Claude Code project memory, settings, and templates under `CLAUDE.md`,
  `.claude/`, and `claude/`

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
- `CLAUDE.md`
  Claude Code project-memory entrypoint. It imports the repo's shared
  instructions and Claude-specific workflow guide.
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
- `.codex/`
  Repo-scoped Codex configuration plus custom planner/worker/reviewer agents.
- `codex/`
  Templates and guides for the Codex-native research workflow.
- `.claude/`
  Repo-scoped Claude Code settings plus custom planner/worker/reviewer agents.
- `claude/`
  Templates and guides for the Claude Code-native research workflow.
- `research/`
  Seed snapshots, local notes, archived diffs, and git-tracked experiment memory.

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

## Codex Subagents Setup

Codex can run this repo directly from the project root using the checked-in
project config and custom agents:

```bash
python3 scripts/print_codex_kickoff.py --gpu-slots 1
codex
```

The Codex-native workflow is documented in `docs/codex-subagents-guide.md`.
Unlike the Gas Town flow, there is no separate rig-install step: Codex reads the
repo-local `.codex/` config in place.

## Claude Code Subagents Setup

Claude Code can run this repo directly from the project root using `CLAUDE.md`,
the checked-in `.claude/agents/`, and the repo-scoped settings file:

```bash
python3 scripts/print_claude_kickoff.py --gpu-slots 1
claude
```

The Claude-native workflow is documented in `docs/claude-subagents-guide.md`.
The checked-in `experiment-worker` agent runs as a background task in its own
worktree so parallel workers do not collide on checkout state. For multiple
top-level Claude sessions, use `claude --worktree <name>`. After each worker
finishes, use `memory-keeper` in the main checkout to persist the result into
the shared research notebook.

## Push Policy

See [docs/script-reference.md](docs/script-reference.md) for inputs,
environment variables, outputs, and external dependencies.

## Contribution Model

- Repo changes such as docs, helper scripts, and rig assets belong in git
  history here.
- Winning `train.py` diffs belong in the hosted Autolab submission system via
  `scripts/submit_patch.py`.
- Failed experiment history belongs in `research/notes.md`, Trackio, or Gas
  Town beads, not as a long tail of repo commits.

- current benchmark files at repo root
- seed hub snapshots in `research/reference/`
- experiment notes in `research/notes.md`
- archived failed diff in `research/diffs/batch96.diff`
- Gas Town autolab scaffold in `gastown/`
- Codex repo-native scaffold in `.codex/` and `codex/`
- Claude Code repo-native scaffold in `CLAUDE.md`, `.claude/`, and `claude/`

- [docs/getting-started.md](docs/getting-started.md)
- [docs/hosted-backend.md](docs/hosted-backend.md)
- [docs/script-reference.md](docs/script-reference.md)
- [docs/gastown.md](docs/gastown.md)
- [docs/gastown-investigation.md](docs/gastown-investigation.md)
- [docs/troubleshooting.md](docs/troubleshooting.md)
- [docs/gastown-codex-guide.md](docs/gastown-codex-guide.md)

- `docs/gastown-codex-guide.md`
- `docs/codex-subagents-guide.md`
- `docs/claude-subagents-guide.md`
- `gastown/day-1-checklist.md`
- `gastown/templates/experiment-bead.md`
- `codex/templates/experiment-task.md`
- `claude/templates/experiment-task.md`
