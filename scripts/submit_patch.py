#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from difflib import unified_diff
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_credentials() -> dict[str, str]:
    creds: dict[str, str] = {}
    creds_path = Path.home() / ".autolab" / "credentials"
    if creds_path.exists():
        for line in creds_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            creds[key] = value

    creds.update({k: v for k, v in os.environ.items() if k in {"AUTOLAB", "AUTOLAB_KEY"}})
    if "AUTOLAB" not in creds:
        creds["AUTOLAB"] = "http://autoresearchhub.com"
    missing = [key for key in ("AUTOLAB_KEY",) if key not in creds]
    if missing:
        raise SystemExit(
            f"missing required credentials: {', '.join(missing)}; source ~/.autolab/credentials first"
        )
    return creds


def load_parent_hash(explicit: str | None) -> str:
    if explicit:
        return explicit

    candidates = [
        ROOT / "research" / "live" / "master.json",
        ROOT / "research" / "reference" / "master.seed.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        if isinstance(data, dict) and "hash" in data:
            return data["hash"]
    raise SystemExit("could not find parent master hash; pass --parent-hash explicitly")


def build_diff() -> str:
    original = (ROOT / "train_orig.py").read_text().splitlines()
    updated = (ROOT / "train.py").read_text().splitlines()
    diff_lines = list(
        unified_diff(
            original,
            updated,
            fromfile="train_orig.py",
            tofile="train.py",
            lineterm="",
        )
    )
    if not diff_lines:
        raise SystemExit("train.py matches train_orig.py; nothing to submit")
    return "\n".join(diff_lines) + "\n"


def post_patch(base: str, api_key: str, payload: dict[str, object]) -> dict | list | str:
    request = urllib.request.Request(
        f"{base.rstrip('/')}/api/patches",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"submit failed ({exc.code}): {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"submit failed: {exc}") from exc

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


def main() -> int:
    parser = argparse.ArgumentParser(description="Submit the current train.py diff to autolab.")
    parser.add_argument("--comment", required=True, help="submission comment")
    parser.add_argument("--priority", type=int, default=0, help="submission priority")
    parser.add_argument("--parent-hash", help="override parent master hash")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the payload summary without posting it",
    )
    args = parser.parse_args()

    creds = load_credentials()
    diff = build_diff()
    payload = {
        "parent_hash": load_parent_hash(args.parent_hash),
        "diff": diff,
        "comment": args.comment,
        "priority": args.priority,
    }

    if args.dry_run:
        print(json.dumps({**payload, "diff": f"<{len(diff.splitlines())} diff lines>"}, indent=2))
        return 0

    response = post_patch(creds["AUTOLAB"], creds["AUTOLAB_KEY"], payload)
    if isinstance(response, (dict, list)):
        print(json.dumps(response, indent=2))
    else:
        print(response)
    return 0


if __name__ == "__main__":
    sys.exit(main())
