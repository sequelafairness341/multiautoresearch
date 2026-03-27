# Hosted Backend Contract

This repo targets a hosted Autolab service. The backend is not bundled here.

All local operator commands treat `AUTOLAB` as the base URL for that service.

## Authentication Model

- Read-only benchmark refresh endpoints are used without auth by the current
  client scripts.
- Patch submission uses bearer authentication via `AUTOLAB_KEY`.

The local credentials contract is:

```bash
export AUTOLAB="https://your-autolab-host.example"
export AUTOLAB_KEY="replace-with-your-autolab-api-key"
```

## Required Endpoints

### `GET /api/git/master`

Used by `scripts/refresh_master.py`.

Minimum response contract:

```json
{
  "hash": "765a36b0700b3a20d552f48b8ca2b75636aa3e69",
  "val_bpb": 0.962777
}
```

Required fields:

- `hash`: current benchmark master hash

Common fields:

- `val_bpb`: current master score

### `GET /api/git/commits/<hash>`

Used by `scripts/refresh_master.py`.

Minimum response contract:

```json
{
  "hash": "765a36b0700b3a20d552f48b8ca2b75636aa3e69",
  "source": "<full train.py source as a string>"
}
```

Accepted hash placement:

- top-level `hash`
- nested `commit.hash`

Required field:

- `source`: the full benchmark-master `train.py` source

### `GET /api/git/dag`

Used by `scripts/refresh_master.py --fetch-dag`.

The local client stores this payload verbatim in `research/live/dag.json`. The
schema can evolve, but it must remain valid JSON.

### `POST /api/patches`

Used by `scripts/submit_patch.py`.

Request headers:

```text
Authorization: Bearer <AUTOLAB_KEY>
Content-Type: application/json
```

Request body:

```json
{
  "parent_hash": "765a36b0700b3a20d552f48b8ca2b75636aa3e69",
  "diff": "--- train_orig.py\n+++ train.py\n...",
  "comment": "one-sentence hypothesis and observed val_bpb",
  "priority": 0
}
```

The diff must be a unified diff from `train_orig.py` to `train.py`.

## Client Expectations

The public repo assumes:

- `scripts/refresh_master.py` can refresh master source at any time
- `scripts/submit_patch.py` can submit directly to the hosted backend
- users do not need repo git history to know benchmark truth

If you change the hosted API contract, update the public docs and the client
scripts in the same repo change.
