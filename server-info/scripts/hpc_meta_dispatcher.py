#!/usr/bin/env python3
"""
hpc_meta_dispatcher.py

Intelligent General HPC Meta-Scheduler & Dispatcher Engine.
Audits live clusters (Carbono, Huk, Iskay, Local), evaluates node-level core
fragmentation, computes empirical turnaround times, dynamically adapts Slurm
batch scripts to target hardware architectures, syncs inputs, and submits jobs.

Usage:
  hpc_meta_dispatcher.py --decide [--dir <calc_dir>] [--steps N] [--atoms N]
  hpc_meta_dispatcher.py --dispatch <calc_dir> [--target <cluster>] [--hook <continuation_hook>]
"""

import sys
import os
import json
import re
import math
import shutil
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

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

CLUSTERS = {
    "carbono": {
        "name": "Carbono",
        "host": "carbono",
        "user": "carlos.primo",
        "arch": "AMD EPYC (Zen 2/3, 128/192c)",
        "remote_base": "~/crcl3-HER",
        "base_rate_64": 4.14,  # min / ionic step for ~33 atoms
        "base_rate_32": 6.41,
        "partitions": {
            "fulereno": {"min_cpus": 64, "max_cpus": 128, "max_tres_pu": 384, "walltime": "5-00:00:00"},
            "nanotubo": {"min_cpus": 17, "max_cpus": 64, "max_tres_pu": 384, "walltime": "5-00:00:00"},
            "grafeno":  {"min_cpus": 1,  "max_cpus": 16, "max_tres_pu": 384, "walltime": "5-00:00:00"}
        },
        "modules": "module load vasp\nmodule load intel/2021.4\nmodule load openmpi/4.1.2-intel",
        "mpirun_cmd": "mpirun vasp_std"
    },
    "huk": {
        "name": "Huk",
        "host": "huk",
        "user": "carlos",
        "arch": "Intel Xeon (28c medio / 36c alto)",
        "remote_base": "/home/carlos/crcl3-newcals",
        "base_rate_alto": 8.50,   # min / step for ~33 atoms on 36c
        "base_rate_medio": 12.62, # min / step for ~33 atoms on 28c
        "partitions": {
            "alto":  {"nodes": ["huk120", "huk121"], "cores": 36, "max_walltime_days": 7},
            "medio": {"nodes": ["huk122", "huk123", "huk124"], "cores": 28, "max_walltime_days": 30},
            "hram":  {"nodes": ["huk119"], "cores": 40, "ram_gb": 504, "max_walltime_days": 7},
            "normal":{"nodes": ["huk125", "huk126", "huk127", "huk128"], "cores": 24, "max_walltime_days": 90}
        },
        "mpirun_cmd": "mpirun -np {CORES} vasp_std"
    },
    "iskay": {
        "name": "Iskay",
        "host": "iskay",
        "user": "juan",
        "arch": "High Density AMD EPYC (256c per node)",
        "remote_base": "/home/juan/Carlos/crcl3-HER",
        "base_rate_64": 4.50,
        "base_rate_32": 7.00,
        "partitions": {
            "normal": {"nodes": ["iskay201", "iskay202"], "cores_per_node": 256, "max_walltime_days": 14}
        },
        "mpirun_cmd": "mpirun -np {CORES} vasp_std"
    }
}


def run_ssh(host: str, cmd: str, timeout: int = 8) -> Optional[str]:
    try:
        res = subprocess.run(
            ["ssh", "-q", "-o", "BatchMode=yes", "-o", f"ConnectTimeout={timeout}", host, cmd],
            capture_output=True, text=True, check=True, timeout=timeout
        )
        return res.stdout
    except Exception:
        return None


