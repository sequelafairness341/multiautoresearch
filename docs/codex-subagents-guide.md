# Winning Autolab With Codex Subagents

This guide replaces Gas Town's planner and polecat coordination layer with
project-scoped Codex subagents that run directly from this repo.

The goal is unchanged: maximize useful, non-duplicated experiments per
GPU-hour until you beat current master on `val_bpb`.

## Concept Map

- Gas Town `crew` -> Codex `planner`
- Gas Town `polecat` -> Codex `experiment_worker`
- Gas Town `witness` -> Codex `reviewer` or `memory_keeper`
- Gas Town convoy -> `research/campaigns/*.md`
- Gas Town bead -> `research/experiments/*.md`

## Checked-In Codex Assets

- `.codex/config.toml`
  Repo-scoped Codex defaults and custom agent registration.
- `.codex/agents/planner.toml`
  Read-only experiment planner.
- `.codex/agents/experiment-worker.toml`
  One-hypothesis benchmark executor.
- `.codex/agents/memory-keeper.toml`
  Durable note and duplicate-prevention maintainer.
- `.codex/agents/reviewer.toml`
  Read-only rule and comparability reviewer.
- `codex/templates/campaign.md`
  Template for one research campaign.
- `codex/templates/experiment-task.md`
  Template for one experiment assignment.
- `research/do-not-repeat.md`
  Shared duplicate-prevention ledger.

## Minimal Workflow

1. Refresh current master and the DAG:

```bash
python3 scripts/refresh_master.py --fetch-dag
```

2. Review the current notebook:

- `research/notes.md`
- `research/do-not-repeat.md`
- `research/campaigns/`
- `research/experiments/`

3. Start Codex from the repo root and use the kickoff prompt:

```bash
python3 scripts/print_codex_kickoff.py --gpu-slots 1
codex
```

4. In the parent Codex session:

- ask `planner` for a short ranked queue of fresh, non-duplicate experiments
- create or update a campaign note in `research/campaigns/`
- create one experiment note per hypothesis in `research/experiments/`
- spawn at most one active `experiment_worker` per real H100
- use `reviewer` when you want a read-only rule check before running or submitting
- use `memory_keeper` after each run to fold the result back into the durable ledger

## Parent Session Prompt

The helper script prints a standard parent prompt. The important constraints are:

- active `experiment_worker` count must never exceed real GPU capacity
- planner stays read-only
- each worker gets one hypothesis only
- benchmark runs must use the canonical local scripts
- every run, including failures, must be persisted to markdown

## Experiment Note Discipline

Use `codex/templates/experiment-task.md` for every worker assignment. Keep each
note self-contained so a worker can execute without improvising. Every
assignment should include:

- one-sentence hypothesis
- parent master hash
- master `val_bpb` at dispatch time
- exact single variable being changed
- expected upside
- reason it is not a duplicate

After the run, record:

- local `val_bpb`
- submit or no-submit
- short interpretation
- failure mode if invalid or regressed

## Campaign Discipline

Use `codex/templates/campaign.md` to group related experiments. A campaign
should have one theme only. Pause or close the campaign when:

- master changes invalidate the queue
- the theme is exhausted
- recent runs show the branch is weak

## Scaling Rules

Codex can open more subagent threads than your machine can use productively.
Treat the checked-in thread limit as a ceiling, not a scheduling target.

Rules:

- one usable H100 = one active `experiment_worker`
- start with one parent session and one worker
- only increase worker count after duplicate-prevention is working
- planner and memory updates do not justify extra GPUs

## What Good Looks Like

You are using the Codex-native flow well when:

- experiment notes are consistently well-formed
- duplicate ideas are being rejected early
- regressions are being captured in `research/do-not-repeat.md`
- workers stop stale-master work instead of improvising
- submissions happen only after a valid local win
