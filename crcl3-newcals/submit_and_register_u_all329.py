#!/usr/bin/env python3
"""
Submit and register multi-site Hubbard U (U=3.29 eV on Cr, Co, Fe, Ni) calculations.
Enforces multi-cluster distribution:
- 4 jobs on Huk (medio,normal, 28 cores)
- 8 jobs on Carbono (nanotubo, 32 cores)
Records all Job IDs into ~/.hpc_jobs_ledger.json.
"""

import subprocess
import json
import datetime
import os
import re

LEDGER_PATH = os.path.expanduser("~/.hpc_jobs_ledger.json")

huk_jobs = [
    ("adsorbed/Fe/clean", "Fe_ads_c_Uall", 28, "medio,normal"),
    ("adsorbed/Fe/H_ads", "Fe_ads_H_Uall", 28, "medio,normal"),
    ("adsorbed/Ni/clean", "Ni_ads_c_Uall", 28, "medio,normal"),
    ("adsorbed/Ni/H_ads", "Ni_ads_H_Uall", 28, "medio,normal"),
]

carbono_jobs = [
    ("embedded/Co/clean", "Co_emb_c_Uall", 32, "nanotubo"),
    ("embedded/Co/H_ads", "Co_emb_H_Uall", 32, "nanotubo"),
    ("embedded/Fe/clean", "Fe_emb_c_Uall", 32, "nanotubo"),
    ("embedded/Fe/H_ads", "Fe_emb_H_Uall", 32, "nanotubo"),
    ("embedded/Ni/clean", "Ni_emb_c_Uall", 32, "nanotubo"),
    ("embedded/Ni/H_ads", "Ni_emb_H_Uall", 32, "nanotubo"),
    ("adsorbed/Co/clean", "Co_ads_c_Uall", 32, "nanotubo"),
    ("adsorbed/Co/H_ads", "Co_ads_H_Uall", 32, "nanotubo"),
]

def load_ledger():
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH, 'r') as f:
            return json.load(f)
    return []

def save_ledger(ledger):
    with open(LEDGER_PATH, 'w') as f:
        json.dump(ledger, f, indent=2)

def submit_huk(rel_dir, job_name, cores, partition):
    remote_dir = f"/home/carlos/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/{rel_dir}"
    local_dir = f"/home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/{rel_dir}"
    cmd = f'ssh huk "cd {remote_dir} && sbatch job_huk.sh"'
    print(f"[HUK] Submitting {rel_dir}...")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"ERROR on Huk for {rel_dir}: {res.stderr}")
        return None
    match = re.search(r"Submitted batch job (\d+)", res.stdout)
    if not match:
        print(f"Could not parse job id from: {res.stdout}")
        return None
    job_id = int(match.group(1))
    print(f"[HUK] SUCCESS: Job {job_id} ({job_name}) submitted.")
    return {
        "job_id": job_id,
        "name": job_name,
        "cluster": "huk",
        "partition": partition,
        "cores": cores,
        "local_dir": local_dir,
        "remote_dir": remote_dir,
        "status": "SUBMITTED",
        "submitted_at": datetime.datetime.now().isoformat(),
        "expected_steps": 100,
        "continuation_hook": "u_all329_her_analysis"
    }

def submit_carbono(rel_dir, job_name, cores, partition):
    remote_dir = f"/home/carlos.primo/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/{rel_dir}"
    local_dir = f"/home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/{rel_dir}"
    cmd = f'ssh carbono "cd {remote_dir} && sbatch -p {partition} --ntasks={cores} job_carbono.sh"'
    print(f"[CARBONO] Submitting {rel_dir}...")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"ERROR on Carbono for {rel_dir}: {res.stderr}")
        return None
    match = re.search(r"Submitted batch job (\d+)", res.stdout)
    if not match:
        print(f"Could not parse job id from: {res.stdout}")
        return None
    job_id = int(match.group(1))
    print(f"[CARBONO] SUCCESS: Job {job_id} ({job_name}) submitted.")
    return {
        "job_id": job_id,
        "name": job_name,
        "cluster": "carbono",
        "partition": partition,
        "cores": cores,
        "local_dir": local_dir,
        "remote_dir": remote_dir,
        "status": "SUBMITTED",
        "submitted_at": datetime.datetime.now().isoformat(),
        "expected_steps": 100,
        "continuation_hook": "u_all329_her_analysis"
    }

def main():
    ledger = load_ledger()
    new_entries = []

    print("=== Submitting Huk Jobs ===")
    for rel_dir, name, cores, part in huk_jobs:
        entry = submit_huk(rel_dir, name, cores, part)
        if entry:
            new_entries.append(entry)
            ledger.append(entry)

    print("\n=== Submitting Carbono Jobs ===")
    for rel_dir, name, cores, part in carbono_jobs:
        entry = submit_carbono(rel_dir, name, cores, part)
        if entry:
            new_entries.append(entry)
            ledger.append(entry)

    save_ledger(ledger)
    print(f"\nAll {len(new_entries)} jobs submitted and recorded in {LEDGER_PATH}!")

if __name__ == '__main__':
    main()