def inspect_calculation_dir(calc_dir: str) -> Dict[str, Any]:
    """
    Parses POSCAR, INCAR, KPOINTS in calc_dir to extract system parameters.
    """
    calc_path = Path(calc_dir).resolve()
    info = {
        "dir": str(calc_path),
        "name": calc_path.name,
        "atoms": 33,
        "elements": [],
        "supercell": "2x2",
        "kpoints": 4,
        "steps": 40,
        "is_hybrid": False,
        "has_u": False,
        "u_val": 0.0,
        "valid": False
    }

    poscar = calc_path / "POSCAR"
    if poscar.exists():
        try:
            with open(poscar, "r") as f:
                lines = [l.strip() for l in f if l.strip()]
            if len(lines) >= 7:
                # Line 6: species, Line 7: counts
                species = lines[5].split()
                counts = [int(x) for x in lines[6].split() if x.isdigit()]
                tot_atoms = sum(counts)
                info["atoms"] = tot_atoms
                info["elements"] = species
                if tot_atoms <= 12:
                    info["supercell"] = "1x1"
                elif tot_atoms <= 40:
                    info["supercell"] = "2x2"
                else:
                    info["supercell"] = "3x3"
                info["valid"] = True
        except Exception:
            pass

    incar = calc_path / "INCAR"
    if incar.exists():
        try:
            with open(incar, "r") as f:
                text = f.read()
            m_nsw = re.search(r"NSW\s*=\s*(\d+)", text, re.IGNORECASE)
            if m_nsw:
                info["steps"] = int(m_nsw.group(1))
            if "LHFCALC = .TRUE." in text or "HSE" in text:
                info["is_hybrid"] = True
            if "LDAU = .TRUE." in text:
                info["has_u"] = True
                m_u = re.search(r"LDAUU\s*=\s*([0-9\.\s]+)", text)
                if m_u:
                    vals = [float(x) for x in m_u.group(1).split() if re.match(r"^\d", x)]
                    info["u_val"] = max(vals) if vals else 0.0
        except Exception:
            pass

    kpoints = calc_path / "KPOINTS"
    if kpoints.exists():
        try:
            with open(kpoints, "r") as f:
                klines = [l.strip() for l in f if l.strip()]
            if len(klines) >= 4:
                grid = [int(x) for x in klines[3].split()[:3] if x.isdigit()]
                if len(grid) == 3:
                    info["kpoints"] = grid[0] * grid[1] * grid[2]
        except Exception:
            pass

    return info


def audit_cluster_nodes(host: str) -> Optional[Dict[str, Any]]:
    """
    Parses node status and detects fragmentation per partition.
    Filters out GPU / non-compute partitions.
    """
    raw = run_ssh(host, "sinfo -N -o '%N|%P|%T|%C|%E'")
    if not raw:
        return None

    node_data = {}
    partition_nodes = {}

    for line in raw.strip().split("\n")[1:]:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue
        node, partition, state, cpus = parts[0], parts[1].rstrip("*"), parts[2], parts[3]

        # Ignore GPU nodes on Carbono
        if host == "carbono" and (node.startswith("gn") or partition in ("metano", "grafite", "etileno", "benzeno")):
            continue

        m = re.match(r"(\d+)/(\d+)/(\d+)/(\d+)", cpus)
        if m:
            alloc_c, idle_c, other_c, total_c = map(int, m.groups())
        else:
            alloc_c, idle_c, other_c, total_c = 0, 0, 0, 0

        if node not in node_data:
            node_data[node] = {
                "state": state,
                "partitions": [partition],
                "alloc": alloc_c,
                "idle": idle_c,
                "total": total_c,
            }
        else:
            if partition not in node_data[node]["partitions"]:
                node_data[node]["partitions"].append(partition)

        if partition not in partition_nodes:
            partition_nodes[partition] = []
        if node not in partition_nodes[partition]:
            partition_nodes[partition].append(node)

    total_idle = sum(n["idle"] for n in node_data.values())
    max_contiguous_idle = max((n["idle"] for n in node_data.values()), default=0)
    ready_nodes = [node for node, n in node_data.items() if n["idle"] > 0]
    fully_free_nodes = [node for node, n in node_data.items() if n["alloc"] == 0 and n["idle"] == n["total"] and "down" not in n["state"]]

    # Partition-specific contiguous idle
    part_contiguous = {}
    for part, p_nodes in partition_nodes.items():
        part_contiguous[part] = max((node_data[n]["idle"] for n in p_nodes if n in node_data), default=0)

    return {
        "nodes": node_data,
        "partition_nodes": partition_nodes,
        "partition_contiguous": part_contiguous,
        "total_idle_cpus": total_idle,
        "max_contiguous_idle": max_contiguous_idle,
        "ready_nodes": ready_nodes,
        "fully_free_nodes": fully_free_nodes,
    }


