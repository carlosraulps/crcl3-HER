#!/usr/bin/env python3
"""
================================================================================
 VASP REAL-TIME ESTIMATION & CONVERGENCE ANALYTICS ENGINE
================================================================================
 Calculates and displays:
   1. Micro-Progress: Electronic SCF loop convergence % via logarithmic dE decay.
   2. Macro-Progress: Structural force relaxation % (F_max -> EDIFFG = 0.025 eV/A).
   3. Speed Analytics: Computation rate (seconds/SCF cycle, minutes/ionic step).
   4. Predictive ETA: Dynamic time-to-completion projection.
================================================================================
"""

import os
import sys
import re
import math
import time
import subprocess
from datetime import datetime, timedelta

ROOT_DIRS = [
    ("/home/juan/Carlos/crcl3-3x3-h_ads-without-U", "3x3"),
    ("/home/juan/Carlos/crcl3-1x1-h_ads-without-U", "1x1"),
    ("/home/juan/Carlos/crcl3-2x2-h_ads-without-U", "2x2"),
]


def get_slurm_jobs():
    """Returns mapping of workdir -> slurm job info."""
    jobs = {}
    try:
        out = subprocess.check_output(
            ["squeue", "-u", os.getenv("USER", "juan"), "-h", "-o", "%i|%j|%T|%M|%Z"],
            text=True
        )
        for line in out.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.strip().split("|")
            if len(parts) >= 5:
                job_id, name, state, walltime, workdir = parts[0], parts[1], parts[2], parts[3], parts[4]
                jobs[os.path.abspath(workdir)] = {
                    "id": job_id, "name": name, "state": state, "walltime": walltime
                }
    except Exception:
        pass
    return jobs


def parse_elapsed_seconds(walltime_str):
    """Parses SLURM walltime [days-]hours:minutes:seconds into seconds."""
    if not walltime_str or walltime_str == "N/A":
        return 0
    days = 0
    if "-" in walltime_str:
        d_part, walltime_str = walltime_str.split("-", 1)
        days = int(d_part)
    parts = [int(p) for p in walltime_str.split(":")]
    if len(parts) == 2:
        return days * 86400 + parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return days * 86400 + parts[0] * 3600 + parts[1] * 60 + parts[2]
    return 0


def format_duration(seconds):
    """Format seconds into readable H:MM:SS or MM:SS."""
    if seconds <= 0 or math.isnan(seconds) or math.isinf(seconds):
        return "--:--"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m:02d}m"
    return f"{m:02d}m {s:02d}s"


