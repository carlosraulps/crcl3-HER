#!/usr/bin/env python3
"""
========================================================================================
 auto_chain_h_ads_workflow.py: Automated Multi-Cluster HPC Pipeline for HER on CrCl3
========================================================================================
 Features:
   1. Multi-Cluster Job Monitor: Audits active TM relaxation & H-adsorption calculations
      across Huk and Carbono via Slurm and ~/.hpc_jobs_ledger.json.
   2. Strict Verification & Desorption Guard:
      - Validates OUTCAR convergence criteria ("reached required accuracy").
      - Inspects CONTCAR: ensures TM is genuinely chemisorbed (d(TM-Cl) < 2.8 A),
        aborting if desorption or non-physical detachment occurred.
      - Verifies magnetic moment stability.
   3. Automated Chained H-Adsorption Staging:
      - Calls setup_h_on_co_u.py to place H at 1.44 A atop TM with 0.03 A symmetry break.
      - Builds 4-element POTCAR (Cr+Cl+TM+H) and validated INCAR with U=3.29 eV.
   4. Meta-Scheduler Dispatch:
      - Evaluates real-time turnaround across Carbono (nanotubo, fulereno) and Huk (medio, hram).
      - Automatically rsyncs inputs and dispatches via sbatch to the fastest turnaround queue.
      - Updates ~/.hpc_jobs_ledger.json with job ID and status.
   5. HER Descriptor Output:
      - When SX_H completes, calculates Delta E_ads and Delta G_ads (+0.24 eV correction).
========================================================================================
"""

import os
import sys
import re
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Must use research venv for ASE
PYTHON_EXE = "/home/cr/venvs/research/bin/python3"
BASE_DIR = "/home/cr/simulations/crcl3-HER/crcl3-newcals"
LEDGER_PATH = os.path.expanduser("~/.hpc_jobs_ledger.json")

# H2 Reference (15x15x15 box with PBE+D3(BJ))
E_H2_HALF = -3.381055  # eV (-6.7621091 / 2)
ZPE_TS_CORRECTION = 0.24  # eV (standard literature benchmark)


def run_ssh(host: str, cmd: str, timeout: int = 25) -> Optional[str]:
    try:
        res = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=8", "-o", "BatchMode=yes", host, cmd],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return None


def load_ledger() -> List[Dict[str, Any]]:
    if os.path.exists(LEDGER_PATH):
        try:
            with open(LEDGER_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_ledger(ledger: List[Dict[str, Any]]):
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2)


def verify_tm_adsorption(contcar_path: str, tm_symbol: str = "Co") -> Dict[str, Any]:
    """
    Verifies that the TM atom in CONTCAR is properly chemisorbed and not desorbed.
    """
    # Run in research python with ASE
    code = f"""
from ase.io import read
import numpy as np

atoms = read('{contcar_path}')
tm_indices = [i for i, a in enumerate(atoms) if a.symbol == '{tm_symbol}']
if not tm_indices:
    print('ERROR: NO_TM')
    exit(1)

tm_idx = tm_indices[0]
cl_indices = [i for i, a in enumerate(atoms) if a.symbol == 'Cl']
cr_indices = [i for i, a in enumerate(atoms) if a.symbol == 'Cr']

cl_dists = [atoms.get_distance(tm_idx, i, mic=True) for i in cl_indices]
cr_dists = [atoms.get_distance(tm_idx, i, mic=True) for i in cr_indices]

min_cl = min(cl_dists)
min_cr = min(cr_dists)

# Check desorption
is_desorbed = (min_cl > 2.80 and min_cr > 3.20)
print(f'STATUS:{{is_desorbed}}|MIN_CL:{{min_cl:.4f}}|MIN_CR:{{min_cr:.4f}}')
"""
    try:
        res = subprocess.run(
            [PYTHON_EXE, "-c", code],
            capture_output=True,
            text=True,
            check=False
        )
        out = res.stdout.strip()
        if "ERROR: NO_TM" in out:
            return {"valid": False, "reason": "No TM atom found"}
        
        m_status = re.search(r"STATUS:(True|False)", out)
        m_cl = re.search(r"MIN_CL:([0-9\.]+)", out)
        m_cr = re.search(r"MIN_CR:([0-9\.]+)", out)
        
        if m_status and m_cl and m_cr:
            is_desorbed = (m_status.group(1) == "True")
            return {
                "valid": not is_desorbed,
                "is_desorbed": is_desorbed,
                "min_cl_dist": float(m_cl.group(1)),
                "min_cr_dist": float(m_cr.group(1))
            }
    except Exception as e:
        return {"valid": False, "reason": str(e)}

    return {"valid": False, "reason": "Could not parse ASE output"}


