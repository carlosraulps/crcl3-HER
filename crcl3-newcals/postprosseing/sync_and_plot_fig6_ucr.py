#!/usr/bin/env python3
"""
sync_and_plot_fig6_ucr.py
=========================
Monitors Huk jobs 8324 (adsorbed Co, Fe, Ni) and 8325 (embedded Co, Fe, Ni),
syncs converged LOBSTER COHP outputs back to the local repository,
and executes plot_fig6_dual_tier_cohp.py to produce Fig6_Ucr.png and Fig6_Ucr.pdf.
"""

import os
import sys
import subprocess
import time

LOCAL_BASE = "/Volumes/KingstonSSD/Krojects/Kresearch/crlcl3-CoFeNi-HER/crcl3-newcals"
LOCAL_UCR_DIR = os.path.join(LOCAL_BASE, "cohp_lobster_Ucr")
POST_DIR = os.path.join(LOCAL_BASE, "postprosseing")
REMOTE_HOST = "huk"
REMOTE_UCR_DIR = "/home/carlos/crcl3-newcals/cohp_lobster_Ucr"

SYSTEMS = [
    ("adsorbed", "Co"), ("adsorbed", "Fe"), ("adsorbed", "Ni"),
    ("embedded", "Co"), ("embedded", "Fe"), ("embedded", "Ni")
]

def check_remote_status():
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", REMOTE_HOST, "squeue -u carlos -j 8324,8325 -o '%i %j %T %M %N'"]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return res.stdout.strip()
    except Exception as e:
        return f"Error checking queue: {e}"

def check_remote_completed_cohps():
    cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", REMOTE_HOST, 
           f"for m in adsorbed embedded; do for tm in Co Fe Ni; do f={REMOTE_UCR_DIR}/$m/$tm/COHPCAR.lobster; [ -s $f ] && echo $m/$tm; done; done"]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        lines = [line.strip() for line in res.stdout.strip().splitlines() if line.strip()]
        return lines
    except Exception:
        return []

def sync_completed_cohps():
    print(f"[*] Syncing {REMOTE_UCR_DIR} from {REMOTE_HOST}...")
    rsync_cmd = [
        "rsync", "-avz", "--include=*/", 
        "--include=COHPCAR.lobster", "--include=ICOHPLIST.lobster", "--include=DOSCAR.lobster", 
        "--include=OUTCAR", "--include=OSZICAR", "--include=lobsterout", "--exclude=*",
        f"{REMOTE_HOST}:{REMOTE_UCR_DIR}/", f"{LOCAL_UCR_DIR}/"
    ]
    try:
        subprocess.run(rsync_cmd, check=True)
        print("[✔] Sync successful.")
    except Exception as e:
        print(f"[!] Rsync warning: {e}")

def verify_local_completion():
    missing = []
    for mode, tm in SYSTEMS:
        f = os.path.join(LOCAL_UCR_DIR, mode, tm, "COHPCAR.lobster")
        if not os.path.exists(f) or os.path.getsize(f) < 1000:
            missing.append(f"{mode}/{tm}")
    return missing

def run_plot_pipeline():
    print("[*] All 6 COHP systems converged! Executing plot_fig6_dual_tier_cohp.py...")
    plot_script = os.path.join(POST_DIR, "plot_fig6_dual_tier_cohp.py")
    res = subprocess.run([sys.executable, plot_script], cwd=POST_DIR, text=True, capture_output=True)
    print(res.stdout)
    if res.returncode != 0:
        print(f"[!] Plotting error:\n{res.stderr}")
    else:
        print("[✔] Fig6_Ucr publication figures successfully generated and synced!")

if __name__ == "__main__":
    print("=" * 70)
    print(" HPC LOBSTER COHP (+U_Cr) MONITOR & AUTO-PLOTTER")
    print("=" * 70)
    
    q_status = check_remote_status()
    print("Remote Queue Status:")
    print(q_status)
    print("-" * 70)
    
    completed = check_remote_completed_cohps()
    print(f"Remote Completed Systems ({len(completed)}/6): {', '.join(completed) if completed else 'None yet (in SCF)'}")
    
    if len(completed) > 0:
        sync_completed_cohps()
        
    missing = verify_local_completion()
    if not missing:
        run_plot_pipeline()
    else:
        print(f"Waiting on {len(missing)} system(s): {', '.join(missing)}")
    print("=" * 70)