def audit_cluster_queue(host: str, user: str) -> Dict[str, Any]:
    raw_user = run_ssh(host, f"squeue -u {user} -o '%i|%P|%j|%T|%M|%D|%C|%R'")
    raw_all = run_ssh(host, "squeue -o '%i|%P|%u|%T|%M|%D|%C|%R'")

    user_jobs = []
    if raw_user:
        for line in raw_user.strip().split("\n")[1:]:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 8:
                user_jobs.append({
                    "id": parts[0],
                    "partition": parts[1],
                    "name": parts[2],
                    "state": parts[3],
                    "time": parts[4],
                    "nodes": parts[5],
                    "cpus": parts[6],
                    "reason": parts[7]
                })

    all_jobs_count = len(raw_all.strip().split("\n")[1:]) if raw_all else 0
    running_count = len([l for l in raw_all.strip().split("\n")[1:] if "|R|" in l]) if raw_all else 0
    pending_count = len([l for l in raw_all.strip().split("\n")[1:] if "|PD|" in l]) if raw_all else 0

    return {
        "user_jobs": user_jobs,
        "total_jobs": all_jobs_count,
        "running_jobs": running_count,
        "pending_jobs": pending_count,
    }


def compute_turnaround_matrix(calc_info: Dict[str, Any]) -> Dict[str, Any]:
    atoms = calc_info.get("atoms", 33)
    steps = calc_info.get("steps", 40)
    scale_factor = (atoms / 33.0) ** 1.35

    audits = {}
    evaluations = {}

    for c_key, c_conf in CLUSTERS.items():
        n_audit = audit_cluster_nodes(c_conf["host"])
        q_audit = audit_cluster_queue(c_conf["host"], c_conf["user"])
        audits[c_key] = {"nodes": n_audit, "queue": q_audit}

    # 1. Huk Evaluation
    huk_n = audits["huk"]["nodes"]
    if huk_n:
        huk_idle_alto = any(n in ("huk120", "huk121") and huk_n["nodes"][n]["alloc"] == 0 for n in huk_n["fully_free_nodes"])
        huk_idle_medio = any(n in ("huk122", "huk123", "huk124") and huk_n["nodes"][n]["alloc"] == 0 for n in huk_n["fully_free_nodes"])
        huk_idle_hram = any(n == "huk119" and huk_n["nodes"][n]["alloc"] == 0 for n in huk_n["fully_free_nodes"])

        if huk_idle_alto:
            wait_huk = 0.0
            cores_huk = 36
            part_huk = "alto"
            rate_huk = CLUSTERS["huk"]["base_rate_alto"] * scale_factor
            target_node = "huk120/121 (alto, 36 CPUs, 100% idle)"
        elif huk_idle_medio:
            wait_huk = 0.0
            cores_huk = 28
            part_huk = "medio"
            rate_huk = CLUSTERS["huk"]["base_rate_medio"] * scale_factor
            target_node = "huk122-124 (medio, 28 CPUs, 100% idle)"
        elif huk_idle_hram and (calc_info.get("is_hybrid") or atoms >= 50):
            wait_huk = 0.0
            cores_huk = 40
            part_huk = "hram"
            rate_huk = CLUSTERS["huk"]["base_rate_alto"] * 0.9 * scale_factor
            target_node = "huk119 (hram, 40 CPUs, 100% idle)"
        else:
            # Active jobs waiting in queue
            user_active = len(audits["huk"]["queue"]["user_jobs"])
            wait_huk = 2.5 * user_active if user_active > 0 else 1.0
            cores_huk = 36
            part_huk = "alto,medio"
            rate_huk = CLUSTERS["huk"]["base_rate_alto"] * scale_factor
            target_node = f"Queued on Huk ({user_active} jobs ahead)"

        calc_huk = (steps * rate_huk) / 60.0
        evaluations["huk"] = {
            "cluster": "huk",
            "name": "Huk",
            "status": "READY_IMMEDIATE" if wait_huk == 0 else "QUEUED",
            "partition": part_huk,
            "cores": cores_huk,
            "wait_hr": wait_huk,
            "calc_hr": calc_huk,
            "tot_hr": wait_huk + calc_huk,
            "target": target_node,
            "rate_min_step": rate_huk,
            "confidence": "HIGH (Empirical)"
        }

    # 2. Carbono Evaluation
    carb_n = audits["carbono"]["nodes"]
    if carb_n:
        max_fulereno = carb_n["partition_contiguous"].get("fulereno", 0)
        max_nanotubo = carb_n["partition_contiguous"].get("nanotubo", 0)

        if max_fulereno >= 64:
            wait_c = 0.0
            cores_c = 64
            part_c = "fulereno"
            rate_c = CLUSTERS["carbono"]["base_rate_64"] * scale_factor
            target_c = f"Immediate in fulereno (Contiguous {max_fulereno} CPUs free)"
        elif max_nanotubo >= 32 and atoms <= 40:
            wait_c = 0.0
            cores_c = 32
            part_c = "nanotubo"
            rate_c = CLUSTERS["carbono"]["base_rate_32"] * scale_factor
            target_c = f"Immediate in nanotubo (32 CPUs free)"
        else:
            # Fragmented on standard compute nodes!
            wait_c = 24.0 # High wait when fragmented (empirical ~24-48h)
            cores_c = 64
            part_c = "fulereno"
            rate_c = CLUSTERS["carbono"]["base_rate_64"] * scale_factor
            target_c = f"Fragmented queue (Max contiguous={max_fulereno}c, need 64c)"

        calc_c = (steps * rate_c) / 60.0
        evaluations["carbono"] = {
            "cluster": "carbono",
            "name": "Carbono",
            "status": "READY_IMMEDIATE" if wait_c == 0 else "FRAGMENTED_WAIT",
            "partition": part_c,
            "cores": cores_c,
            "wait_hr": wait_c,
            "calc_hr": calc_c,
            "tot_hr": wait_c + calc_c,
            "target": target_c,
            "rate_min_step": rate_c,
            "confidence": "HIGH (Empirical)"
        }

    # Pick Winner
    winner_key = min(evaluations.keys(), key=lambda k: evaluations[k]["tot_hr"]) if evaluations else None

    return {
        "calc_info": calc_info,
        "audits": audits,
        "evaluations": evaluations,
        "winner": evaluations[winner_key] if winner_key else None
    }


