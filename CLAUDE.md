@AGENTS.md
@docs/claude-subagents-guide.md

## Claude Code

- Use the checked-in project subagents from `.claude/agents/`.
- Prefer `planner` for fresh experiment queues, `reviewer` for read-only rule checks, `experiment-worker` for one benchmark run, and `memory-keeper` to persist results in the main checkout.
- Keep active `experiment-worker` count at or below real GPU capacity.
- Keep worker benchmark logs under `research/live/` so parallel workers do not collide on `/tmp/autolab-run.log`.
- Keep per-developer Claude overrides in `.claude/settings.local.json`; `.worktreeinclude` copies that file into Claude worktrees when present.
