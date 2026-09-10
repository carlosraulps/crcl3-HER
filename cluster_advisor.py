#!/usr/bin/env python3
"""
================================================================================
 ISKAY CLUSTER HEALTH, AVAILABILITY & SUBMISSION ADVISOR
================================================================================
 Analyzes:
   1. Node status (up/drain/down/mixed), CPU/memory allocation
   2. Running jobs and their resource usage
   3. Available capacity for new jobs
   4. Submission recommendations for pending calculations
   5. Performance metrics from running calculations
================================================================================
 Usage:  python3 cluster_advisor.py
         python3 cluster_advisor.py --submit-check    (only show submission advice)
         python3 cluster_advisor.py --watch            (continuous monitoring, 60s)
================================================================================
"""

import subprocess
import os
import sys
import re
import math
import json
from datetime import datetime, timedelta


# ─── Configuration ───────────────────────────────────────────────────────────
PROJECT_ROOT = "/home/juan/Carlos"
CALCS = {
    "1x1": {
        "dir": f"{PROJECT_ROOT}/crcl3-1x1-h_ads-without-U",
        "atoms_clean": 8, "atoms_ads": 9,
        "cores_per_job": 16, "mem_per_job_gb": 16,
    },
    "2x2": {
        "dir": f"{PROJECT_ROOT}/crcl3-2x2-h_ads-without-U",
        "atoms_clean": 32, "atoms_ads": 33,
        "cores_per_job": 16, "mem_per_job_gb": 16,
    },
    "3x3": {
        "dir": f"{PROJECT_ROOT}/crcl3-3x3-h_ads-without-U",
        "atoms_clean": 72, "atoms_ads": 73,
        "cores_per_job": 32, "mem_per_job_gb": 32,
    },
    "H2_ref": {
        "dir": f"{PROJECT_ROOT}/H2_reference",
        "atoms_clean": 0, "atoms_ads": 2,
        "cores_per_job": 16, "mem_per_job_gb": 16,
    },
}
VARIANTS = ["no_vdw", "yes_vdw"]
SITES = ["clean", "S1", "S2", "S3"]

# ─── SLURM Queries ──────────────────────────────────────────────────────────

def run_cmd(cmd):
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"


def get_node_info():
    """Parse detailed node information from scontrol."""
    nodes = []
    for node_name in ["iskay201", "iskay202"]:
        raw = run_cmd(f"scontrol show node {node_name}")
        if "ERROR" in raw or not raw:
            continue
        info = {}
        info["name"] = node_name
        # Parse key fields
        for line in raw.split("\n"):
            line = line.strip()
            for field in line.split():
                if "=" in field:
                    key, _, val = field.partition("=")
                    info[key] = val

        nodes.append({
            "name": node_name,
            "state": info.get("State", "UNKNOWN"),
            "cpu_total": int(info.get("CPUTot", 0)),
            "cpu_alloc": int(info.get("CPUAlloc", 0)),
            "cpu_load": float(info.get("CPULoad", 0)),
            "mem_total_mb": int(info.get("RealMemory", 0)),
            "mem_alloc_mb": int(info.get("AllocMem", 0)),
            "mem_free_mb": int(info.get("FreeMem", 0)),
            "sockets": int(info.get("Sockets", 0)),
            "cores_per_socket": int(info.get("CoresPerSocket", 0)),
            "threads_per_core": int(info.get("ThreadsPerCore", 1)),
            "os": info.get("OS", ""),
            "boot_time": info.get("BootTime", ""),
            "reason": info.get("Reason", "None"),
            "arch": info.get("Arch", ""),
        })
    return nodes


def get_partition_info():
    """Get partition configuration."""
    raw = run_cmd("scontrol show partition normal")
    info = {}
    for line in raw.split("\n"):
        line = line.strip()
        for field in line.split():
            if "=" in field:
                key, _, val = field.partition("=")
                info[key] = val
    return {
        "name": info.get("PartitionName", "normal"),
        "state": info.get("State", "UNKNOWN"),
        "max_time": info.get("MaxTime", "UNLIMITED"),
        "total_cpus": int(info.get("TotalCPUs", 0)),
        "total_nodes": int(info.get("TotalNodes", 0)),
        "def_mem_per_cpu": info.get("DefMemPerCPU", "N/A"),
        "oversubscribe": info.get("OverSubscribe", "NO"),
    }