def print_decision_report(matrix: Dict[str, Any]):
    calc = matrix["calc_info"]
    evals = matrix["evaluations"]
    winner = matrix["winner"]

    print(f"\n{BOLD}{CYAN}========================================================================================{RESET}")
    print(f"{BOLD}{CYAN}       🎯 HPC META-SCHEDULER & TURNAROUND OPTIMIZATION ENGINE{RESET}")
    print(f"{BOLD}{CYAN}========================================================================================{RESET}")
    print(f"System: {BOLD}{calc.get('name', 'Calculation')}{RESET} | Atoms: {calc['atoms']} | Steps: {calc['steps']} | Grid: {calc['kpoints']} k-points")
    print(f"Features: {'Hubbard U (' + str(calc['u_val']) + ' eV)' if calc['has_u'] else 'Standard DFT'} | Supercell: {calc['supercell']}")
    print("-" * 105)

    print(f"{'Cluster':<10} | {'Status':<20} | {'Wait Time':<12} | {'Compute Time':<14} | {'Total Turnaround':<18} | {'Partition & Node Target'}")
    print("-" * 105)

    for c_key, ev in evals.items():
        st_color = GREEN if ev['wait_hr'] == 0 else RED
        print(f"{BOLD}{ev['name']:<10}{RESET} | {st_color}{ev['status']:<20}{RESET} | {ev['wait_hr']:<5.1f} hours   | {ev['calc_hr']:<5.1f} hours    | {BOLD}{ev['tot_hr']:<5.1f} hours{RESET}        | {ev['partition']} ({ev['target']})")
    print("-" * 105)

    if winner:
        print(f"\n{BOLD}{GREEN}🏆 DISPATCH RECOMMENDATION: TARGET [{winner['name'].upper()}]!{RESET}")
        print(f"  • Partition      : {winner['partition']} ({winner['cores']} cores)")
        print(f"  • Turnaround     : {BOLD}{winner['tot_hr']:.1f} hours{RESET} (Compute: {winner['calc_hr']:.1f}h + Queue: {winner['wait_hr']:.1f}h)")
        print(f"  • Execution Rate : {winner['rate_min_step']:.2f} min / ionic step")
        print(f"  • Placement      : {winner['target']}\n")


def generate_slurm_job_script(calc_info: Dict[str, Any], cluster: str, partition: str, cores: int) -> str:
    """
    Generates a zero-redundancy, cluster-tailored Slurm script adhering to
    ponytail VASP defaults and micro-batch checkpoint traps.
    """
    job_name = calc_info.get("name", "dft_calc")[:12]
    
    if cluster == "carbono":
        script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --partition={partition}
