# Gas Town Mode

This repo supports two operator modes:

- direct script-driven operation
- Gas Town orchestration with planner, polecats, researcher, and reporter roles

Direct mode is the simplest way to try the benchmark. Gas Town mode is the
right choice when you want parallel experiment management and role separation.

## Install The Rig

```bash
gt rig add autolab <repo-url>
./scripts/install-rig-assets.sh ~/gt/autolab
./scripts/install-rig-assets.sh --check ~/gt/autolab
```

The install copies:

- planner and polecat directives
- convoy and experiment templates
- taxonomy and checklist docs
- the detailed Codex operator guide
- paper idea notebook seed

## Recommended Roles

### Planner

Owns:

- reading `research/notes.md` and `research/paper-ideas.md`
- creating experiment beads
- keeping hypotheses non-overlapping
- deciding which runs are worth launching

### Polecats

Own:

- one benchmark run each
- one hypothesis change each
- result capture and submission only on a real win

### Researcher

Owns:

- Hugging Face paper scouting
- translating papers into clean single-change `train.py` ideas
- maintaining the rig-level paper notebook

### Reporter

Owns:

- local Trackio sync
- duplicate-job detection
- slot-leak detection
- operator summaries before new launches

## Bring Up Dedicated Workers

```bash
cd ~/gt/autolab
gt crew add researcher --rig autolab
gt crew add reporter --rig autolab
```

The live rig directives recognize the `researcher` and `reporter` workspaces as
specialized control-plane roles.

## Operating Rules

- refresh from hosted master before every experiment
- use exactly one hypothesis change per bead
- avoid launching multiple workers into the same hypothesis bucket
- consult the reporter summary before opening more paid slots

## Detailed Guide

For the longer operator walkthrough, see
[gastown-codex-guide.md](gastown-codex-guide.md).
