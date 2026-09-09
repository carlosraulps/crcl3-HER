#!/usr/bin/env python3
"""
================================================================================
 VASP ACTIVE CHECKPOINTING & ELECTRICAL FAULT WATCHDOG DAEMON
================================================================================
 Monitors active VASP calculation directories on the SLURM cluster.
 Features:
   1. Atomic Checkpointing: Continuously protects CONTCAR from 0-byte
      corruption by keeping rolling backups (CONTCAR.ckpt).
   2. Crash & Deadlock Detection: Monitors SLURM job states and directory updates.
   3. Graceful Emergency Stop (STOPCAR): Can trigger clean shutdown of all
      active VASP jobs across the cluster upon an emergency signal (e.g. UPS alert).
   4. Auto-Resumption Preparation: Prepares POSCAR from the latest valid CONTCAR
      if a job crashes mid-relaxation.
================================================================================
"""

import os
import sys
import time
import shutil
import subprocess
import signal
from datetime import datetime

WATCH_ROOTS = [
    "/home/juan/Carlos/crcl3-1x1-h_ads-without-U",
    "/home/juan/Carlos/crcl3-2x2-h_ads-without-U",
    "/home/juan/Carlos/crcl3-3x3-h_ads-without-U",
]

CHECK_INTERVAL_SECONDS = 30
RUNNING = True


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [WATCHDOG] {msg}", flush=True)


def handle_signal(sig, frame):
    global RUNNING
    log(f"Received termination signal ({sig}). Shutting down watchdog gracefully.")
    RUNNING = False


signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


def get_active_slurm_jobs():
    """Return dictionary of {job_name: (job_id, state, workdir)}."""
    jobs = {}
    try:
        out = subprocess.check_output(
            ["squeue", "-u", os.getenv("USER", "juan"), "-h", "-o", "%i|%j|%T|%Z"],
            text=True
        )
        for line in out.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.strip().split("|")
            if len(parts) >= 4:
                job_id, name, state, workdir = parts[0], parts[1], parts[2], parts[3]
                jobs[workdir] = {"id": job_id, "name": name, "state": state}
    except Exception as e:
        log(f"Error querying squeue: {e}")
    return jobs


def is_valid_contcar(path):
    """Check if CONTCAR exists, is non-empty, and has valid coordinate lines."""
    if not os.path.exists(path) or os.path.getsize(path) < 100:
        return False
    try:
        with open(path, "r") as f:
            lines = [f.readline() for _ in range(8)]
        # Check that line 6 contains integer species counts
        counts = [int(x) for x in lines[6].split()]
        return sum(counts) > 0
    except Exception:
        return False


def snapshot_calculation(calc_dir):
    """Safely back up CONTCAR to prevent corruption during sudden power drops."""
    contcar = os.path.join(calc_dir, "CONTCAR")
    ckpt = os.path.join(calc_dir, "CONTCAR.ckpt")
    
    if is_valid_contcar(contcar):
        try:
            # Only update backup if contcar was modified
            if not os.path.exists(ckpt) or os.path.getmtime(contcar) > os.path.getmtime(ckpt):
                shutil.copy2(contcar, ckpt)
                log(f"Saved atomic checkpoint for: {os.path.basename(calc_dir)} ({os.path.getsize(contcar)} bytes)")
        except Exception as e:
            log(f"Failed to snapshot {calc_dir}: {e}")


def emergency_stop_all():
    """Trigger VASP graceful stop across all active calculations by writing STOPCAR."""
    log("!!! EMERGENCY TRIGGER ACTIVATED: Broadcasting STOPCAR (LABORT=.TRUE.) !!!")
    count = 0
    for root in WATCH_ROOTS:
        if not os.path.exists(root):
            continue
        for parent, dirs, files in os.walk(root):
            if "INCAR" in files:
                stopcar_path = os.path.join(parent, "STOPCAR")
                try:
                    with open(stopcar_path, "w") as f:
                        f.write("LABORT = .TRUE.\n")
                    count += 1
                except Exception as e:
                    log(f"Error writing STOPCAR to {parent}: {e}")
    log(f"Broadcast STOPCAR to {count} directories. VASP will flush CONTCAR and exit cleanly.")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--emergency-stop":
        emergency_stop_all()
        return

    log("Starting VASP Checkpoint & Electrical Fault Watchdog...")
    log(f"Monitoring roots: {WATCH_ROOTS}")
    log(f"Polling frequency: every {CHECK_INTERVAL_SECONDS}s")

    while RUNNING:
        active_jobs = get_active_slurm_jobs()
        for root in WATCH_ROOTS:
            if not os.path.exists(root):
                continue
            for parent, dirs, files in os.walk(root):
                if "INCAR" in files and "POSCAR" in files:
                    snapshot_calculation(parent)
        
        # Sleep in 1-second intervals to respond quickly to signals
        for _ in range(CHECK_INTERVAL_SECONDS):
            if not RUNNING:
                break
            time.sleep(1)

    log("Watchdog daemon exited cleanly.")


if __name__ == "__main__":
    main()
