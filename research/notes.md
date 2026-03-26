# Autolab Notes

## Repo layout

- Seed hub snapshots live in `research/reference/`.
- Live hub refreshes should be written to `research/live/`.
- Archived local experiment diffs live in `research/diffs/`.

## Local environment

- GPU: NVIDIA H100 80GB HBM3 (GPU 0)
- Local host GLIBC is 2.31, so the Hopper-only `varunneal/flash-attention-3` wheel does not import here.
- Local runs use `sitecustomize.py` plus `run-local.sh` to redirect that kernel lookup to `kernels-community/flash-attn3` without editing `train.py`.

## Baseline

- Master hash: `765a36b0700b3a20d552f48b8ca2b75636aa3e69`
- Hub master val_bpb: `0.962777`
- Local baseline val_bpb under compatibility redirect: `0.962846`
- Local baseline peak_vram_mb: `33609.3`
- Local baseline mfu_percent: `43.84`
- Local baseline total_tokens_M: `304.5`
- Local baseline num_steps: `2323`

## Experiment: batch96

Hypothesis:
- Increase microbatch and total batch together to exploit large VRAM headroom while keeping `grad_accum_steps=1`.

Change:
- `DEVICE_BATCH_SIZE = 96`
- `TOTAL_BATCH_SIZE = 96 * 2048`

Observed early behavior:
- Peak memory around 50 GB, so it fits.
- Steady-state tok/sec stayed roughly flat around 1.02M to 1.04M instead of increasing materially.
- Training steps over the 300-second budget dropped substantially relative to baseline.

Conclusion:
- This looks weak. It spent much more memory for little or no throughput gain and likely sacrifices update count.
- Keep the diff in `research/diffs/batch96.diff` for reference, but do not treat it as a leading candidate.

## Experiment: flr021

Hypothesis:
- Lower the final LR floor from `0.025` to `0.021`.
- Post-master hub history showed `FINAL_LR_FRAC=0.021` as the strongest near-miss after current master.

Change:
- `FINAL_LR_FRAC = 0.021`

Result:
- Local val_bpb: `0.962717`
- Local training_seconds: `300.1`
- Local total_seconds: `383.7`
- Local peak_vram_mb: `33612.7`
- Local mfu_percent: `43.88`
- Local total_tokens_M: `304.7`
- Local num_steps: `2325`

Conclusion:
- This beat both the local baseline (`0.962846`) and the current hub master (`0.962777`).
- Submitted as patch `14808` against master `765a36b0700b3a20d552f48b8ca2b75636aa3e69`.
- Workspace `train.py` was reset back to master after submission so the next experiment starts clean.
