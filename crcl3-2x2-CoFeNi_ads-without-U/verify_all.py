#!/usr/bin/env python3
import os
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
subdirs = [
    "crcl3-2x2-co_ads-without-U",
    "crcl3-2x2-fe_ads-without-U",
    "crcl3-2x2-ni_ads-without-U"
]

total_pass = 0
total_fail = 0

print("=" * 85)
print("   RUNNING FULL VERIFICATION FOR Co, Fe, Ni SUITES")
print("=" * 85)

for d in subdirs:
    vscript = os.path.join(SCRIPT_DIR, d, "verify_supercell.py")
    res = subprocess.run([sys.executable, vscript], cwd=os.path.join(SCRIPT_DIR, d), capture_output=True, text=True)
    print(f"\n--- {d} ---")
    for line in res.stdout.splitlines():
        if "VERIFICATION SUMMARY" in line:
            print("  " + line.strip())
            parts = line.split()
            # ... SUMMARY: X PASSED, Y FAILED
            for i, p in enumerate(parts):
                if p == "PASSED,":
                    total_pass += int(parts[i-1])
                elif p == "FAILED":
                    total_fail += int(parts[i-1])

print("\n" + "=" * 85)
print(f"   GRAND TOTAL: {total_pass} CHECKS PASSED, {total_fail} FAILED")
print("=" * 85)

if total_fail > 0:
    sys.exit(1)
