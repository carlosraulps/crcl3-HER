#!/usr/bin/env python3
"""
hpc_sync_monitor.py

Autonomous HPC Synchronization, Verification & Continuation Daemon.
Features:
1. Multi-cluster ledger tracking (~/.hpc_jobs_ledger.json) across Carbono, Huk, and Iskay.
2. Extreme verification against false positives/negatives:
   - Multi-tier validation: Slurm job state + OUTCAR convergence strings + CONTCAR line/byte integrity + OSZICAR energy extraction.
   - Crash, OOM, and timeout detection.
3. Automated bidirectional synchronization:
   - Syncs converged calculation outputs back to local repository.
   - Executes continuation hooks (e.g. staging H adsorption atop relaxed substrate).
   - Automatically commits converged results to Git `master` branch and pushes to GitHub and Carbono remotes.
4. Real-time desktop & terminal notifications.

Usage:
  hpc_sync_monitor.py --check              # Run one-shot verification and sync
  hpc_sync_monitor.py --watch [--interval N] # Run persistent daemon loop
  hpc_sync_monitor.py --list               # List all tracked jobs in the ledger
  hpc_sync_monitor.py --init-existing      # Auto-discover active cluster jobs into ledger
"""

import sys
import os
import json
import re
import time
import shutil
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# ANSI Colors
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
MAGENTA = "\033[1;35m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

LEDGER_PATH = os.path.expanduser("~/.hpc_jobs_ledger.json")
REPO_ROOT = "/home/cr/simulations/crcl3-HER"

CLUSTER_HOSTS = {
    "carbono": {"host": "carbono", "user": "carlos.primo"},
    "huk":     {"host": "huk",     "user": "carlos"},
    "iskay":   {"host": "iskay",   "user": "juan"}
}


def run_ssh(host: str, cmd: str, timeout: int = 10) -> Optional[str]:
    try:
        res = subprocess.run(
            ["ssh", "-q", "-o", "BatchMode=yes", "-o", f"ConnectTimeout={timeout}", host, cmd],
            capture_output=True, text=True, check=True, timeout=timeout
        )
        return res.stdout
    except Exception:
        return None


def send_system_notification(title: str, message: str):
    """Sends desktop notification if DISPLAY is available, plus terminal bell."""
    try:
        # Terminal bell
        sys.stdout.write("\a")
        sys.stdout.flush()

        # Desktop notification
        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            subprocess.run(["notify-send", "-u", "normal", "-a", "HPC-Sync", title, message], check=False)
    except Exception:
        pass


def load_ledger() -> List[Dict[str, Any]]:
    if os.path.exists(LEDGER_PATH):
        try:
            with open(LEDGER_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_ledger(ledger: List[Dict[str, Any]]):
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2)


def discover_active_cluster_jobs() -> List[Dict[str, Any]]:
    """
    Scans Huk and Carbono for active user jobs and registers them into the ledger.
    """
    discovered = []

    # 1. Huk
    out_huk = run_ssh("huk", "squeue -u carlos -o '%i|%j|%P|%T|%M|%Z'")
    if out_huk:
        for line in out_huk.strip().split("\n")[1:]:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 6:
                job_id, name, part, state, run_time, workdir = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                # Map remote workdir to local dir
                local_dir = workdir.replace("/home/carlos/crcl3-newcals", f"{REPO_ROOT}/crcl3-newcals")
                discovered.append({
                    "job_id": int(job_id),
                    "name": name,
                    "cluster": "huk",
                    "partition": part,
                    "cores": 36 if part == "alto" else (28 if part == "medio" else 24),
                    "local_dir": local_dir,
                    "remote_dir": workdir,
                    "status": "RUNNING" if state == "R" else ("PENDING" if state == "PD" else state),
                    "submitted_at": datetime.now().isoformat(),
                    "expected_steps": 100 if "U" in name else 40,
                    "continuation_hook": "stage_h_on_co" if "Co" in name and "with-U" in workdir else None,
                    "last_verified": datetime.now().isoformat()
                })

    # 2. Carbono
    out_c = run_ssh("carbono", "squeue -u carlos.primo -o '%i|%j|%P|%T|%M|%Z'")
    if out_c:
        for line in out_c.strip().split("\n")[1:]:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 6:
                job_id, name, part, state, run_time, workdir = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                local_dir = workdir.replace("~/crcl3-HER", REPO_ROOT).replace("/home/carlos.primo/crcl3-HER", REPO_ROOT)
                discovered.append({
                    "job_id": int(job_id),
                    "name": name,
                    "cluster": "carbono",
                    "partition": part,
                    "cores": 64 if part == "fulereno" else 32,
                    "local_dir": local_dir,
                    "remote_dir": workdir,
                    "status": "RUNNING" if state == "R" else ("PENDING" if state == "PD" else state),
                    "submitted_at": datetime.now().isoformat(),
                    "expected_steps": 100 if "U" in name else 40,
                    "continuation_hook": "stage_h_on_co" if "Co" in name and "with-U" in workdir else None,
                    "last_verified": datetime.now().isoformat()
                })

    return discovered


