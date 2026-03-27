# Security Policy

## Secrets

Keep all credentials out of the repository.

- Store Autolab credentials in `~/.autolab/credentials`.
- Authenticate the Hugging Face CLI out of band with `hf auth login`.
- Treat `AUTOLAB_KEY`, `HF_TOKEN`, and any private Autolab endpoint details as
  secrets.

Do not paste secrets into:

- git history
- public issues
- pull requests
- `research/notes.md`
- Trackio reports or shared screenshots

## Sensitive Local State

These paths are local operator state and should not be committed:

- `~/.autolab/credentials`
- `.runtime/`
- `.beads/`
- `.logs/`
- `.codex/`

`research/live/*` is generated benchmark state fetched from the hosted backend.
Treat it as disposable cache and regenerate it with
`python3 scripts/refresh_master.py --fetch-dag`.

## Reporting A Security Issue

If the issue involves credentials, private endpoints, or backend access control:

- do not open a public issue with the full details
- use the same private channel you used to obtain Autolab access, or contact
  the maintainers directly

If you accidentally exposed a token:

1. revoke it
2. rotate it
3. scrub the local copies
4. notify the maintainers privately if the token reached shared infrastructure
