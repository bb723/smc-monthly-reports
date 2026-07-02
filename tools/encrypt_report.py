"""Encrypt a markdown report for the SMC monthly-reports GitHub Page.

Usage:
    python tools/encrypt_report.py <input.md> <report-id> "<Title>" [--password PW]

Writes reports/<report-id>.enc.json (AES-256-GCM, key = PBKDF2-HMAC-SHA256,
600k iterations) and updates manifest.json. The plaintext never lands in the
repo. Ask Brett for the password out-of-band.
"""
from __future__ import annotations
import argparse
import base64
import getpass
import json
import os
import sys
from hashlib import pbkdf2_hmac
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ITERATIONS = 600_000
ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_md")
    ap.add_argument("report_id", help="e.g. 2026-06")
    ap.add_argument("title", help="e.g. 'June 2026 — Cash Report'")
    ap.add_argument("--password", default=None)
    a = ap.parse_args()

    pw = a.password or getpass.getpass("Password: ")
    plaintext = Path(a.input_md).read_text(encoding="utf-8").encode("utf-8")

    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = pbkdf2_hmac("sha256", pw.encode("utf-8"), salt, ITERATIONS, dklen=32)
    ct = AESGCM(key).encrypt(nonce, plaintext, None)

    out_dir = ROOT / "reports"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{a.report_id}.enc.json"
    out.write_text(json.dumps({
        "v": 1,
        "kdf": "PBKDF2-SHA256",
        "iterations": ITERATIONS,
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ct).decode(),
    }), encoding="utf-8")
    print(f"wrote {out}")

    man_path = ROOT / "manifest.json"
    manifest = json.loads(man_path.read_text(encoding="utf-8")) if man_path.exists() else {"reports": []}
    manifest["reports"] = [r for r in manifest["reports"] if r["id"] != a.report_id]
    manifest["reports"].append({"id": a.report_id, "title": a.title,
                                 "file": f"reports/{a.report_id}.enc.json"})
    manifest["reports"].sort(key=lambda r: r["id"], reverse=True)
    man_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"updated {man_path} ({len(manifest['reports'])} reports)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
