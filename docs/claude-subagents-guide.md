# Winning Autolab With Claude Code Subagents

This guide adds a Claude Code-native coordination path to this repo.

The goal is unchanged: maximize useful, non-duplicated experiments per
GPU-hour until you beat current master on `val_bpb`.

## Concept Map

- repo instructions -> `CLAUDE.md`
- custom agents -> `.claude/agents/`
- repo guardrails -> `.claude/settings.json`
- research campaign template -> `claude/templates/campaign.md`
- experiment assignment template -> `claude/templates/experiment-task.md`
- durable ledger -> `research/do-not-repeat.md`

## Checked-In Claude Assets

- `CLAUDE.md`
  Project memory entrypoint for Claude Code. It imports `AGENTS.md` and this
  guide so the repo rules load at session start.
- `.claude/settings.json`
  Project permission guardrails. It blocks direct edits to `prepare.py`.
- `.claude/agents/planner.md`
  Read-only experiment planner.
- `.claude/agents/experiment-worker.md`
  Background, worktree-isolated benchmark executor.
- `.claude/agents/memory-keeper.md`
  Durable markdown and duplicate-prevention maintainer.
- `.claude/agents/reviewer.md`
  Read-only rule and comparability reviewer.
- `.worktreeinclude`
  Copies `.claude/settings.local.json` into Claude worktrees when present.
- `claude/templates/campaign.md`
  Template for one research campaign.
- `claude/templates/experiment-task.md`
  Template for one experiment assignment.
- `claude/templates/do-not-repeat.md`
  Template for the duplicate-prevention ledger.

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

3. Start Claude Code from the repo root and use the kickoff prompt:

```bash
python3 scripts/print_claude_kickoff.py --gpu-slots 1
claude
```

4. In the parent Claude session:

- ask `planner` for a short ranked queue of fresh, non-duplicate experiments
- create or update a campaign note in `research/campaigns/`
- create one experiment note per hypothesis in `research/experiments/`
- spawn at most one active `experiment-worker` per real H100
- use `reviewer` when you want a read-only rule check before running or submitting
- use `memory-keeper` after each worker finishes to persist the result in the main checkout

## Parent Session Prompt

The helper script prints a standard parent prompt. The important constraints are:

- active `experiment-worker` count must never exceed real GPU capacity
- planner and reviewer stay read-only
- each worker gets one hypothesis only
- benchmark runs must use the canonical local scripts
- every run, including failures, must be persisted to markdown

## Parallelism And Worktrees

The checked-in `experiment-worker` agent is configured with:

- `background: true` so long-running workers do not block the parent session
- `isolation: worktree` so parallel workers edit and benchmark in separate worktrees

Operational rules:

- keep worker benchmark logs under `research/live/` with unique names per experiment
- do not rely on a worker's markdown edits in its isolated worktree as the durable notebook
- after each worker result, run `memory-keeper` in the main checkout to update the shared ledger

For multiple top-level Claude sessions, you can also start independent worktrees:

```bash
claude --worktree planner
claude --worktree worker-0
```

## Experiment Note Discipline

Use `claude/templates/experiment-task.md` for every worker assignment. Keep each
note self-contained so a worker can execute without improvising. Every
assignment should include:

- one-sentence hypothesis
- parent master hash
- master `val_bpb` at dispatch time
- exact single variable being changed
- expected upside
- reason it is not a duplicate
- a unique log path under `research/live/`

After the run, record:

- local `val_bpb`
- submit or no-submit
- short interpretation
- failure mode if invalid or regressed
- one short note that `memory-keeper` can fold into `research/notes.md`

## Campaign Discipline

Use `claude/templates/campaign.md` to group related experiments. A campaign
should have one theme only. Pause or close the campaign when:

- master changes invalidate the queue
- the theme is exhausted
- recent runs show the branch is weak

## What Good Looks Like

You are using the Claude-native flow well when:

- experiment notes are consistently well-formed
- duplicate ideas are being rejected early
- regressions are being captured in `research/do-not-repeat.md`
- workers stop stale-master work instead of improvising
- submissions happen only after a valid local win
- parallel workers do not collide on checkout state or log paths