#SBATCH --nodes=1
#SBATCH --ntasks-per-node={cores}
#SBATCH --time=04:00:00
#SBATCH --signal=B:USR1@300
#SBATCH --output=job.%j.out
#SBATCH --error=job.%j.err

# Resubmission trap for micro-batching
resubmit() {{
    echo "Checkpoint signal caught at $(date). Preparing restart..."
    if [ -f CONTCAR ] && [ -s CONTCAR ]; then
        cp CONTCAR POSCAR
    fi
    sbatch $0
    exit 0
}}
trap 'resubmit' USR1

module purge
module load vasp/6.3.2
module load openmpi/4.1.2-intel

export OMP_NUM_THREADS=1
ulimit -s unlimited

mpirun vasp_std > run.log 2>&1
"""
    elif cluster == "huk":
        # Huk uses OpenMPI with full path to vasp_std
        script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --partition={partition}
#SBATCH --nodes=1
#SBATCH --ntasks={cores}
#SBATCH --output=job.%j.out
#SBATCH --error=job.%j.err

source /etc/profile.d/modules.sh 2>/dev/null || true
export OMP_NUM_THREADS=1
ulimit -s unlimited

# Auto-detect optimal NCORE
export NCORE={6 if cores % 6 == 0 else (4 if cores % 4 == 0 else 2)}

mpirun -np {cores} /opt/vasp/vasp.6.3.0/bin/vasp_std > run.log 2>&1
"""
    else:
        script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --partition={partition}
#SBATCH --nodes=1
#SBATCH --ntasks={cores}
#SBATCH --output=job.%j.out
#SBATCH --error=job.%j.err