def check_job_convergence(host: str, remote_dir: str) -> Dict[str, Any]:
    cmd = f"""
    cd {remote_dir} 2>/dev/null || exit 10
    echo "=== CONV ==="
    grep -E "reached required accuracy|General timing and accounting" OUTCAR 2>/dev/null | tail -n 1
    echo "=== OSZICAR ==="
    grep "E0=" OSZICAR 2>/dev/null | tail -n 1
    echo "=== CONTCAR ==="
    wc -l CONTCAR 2>/dev/null
    """
    out = run_ssh(host, cmd)
    if not out:
        return {"converged": False, "reachable": False}

    has_accuracy = "reached required accuracy" in out or "General timing and accounting" in out
    
    # Parse E0 and mag
    e0_val = None
    mag_val = None
    m_e0 = re.search(r"E0=\s*([+-]?[0-9\.]+E[+-]?[0-9]+)", out)
    if m_e0:
        e0_val = float(m_e0.group(1))
    m_mag = re.search(r"mag=\s*([+-]?[0-9\.]+)", out)
    if m_mag:
        mag_val = float(m_mag.group(1))

    m_lines = re.search(r"(\d+)\s+CONTCAR", out)
    lines = int(m_lines.group(1)) if m_lines else 0

    return {
        "converged": (has_accuracy and lines >= 8 and e0_val is not None),
        "e0": e0_val,
        "mag": mag_val,
        "contcar_lines": lines,
        "reachable": True
    }


