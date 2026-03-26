#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIVE_DIR = ROOT / "research" / "live"


def load_autolab_base() -> str:
    base = os.environ.get("AUTOLAB")
    creds_path = Path.home() / ".autolab" / "credentials"
    if not base and creds_path.exists():
        for line in creds_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key == "AUTOLAB":
                base = value
                break
    return base or "http://autoresearchhub.com"


def fetch_json(url: str) -> dict | list:
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            return json.load(response)
    except urllib.error.URLError as exc:
        raise SystemExit(f"failed to fetch {url}: {exc}") from exc


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def train_files_diverged() -> bool:
    train_path = ROOT / "train.py"
    train_orig_path = ROOT / "train_orig.py"
    if not train_path.exists() or not train_orig_path.exists():
        return False
    return train_path.read_text() != train_orig_path.read_text()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refresh train.py and train_orig.py from the current autolab master."
    )
    parser.add_argument(
        "--fetch-dag",
        action="store_true",
        help="also refresh research/live/dag.json",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite local train.py even if it diverged from train_orig.py",
    )
    args = parser.parse_args()

    if train_files_diverged() and not args.force:
        raise SystemExit(
            "train.py differs from train_orig.py; use --force if you really want to overwrite it"
        )

    base = load_autolab_base().rstrip("/")
    master = fetch_json(f"{base}/api/git/master")
    if not isinstance(master, dict) or "hash" not in master:
        raise SystemExit("master response was missing hash")

    detail = fetch_json(f"{base}/api/git/commits/{master['hash']}")
    if not isinstance(detail, dict) or "source" not in detail:
        raise SystemExit("commit detail response was missing source")

    write_json(LIVE_DIR / "master.json", master)
    write_json(LIVE_DIR / "master_detail.json", detail)

    if args.fetch_dag:
        dag = fetch_json(f"{base}/api/git/dag")
        write_json(LIVE_DIR / "dag.json", dag)

    source = detail["source"]
    if not isinstance(source, str):
        raise SystemExit("commit detail source was not a string")

    (ROOT / "train_orig.py").write_text(source)
    (ROOT / "train.py").write_text(source)

    val_bpb = master.get("val_bpb", "unknown")
    print(f"refreshed master {master['hash']} (val_bpb={val_bpb})")
    print(f"wrote {(ROOT / 'train.py').relative_to(ROOT)}")
    print(f"wrote {(ROOT / 'train_orig.py').relative_to(ROOT)}")
    print(f"wrote {(LIVE_DIR / 'master.json').relative_to(ROOT)}")
    print(f"wrote {(LIVE_DIR / 'master_detail.json').relative_to(ROOT)}")
    if args.fetch_dag:
        print(f"wrote {(LIVE_DIR / 'dag.json').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
