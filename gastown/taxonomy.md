# Autolab Taxonomy

Use a narrow, explicit vocabulary so experiment state is searchable and duplicate
work is easy to spot.

## Recommended Bead Types

- `task`
  Standard experiment candidate.
- `question`
  Result interpretation, unclear regression, or follow-up decision.
- `docs`
  Research synthesis, win summaries, and operating notes.

## Recommended Labels

Core labels:
- `autolab:experiment`
- `autolab:submitted`
- `autolab:won`
- `autolab:regressed`
- `autolab:duplicate`
- `autolab:do-not-repeat`

Change-class labels:
- `autolab:optimizer`
- `autolab:architecture`
- `autolab:attention`
- `autolab:ffn`
- `autolab:normalization`
- `autolab:batching`
- `autolab:throughput`
- `autolab:schedule`
- `autolab:regularization`

Control labels:
- `autolab:planner`
- `autolab:stale-master`
- `autolab:needs-rebase`
- `autolab:retry-authorized`

## Required Experiment Metadata

Every experiment bead should contain:

- hypothesis: one sentence
- parent master hash
- master val_bpb at dispatch time
- exact single variable being changed
- expected upside
- reason it is not a duplicate

Every completed experiment should record:

- local val_bpb
- submit or no-submit decision
- short interpretation
- failure mode if regressed or invalid

## Duplicate Rules

Treat two beads as duplicates if they share all of:

- same parent master hash
- same subsystem or change class
- materially same hypothesis

If a follow-up is intentional, make that explicit by naming the changed variable.

Bad:
- "try optimizer tweak again"

Good:
- "repeat lower beta2 on latest master after warmup schedule changed"