def get_running_jobs():
    """Get all running/pending jobs for the current user."""
    raw = run_cmd(
        f'squeue -u {os.getenv("USER", "juan")} -h '
        f'-o "%i|%j|%T|%M|%C|%D|%l|%Z|%R"'
    )
    jobs = []
    if not raw:
        return jobs
    for line in raw.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.strip().split("|")
        if len(parts) >= 9:
            jobs.append({
                "id": parts[0],
                "name": parts[1],
                "state": parts[2],
                "elapsed": parts[3],
                "cpus": int(parts[4]),
                "nodes": int(parts[5]),
                "time_limit": parts[6],
                "workdir": parts[7],
                "reason": parts[8],
            })
    return jobs


def get_all_jobs():
    """Get ALL running/pending jobs from ALL users."""
    raw = run_cmd('squeue -h -o "%i|%u|%j|%T|%M|%C|%D|%R"')
    jobs = []
    if not raw:
        return jobs
    for line in raw.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.strip().split("|")
        if len(parts) >= 8:
            jobs.append({
                "id": parts[0],
                "user": parts[1],
                "name": parts[2],
                "state": parts[3],
                "elapsed": parts[4],
                "cpus": int(parts[5]),
                "nodes": int(parts[6]),
                "reason": parts[7],
            })
    return jobs


# ─── Calculation Status ─────────────────────────────────────────────────────