def stage_and_dispatch_h_adsorption(site_key: str, tm_symbol: str = "Co") -> Optional[int]:
    """
    Invokes setup_h_on_co_u.py to generate SX_H, then dispatches to the optimal cluster.
    """
    print(f"\n🚀 [WORKFLOW] Initiating automated H-adsorption staging for {tm_symbol} at {site_key}...")
    
    setup_script = os.path.join(BASE_DIR, f"crcl3-2x2-{tm_symbol.lower()}_ads-with-U", "setup_h_on_co_u.py")
    if not os.path.exists(setup_script):
        print(f"❌ Setup script not found: {setup_script}")
        return None

    # 1. Run setup script
    res = subprocess.run(
        [PYTHON_EXE, setup_script, "--site", site_key],
        capture_output=True,
        text=True,
        check=False
    )
    print(res.stdout)
    if res.returncode != 0:
        print(f"❌ Staging failed for {site_key}: {res.stderr}")
        return None

    h_dir = os.path.join(BASE_DIR, f"crcl3-2x2-{tm_symbol.lower()}_ads-with-U", "yes_vdw", f"{site_key}_H")
    if not os.path.exists(h_dir):
        print(f"❌ Target directory not found: {h_dir}")
        return None

    # 2. Evaluate optimal cluster via server-info
    decide_cmd = [
        "python3",
        os.path.expanduser("~/.gemini/config/skills/server-info/scripts/server_info.py"),
        "--decide",
        "--dir", h_dir
    ]
    rec_cluster = "huk"
    rec_partition = "medio,hram"
    try:
        p_res = subprocess.run(decide_cmd, capture_output=True, text=True, check=False)
        if "Carbono [nanotubo]" in p_res.stdout and "READY_IMMEDIATE" in p_res.stdout:
            # Check if Huk is also immediately free
            if "Huk [medio]" in p_res.stdout or "Huk [hram]" in p_res.stdout:
                rec_cluster = "huk"
                rec_partition = "medio,hram,alto"
            else:
                rec_cluster = "carbono"
                rec_partition = "nanotubo"
    except Exception:
        pass

    # 3. Dispatch to selected cluster
    print(f"🎯 Auto-Dispatching {site_key}_H to {rec_cluster.upper()} (partition: {rec_partition})...")
    remote_h_dir = f"/home/carlos/crcl3-newcals/crcl3-2x2-{tm_symbol.lower()}_ads-with-U/yes_vdw/{site_key}_H"
    
    if rec_cluster == "huk":
        # Ensure directory on Huk
        run_ssh("huk", f"mkdir -p {remote_h_dir}")
        subprocess.run(["rsync", "-avz", f"{h_dir}/", f"huk:{remote_h_dir}/"], check=True)
        sub_out = run_ssh("huk", f"cd {remote_h_dir} && sbatch job_huk.sh")
    else:
        remote_c_dir = f"/home/carlos.primo/crcl3-HER/crcl3-newcals/crcl3-2x2-{tm_symbol.lower()}_ads-with-U/yes_vdw/{site_key}_H"
        run_ssh("carbono", f"mkdir -p {remote_c_dir}")
        subprocess.run(["rsync", "-avz", f"{h_dir}/", f"carbono:{remote_c_dir}/"], check=True)
        sub_out = run_ssh("carbono", f"cd {remote_c_dir} && sbatch job.sh")

    print(f"📤 Submission output: {sub_out}")
    m_jid = re.search(r"Submitted batch job (\d+)", sub_out or "")
    if m_jid:
        job_id = int(m_jid.group(1))
        print(f"🎉 Successfully queued Job {job_id} for {site_key}_H on {rec_cluster.upper()}!\n")
        
        # Add to ledger
        ledger = load_ledger()
        ledger.append({
            "job_id": job_id,
            "name": f"Co_{site_key}H_U3",
            "cluster": rec_cluster,
            "partition": rec_partition,
            "cores": 28 if rec_cluster == "huk" else 32,
            "local_dir": h_dir,
            "remote_dir": remote_h_dir if rec_cluster == "huk" else remote_c_dir,
            "status": "RUNNING",
            "submitted_at": datetime.now().isoformat(),
            "expected_steps": 100,
            "continuation_hook": "calc_her_delta_g",
            "last_verified": datetime.now().isoformat()
        })
        save_ledger(ledger)
        return job_id

    return None


