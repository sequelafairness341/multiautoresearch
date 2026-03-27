# Script Reference

These scripts are the public operator entrypoints for this repo.

## Summary

| Script | Purpose | External Systems | Safe Without Gastown |
| --- | --- | --- | --- |
| `scripts/refresh_master.py` | Refresh current benchmark master into local files | Autolab API | Yes |
| `scripts/hf_job.py` | Preflight, render, launch, inspect, and tail managed HF Jobs | Hugging Face Jobs, local files | Yes |
| `scripts/parse_metric.py` | Parse the final metric block from a run log | Local files only | Yes |
| `scripts/submit_patch.py` | Submit a winning unified diff to hosted Autolab | Autolab API | Yes |
| `scripts/trackio_reporter.py` | Sync jobs to Trackio and render a local dashboard | Hugging Face Jobs, Trackio, local files | Yes |

## `scripts/refresh_master.py`

- Inputs:
  - `--fetch-dag`
  - `--force`
- Environment:
  - `AUTOLAB` optional, defaults to `http://autoresearchhub.com`
  - `AUTOLAB_HTTP_TIMEOUT` optional
  - `AUTOLAB_HTTP_RETRIES` optional
- Outputs:
  - rewrites `train.py`, `train_orig.py`, and files under `research/live/`
- Use when:
  - starting any fresh benchmark run
  - re-syncing local state to hosted benchmark truth

## `scripts/hf_job.py`

- Inputs:
  - `preflight`, `render`, `launch`, `inspect`, `logs`
- Environment:
  - `AUTOLAB_HF_BUCKET` required for `prepare` and `experiment`
  - `AUTOLAB_HF_NAMESPACE` recommended
  - `AUTOLAB_HF_PREPARE_FLAVOR`, `AUTOLAB_HF_PREPARE_TIMEOUT`
  - `AUTOLAB_HF_EXPERIMENT_FLAVOR`, `AUTOLAB_HF_EXPERIMENT_TIMEOUT`
  - `AUTOLAB_HF_CLI` optional
  - `AUTOLAB_HF_SECRETS` optional
- Outputs:
  - rendered job bundles under `.runtime/`
  - job metadata under `.runtime/hf-jobs/`
  - streamed logs when requested
- Use when:
  - validating a workspace before launch
  - starting and monitoring managed benchmark runs

## `scripts/parse_metric.py`

- Inputs:
  - a path to a job or local run log
- Environment:
  - none
- Outputs:
  - JSON metric block to stdout
- Use when:
  - extracting `val_bpb`, timing, and utilization metrics after a completed run

## `scripts/submit_patch.py`

- Inputs:
  - `--comment`
  - optional `--priority`, `--parent-hash`, `--dry-run`
- Environment:
  - `AUTOLAB_KEY` required for real submission
  - `AUTOLAB` optional, defaults to `http://autoresearchhub.com`
- Outputs:
  - submits the unified diff from `train_orig.py` to `train.py`
  - prints backend response JSON
- Use when:
  - you have a real improvement over the current hosted master

## `scripts/trackio_reporter.py`

- Inputs:
  - `sync`, `dashboard`, `summary`
- Environment:
  - `AUTOLAB_TRACKIO_PROJECT` optional, defaults to `autolab`
  - `AUTOLAB_HF_NAMESPACE` recommended
  - `AUTOLAB_HF_CLI` optional
  - `AUTOLAB_TRACKIO_BIN` optional
- Outputs:
  - local reporter state and markdown summaries under `.runtime/`
  - Trackio runs and dashboard output
- Use when:
  - checking active jobs
  - finding duplicate launches
  - monitoring experiment results locally