def parse_calculation(calc_dir, slurm_info=None):
    incar_path = os.path.join(calc_dir, "INCAR")
    outcar_path = os.path.join(calc_dir, "OUTCAR")
    oszicar_path = os.path.join(calc_dir, "OSZICAR")
    vaspout_path = os.path.join(calc_dir, "vasp.out")

    ediff = 1.0e-6
    ediffg = 0.025
    nsw = 100
    if os.path.exists(incar_path):
        try:
            with open(incar_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "EDIFF" in line and "=" in line and "EDIFFG" not in line:
                        ediff = float(line.split("=")[1].split("#")[0].strip())
                    elif "EDIFFG" in line and "=" in line:
                        ediffg = abs(float(line.split("=")[1].split("#")[0].strip()))
                    elif "NSW" in line and "=" in line:
                        nsw = int(line.split("=")[1].split("#")[0].strip())
        except Exception:
            pass

    # Electronic SCF progress
    current_iter = 0
    init_de = None
    curr_de = None
    curr_energy = None
    algo = "DAV"
    if os.path.exists(vaspout_path):
        try:
            with open(vaspout_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line_s = line.strip()
                    if line_s.startswith("DAV:") or line_s.startswith("RMM:"):
                        parts = line_s.split()
                        algo = parts[0].replace(":", "")
                        current_iter = int(parts[1])
                        curr_energy = float(parts[2])
                        de_val = abs(float(parts[3]))
                        if init_de is None and current_iter > 1:
                            init_de = de_val
                        curr_de = de_val
        except Exception:
            pass

    # Logarithmic SCF progress %
    scf_pct = 0.0
    if current_iter > 0:
        if curr_de is not None and init_de is not None and init_de > ediff:
            log_init = math.log10(max(init_de, 1.0))
            log_target = math.log10(ediff)
            log_curr = math.log10(max(curr_de, ediff))
            scf_pct = max(5.0, min(99.0, ((log_init - log_curr) / (log_init - log_target)) * 100.0))
        else:
            scf_pct = min(85.0, current_iter * 6.0)

    # Ionic step progress
    ionic_steps = 0
    if os.path.exists(oszicar_path):
        try:
            with open(oszicar_path, "r", encoding="utf-8", errors="ignore") as f:
                ionic_steps = sum(1 for line in f if "F=" in line)
        except Exception:
            pass

    # Force convergence & OUTCAR analysis
    converged = False
    init_force = None
    max_force = None
    if os.path.exists(outcar_path):
        try:
            with open(outcar_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if "reached required accuracy" in content:
                converged = True
            force_matches = re.findall(r"TOTAL-FORCE \(eV/Angst\)\s+-+\s+([\s\S]+?)\s+-+", content)
            if force_matches:
                for block in force_matches:
                    f_list = []
                    for row in block.strip().split("\n"):
                        cols = row.split()
                        if len(cols) >= 6:
                            try:
                                fx, fy, fz = float(cols[3]), float(cols[4]), float(cols[5])
                                f_list.append(math.sqrt(fx*fx + fy*fy + fz*fz))
                            except Exception:
                                pass
                    if f_list:
                        if init_force is None:
                            init_force = max(f_list)
                        max_force = max(f_list)
        except Exception:
            pass

    # Macro geometric progress %
    if converged:
        geom_pct = 100.0
    elif max_force is not None and init_force is not None and init_force > ediffg:
        log_init_f = math.log10(init_force)
        log_targ_f = math.log10(ediffg)
        log_curr_f = math.log10(max(max_force, ediffg))
        geom_pct = max(0.0, min(99.0, ((log_init_f - log_curr_f) / (log_init_f - log_targ_f)) * 100.0))
    elif ionic_steps > 0:
        geom_pct = min(95.0, (ionic_steps / nsw) * 100.0)
    else:
        # First ionic step in progress (represents initial ~10% of total calculation)
        geom_pct = scf_pct * 0.10

    # Speed & ETA calculation
    elapsed_sec = parse_elapsed_seconds(slurm_info.get("walltime") if slurm_info else "0")
    sec_per_iter = None
    eta_step_str = "--"
    eta_total_str = "--"

    if current_iter > 0 and elapsed_sec > 60:
        sec_per_iter = elapsed_sec / current_iter
        # Typical first step takes ~18-22 iterations
        rem_iters = max(1, 20 - current_iter)
        eta_step_sec = rem_iters * sec_per_iter
        eta_step_str = format_duration(eta_step_sec)
        
        # Typical relaxation takes ~10-15 ionic steps, where subsequent steps take ~6-8 iters
        rem_steps = max(1, 10 - ionic_steps)
        eta_total_sec = eta_step_sec + (rem_steps - 1) * (7 * sec_per_iter)
        eta_total_str = format_duration(eta_total_sec)

    return {
        "dir": calc_dir,
        "algo": algo,
        "current_iter": current_iter,
        "scf_pct": scf_pct,
        "curr_energy": curr_energy,
        "curr_de": curr_de,
        "ionic_steps": ionic_steps,
        "nsw": nsw,
        "max_force": max_force,
        "ediffg": ediffg,
        "geom_pct": geom_pct,
        "converged": converged,
        "sec_per_iter": sec_per_iter,
        "eta_step": eta_step_str,
        "eta_total": eta_total_str,
    }


def make_bar(percent, width=12):
    """Render a visual ASCII progress bar."""
    filled = int(round((percent / 100.0) * width))
    filled = min(width, max(0, filled))
    bar = "=" * filled + ">" if filled < width else "=" * width
    return f"[{bar:<{width}}] {percent:5.1f}%"


def main():
    slurm_jobs = get_slurm_jobs()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n" + "=" * 115)
    print(f" VASP CONVERGENCE, SPEED & COMPLETION ESTIMATION DASHBOARD  |  {now_str}")
    print("=" * 115)
    header = (
        f"{'Scale':<5} {'Variant':<8} {'Site':<6} {'Job ID':<7} {'State':<8} "
        f"{'Elapsed':<8} {'SCF Loop':<10} {'SCF %':<19} {'Forces (eV/A)':<15} "
        f"{'Total %':<19} {'ETA Step':<9} {'ETA Total'}"
    )
    print(header)
    print("-" * 115)

    total_calcs = 0
    active_calcs = 0

    for root, scale_label in ROOT_DIRS:
        if not os.path.exists(root):
            continue
        variants = ["no_vdw", "yes_vdw"]
        sites = ["clean", "S1", "S2", "S3"]
        for v in variants:
            for s in sites:
                calc_dir = os.path.join(root, v, s)
                if not os.path.exists(calc_dir):
                    continue
                total_calcs += 1
                slurm_info = slurm_jobs.get(os.path.abspath(calc_dir), {})
                state = slurm_info.get("state", "IDLE")
                job_id = slurm_info.get("id", "--")
                walltime = slurm_info.get("walltime", "--")

                if state == "RUNNING":
                    active_calcs += 1

                data = parse_calculation(calc_dir, slurm_info)

                # Format columns
                scf_str = f"{data['algo']}:{data['current_iter']}" if data['current_iter'] > 0 else "--"
                scf_bar = make_bar(data["scf_pct"], width=10) if state == "RUNNING" else "[----------]   0.0%"
                
                if data["converged"]:
                    force_str = "CONVERGED"
                    geom_bar = "[==========] 100.0%"
                elif data["max_force"] is not None:
                    force_str = f"{data['max_force']:.4f} / {data['ediffg']}"
                    geom_bar = make_bar(data["geom_pct"], width=10)
                else:
                    force_str = f"-- / {data['ediffg']}"
                    geom_bar = make_bar(data["geom_pct"], width=10) if state == "RUNNING" else "[----------]   0.0%"

                print(
                    f"{scale_label:<5} {v:<8} {s:<6} {job_id:<7} {state:<8} "
                    f"{walltime:<8} {scf_str:<10} {scf_bar:<19} {force_str:<15} "
                    f"{geom_bar:<19} {data['eta_step']:<9} {data['eta_total']}"
                )

    print("-" * 115)
    print(f" Summary: {active_calcs} of {total_calcs} calculations actively computing on cluster.")
    print(" Progress Metrics Legend:")
    print("   * SCF %: Logarithmic electronic decay progress towards EDIFF = 1e-6 eV (|dE_curr| -> 1e-6).")
    print("   * Total %: Structural relaxation progress (Step 1 SCF weight + Max Force reduction -> 0.025 eV/A).")
    print("   * ETA Step: Estimated time until current ionic step completes.")
    print("   * ETA Total: Estimated time to complete full structural relaxation (paper standard).")
    print("=" * 115 + "\n")


if __name__ == "__main__":
    main()