def check_calc_status(calc_dir):
    """Check convergence status of a VASP calculation directory."""
    outcar = os.path.join(calc_dir, "OUTCAR")
    oszicar = os.path.join(calc_dir, "OSZICAR")

    if not os.path.exists(outcar):
        return "NOT_STARTED", 0, None, None

    converged = False
    ionic_steps = 0
    final_energy = None
    max_force = None

    try:
        with open(outcar, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if "reached required accuracy" in content:
            converged = True
        # Get final energy
        for m in re.finditer(r"free  energy   TOTEN\s+=\s+([-\d.]+)", content):
            final_energy = float(m.group(1))
    except Exception:
        pass

    try:
        if os.path.exists(oszicar):
            with open(oszicar, "r") as f:
                ionic_steps = sum(1 for line in f if "F=" in line)
    except Exception:
        pass

    # Get max force from last TOTAL-FORCE block
    try:
        force_blocks = re.findall(
            r"TOTAL-FORCE \(eV/Angst\)\s+-+\s+([\s\S]+?)\s+-+", content
        )
        if force_blocks:
            last_block = force_blocks[-1]
            forces = []
            for row in last_block.strip().split("\n"):
                cols = row.split()
                if len(cols) >= 6:
                    try:
                        fx, fy, fz = float(cols[3]), float(cols[4]), float(cols[5])
                        forces.append(math.sqrt(fx*fx + fy*fy + fz*fz))
                    except (ValueError, IndexError):
                        pass
            if forces:
                max_force = max(forces)
    except Exception:
        pass

    if converged:
        return "CONVERGED", ionic_steps, final_energy, max_force
    elif ionic_steps > 0:
        return "INTERRUPTED", ionic_steps, final_energy, max_force
    else:
        return "STARTED_NO_IONIC", 0, final_energy, max_force


def get_pending_calculations():
    """Identify all calculations that need to be submitted."""
    pending = []
    running_jobs = get_running_jobs()
    running_workdirs = set()
    for j in running_jobs:
        running_workdirs.add(os.path.abspath(j["workdir"]))

    for scale, cfg in CALCS.items():
        base_dir = cfg["dir"]
        if scale == "H2_ref":
            # H2 reference has no_vdw and yes_vdw only (no sites)
            for v in VARIANTS:
                calc_dir = os.path.join(base_dir, v)
                if not os.path.isdir(calc_dir):
                    continue
                status, steps, energy, fmax = check_calc_status(calc_dir)
                is_running = os.path.abspath(calc_dir) in running_workdirs
                if is_running:
                    status = "RUNNING"
                if status not in ("CONVERGED",):
                    pending.append({
                        "scale": scale,
                        "variant": v,
                        "site": "H2",
                        "dir": calc_dir,
                        "status": status,
                        "cores": cfg["cores_per_job"],
                        "mem_gb": cfg["mem_per_job_gb"],
                        "ionic_steps": steps,
                        "energy": energy,
                        "fmax": fmax,
                        "est_hours": 0.2,  # H2 is very fast
                    })
        else:
            for v in VARIANTS:
                for s in SITES:
                    calc_dir = os.path.join(base_dir, v, s)
                    if not os.path.isdir(calc_dir):
                        continue
                    status, steps, energy, fmax = check_calc_status(calc_dir)
                    is_running = os.path.abspath(calc_dir) in running_workdirs
                    if is_running:
                        status = "RUNNING"

                    # Estimate remaining time
                    est_hours = 0
                    if status == "INTERRUPTED":
                        if fmax is not None and fmax < 0.025:
                            est_hours = 0.2  # Just needs confirmation
                        elif scale == "1x1":
                            est_hours = 4.0
                        elif scale == "2x2":
                            est_hours = 24.0
                        elif scale == "3x3":
                            est_hours = 120.0
                    elif status == "NOT_STARTED":
                        if s == "clean":
                            est_hours = {"1x1": 1, "2x2": 6, "3x3": 48}[scale]
                        else:
                            est_hours = {"1x1": 6, "2x2": 36, "3x3": 168}[scale]

                    if status not in ("CONVERGED",):
                        pending.append({
                            "scale": scale,
                            "variant": v,
                            "site": s,
                            "dir": calc_dir,
                            "status": status,
                            "cores": cfg["cores_per_job"],
                            "mem_gb": cfg["mem_per_job_gb"],
                            "ionic_steps": steps,
                            "energy": energy,
                            "fmax": fmax,
                            "est_hours": est_hours,
                        })
    return pending


# ─── Parse elapsed time ─────────────────────────────────────────────────────

def parse_elapsed(elapsed_str):
    """Parse SLURM elapsed time string into hours."""
    days = 0
    if "-" in elapsed_str:
        d, elapsed_str = elapsed_str.split("-", 1)
        days = int(d)
    parts = elapsed_str.split(":")
    if len(parts) == 3:
        return days * 24 + int(parts[0]) + int(parts[1]) / 60 + int(parts[2]) / 3600
    elif len(parts) == 2:
        return days * 24 + int(parts[0]) / 60 + int(parts[1]) / 3600
    return 0


# ─── Display Functions ───────────────────────────────────────────────────────

def print_header(title, width=100):
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_section(title, width=100):
    print(f"\n--- {title} " + "-" * max(1, width - len(title) - 5))


def state_icon(state):
    """Return emoji icon for node state."""
    s = state.upper()
    if "DRAIN" in s and "IDLE" in s:
        return "🔴"
    elif "DRAIN" in s:
        return "🟡"
    elif "DOWN" in s:
        return "⛔"
    elif "IDLE" in s:
        return "🟢"
    elif "MIXED" in s:
        return "🟠"
    elif "ALLOC" in s:
        return "🔵"
    return "⚪"


def format_mem(mb):
    """Format memory in human-readable form."""
    if mb >= 1024:
        return f"{mb / 1024:.1f} GB"
    return f"{mb} MB"


# ─── Main Report ─────────────────────────────────────────────────────────────

def main():
    watch_mode = "--watch" in sys.argv
    submit_only = "--submit-check" in sys.argv

    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nodes = get_node_info()
        partition = get_partition_info()
        my_jobs = get_running_jobs()
        all_jobs = get_all_jobs()
        pending = get_pending_calculations()

        # ── Header ──
        print_header(f"ISKAY CLUSTER HEALTH & AVAILABILITY REPORT  |  {now}")

        # ── 1. Cluster Overview ──
        if not submit_only:
            print_section("1. CLUSTER OVERVIEW")
            total_cpus = sum(n["cpu_total"] for n in nodes)
            total_alloc = sum(n["cpu_alloc"] for n in nodes)
            total_free = total_cpus - total_alloc
            total_mem = sum(n["mem_total_mb"] for n in nodes)
            total_mem_alloc = sum(n["mem_alloc_mb"] for n in nodes)

            print(f"  Partition: {partition['name']} | State: {partition['state']} | "
                  f"Max walltime: {partition['max_time']}")
            print(f"  Total: {partition['total_nodes']} nodes, {total_cpus} cores, "
                  f"{format_mem(total_mem)} RAM")
            print(f"  Allocated: {total_alloc} cores ({total_alloc/total_cpus*100:.0f}%) | "
                  f"Free: {total_free} cores ({total_free/total_cpus*100:.0f}%)")
            print(f"  Memory: {format_mem(total_mem_alloc)} allocated / {format_mem(total_mem)} total")

        # ── 2. Node Details ──
        if not submit_only:
            print_section("2. NODE STATUS")
            print(f"  {'Node':<12} {'State':<20} {'Icon':^4} {'CPUs':^15} "
                  f"{'Load':^8} {'Memory':^25} {'Reason'}")
            print(f"  {'─'*12} {'─'*20} {'─'*4} {'─'*15} "
                  f"{'─'*8} {'─'*25} {'─'*30}")

            can_accept_jobs = False
            accepting_nodes = []
            for n in nodes:
                cpu_str = f"{n['cpu_alloc']}/{n['cpu_total']}"
                cpu_free = n["cpu_total"] - n["cpu_alloc"]
                mem_str = f"{format_mem(n['mem_alloc_mb'])}/{format_mem(n['mem_total_mb'])}"
                icon = state_icon(n["state"])

                # Determine if node accepts new jobs
                accepts = "DRAIN" not in n["state"].upper() and "DOWN" not in n["state"].upper()
                if accepts and cpu_free > 0:
                    can_accept_jobs = True
                    accepting_nodes.append((n["name"], cpu_free, n["mem_total_mb"] - n["mem_alloc_mb"]))

                # Truncate reason
                reason = n.get("reason", "None")
                if len(reason) > 30:
                    reason = reason[:27] + "..."

                print(f"  {n['name']:<12} {n['state']:<20} {icon:^4} {cpu_str:^15} "
                      f"{n['cpu_load']:>6.1f}  {mem_str:^25} {reason}")

            # Node hardware details
            if nodes:
                n = nodes[0]
                print(f"\n  Hardware: {n['arch']}, {n['sockets']} sockets × "
                      f"{n['cores_per_socket']} cores = {n['cpu_total']} cores/node")
                print(f"  OS: {n['os'][:60]}...")

        # ── 3. Running Jobs ──
        if not submit_only:
            print_section("3. RUNNING JOBS (yours)")
            if my_jobs:
                total_cores_used = 0
                print(f"  {'ID':<8} {'Name':<25} {'State':<10} {'Elapsed':>12} "
                      f"{'Cores':>6} {'Node':<12}")
                print(f"  {'─'*8} {'─'*25} {'─'*10} {'─'*12} {'─'*6} {'─'*12}")
                for j in my_jobs:
                    total_cores_used += j["cpus"]
                    print(f"  {j['id']:<8} {j['name']:<25} {j['state']:<10} {j['elapsed']:>12} "
                          f"{j['cpus']:>6} {j['reason']:<12}")
                print(f"\n  Total: {len(my_jobs)} jobs using {total_cores_used} cores")
            else:
                print("  No running jobs.")

            # Check if other users have jobs
            other_jobs = [j for j in all_jobs if j["user"] != os.getenv("USER", "juan")]
            if other_jobs:
                other_cores = sum(j["cpus"] for j in other_jobs)
                other_users = set(j["user"] for j in other_jobs)
                print(f"\n  Other users: {len(other_jobs)} jobs from {other_users}, "
                      f"using {other_cores} cores")
            else:
                print(f"\n  No other users on the cluster.")

        # ── 4. Availability Analysis ──
        print_section("4. AVAILABILITY ANALYSIS")

        # Check each node
        for n in nodes:
            cpu_free = n["cpu_total"] - n["cpu_alloc"]
            mem_free_mb = n["mem_total_mb"] - n["mem_alloc_mb"]
            is_draining = "DRAIN" in n["state"].upper()
            is_down = "DOWN" in n["state"].upper()

            status_msg = ""
            if is_down:
                status_msg = "⛔ DOWN — completely unavailable"
            elif is_draining and n["cpu_alloc"] > 0:
                status_msg = (f"🟡 DRAINING — {cpu_free} cores free but BLOCKED. "
                              f"Existing {n['cpu_alloc']} cores will run to completion.")
            elif is_draining and n["cpu_alloc"] == 0:
                status_msg = f"🔴 DRAINED — {cpu_free} cores idle but BLOCKED. No jobs accepted."
            elif cpu_free > 0:
                status_msg = f"🟢 AVAILABLE — {cpu_free} cores free, ready for jobs!"
            else:
                status_msg = f"🔵 FULLY ALLOCATED — {n['cpu_alloc']}/{n['cpu_total']} cores in use"

            print(f"  {n['name']}: {status_msg}")
            if is_draining or is_down:
                print(f"    Reason: {n.get('reason', 'unknown')}")

        # Overall verdict
        total_free_usable = sum(
            n["cpu_total"] - n["cpu_alloc"]
            for n in nodes
            if "DRAIN" not in n["state"].upper() and "DOWN" not in n["state"].upper()
        )
        total_free_blocked = sum(
            n["cpu_total"] - n["cpu_alloc"]
            for n in nodes
            if "DRAIN" in n["state"].upper() or "DOWN" in n["state"].upper()
        )

        print(f"\n  ┌─────────────────────────────────────────────────┐")
        if total_free_usable > 0:
            print(f"  │  ✅ {total_free_usable} cores AVAILABLE for new jobs          │")
        else:
            print(f"  │  ❌ NO CORES available — {total_free_blocked} cores blocked    │")
            print(f"  │  Action: Contact sysadmin to undrain nodes      │")
        print(f"  │  Blocked cores: {total_free_blocked:>3} (DRAIN/DOWN)                │")
        print(f"  └─────────────────────────────────────────────────┘")

        # ── 5. Pending Calculations ──
        print_section("5. PENDING CALCULATIONS & SUBMISSION PLAN")

        if pending:
            # Sort: quick wins first, then by scale
            priority_order = {"RUNNING": 0, "INTERRUPTED": 1, "NOT_STARTED": 2, "STARTED_NO_IONIC": 2}
            pending.sort(key=lambda x: (priority_order.get(x["status"], 3), x["est_hours"]))

            print(f"  {'Scale':<6} {'Variant':<8} {'Site':<6} {'Status':<14} "
                  f"{'Fmax':>8} {'Cores':>5} {'Est.Time':>10} {'Priority'}")
            print(f"  {'─'*6} {'─'*8} {'─'*6} {'─'*14} "
                  f"{'─'*8} {'─'*5} {'─'*10} {'─'*15}")

            total_pending_cores = 0
            quick_wins = []
            medium = []
            heavy = []

            for p in pending:
                fmax_str = f"{p['fmax']:.4f}" if p["fmax"] is not None else "—"
                if p["est_hours"] < 1:
                    time_str = f"{p['est_hours']*60:.0f} min"
                elif p["est_hours"] < 24:
                    time_str = f"{p['est_hours']:.0f} hrs"
                else:
                    time_str = f"{p['est_hours']/24:.1f} days"

                # Priority assignment
                if p["status"] == "RUNNING":
                    priority = "⏳ Running"
                elif p["est_hours"] <= 0.5:
                    priority = "🔥 Quick win"
                    quick_wins.append(p)
                elif p["est_hours"] <= 12:
                    priority = "🟡 Medium"
                    medium.append(p)
                else:
                    priority = "🔴 Heavy"
                    heavy.append(p)

                if p["status"] != "RUNNING":
                    total_pending_cores += p["cores"]

                print(f"  {p['scale']:<6} {p['variant']:<8} {p['site']:<6} {p['status']:<14} "
                      f"{fmax_str:>8} {p['cores']:>5} {time_str:>10} {priority}")

            # Summary
            print(f"\n  Pending calculations: {len([p for p in pending if p['status'] != 'RUNNING'])}")
            print(f"  Quick wins (<30min): {len(quick_wins)} (need {sum(p['cores'] for p in quick_wins)} cores)")
            print(f"  Medium (1-12h): {len(medium)} (need {sum(p['cores'] for p in medium)} cores)")
            print(f"  Heavy (>12h): {len(heavy)} (need {sum(p['cores'] for p in heavy)} cores)")
        else:
            print("  All calculations are either converged or running!")

        # ── 6. 3×3 Submission Analysis ──
        print_section("6. 3×3 SUBMISSION FEASIBILITY")

        pending_3x3 = [p for p in pending if p["scale"] == "3x3"]
        n3x3_jobs = len(pending_3x3)
        cores_3x3 = CALCS["3x3"]["cores_per_job"]
        total_3x3_cores = n3x3_jobs * cores_3x3
        mem_3x3 = CALCS["3x3"]["mem_per_job_gb"]

        print(f"  3×3 jobs pending: {n3x3_jobs}")
        print(f"  Resources per job: {cores_3x3} cores, {mem_3x3} GB RAM")
        print(f"  Total for all 3×3: {total_3x3_cores} cores, {n3x3_jobs * mem_3x3} GB RAM")
        print(f"  K-points: 5×5×1 (per advisor)")
        print(f"  Atoms: 72-73 per cell")
        print(f"  Estimated time per job: 5-7 days")

        can_submit = total_free_usable >= cores_3x3
        if can_submit:
            max_parallel = total_free_usable // cores_3x3
            print(f"\n  ✅ CAN SUBMIT: {max_parallel} jobs simultaneously ({total_free_usable} cores free)")
            if max_parallel >= n3x3_jobs:
                print(f"     → All {n3x3_jobs} jobs can run at once!")
                print(f"     → Total wall time: ~5-7 days for everything")
            else:
                batches = math.ceil(n3x3_jobs / max_parallel)
                print(f"     → Need {batches} batches of {max_parallel} jobs")
                print(f"     → Total wall time: ~{batches * 6:.0f} days sequential")
        else:
            print(f"\n  ❌ CANNOT SUBMIT NOW: Nodes are DRAINED")
            print(f"     Both nodes report: 'Kill task failed'")
            print(f"     → Contact sysadmin to clear drain status")
            print(f"\n  IF iskay202 undrained (256 cores):")
            max_on_202 = 256 // cores_3x3
            print(f"     → Can run {max_on_202} × 3×3 jobs simultaneously")
            print(f"     → All {n3x3_jobs} jobs in {math.ceil(n3x3_jobs / max_on_202)} batch(es)")
            print(f"     → Completed in ~5-7 days")
            print(f"\n  IF both nodes undrained (432+ free cores):")
            max_both = 432 // cores_3x3
            print(f"     → Can run {max_both} × 3×3 jobs simultaneously")
            print(f"     → All {n3x3_jobs} jobs in {math.ceil(n3x3_jobs / max_both)} batch(es)")
            print(f"     → Plus all remaining 1×1 jobs (quick wins)")

        # ── 7. Recommended Actions ──
        print_section("7. RECOMMENDED ACTIONS")

        actions = []
        # Check draining
        draining = [n for n in nodes if "DRAIN" in n["state"].upper()]
        if draining:
            actions.append(("🔧 CRITICAL", "Contact sysadmin to undrain nodes",
                           f"Nodes {', '.join(n['name'] for n in draining)} are DRAINED. "
                           f"Reason: {draining[0].get('reason', 'unknown')}"))

        # Check H2 reference
        h2_pending = [p for p in pending if p["scale"] == "H2_ref"]
        if h2_pending:
            actions.append(("⚡ BLOCKER", "Submit H₂ yes_vdw reference",
                           "Required for ALL PBE+D3 adsorption energies. ~10 min job."))

        # Near-converged
        near_done = [p for p in pending if p["fmax"] is not None and p["fmax"] < 0.025
                     and p["status"] == "INTERRUPTED"]
        if near_done:
            names = ", ".join(f"{p['scale']} {p['variant']}/{p['site']}" for p in near_done)
            actions.append(("⚡ QUICK WIN", f"Restart {len(near_done)} near-converged jobs",
                           f"Jobs with Fmax < EDIFFG: {names}. Need ~1 ionic step each."))

        # 3×3
        if pending_3x3:
            if can_submit:
                actions.append(("📋 SUBMIT", "Submit 3×3 calculations",
                               f"{n3x3_jobs} jobs ready. KPOINTS = 5×5×1 confirmed."))
            else:
                actions.append(("⏸️  WAIT", "3×3 submission blocked",
                               "Cannot submit until nodes are undrained."))

        for i, (level, action, detail) in enumerate(actions, 1):
            print(f"  {i}. [{level}] {action}")
            print(f"     {detail}")

        print("\n" + "=" * 100 + "\n")

        if not watch_mode:
            break
        else:
            import time
            print("  Refreshing in 60 seconds... (Ctrl+C to stop)")
            try:
                time.sleep(60)
            except KeyboardInterrupt:
                print("\n  Monitoring stopped.")
                break


if __name__ == "__main__":
    main()
