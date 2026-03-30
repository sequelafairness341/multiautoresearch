#!/usr/bin/env python3
"""Print a parent-session kickoff prompt for the repo's Codex subagents."""

from __future__ import annotations

import argparse
from pathlib import Path


def build_prompt(repo_root: Path, campaign: str, gpu_slots: int, max_ideas: int) -> str:
    return f"""Open Codex in:
{repo_root}

Use a parent prompt like:

You are coordinating autolab experiments in this repo.

Read:
- AGENTS.md
- README.md
- docs/codex-subagents-guide.md
- research/notes.md
- research/do-not-repeat.md
- research/campaigns/
- research/experiments/
- research/reference/master.seed.json
- research/reference/dag.seed.json

Spawn the `planner` subagent and ask it for up to {max_ideas} fresh,
non-duplicate experiments for the campaign "{campaign}".

Do not run more than {gpu_slots} `experiment_worker` subagents concurrently.
Use `reviewer` for read-only rule checks when a plan or result looks borderline.
After each worker finishes, use `memory_keeper` to update the durable ledger and
campaign note.

Keep all experiments comparable:
- refresh from current master
- edit `train.py` only unless explicitly authorized otherwise
- one hypothesis change per run
- run the canonical timed benchmark
- submit only if local `val_bpb` beats current master
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print a standard kickoff prompt for the repo's Codex subagent workflow."
    )
    parser.add_argument(
        "--campaign",
        default="recent-master: follow-ups",
        help="Campaign name to mention in the kickoff prompt.",
    )
    parser.add_argument(
        "--gpu-slots",
        type=int,
        default=1,
        help="Maximum concurrent experiment workers to allow.",
    )
    parser.add_argument(
        "--max-ideas",
        type=int,
        default=3,
        help="Maximum number of experiment ideas to ask the planner for.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    print(build_prompt(repo_root, args.campaign, args.gpu_slots, args.max_ideas))


if __name__ == "__main__":
    main()
