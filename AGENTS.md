# Agent Instructions

This repo is a live autolab experiment repo.

## Goal

Lower `val_bpb` on the autolab benchmark with disciplined, comparable
single-change experiments.

## Hard Rules

- Edit `train.py` only unless the task explicitly says otherwise.
- Never modify `prepare.py`.
- Start from current hub master, not stale local history.
- Treat `python3 scripts/refresh_master.py --fetch-dag`, `research/live/master.json`,
  and `train_orig.py` as the benchmark-master source of truth.
- Do not use repo git history such as `main` or `origin/main` to decide whether
  an experiment is fresh; this repository also carries rig/control-plane commits.
- Make exactly one hypothesis change per run.
- Run the timed benchmark before claiming success.
- Submit only if local `val_bpb` beats current master.
- Keep machine-local compatibility shims out of submitted diffs.

## Managed Runner

The default benchmark path in this repo is Hugging Face Jobs, not a local CUDA
host.

One-time bootstrap:
- `hf auth whoami`
- `hf buckets create "$AUTOLAB_HF_BUCKET" --private --exist-ok`
- `python3 scripts/hf_job.py launch --mode prepare`

Per experiment:
- `python3 scripts/hf_job.py launch --mode experiment`
- note the job id from the output
- `python3 scripts/hf_job.py logs <JOB_ID> --follow --output /tmp/autolab-run.log`
- `python3 scripts/parse_metric.py /tmp/autolab-run.log`

## Standard Workflow

1. Refresh from the hub:
   - `python3 scripts/refresh_master.py --fetch-dag`
   - this rewrite of `train.py` and `train_orig.py` defines the benchmark base
2. Edit `train.py`.
3. Launch one managed benchmark job:
   - `python3 scripts/hf_job.py launch --mode experiment`
   - `python3 scripts/hf_job.py logs <JOB_ID> --follow --output /tmp/autolab-run.log`
4. Parse the result:
   - `python3 scripts/parse_metric.py /tmp/autolab-run.log`
5. Record the hypothesis and outcome in `research/notes.md`.
6. Submit if improved:
   - `python3 scripts/submit_patch.py --comment "..."`

## Codex Subagents

- Repo-scoped Codex config lives in `.codex/`.
- Custom planner, worker, reviewer, and memory agents live in `.codex/agents/`.
- Durable Codex-native workflow docs and templates live in `codex/` plus
  `research/campaigns/`, `research/experiments/`, and
  `research/do-not-repeat.md`.
- Active `experiment_worker` count must never exceed real GPU capacity.
- Planner and reviewer agents should stay read-only; experiment workers own the
  benchmark run.

## Claude Code Subagents

- Project memory entrypoint lives in `CLAUDE.md`.
- Repo-scoped Claude settings and custom agents live in `.claude/`.
- Durable Claude-native workflow docs and templates live in `claude/` plus
  `research/campaigns/`, `research/experiments/`, and
  `research/do-not-repeat.md`.
- Active `experiment-worker` count must never exceed real GPU capacity.
- Planner and reviewer should stay read-only; experiment workers run in
  isolated worktrees and own the benchmark run.
- Persist worker results back into the shared notebook with `memory-keeper` in
  the main checkout.

## Repo Layout

- Root benchmark files are the experiment surface.
- `CLAUDE.md` is the Claude Code project-memory entrypoint.
- `research/` is the durable experiment notebook.
- `gastown/` contains the rig assets that should be installed into a live
  `~/gt/<rig>/` container with `scripts/install-rig-assets.sh`.
- `.codex/` contains repo-scoped Codex configuration and custom subagents.
- `codex/` contains templates and operator docs for Codex-native orchestration.
- `.claude/` contains repo-scoped Claude Code settings and custom subagents.
- `claude/` contains templates and operator docs for Claude Code orchestration.

## Literature Scouting

When the task is planner or literature research rather than a timed benchmark
run:

- You may edit `research/*.md`, `gastown/`, and operator docs.
- Use the local `hf-cli` skill plus Hugging Face paper search and read tooling
  to find relevant work.
- Translate papers into single-change `train.py` hypotheses that can be tested
  cleanly.
- Record paper-derived ideas in `research/paper-ideas.md`.
- Do not claim a win or submit a patch without a benchmark run.

## Local Skills

- `autolab-managed-experiment`
  Use for any bead that should become exactly one managed HF Jobs experiment.
- `autolab-reporter`
  Use for Trackio, active-job review, anomaly review, and experiment-board
  summaries.
- `hf-cli`
  Use for Hugging Face Hub CLI operations such as jobs, buckets, auth, and
  papers.

## Local Compatibility

`run-local.sh` sets `AUTOLAB_FORCE_FA3_REDIRECT=1`, and `sitecustomize.py`
redirects the Hopper FA3 kernel lookup for hosts that cannot import the default
wheel locally. Do not bake that redirect into `train.py`. Keep `run-local.sh`
as a local fallback only; do not use it as the default rig path.
