# Troubleshooting

## `missing required credentials`

Cause:

- `~/.autolab/credentials` is missing or incomplete

Fix:

```bash
mkdir -p ~/.autolab
cp .autolab.credentials.example ~/.autolab/credentials
$EDITOR ~/.autolab/credentials
. ~/.autolab/credentials
```

## `hf auth whoami` fails

Cause:

- the Hugging Face CLI is not authenticated on this machine

Fix:

```bash
hf auth login
hf auth whoami
```

## `refresh_master.py` times out on commit detail

Cause:

- the hosted backend took too long to serve `/api/git/commits/<hash>`

Current behavior:

- `scripts/refresh_master.py` retries and then falls back to
  `research/live/master_detail.json` when the cached detail matches the current
  master hash

Fix:

- rerun `python3 scripts/refresh_master.py --fetch-dag`
- if the cache is stale, fix the backend or fetch a fresh matching detail file

## Duplicate HF Jobs For One Bead

Cause:

- a bead was launched by both the managed rig path and a manual HF Jobs launch
- or a stale launcher retried after a manual submission already succeeded

Fix:

```bash
uv run scripts/trackio_reporter.py summary --max-jobs 25
hf jobs ps --namespace "$AUTOLAB_HF_NAMESPACE"
hf jobs cancel <DUPLICATE_JOB_ID>
```

Keep only one active job per bead and update the bead notes with the surviving
job id.

## Stale Polecat Session State

Symptoms:

- `gt polecat status` says a worker is running
- `tmux list-sessions` does not show the matching session
- the bead is hooked or in progress but no useful work is happening

Fix:

- inspect the worktree directly under `~/gt/<rig>/polecats/<name>/`
- verify the current `train.py` diff against `train_orig.py`
- either relaunch one managed job or clean up the stale worker state before
  assigning that bead again

## `val_bpb not found`

Cause:

- the job ended early
- the log never reached final evaluation
- you parsed the wrong log file

Fix:

```bash
python3 scripts/hf_job.py logs <JOB_ID> --follow --output /tmp/autolab-run.log
python3 scripts/parse_metric.py /tmp/autolab-run.log
```

If the log still lacks `val_bpb`, treat the run as non-comparable and do not
submit it.
