# We set up an automated AI lab from agents to train models

tl;dr: a team of agents can research literature, run parallel ML experiments, review them, and make improvements.

Most ML experiment infrastructure solves the execution problem — how to get code onto GPUs. But the harder problem is the one you hit after the run finishes: what did we actually try, why did that one fail, and which result should we trust?

This post walks through a system that treats that retrospective problem as a first-class concern. The stack has three layers: a **control plane** (**Gastown**, **Codex subagents**, or **Claude Code**), **HF Jobs** as the execution plane (managed H200 GPU runs), and **Trackio** as the observability layer (turning events and metrics into something you can investigate after the fact).

The code is public at [burtenshaw/autolab-gastown](https://github.com/burtenshaw/autolab-gastown). Everything below comes from a real wave of experiments — `2026-03-28-wave2` — optimizing a language model training benchmark.

## What the experiment actually is

The benchmark is a short, fixed-budget language model training run. The target metric is `val_bpb` (validation bits-per-byte). The current best score lives on a hosted Autolab service, and the goal is to beat it by making small, isolated changes to `train.py`.

Each experiment follows one strict rule: **one hypothesis, one edit, one run**. You refresh from the hosted master, change exactly one thing in `train.py`, launch a managed H200 job, and submit the diff only if the result improves on the baseline.

```bash
# Pull current benchmark truth
python3 scripts/refresh_master.py --fetch-dag

# Validate the workspace has exactly one change
python3 scripts/hf_job.py preflight

# Launch the run
python3 scripts/hf_job.py launch --mode experiment

# Stream logs and extract the result
python3 scripts/hf_job.py logs <JOB_ID> --follow --output /tmp/run.log
python3 scripts/parse_metric.py /tmp/run.log

# Submit only if it wins
python3 scripts/submit_patch.py --comment "warmdown ratio 0.925, val_bpb 0.958973"
```

That sequence is the whole experiment loop for one hypothesis. The question is how to run many of them in parallel and still understand what happened afterward.


## Gastown: the control plane

Gastown is a multi-agent workspace manager. In this setup it has four primitives that matter:

| Primitive | What it is |
|--|--|
| **Convoy** | A batch of experiments dispatched together |
| **Bead** | One tracked hypothesis — the unit of work |
| **Polecat** | An isolated worker agent with its own git worktree |
| **Sling** | The dispatch event that assigns a bead to a polecat |

These aren't just scheduling abstractions, they're **work objects** with durable state. After a wave finishes, you can inspect any of them:

```bash
# What was in the batch?
gt convoy status

# What was the hypothesis?
bd show --long --id au-2rf

# Who ran it?
gt polecat status autolab/turquoise
```

Each bead carries the full context: the hypothesis text, the parent master hash it branched from, the polecat that executed it, the HF Job ID, and the final metric. That chain is what makes the process legible after the fact.

### Creating a wave

A typical wave starts with the planner creating beads from a mix of exploit brackets (tightening around known winners) and paper-derived exploration (new ideas from recent research):

```bash
# Exploit bracket: tighten around a known warmdown winner
bd create --type task --priority 1 \
  --labels autolab:experiment,autolab:scheduler \
  --title "scheduler: warmdown ratio 0.925 hub-master bracket" \
  --description "$(cat <<'EOF'
Hypothesis:
- The strong warmdown win at 0.90 suggests the optimum may sit
  slightly higher on current hub master.
Single change:
- WARMDOWN_RATIO = 0.925
Parent:
- current hub master 765a36b0700b
EOF
)"

# Paper-derived: attention temperature from 2411.12892
bd create --type task --priority 1 \
  --labels autolab:experiment,autolab:architecture,autolab:paper \
  --title "attn: q temperature 0.9 hub-master paper check" \
  --description "..."
```

### Dispatching in parallel

Once beads exist, Gastown fans them out to separate polecats. Each polecat gets its own git worktree, so there's no cross-contamination between experiments:

```bash
# Dispatch five beads in one batch
gt sling au-2rf au-drk au-47r au-kxn au-yfd autolab \
  --agent codex --max-concurrent 5

# Each bead lands on a fresh polecat
# au-2rf -> autolab/polecats/turquoise
# au-drk -> autolab/polecats/amber
# ...
```

Each polecat then independently refreshes from master, applies its one-line edit, runs `hf_job.py preflight` to verify the diff is clean, and launches a single H200 job.


## Codex subagents: a lighter control plane

The comparable Codex-native variant keeps the same experimental discipline, but
it replaces Gastown's explicit work objects with project-scoped custom agents
and markdown state inside the repo.

The role mapping is direct:

| Gastown | Codex subagents |
|--|--|
| **Convoy** | `research/campaigns/*.md` campaign note |
| **Bead** | `research/experiments/*.md` experiment note |
| **Crew / Mayor** | `planner` subagent |
| **Polecat** | `experiment_worker` subagent |
| **Witness** | `reviewer` or `memory_keeper` subagent |
| **Sling** | Parent Codex session spawning a worker |

Instead of `gt sling`, the operator starts a parent Codex session in the repo,
uses the checked-in `.codex/config.toml`, and delegates to custom subagents that
already know the autolab rules.

### Running the same experiment with Codex subagents

Here's the same kind of warmdown-ratio follow-up as a Codex-native session:

```bash
# Refresh benchmark truth first
python3 scripts/refresh_master.py --fetch-dag

# Print the standard parent-session prompt
python3 scripts/print_codex_kickoff.py \
  --campaign "scheduler: warmdown-ratio follow-ups" \
  --gpu-slots 1

# Start Codex from the repo root
codex
```

Inside that parent session, the flow is lighter-weight but structurally similar:

```text
Read AGENTS.md, research/notes.md, research/do-not-repeat.md,
research/reference/master.seed.json, and research/reference/dag.seed.json.

Spawn the `planner` subagent and ask for up to 3 fresh scheduler experiments for
the current master.

Create `research/campaigns/scheduler-warmdown.md` from
`codex/templates/campaign.md`.

Create `research/experiments/warmdown-0925.md` from
`codex/templates/experiment-task.md` and assign:
- Hypothesis: WARMDOWN_RATIO = 0.925
- Parent master hash: 765a36b0700b
- Single variable: warmdown ratio only

Spawn one `experiment_worker` for GPU 0 and tell it to:
- refresh from current master
- edit `train.py` only
- run `CUDA_VISIBLE_DEVICES=0 ./run-local.sh /tmp/autolab-run.log`
- parse `python3 scripts/parse_metric.py /tmp/autolab-run.log`
- submit only if the local `val_bpb` beats master
- record the result in `research/notes.md` and the experiment note
```

That gives you the same planner/worker split as Gastown, but without requiring a
separate rig, convoy state, or named worktrees.

## Claude Code: repo-local control with worktree isolation

The Claude-native variant sits between the other two approaches. Like the Codex
path, it keeps the durable notebook in the repo. Unlike the Codex path, the
checked-in `experiment-worker` is designed to run in the background and in its
own worktree, so parallel workers get stronger checkout isolation.

The role mapping is also direct:

| Gastown | Claude Code |
|--|--|
| **Convoy** | `research/campaigns/*.md` campaign note |
| **Bead** | `research/experiments/*.md` experiment note |
| **Crew / Mayor** | `planner` subagent |
| **Polecat** | `experiment-worker` subagent |
| **Witness** | `reviewer` or `memory-keeper` subagent |
| **Sling** | Parent Claude session spawning a worker |

Instead of a rig-level scheduler, the operator starts Claude Code in the repo,
loads `CLAUDE.md`, checks the project agents under `.claude/agents/`, and then
delegates from one parent session.

### Running the same experiment with Claude Code

Here's the same warmdown-ratio follow-up through the Claude-native path:

```bash
# Refresh benchmark truth first
python3 scripts/refresh_master.py --fetch-dag

# Print the standard parent-session prompt
python3 scripts/print_claude_kickoff.py \
  --campaign "scheduler: warmdown-ratio follow-ups" \
  --gpu-slots 1

# Start Claude Code from the repo root
claude
```

Inside that parent session, the flow looks like this:

```text
Read CLAUDE.md, AGENTS.md, research/notes.md, research/do-not-repeat.md,
research/reference/master.seed.json, and research/reference/dag.seed.json.

Run `/agents` and confirm the checked-in project agents are loaded.

Ask the `planner` subagent for up to 3 fresh scheduler experiments for the
current master.

Create `research/campaigns/scheduler-warmdown.md` from
`claude/templates/campaign.md`.

Create `research/experiments/warmdown-0925.md` from
`claude/templates/experiment-task.md` and assign:
- Hypothesis: WARMDOWN_RATIO = 0.925
- Parent master hash: 765a36b0700b
- Single variable: warmdown ratio only
- Log path: research/live/warmdown-0925.log

Spawn one background `experiment-worker` for GPU 0 and tell it to:
- refresh from current master
- edit `train.py` only
- run `CUDA_VISIBLE_DEVICES=0 ./run-local.sh research/live/warmdown-0925.log`
- parse `python3 scripts/parse_metric.py research/live/warmdown-0925.log`
- leave a short result summary for `memory-keeper`

After the worker finishes, use `memory-keeper` in the main checkout to update
`research/notes.md`, the experiment note, and `research/do-not-repeat.md`.
```

That gives you a single parent session like the Codex flow, but with a more
explicit worktree story for parallel workers.

### Gastown vs Codex vs Claude Code

All three approaches can enforce the same research discipline. The difference is
where the structure lives.

| Dimension | Gastown | Codex subagents | Claude Code |
|--|--|--|--|
| **Primary state** | External named objects: convoys, beads, polecats | Repo-local markdown plus `.codex/agents/*.toml` | Repo-local markdown plus `CLAUDE.md`, `.claude/agents/*.md`, and `.claude/settings.json` |
| **Dispatch** | `gt sling` sends a bead to a polecat | Parent session spawns `planner` / `experiment_worker` | Parent session delegates via `/agents` and `planner` / `experiment-worker` |
| **Isolation** | Separate worktrees per polecat | Shared repo, with isolation coming from task scope and agent instructions | Background `experiment-worker` subagents running in isolated worktrees |
| **Setup cost** | Higher: rig install, directives, overlays, scheduler tuning | Lower: open the repo and run Codex with the checked-in config | Lower than Gastown: open the repo in Claude Code and use the checked-in agents/settings |
| **Best at** | Larger waves, explicit operator audit trail, stronger worker separation | Fast iteration, lighter operator overhead, staying entirely inside one repo | Repo-local steering with stronger per-worker checkout isolation than the Codex path |
| **Memory model** | Beads and convoy notes are first-class control-plane objects | Markdown notes in `research/` are the first-class memory | Markdown notes in `research/` are the first-class memory, with `memory-keeper` folding worker output back into the main checkout |

The practical tradeoff:

- Use **Gastown** when you want explicit work queues, named workers, and hard
  separation between parallel experiments.
- Use **Codex subagents** when you want roughly the same planner/worker
  discipline with less machinery and more direct steering from one parent
  session.
- Use **Claude Code** when you want a repo-local parent session but still want
  background workers and worktree isolation for parallel experiments.

In the Hub-oriented stack, only the control plane changes. HF Jobs and Trackio
can stay exactly the same underneath any of the three workflows.


## HF Jobs: the execution plane

Once the control plane decides what to run, Hugging Face Jobs handles the
execution. The launcher (`scripts/hf_job.py`) renders a self-contained UV script
from the current workspace, bundles it with the experiment's `train.py`, and
submits it as a managed job:

```bash
python3 scripts/hf_job.py launch --mode experiment
```

Under the hood, this calls `hf jobs uv run` with explicit hardware, timeout, secrets, and a mounted cache bucket:

```bash
hf jobs uv run \
  --flavor h200 \
  --timeout 90m \
  --namespace burtenshaw \
  --detach \
  --label autolab \
  --label bead=au-2rf \
  --label hypothesis=warmdown_ratio_0_925 \
  --secrets HF_TOKEN \
  --volume "hf://buckets/burtenshaw/autolab-cache:/autolab-home/.cache/autoresearch" \
  .runtime/autolab-hf-job.py
```

Labels tie each job back to the bead that created it. Each run takes roughly 5 minutes of actual training (~300 seconds on H200), and the final summary block contains everything needed to evaluate the result:

```
val_bpb:          0.958973
training_seconds: 300.0
peak_vram_mb:     33609.6
mfu_percent:      46.79
total_tokens_M:   324.8
num_steps:        2478
```

The shared HF bucket means you only pay the data bootstrap cost once. After the first `--mode prepare` job primes the cache, every subsequent experiment reuses it.

### Inspecting jobs

```bash
# Check a specific job
python3 scripts/hf_job.py inspect 69c7b085bf20ec90acee3a4f

# Stream logs from a running job
python3 scripts/hf_job.py logs 69c7b085bf20ec90acee3a4f --follow

# List all autolab-tagged jobs
hf jobs ps --namespace burtenshaw
```


## The failure and retry path

In the `2026-03-28-wave2` wave, several jobs timed out or hit environment errors. Without structured tracking, those failures are noise in a terminal history. With beads, each failure is a closed record with a reason:

```bash
bd show --long --id au-yfd
# Status: CLOSED
# Notes: "HF job 69c7a... timed out after 90m.
#         Hypothesis was valid but execution failed.
#         Replacement bead: au-2rf"
```

The replacement bead (`au-2rf`) carries a reference to the original, so the retry chain is inspectable:

```bash
bd show --long --id au-2rf
# Status: COMPLETED
# Notes: "Retry of au-yfd. HF job 69c7b085bf20ec90acee3a4f
#         completed with val_bpb=0.958973.
#         Submitted as patch 14822."
```

Failures aren't always handled automatically. What matters is that they're **preserved as named objects** with enough context to understand what went wrong and what replaced them.


## Trackio: the retrospective layer

Trackio turns the control-plane events and execution metadata into something you can browse after the wave is over. The reporter script syncs HF Jobs status, bead state, and metrics into a local Trackio project:

```bash
# Sync a specific wave
python3 scripts/trackio_reporter.py sync \
  --project autolab \
  --wave-id 2026-03-28-wave2

# Generate the deck summary
python3 scripts/trackio_reporter.py deck-summary \
  --wave-id 2026-03-28-wave2

# Export investigation assets
python3 scripts/trackio_reporter.py deck-assets \
  --wave-id 2026-03-28-wave2
```

This produces three things:

1. **A wave report** — master baseline, hypothesis themes, win/loss counts, and the ranked leaderboard
2. **A timeline table** — every control-plane event in chronological order (bead created, polecat assigned, job launched, job completed, result recorded)
3. **A job board** — every HF Job with its bead, status, hypothesis, and final metric

You can also run the live dashboard:

```bash
trackio show --project autolab
```

The dashboard surfaces anomalies that matter during active waves: duplicate jobs burning the same hypothesis, stale beads still marked as running, prepare jobs tied to closed beads. But the more important use case is after the wave finishes — when someone who wasn't watching the system live needs to understand what happened.

### Publishing to the Hub

The final step pushes the Trackio project to a Hugging Face Space, which becomes the durable retrospective interface:

```bash
trackio sync \
  --project autolab \
  --space-id burtenshaw/autolab-trackio
```


## The full investigation sequence

After a wave finishes, you can reconstruct the full story from any starting point:

```bash
# Start from the batch
gt convoy status

# Drill into one hypothesis
bd show --long --id au-2rf

# See who ran it
gt polecat status autolab/turquoise

# Check the raw execution
python3 scripts/hf_job.py inspect 69c7b085bf20ec90acee3a4f

# See how it unfolded in context
python3 scripts/trackio_reporter.py summary --max-jobs 40

# Look at the polecat's terminal history
gt peek autolab/turquoise -n 200
```

Each layer gives you a different resolution: the convoy tells you the batch, the bead tells you the hypothesis, the polecat tells you who ran it, the HF Job tells you what executed, and Trackio tells you how it all unfolded.


## What this gets you

The automation is straightforward — dispatching shell commands to cloud GPUs. The harder part is **retrospective legibility**.

After a wave of 7–10 parallel experiments finishes, anyone can:

- See which hypotheses were tested and which won
- Trace any result back to its exact `train.py` diff
- Understand why a particular run failed and what replaced it
- Compare results against the hosted master baseline
- Find the Trackio timeline to see the order of operations

You do not need to watch the system live to understand what happened.


## Getting started

The repo is at [burtenshaw/autolab-gastown](https://github.com/burtenshaw/autolab-gastown). The direct operator path (no Gastown required) is:

```bash
git clone https://github.com/burtenshaw/autolab-gastown.git
cd autolab-gastown
uv sync
cp .autolab.credentials.example ~/.autolab/credentials
# Edit credentials with your Autolab endpoint and HF namespace
hf auth login
bash scripts/bootstrap_public.sh
```

From there you can choose whichever control plane fits the wave:

- **Gastown**: follow [the Gastown guide](docs/gastown-codex-guide.md) if you
  want convoys, beads, polecats, and a more explicit multi-worker rig.
- **Codex subagents**: follow [the Codex subagents guide](docs/codex-subagents-guide.md)
  if you want to stay inside one repo-local parent session and delegate through
  checked-in custom agents.
- **Claude Code**: follow [the Claude Code guide](docs/claude-subagents-guide.md)
  if you want a repo-local parent session with checked-in project agents,
  worktree-isolated workers, and a shared markdown notebook.

If you're undecided:

- start with **Codex subagents** for one planner and one worker
- move to **Claude Code** when you want a similar repo-local flow but cleaner
  worker isolation
- move to **Gastown** once you need stronger isolation and more formal wave management
