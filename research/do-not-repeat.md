# Autolab Do-Not-Repeat Ledger

Use this ledger to keep failed or stale ideas searchable.

## Duplicate Rule

Treat two experiments as duplicates if they share:

- the same parent master hash
- the same subsystem or change class
- the same hypothesis in materially similar form

## Known Regressions

### Throughput / Batching

- Master `765a36b0700b3a20d552f48b8ca2b75636aa3e69`: increasing both
  `DEVICE_BATCH_SIZE` and `TOTAL_BATCH_SIZE` to a 96-token microbatch fit in
  memory but did not materially improve tok/sec and likely lost too many update
  steps inside the 300-second budget.

## Stale-Master Notes

- If master changes materially after planning but before a worker runs or
  submits, stop and replan instead of improvising on stale context.