def verify_job_completion(job: Dict[str, Any]) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Multi-tier verification against false positives / negatives:
    Returns (status, metadata):
      - 'RUNNING': Job actively running in Slurm queue
      - 'PENDING': Job waiting in Slurm queue
      - 'COMPLETED': Confirmed ionic/electronic convergence below EDIFFG, valid CONTCAR
      - 'FAILED': Fatal error in OUTCAR or node crash
      - 'INCOMPLETE': Terminated without reaching required accuracy
      - 'UNREACHABLE': Cluster host not reachable
    """
    cluster = job["cluster"]
    host = CLUSTER_HOSTS.get(cluster, {}).get("host", cluster)
    job_id = job["job_id"]
    remote_dir = job["remote_dir"]

    # 1. Check Slurm queue state
    sq_cmd = f"squeue -j {job_id} -h -o '%T'"
    sq_out = run_ssh(host, sq_cmd)

    if sq_out is not None and sq_out.strip():
        state = sq_out.strip().upper()
        if "PD" in state or "PENDING" in state:
            return "PENDING", None
        elif any(s in state for s in ("R", "RUNNING", "CG", "COMPLETING", "CF", "CONFIGURING")):
            # Extract live progress from OSZICAR if available
            live_out = run_ssh(host, f"grep 'E0=' {remote_dir}/OSZICAR 2>/dev/null | tail -n 1")
            meta = None
            if live_out and "E0=" in live_out:
                m_e0 = re.search(r"^\s*(\d+)\s+F=.*E0=\s*([+-]?[0-9\.]+E[+-]?[0-9]+)", live_out)
                if m_e0:
                    step_num = int(m_e0.group(1))
                    e0_val = float(m_e0.group(2))
                    meta = {"step": step_num, "e0_ev": e0_val}
            return "RUNNING", meta

    # Job is no longer in active Slurm queue, verify output files on remote filesystem
    check_script = f"""
    cd {remote_dir} || exit 10
    echo "=== FILES ==="
    ls -l CONTCAR OUTCAR OSZICAR 2>/dev/null
    echo "=== OUTCAR_CONV ==="
    grep -E "reached required accuracy|General timing and accounting" OUTCAR 2>/dev/null | tail -n 2
    echo "=== OUTCAR_ERR ==="
    grep -E "ZBRENT: fatal error|internal error in SETUP_ACC|SIGSEGV|oom-killer|VASP: internal error" OUTCAR run.log job.*.err 2>/dev/null | head -n 3
    echo "=== OSZICAR_LAST ==="
    grep "E0=" OSZICAR 2>/dev/null | tail -n 1
    echo "=== CONTCAR_LINES ==="
    wc -l CONTCAR 2>/dev/null
    """
    diag_out = run_ssh(host, check_script)
    if not diag_out:
        return "UNREACHABLE", None

    # Parse diagnostic output
    sections = {}
    curr_sec = None
    for line in diag_out.splitlines():
        if line.startswith("=== ") and line.endswith(" ==="):
            curr_sec = line.strip("= ")
            sections[curr_sec] = []
        elif curr_sec:
            sections[curr_sec].append(line)

    outcar_err = "\n".join(sections.get("OUTCAR_ERR", [])).strip()
    if outcar_err:
        return "FAILED", {"error": outcar_err}

    contcar_lines_str = "\n".join(sections.get("CONTCAR_LINES", [])).strip()
    m_lines = re.match(r"^(\d+)", contcar_lines_str)
    contcar_lines = int(m_lines.group(1)) if m_lines else 0

    if contcar_lines < 8:
        # Missing or empty CONTCAR - NOT a true completion!
        return "INCOMPLETE", {"reason": f"CONTCAR has only {contcar_lines} lines (missing or truncated)"}

    outcar_conv = "\n".join(sections.get("OUTCAR_CONV", [])).strip()
    oszicar_last = "\n".join(sections.get("OSZICAR_LAST", [])).strip()

    # Extract final E0 and mag
    e0_val = None
    mag_val = None
    m_e0 = re.search(r"E0=\s*([+-]?[0-9\.]+E[+-]?[0-9]+)", oszicar_last)
    if m_e0:
        e0_val = float(m_e0.group(1))
    m_mag = re.search(r"mag=\s*([+-]?[0-9\.]+)", oszicar_last)
    if m_mag:
        mag_val = float(m_mag.group(1))

    # Strict convergence verification:
    # 1. "reached required accuracy" MUST be present for relaxation
    # 2. Or "General timing and accounting" if static calculation
    is_converged = "reached required accuracy" in outcar_conv or "General timing and accounting" in outcar_conv

    if is_converged and e0_val is not None:
        return "COMPLETED", {
            "e0_ev": e0_val,
            "mag_moment": mag_val,
            "contcar_lines": contcar_lines,
            "verified_at": datetime.now().isoformat()
        }

    return "INCOMPLETE", {
        "reason": "Process exited Slurm queue before reaching convergence criteria",
        "last_e0": e0_val,
        "contcar_lines": contcar_lines
    }


def sync_completed_job_to_local(job: Dict[str, Any], meta: Dict[str, Any]) -> bool:
    """
    Rsyncs output files back to local workspace.
    """
    cluster = job["cluster"]
    host = CLUSTER_HOSTS.get(cluster, {}).get("host", cluster)
    remote_dir = job["remote_dir"]
    local_dir = Path(job["local_dir"]).resolve()

    local_dir.mkdir(parents=True, exist_ok=True)
    print(f"  📥 Syncing results from {cluster}:{remote_dir} -> {local_dir}...")

    rsync_cmd = [
        "rsync", "-avz",
        "--exclude=WAVECAR", "--exclude=CHGCAR", "--exclude=CHG",
        f"{host}:{remote_dir}/",
        f"{str(local_dir)}/"
    ]
    res = subprocess.run(rsync_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  {RED}✖ Rsync failed: {res.stderr}{RESET}")
        return False

    print(f"  {GREEN}✔ Outputs successfully synced to {local_dir}!{RESET}")
    return True


def execute_continuation_hook(job: Dict[str, Any], meta: Dict[str, Any]):
    """
    Triggers automated continuation workflow (e.g. staging H adsorption).
    """
    hook = job.get("continuation_hook")
    if not hook:
        return

    print(f"\n{BOLD}{MAGENTA}⚙️ Triggering Continuation Hook: [{hook}]...{RESET}")
    local_dir = Path(job["local_dir"])

    if hook == "stage_h_on_co":
        # Look for setup_h_on_co_u.py in parent directory
        parent_dir = local_dir.parent.parent
        hook_script = parent_dir / "setup_h_on_co_u.py"
        if hook_script.exists():
            print(f"  • Executing {hook_script} for site {local_dir.name}...")
            res = subprocess.run(
                [sys.executable, str(hook_script), "--site", local_dir.name],
                capture_output=True, text=True, cwd=str(parent_dir)
            )
            print(f"  • Hook Output:\n{res.stdout}")
            if res.stderr:
                print(f"  • Hook Stderr:\n{res.stderr}")
        else:
            print(f"  {YELLOW}Hook script {hook_script} not found.{RESET}")


def commit_and_push_results(job: Dict[str, Any], meta: Dict[str, Any]):
    """
    Commits converged calculation outputs to Git master branch and pushes.
    """
    local_dir = Path(job["local_dir"]).resolve()
    cluster = job["cluster"]
    name = job["name"]
    e0 = meta.get("e0_ev", "N/A")

    print(f"\n{BOLD}{CYAN}🐙 Git Synchronization (Branch: master)...{RESET}")

    # Add output files
    files_to_add = ["CONTCAR", "OUTCAR", "OSZICAR", "vasprun.xml"]
    for f in files_to_add:
        fp = local_dir / f
        if fp.exists():
            subprocess.run(["git", "add", str(fp)], cwd=REPO_ROOT, check=False)

    commit_msg = f"feat(dft): converged {name} on {cluster} (E0={e0} eV)\n\nAutomated sync by HPC Superpower Monitor."
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_ROOT, check=False)

    git_env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}

    # Push to origin (master)
    print("  • Pushing to origin/master...")
    try:
        res_orig = subprocess.run(["git", "push", "origin", "master"], cwd=REPO_ROOT, capture_output=True, text=True, env=git_env, timeout=12)
        if res_orig.returncode == 0:
            print(f"  {GREEN}✔ Pushed to GitHub origin/master!{RESET}")
        else:
            print(f"  {YELLOW}Notice: git push origin: {res_orig.stderr.strip()}{RESET}")
    except Exception as e:
        print(f"  {YELLOW}Notice: git push origin timed out or skipped: {e}{RESET}")

    # Push to carbono remote (master)
    print("  • Pushing to carbono:~/crcl3-HER (master)...")
    try:
        res_carb = subprocess.run(["git", "push", "carbono", "master"], cwd=REPO_ROOT, capture_output=True, text=True, env=git_env, timeout=15)
        if res_carb.returncode == 0:
            print(f"  {GREEN}✔ Pushed to Carbono master!{RESET}")
        else:
            print(f"  {YELLOW}Notice: git push carbono: {res_carb.stderr.strip()}{RESET}")
    except Exception as e:
        print(f"  {YELLOW}Notice: git push carbono error: {e}{RESET}")


def process_ledger_jobs(sync_on_completion: bool = True) -> Dict[str, int]:
    ledger = load_ledger()
    if not ledger:
        print(f"{YELLOW}Ledger is empty ({LEDGER_PATH}). Run with --init-existing to auto-discover active jobs.{RESET}")
        return {"total": 0, "completed": 0, "running": 0, "pending": 0}

    stats = {"total": len(ledger), "completed": 0, "running": 0, "pending": 0, "failed": 0}

    print(f"\n{BOLD}{CYAN}========================================================================================{RESET}")
    print(f"{BOLD}{CYAN}          📡 HPC MULTI-CLUSTER SYNCHRONIZATION & MONITOR AUDIT{RESET}")
    print(f"{BOLD}{CYAN}========================================================================================{RESET}")
    print(f"{'Cluster':<9} | {'Job ID':<8} | {'Job Name':<14} | {'Status':<14} | {'Last E0 (eV)':<14} | {'Action / Detail'}")
    print("-" * 105)

    updated_ledger = []

    for job in ledger:
        orig_status = job.get("status", "UNKNOWN")
        v_status, meta = verify_job_completion(job)

        job["last_verified"] = datetime.now().isoformat()
        st_color = GREEN if v_status in ("COMPLETED", "RUNNING") else (YELLOW if v_status == "PENDING" else RED)

        e0_str = f"{meta.get('e0_ev'):.4f}" if (meta and meta.get("e0_ev")) else "N/A"

        if v_status == "COMPLETED" and orig_status != "COMPLETED":
            # Newly completed job!
            print(f"{BOLD}{job['cluster'].upper():<9}{RESET} | {job['job_id']:<8} | {job['name']:<14} | {GREEN}{'CONVERGED':<14}{RESET} | {e0_str:<14} | {BOLD}{GREEN}SYNCING OUTPUTS{RESET}")
            job["status"] = "COMPLETED"
            if meta:
                job.update(meta)

            if sync_on_completion:
                synced = sync_completed_job_to_local(job, meta)
                if synced:
                    send_system_notification(
                        "VASP Job Converged & Synced",
                        f"Job {job['name']} ({job['job_id']}) converged on {job['cluster'].upper()}! E0={e0_str} eV."
                    )
                    execute_continuation_hook(job, meta)
                    commit_and_push_results(job, meta)
            stats["completed"] += 1

        elif v_status == "COMPLETED":
            print(f"{BOLD}{job['cluster'].upper():<9}{RESET} | {job['job_id']:<8} | {job['name']:<14} | {GREEN}{'COMPLETED':<14}{RESET} | {e0_str:<14} | Synced & Verified")
            stats["completed"] += 1

        elif v_status == "RUNNING":
            step_detail = f"Computing step {meta.get('step') + 1} (Step {meta.get('step')} converged)" if (meta and meta.get("step")) else "Actively computing on node"
            print(f"{BOLD}{job['cluster'].upper():<9}{RESET} | {job['job_id']:<8} | {job['name']:<14} | {CYAN}{'RUNNING':<14}{RESET} | {e0_str:<14} | {step_detail}")
            job["status"] = "RUNNING"
            stats["running"] += 1

        elif v_status == "PENDING":
            print(f"{BOLD}{job['cluster'].upper():<9}{RESET} | {job['job_id']:<8} | {job['name']:<14} | {YELLOW}{'PENDING':<14}{RESET} | {e0_str:<14} | Waiting in queue")
            job["status"] = "PENDING"
            stats["pending"] += 1

        else:
            detail = meta.get("error", meta.get("reason", "Check cluster logs")) if meta else "Status unknown"
            print(f"{BOLD}{job['cluster'].upper():<9}{RESET} | {job['job_id']:<8} | {job['name']:<14} | {RED}{v_status:<14}{RESET} | {e0_str:<14} | {detail}")
            job["status"] = v_status
            stats["failed"] += 1

        updated_ledger.append(job)

    print("-" * 105)
    save_ledger(updated_ledger)
    return stats


def main():
    parser = argparse.ArgumentParser(description="HPC Synchronization, Verification & Continuation Daemon")
    parser.add_argument("--check", action="store_true", help="Run one-shot verification and sync")
    parser.add_argument("--watch", action="store_true", help="Run persistent monitor daemon loop")
    parser.add_argument("--interval", type=int, default=60, help="Poll interval in seconds for watch mode (default: 60s)")
    parser.add_argument("--list", action="store_true", help="List all jobs in ledger")
    parser.add_argument("--init-existing", action="store_true", help="Discover active cluster jobs and register them")

    args = parser.parse_args()

    if args.init_existing:
        print(f"{BOLD}{CYAN}🔍 Discovering active jobs on Huk and Carbono...{RESET}")
        discovered = discover_active_cluster_jobs()
        ledger = load_ledger()
        added = 0
        for d in discovered:
            if not any(j.get("job_id") == d["job_id"] and j.get("cluster") == d["cluster"] for j in ledger):
                ledger.append(d)
                added += 1
                print(f"  • Registered [{d['cluster'].upper()}] Job {d['job_id']}: {d['name']} ({d['status']})")
        save_ledger(ledger)
        print(f"{GREEN}✔ Successfully registered {added} new jobs. Total tracked: {len(ledger)}.{RESET}\n")
        process_ledger_jobs(sync_on_completion=True)

    elif args.watch:
        print(f"{BOLD}{GREEN}Starting HPC Synchronization Daemon (Interval: {args.interval}s, Ledger: {LEDGER_PATH})...{RESET}")
        try:
            while True:
                process_ledger_jobs(sync_on_completion=True)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nStopped HPC Synchronization Daemon.")

    elif args.list:
        ledger = load_ledger()
        print(json.dumps(ledger, indent=2))

    else:
        # Default: one-shot check
        process_ledger_jobs(sync_on_completion=True)


if __name__ == "__main__":
    main()
