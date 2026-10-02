#!/usr/bin/env python3
"""Encrypt the job list into data.json for the glasses app.

Usage:  RBJOBS_PIN=123456 python3 tools/encrypt_jobs.py <jobs_dir_or_json> [meta.json]
(writes data.json in the current folder)

Input: a folder of job JSON files (one per job, as exported from the RB Cable Job Board)
or a single JSON file holding a list of jobs. Never commit the plaintext input.
Requires: pip install cryptography
"""
import base64, glob, json, os, sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ITER = 250_000
KEEP = ["id", "title", "short", "site", "client", "ref", "status", "start", "end", "due",
        "next", "contact", "scope", "notes", "updates"]

def load_jobs(src):
    if os.path.isdir(src):
        rows = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(src, "*.json")))]
    else:
        rows = json.load(open(src))
    rows = [r.get("data", r) for r in rows]
    out = []
    for r in rows:
        if r.get("status") == "done":
            continue
        j = {k: r[k] for k in KEEP if r.get(k)}
        if "updates" in j:
            j["updates"] = j["updates"][-3:]
        out.append(j)
    return out

def main():
    pin = os.environ.get("RBJOBS_PIN", "")
    if not (pin.isdigit() and len(pin) == 6):
        sys.exit("Set RBJOBS_PIN to a 6-digit PIN")
    payload = {"jobs": load_jobs(sys.argv[1])}
    if len(sys.argv) > 2:
        meta = json.load(open(sys.argv[2]))
        meta = meta.get("data", meta)
        payload["lastChecked"] = meta.get("lastChecked")
        payload["summary"] = meta.get("lastSummary")
    # Reuse the previous salt (if any) so the glasses stay unlocked across data updates.
    prev = os.environ.get("RBJOBS_PREV", "data.json")
    salt = base64.b64decode(json.load(open(prev))["salt"]) if os.path.exists(prev) else os.urandom(16)
    iv = os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pin.encode())
    ct = AESGCM(key).encrypt(iv, json.dumps(payload, separators=(",", ":")).encode(), None)
    e = lambda b: base64.b64encode(b).decode()
    tmp = prev + ".tmp"
    json.dump({"v": 1, "iter": ITER, "salt": e(salt), "iv": e(iv), "ct": e(ct)}, open(tmp, "w"))
    os.replace(tmp, prev)
    print(f"Wrote {prev}: {len(payload['jobs'])} open jobs")

if __name__ == "__main__":
    main()
