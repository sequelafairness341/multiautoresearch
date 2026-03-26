# Autolab Day-1 Checklist

Use this when turning the scaffold into a live rig.

## Rig Setup

1. Create or select the `autolab` rig.
2. Install the directives:
   - `directives/crew.md`
   - `directives/polecat.md`
3. Install the formula overlay:
   - `formula-overlays/mol-polecat-work.toml`
4. Decide who is the planner:
   - one crew worker or the Mayor
5. Set scheduler capacity to real GPU count.

## Research Discipline

1. Define the bead label vocabulary from `taxonomy.md`.
2. Create one convoy for the initial research theme.
3. Use one planner and one worker first.
4. Do not add more workers until duplicate-prevention is actually working.

## Live Autolab Setup

1. Verify an H100 is available.
2. Register or load autolab credentials.
3. Create the local autolab contributor workspace.
4. Fetch the current master and full experiment DAG.
5. Read the research history before running any experiment.
6. Dispatch only one fresh hypothesis per GPU slot.

## First Success Criteria

You are ready to scale beyond one worker only when:

- experiment beads are consistently well-formed
- recent failures are being recorded clearly
- duplicate experiments are being avoided
- the planner is reacting to new master changes quickly