export OMP_NUM_THREADS=1
mpirun -np {cores} vasp_std > run.log 2>&1
"""
    return script


def register_job_in_ledger(entry: Dict[str, Any]):
    ledger = []
    if os.path.exists(LEDGER_PATH):
        try:
            with open(LEDGER_PATH, "r") as f:
                ledger = json.load(f)
        except Exception:
            ledger = []

    # Update if existing ID, else append
    existing_idx = next((i for i, j in enumerate(ledger) if j.get("job_id") == entry["job_id"] and j.get("cluster") == entry["cluster"]), None)
    if existing_idx is not None:
        ledger[existing_idx].update(entry)
    else:
        ledger.append(entry)

    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2)


def dispatch_calculation(calc_dir: str, target_cluster: Optional[str] = None, continuation_hook: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
    calc_path = Path(calc_dir).resolve()
    if not calc_path.exists():
        raise FileNotFoundError(f"Calculation directory {calc_dir} does not exist.")

    calc_info = inspect_calculation_dir(str(calc_path))
    matrix = compute_turnaround_matrix(calc_info)
    print_decision_report(matrix)

    winner = matrix["winner"]
    if target_cluster:
        c_key = target_cluster.lower()
        if c_key not in matrix["evaluations"]:
            raise ValueError(f"Unknown cluster '{target_cluster}'. Available: {list(matrix['evaluations'].keys())}")
        chosen = matrix["evaluations"][c_key]
    else:
        chosen = winner

    if not chosen:
        raise RuntimeError("No suitable cluster available for dispatch.")

    c_conf = CLUSTERS[chosen["cluster"]]
    host = c_conf["host"]
    user = c_conf["user"]
    partition = chosen["partition"]
    cores = chosen["cores"]

    print(f"{BOLD}🚀 Initiating Dispatch to {chosen['name'].upper()}...{RESET}")
    print(f"  • Target Node / Queue: {chosen['target']}")
    print(f"  • Partition & Cores  : {partition} ({cores} cores)")

    # 1. Generate & write tailored Slurm script in local directory
    job_script_content = generate_slurm_job_script(calc_info, chosen["cluster"], partition, cores)
    local_job_script = calc_path / f"job_{chosen['cluster']}.sh"
    with open(local_job_script, "w") as f:
        f.write(job_script_content)
    os.chmod(local_job_script, 0o755)

    # Also keep standard job.sh
    shutil.copyfile(local_job_script, calc_path / "job.sh")
    os.chmod(calc_path / "job.sh", 0o755)

    # 2. Determine remote destination path
    # Map relative to workspace
    ws_base = "/home/cr/simulations/crcl3-HER"
    if str(calc_path).startswith(ws_base):
        rel_path = os.path.relpath(str(calc_path), ws_base)
    else:
        rel_path = calc_path.name

    if chosen["cluster"] == "carbono":
        remote_dir = f"~/crcl3-HER/{rel_path}"
    elif chosen["cluster"] == "huk":
        if rel_path.startswith("crcl3-newcals/"):
            remote_dir = f"/home/carlos/{rel_path}"
        else:
            remote_dir = f"/home/carlos/crcl3-newcals/{rel_path}"
    else:
        remote_dir = f"~/crcl3-HER/{rel_path}"

    print(f"  • Syncing inputs to {host}:{remote_dir}...")

    if dry_run:
        print(f"{YELLOW}[DRY RUN] Would rsync and execute sbatch on {host}. Exiting.{RESET}")
        return {"status": "DRY_RUN", "cluster": chosen["cluster"], "remote_dir": remote_dir}

    # Ensure remote directory exists
    run_ssh(host, f"mkdir -p {remote_dir}")

    # Rsync calculation directory
    rsync_cmd = [
        "rsync", "-avz", "--delete",
        "--exclude=WAVECAR", "--exclude=CHGCAR", "--exclude=CHG",
        "--exclude=*.out", "--exclude=*.err", "--exclude=run.log",
        f"{str(calc_path)}/",
        f"{host}:{remote_dir}/"
    ]
    res_rsync = subprocess.run(rsync_cmd, capture_output=True, text=True)
    if res_rsync.returncode != 0:
        raise RuntimeError(f"Rsync failed: {res_rsync.stderr}")

    # 3. Submit via sbatch
    print(f"  • Submitting Slurm job on {host}...")
    sbatch_cmd = f"cd {remote_dir} && sbatch job.sh"
    submit_out = run_ssh(host, sbatch_cmd)
    if not submit_out:
        raise RuntimeError(f"Failed to submit batch job on {host}")

    m_id = re.search(r"Submitted batch job (\d+)", submit_out)
    if not m_id:
        raise RuntimeError(f"Unexpected sbatch response: {submit_out}")

    job_id = int(m_id.group(1))
    print(f"{BOLD}{GREEN}✔ Successfully submitted Job ID {job_id} on {chosen['name']}!{RESET}")

    ledger_entry = {
        "job_id": job_id,
        "name": calc_info.get("name", "dft_calc"),
        "cluster": chosen["cluster"],
        "partition": partition,
        "cores": cores,
        "local_dir": str(calc_path),
        "remote_dir": remote_dir,
        "status": "RUNNING",
        "submitted_at": datetime.now().isoformat(),
        "expected_steps": calc_info.get("steps", 40),
        "continuation_hook": continuation_hook,
        "last_verified": datetime.now().isoformat()
    }
    register_job_in_ledger(ledger_entry)
    print(f"  • Registered in global ledger: {LEDGER_PATH}\n")

    return ledger_entry


def main():
    parser = argparse.ArgumentParser(description="Intelligent HPC Meta-Scheduler & Dispatcher")
    parser.add_argument("--decide", action="store_true", help="Run multi-cluster turnaround decision matrix")
    parser.add_argument("--dispatch", type=str, metavar="DIR", help="Directory of calculation to dispatch")
    parser.add_argument("--target", type=str, help="Force specific target cluster (carbono, huk, iskay)")
    parser.add_argument("--hook", type=str, help="Continuation hook script or action upon completion")
    parser.add_argument("--steps", type=int, default=40, help="Expected ionic steps for estimation")
    parser.add_argument("--atoms", type=int, default=33, help="Atom count for estimation")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without submitting")

    args = parser.parse_args()

    if args.dispatch:
        dispatch_calculation(args.dispatch, target_cluster=args.target, continuation_hook=args.hook, dry_run=args.dry_run)
    elif args.decide:
        calc_info = {
            "name": "Manual Query",
            "atoms": args.atoms,
            "steps": args.steps,
            "kpoints": 4,
            "supercell": "2x2" if args.atoms <= 40 else "3x3",
            "has_u": False,
            "u_val": 0.0
        }
        matrix = compute_turnaround_matrix(calc_info)
        print_decision_report(matrix)
    else:
        calc_info = {
            "name": "General Cluster Audit",
            "atoms": args.atoms,
            "steps": args.steps,
            "kpoints": 4,
            "supercell": "2x2",
            "has_u": False,
            "u_val": 0.0
        }
        matrix = compute_turnaround_matrix(calc_info)
        print_decision_report(matrix)


if __name__ == "__main__":
    main()
