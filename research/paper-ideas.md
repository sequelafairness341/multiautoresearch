# Hugging Face Paper Ideas

Use this file to turn literature scans into Autolab-ready hypotheses.

Rules:

- Start from current hub master and refreshed DAG state.
- Propose only ideas that fit a single disciplined change in `train.py`.
- Reject ideas that are already present in the current code or already tested in
  `research/notes.md`.
- Promote only one hypothesis per bead.

## Current Paper-Derived Candidates

### Selective attention temperature

- Paper: `2411.12892` "Selective Attention: Enhancing Transformer through
  Principled Context Control"
- Why it matches this repo:
  - `train.py` already normalizes `q` and `k`, so the clean insertion point is
    the attention logit scale after QK normalization.
  - The model already uses lightweight value gating, so query-temperature or
    value-temperature extensions are architecturally compatible.
- Smallest credible experiments:
  - add one scalar attention-temperature multiplier to the attention logits
  - add one learned per-layer or per-head inverse-temperature initialized at
    `1.0`
- Keep it single-change:
  - do not combine query-temperature and value-temperature in the same run
  - do not change the window pattern in the same bead
- Main risk:
  - over-sharpening attention may hurt sliding-window layers

### Power-law cooldown schedule

- Paper: `2408.13359` "Power Scheduler: A Batch Size and Token Number Agnostic
  Learning Rate Scheduler"
- Related cooldown analysis: `2508.01483` "Training Dynamics of the Cooldown
  Stage in Warmup-Stable-Decay Learning Rate Scheduler"
- Why it matches this repo:
  - the current schedule is a simple linear warmdown controlled by
    `WARMDOWN_RATIO` and `FINAL_LR_FRAC`
  - scheduler shape is isolated in `get_lr_multiplier`, so this is a clean
    one-function change
- Smallest credible experiments:
  - replace linear cooldown with a power-law cooldown using one new exponent
    hyperparameter
  - keep the same `FINAL_LR_FRAC` and only vary the cooldown curve shape
- Main risk:
  - changing both the cooldown shape and floor at once would make attribution
    poor

### Gradient-preserving activation scaling

- Paper: `2506.22049` "GPAS: Accelerating Convergence of LLM Pretraining via
  Gradient-Preserving Activation Scaling"
- Why it matches this repo:
  - the model is Pre-LN/RMSNorm and already has explicit residual mixing
    parameters, so residual-path balance is clearly part of the design space
  - GPAS can be tested as a local block-output scaling change without touching
    `prepare.py`
- Smallest credible experiments:
  - add one fixed or learned GPAS-style scale on block outputs while preserving
    gradients with a stop-gradient trick
  - apply it to either the attention output or the MLP output, not both
- Main risk:
  - this is a larger code change than an LR tweak, so isolate it aggressively

### Muon variance adaptation follow-ups

- Papers:
  - `2510.05491` "NorMuon: Making Muon more efficient and scalable"
  - `2601.14603` "Variance-Adaptive Muon: Accelerating LLM Pretraining with
    NSR-Modulated and Variance-Scaled Momentum"
- Why it matches this repo:
  - `train.py` already contains NorMuon-style row/column variance normalization
    in `muon_step_fused`
  - the current Muon groups still default `beta2=0.0`, so the second-moment path
    is underused by default
- Smallest credible experiments:
  - enable a non-zero Muon `beta2`
  - change only the variance statistic or normalization axis, not both
- Main risk:
  - treat this as a follow-up to the current optimizer, not a brand-new
    direction

## Low-Priority Ideas

- `2311.00684` attention alignment for long-context extrapolation:
  interesting but less aligned with the fixed short-budget Autolab benchmark.
- Structured FFN or architecture-replacement papers:
  too invasive for disciplined one-change comparisons here.

## Additional Ranked Candidates

### Local-global window interleave

- Paper: `2408.00118`
- Why it matches this repo:
  - `WINDOW_PATTERN` is already an explicit layerwise attention-pattern knob
  - switching from `SSSL` to `SLSL` is a one-string architectural test, not a
    subsystem rewrite
- Smallest credible experiment:
  - change only `WINDOW_PATTERN` from `"SSSL"` to `"SLSL"`
- Main risk:
  - a denser global pattern may buy quality at the cost of throughput or memory

### Grouped-query attention

- Paper: `2305.13245`
- Why it matches this repo:
  - attention already supports `n_kv_head <= n_head`
  - the current builder still ties `n_kv_head = num_heads`, so halving KV heads
    is a clean existing-capability toggle
- Smallest credible experiment:
  - set `n_kv_head = num_heads // 2`
- Main risk:
  - this changes parameter count and attention cache structure, so compare it
    carefully against optimizer-only wins

### Denser value-embedding cadence

- Paper: `2410.17897`
- Why it matches this repo:
  - the model already has explicit value-embedding placement and gating logic
  - recent wins suggest this subsystem is live rather than decorative
- Smallest credible experiment:
  - change `has_ve()` cadence from every third layer to every second layer
- Main risk:
  - this is adjacent to the current value-embedding regularization line, so keep
    it isolated from any weight-decay changes

### Attention branch scale reset

- Paper: `2305.02790`
- Why it matches this repo:
  - the block already hardcodes a non-residual attention amplification
  - testing `1.0` versus `1.3` is a scalar-only branch-balance experiment
- Smallest credible experiment:
  - change the attention branch scale from `1.3` to `1.0`
- Main risk:
  - the current scale may already be compensating for another architectural
    choice, so this can regress sharply
