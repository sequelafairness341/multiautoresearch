# Experiment: <short title>

## Hypothesis

<One sentence. What single change do you expect to help, and why?>

## Parent Context

- Parent master hash: `<hash>`
- Master val_bpb at dispatch: `<value>`
- Campaign: `<theme>`

## Single Variable

<What exact variable, knob, or logic change is being tested?>

## Expected Upside

<Why this might improve val_bpb or effective throughput inside the 5-minute budget>

## Duplicate Check

<Why this is not a duplicate of an open or recent experiment>

## Allowed Edit Scope

- `train.py` only

## Run Plan

- Refresh master with `python3 scripts/refresh_master.py --fetch-dag`
- Log path: `research/live/<experiment-id>.log`
- Run `CUDA_VISIBLE_DEVICES=<gpu> ./run-local.sh research/live/<experiment-id>.log`
- Parse `python3 scripts/parse_metric.py research/live/<experiment-id>.log`

## Result

- Local val_bpb: `<value>`
- Submitted: `yes|no`
- Interpretation: `<one or two sentences>`
- Failure mode, if any: `<brief note>`

## Memory-Keeper Handoff

- One short note for `research/notes.md`: `<summary>`
- Any do-not-repeat update: `<summary or none>`
