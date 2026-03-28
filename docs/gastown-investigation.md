# Investigating Live Runs

In this repo, a live Autolab run usually looks like:

1. a bead tracks the hypothesis
2. a convoy tracks the batch
3. a polecat owns the work
4. the actual timed benchmark runs as a Hugging Face Job

Use the commands below in that order. Start broad, then drill down.

## 1. See What Is Active

```bash
gt convoy status
gt polecat list autolab
gt crew status --rig autolab
```

Use these when you want the current map of the system:

- `gt convoy status` shows the active convoys and the beads they track.
- `gt polecat list autolab` shows which polecats are working, done, or stuck.
- `gt crew status --rig autolab` shows the persistent control-plane workers such as `researcher` and `reporter`.

## 2. Inspect One Bead

```bash
gt show <BEAD_ID>
bd show <BEAD_ID> --long
bd show <BEAD_ID> --watch
```

This is the fastest way to answer:

- what hypothesis this run is testing
- whether the bead is still `hooked`, `in_progress`, or closed
- which worker owns it
- whether notes already include the HF job id or score

Use `bd show <BEAD_ID> --watch` if you want the bead view to refresh while the run is still moving.

## 3. Inspect One Polecat

```bash
gt polecat status autolab/<POLECAT>
gt peek autolab/<POLECAT> -n 200
```

Use these when the bead says work is active but you want to know what the worker is actually doing:

- `gt polecat status autolab/<POLECAT>` shows lifecycle state, assigned bead, session state, and last activity time.
- `gt peek autolab/<POLECAT> -n 200` shows the recent terminal output from that worker session.

The argument to `gt polecat status` is a single value in `<rig>/<polecat>` form, for example `autolab/quartz`.

If the session output looks stale, inspect the worktree directly:

```bash
cd ~/gt/autolab/polecats/<POLECAT>/autolab
git status --short
git diff -- train.py
```

## 4. Inspect A Crew Worker

```bash
gt crew status reporter --rig autolab
gt peek autolab/crew/reporter -n 200
```

Use this pattern for long-lived control-plane workers such as `planner`,
`researcher`, and `reporter`.

- `gt crew status reporter --rig autolab` shows session state, git status, branch info, and inbox state.
- `gt peek autolab/crew/reporter -n 200` shows the recent output from that worker session.

Swap `reporter` for the worker you care about.

## 5. Watch Town-Level Activity

```bash
gt feed --rig autolab
gt feed --problems --rig autolab
```

Use `gt feed --rig autolab` when you want the live event stream across the rig.

Use `gt feed --problems --rig autolab` when you want the fastest view of workers that look stuck, quiet, or unhealthy.

## 6. Follow The Actual Benchmark Job

Gas Town owns the workflow, but the timed benchmark itself runs on Hugging Face Jobs. Once you have the job id from the bead notes or reporter summary, use:

```bash
uv run scripts/trackio_reporter.py summary --max-jobs 25
python3 scripts/hf_job.py inspect <JOB_ID>
python3 scripts/hf_job.py logs <JOB_ID> --follow --output /tmp/autolab-run.log
python3 scripts/parse_metric.py /tmp/autolab-run.log
```

Use these to answer:

- which jobs are still running
- whether one bead accidentally launched multiple jobs
- whether the remote job is progressing normally
- what final `val_bpb` was recorded

## 7. Common Investigation Paths

### The bead is active, but I do not know who owns it

```bash
gt show <BEAD_ID>
gt convoy status
```

### The polecat looks alive, but I cannot tell if it is making progress

```bash
gt polecat status autolab/<POLECAT>
gt peek autolab/<POLECAT> -n 200
gt feed --problems --rig autolab
```

### The worker looks fine, but I need the real score

```bash
uv run scripts/trackio_reporter.py summary --max-jobs 25
python3 scripts/hf_job.py logs <JOB_ID> --follow --output /tmp/autolab-run.log
python3 scripts/parse_metric.py /tmp/autolab-run.log
```

### The rig says something is running, but nothing useful is happening

```bash
gt polecat status autolab/<POLECAT>
gt peek autolab/<POLECAT> -n 200
bd show <BEAD_ID> --long
```

If the worker is stale, continue with the cleanup guidance in
[troubleshooting.md](troubleshooting.md).
