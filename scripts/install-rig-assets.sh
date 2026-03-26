#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
Usage: scripts/install-rig-assets.sh [RIG_ROOT]

Copy the checked-in Gas Town autolab rig assets into a live Gas Town rig
container. Defaults to ~/gt/autolab.
EOF
  exit 0
fi

TARGET_ROOT="${1:-$HOME/gt/autolab}"

mkdir -p \
  -- \
  "$TARGET_ROOT/directives" \
  "$TARGET_ROOT/formula-overlays" \
  "$TARGET_ROOT/templates"

install -m 0644 "$ROOT/gastown/directives/crew.md" \
  "$TARGET_ROOT/directives/crew.md"
install -m 0644 "$ROOT/gastown/directives/polecat.md" \
  "$TARGET_ROOT/directives/polecat.md"
install -m 0644 "$ROOT/gastown/formula-overlays/mol-polecat-work.toml" \
  "$TARGET_ROOT/formula-overlays/mol-polecat-work.toml"
install -m 0644 "$ROOT/gastown/templates/experiment-bead.md" \
  "$TARGET_ROOT/templates/experiment-bead.md"
install -m 0644 "$ROOT/gastown/templates/convoy-template.md" \
  "$TARGET_ROOT/templates/convoy-template.md"
install -m 0644 "$ROOT/gastown/taxonomy.md" \
  "$TARGET_ROOT/taxonomy.md"
install -m 0644 "$ROOT/gastown/convoys.md" \
  "$TARGET_ROOT/convoys.md"
install -m 0644 "$ROOT/gastown/day-1-checklist.md" \
  "$TARGET_ROOT/day-1-checklist.md"
install -m 0644 "$ROOT/docs/gastown-codex-guide.md" \
  "$TARGET_ROOT/instructions.md"

printf 'installed rig assets into %s\n' "$TARGET_ROOT"