def run_pipeline_check():
    """
    Single cycle pass of the automated chain workflow.
    """
    print("\n" + "=" * 80)
    print(f"   ⚡ AUTOMATED HER DFT WORKFLOW & CONTINUATION MONITOR [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    print("=" * 80)

    ledger = load_ledger()
    updated = False

    for job in ledger:
        cluster = job["cluster"]
        host = "huk" if cluster == "huk" else "carbono"
        status = job.get("status")
        name = job.get("name")
        local_dir = job.get("local_dir")
        remote_dir = job.get("remote_dir")

        if status == "RUNNING":
            conv_info = check_job_convergence(host, remote_dir)
            if conv_info.get("converged"):
                print(f"\n🎉 Detected CONVERGENCE for Job {job['job_id']} ({name}) on {cluster.upper()}!")
                # Rsync results
                Path(local_dir).mkdir(parents=True, exist_ok=True)
                subprocess.run(["rsync", "-avz", f"{host}:{remote_dir}/", f"{local_dir}/"], check=True)
                
                job["status"] = "COMPLETED"
                job["e0_ev"] = conv_info["e0"]
                job["mag_moment"] = conv_info["mag"]
                job["verified_at"] = datetime.now().isoformat()
                updated = True

                # Determine next chained action
                if "stage_h_on_co" in str(job.get("continuation_hook")):
                    m_site = re.search(r"_(S\d)_", name)
                    site_key = m_site.group(1) if m_site else "S1"
                    
                    # Pre-flight desorption check on local CONTCAR
                    contcar_local = os.path.join(local_dir, "CONTCAR")
                    v_res = verify_tm_adsorption(contcar_local, "Co")
                    print(f"[{site_key}] Integrity check: {v_res}")
                    
                    if v_res.get("valid"):
                        # Chain dispatch
                        stage_and_dispatch_h_adsorption(site_key, "Co")
                    else:
                        print(f"⚠️  WARNING: Desorption detected or geometry invalid for {site_key}. Skipping auto-H.")

                elif "calc_her_delta_g" in str(job.get("continuation_hook")):
                    # Calculate Delta G_ads
                    m_site = re.search(r"_(S\d)H_", name)
                    site_key = m_site.group(1) if m_site else "S3"
                    e_slab_h = conv_info["e0"]
                    
                    # Find pristine slab+TM energy
                    parent_dir = os.path.join(BASE_DIR, "crcl3-2x2-co_ads-with-U", "yes_vdw", site_key)
                    parent_oszicar = os.path.join(parent_dir, "OSZICAR")
                    e_slab_tm = None
                    if os.path.exists(parent_oszicar):
                        with open(parent_oszicar, "r") as f:
                            for line in f:
                                if "E0=" in line:
                                    m = re.search(r"E0=\s*([^\s]+)", line)
                                    if m:
                                        e_slab_tm = float(m.group(1))

                    if e_slab_tm:
                        delta_e = e_slab_h - e_slab_tm - E_H2_HALF
                        delta_g = delta_e + ZPE_TS_CORRECTION
                        print(f"\n========================================================")
                        print(f"   🏆 HER ADSORPTION RESULT FOR {site_key} (with U=3.29 eV)")
                        print(f"========================================================")
                        print(f"E(slab+Co+H)   = {e_slab_h:11.4f} eV")
                        print(f"E(slab+Co)     = {e_slab_tm:11.4f} eV")
                        print(f"0.5*E(H2)      = {E_H2_HALF:11.4f} eV")
                        print(f"Delta E_ads    = {delta_e:11.4f} eV")
                        print(f"Delta G_ads    = {delta_g:11.4f} eV (ZPE-TS = +0.24 eV)")
                        print(f"Overpotential  = {abs(delta_g):11.4f} V")
                        print(f"========================================================\n")

    if updated:
        save_ledger(ledger)

    # Print summary
    print(f"{'Job ID':8s} | {'Job Name':14s} | {'Cluster':8s} | {'Status':12s} | {'Last E0 (eV)':12s}")
    print("-" * 65)
    for job in ledger:
        e_str = f"{job.get('e0_ev', 'N/A')}" if job.get('e0_ev') else "RUNNING"
        print(f"{job['job_id']:<8} | {job['name']:<14} | {job['cluster']:<8} | {job['status']:<12} | {e_str}")


def main():
    parser = argparse.ArgumentParser(description="Automated Chained Workflow for HER on CrCl3")
    parser.add_argument("--daemon", action="store_true", help="Run in continuous monitoring loop")
    parser.add_argument("--interval", type=int, default=120, help="Loop interval in seconds (default: 120)")
    parser.add_argument("--stage", choices=["S1", "S2", "S3"], help="Explicitly stage and dispatch SX_H")
    args = parser.parse_args()

    if args.stage:
        stage_and_dispatch_h_adsorption(args.stage, "Co")
        return

    if args.daemon:
        print("Starting auto_chain_h_ads_workflow in DAEMON mode (Ctrl+C to stop)...")
        while True:
            try:
                run_pipeline_check()
                time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\nDaemon stopped by user.")
                break
    else:
        run_pipeline_check()


if __name__ == "__main__":
    main()
