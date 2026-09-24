#!/usr/bin/env python3
"""
================================================================================
DEPLOY AND SUBMIT CRCL3 H-ADSORPTION (IVDW=12) JOBS TO HUK CLUSTER
================================================================================
Tailors job.sh for Huk cluster architecture (Intel oneAPI, native VASP 6.5.1,
multi-partition dispatch alto,medio,normal,hram), syncs to Huk, and submits
all 13 calculations via sbatch.
================================================================================
"""

import os
import sys
import subprocess

REMOTE_HOST = "huk"
REMOTE_BASE = "/home/juan/Carlos"
LOCAL_BASE = "/home/juan/Carlos"

CALCULATIONS = [
    # 1. H2 gas phase reference
    {
        "rel_dir": "H2_reference/yes_vdw_ivdw12",
        "job_name": "H2_ref_vdw12",
        "ntasks": 8,
        "mem": "8G",
        "partition": "alto,medio,normal",
        "time": "1-00:00:00"
    },
    # 2. 1x1 Supercell suite (9 atoms)
    {
        "rel_dir": "crcl3-1x1-h_ads-without-U/yes_vdw_ivdw12/clean",
        "job_name": "H1x1_cl_vdw12",
        "ntasks": 16,
        "mem": "16G",
        "partition": "alto,medio,normal",
        "time": "7-00:00:00"
    },
    {
        "rel_dir": "crcl3-1x1-h_ads-without-U/yes_vdw_ivdw12/S1",
        "job_name": "H1x1_S1_vdw12",
        "ntasks": 16,
        "mem": "16G",
        "partition": "alto,medio,normal",
        "time": "7-00:00:00"
    },
    {
        "rel_dir": "crcl3-1x1-h_ads-without-U/yes_vdw_ivdw12/S2",
        "job_name": "H1x1_S2_vdw12",
        "ntasks": 16,
        "mem": "16G",
        "partition": "alto,medio,normal",
        "time": "7-00:00:00"
    },
    {
        "rel_dir": "crcl3-1x1-h_ads-without-U/yes_vdw_ivdw12/S3",
        "job_name": "H1x1_S3_vdw12",
        "ntasks": 16,
        "mem": "16G",
        "partition": "alto,medio,normal",
        "time": "7-00:00:00"
    },
    # 3. 2x2 Supercell suite (33 atoms)
    {
        "rel_dir": "crcl3-2x2-h_ads-without-U/yes_vdw_ivdw12/clean",
        "job_name": "H2x2_cl_vdw12",
        "ntasks": 24,
        "mem": "64G",
        "partition": "alto,medio,normal",
        "time": "7-00:00:00"
    },
    {
        "rel_dir": "crcl3-2x2-h_ads-without-U/yes_vdw_ivdw12/S1",
        "job_name": "H2x2_S1_vdw12",
        "ntasks": 24,
        "mem": "64G",
        "partition": "alto,medio,normal",
        "time": "7-00:00:00"
    },
    {
        "rel_dir": "crcl3-2x2-h_ads-without-U/yes_vdw_ivdw12/S2",
        "job_name": "H2x2_S2_vdw12",
        "ntasks": 24,
        "mem": "64G",
        "partition": "alto,medio,normal",
        "time": "7-00:00:00"
    },
    {
        "rel_dir": "crcl3-2x2-h_ads-without-U/yes_vdw_ivdw12/S3",
        "job_name": "H2x2_S3_vdw12",
        "ntasks": 24,
        "mem": "64G",
        "partition": "alto,medio,normal",
        "time": "7-00:00:00"
    },
    # 4. 3x3 Supercell suite (73 atoms - large memory)
    {
        "rel_dir": "crcl3-3x3-h_ads-without-U/yes_vdw_ivdw12/clean",
        "job_name": "H3x3_cl_vdw12",
        "ntasks": 24,
        "mem": "100G",
        "partition": "hram,medio,normal",
        "time": "7-00:00:00"
    },
    {
        "rel_dir": "crcl3-3x3-h_ads-without-U/yes_vdw_ivdw12/S1",
        "job_name": "H3x3_S1_vdw12",
        "ntasks": 24,
        "mem": "100G",
        "partition": "hram,medio,normal",
        "time": "7-00:00:00"
    },
    {
        "rel_dir": "crcl3-3x3-h_ads-without-U/yes_vdw_ivdw12/S2",
        "job_name": "H3x3_S2_vdw12",
        "ntasks": 24,
        "mem": "100G",
        "partition": "hram,medio,normal",
        "time": "7-00:00:00"
    },
    {
        "rel_dir": "crcl3-3x3-h_ads-without-U/yes_vdw_ivdw12/S3",
        "job_name": "H3x3_S3_vdw12",
        "ntasks": 24,
        "mem": "100G",
        "partition": "hram,medio,normal",
        "time": "7-00:00:00"
    },
]

JOB_TEMPLATE = """#!/bin/bash
#SBATCH -J {job_name}
#SBATCH -p {partition}
#SBATCH --nodes=1
#SBATCH --ntasks={ntasks}
#SBATCH --cpus-per-task=1
#SBATCH --mem={mem}
#SBATCH --time={time}
#SBATCH --requeue
#SBATCH -o %x.%j.out
#SBATCH -e %x.%j.err

echo "=========================================================="
echo "Job Name:    $SLURM_JOB_NAME"
echo "Job ID:      $SLURM_JOB_ID"
echo "Host:        $(hostname)"
echo "Directory:   $(pwd)"
echo "Start Time:  $(date)"
echo "CPUs Alloc:  $SLURM_NTASKS"
echo "=========================================================="

# 1. Fault Tolerance: Intercept shutdown/preemption signals for graceful VASP exit
trap 'echo "LABORT = .TRUE." > STOPCAR; echo "[$(date)] Intercepted termination signal! Flushed STOPCAR for clean exit."; wait' SIGTERM SIGINT SIGHUP

# 2. Resumption Logic: Check if valid CONTCAR exists from previous step/interruption
if [ -f CONTCAR ] && [ -s CONTCAR ]; then
    NLINES=$(wc -l < CONTCAR)
    if [ "$NLINES" -ge 8 ]; then
        echo "[$(date)] Found existing valid CONTCAR ($NLINES lines). Resuming relaxation..."
        cp POSCAR POSCAR.bak_$(date +%s)
        cp CONTCAR POSCAR
    fi
fi

# 3. Environment Preparation for HUK Cluster
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
ulimit -s unlimited

# 4. In-Situ VASP Execution using native HUK oneAPI MPI & VASP 6.5.1
echo "Executing VASP 6.5.1 with $SLURM_NTASKS MPI ranks..."
mpirun -np $SLURM_NTASKS /opt/vasp/vasp/bin/vasp_std > vasp.out 2>&1
EXIT_CODE=$?

# Remove STOPCAR if present after clean termination
rm -f STOPCAR

echo "=========================================================="
echo "Finished at $(date) with exit code $EXIT_CODE"
echo "=========================================================="
exit $EXIT_CODE
"""

def main():
    print("=" * 80)
    print(" 🚀 PREPARING & DEPLOYING CRCL3 H-ADSORPTION (IVDW=12) TO HUK CLUSTER")
    print("=" * 80)

    # Step 1: Update local job.sh for Huk
    print("\n[Step 1/3] Generating Huk-optimized job.sh scripts...")
    for calc in CALCULATIONS:
        full_dir = os.path.join(LOCAL_BASE, calc["rel_dir"])
        if not os.path.exists(full_dir):
            print(f"❌ Error: {full_dir} does not exist!")
            sys.exit(1)
        job_script = JOB_TEMPLATE.format(**calc)
        job_path = os.path.join(full_dir, "job.sh")
        with open(job_path, "w") as f:
            f.write(job_script)
        os.chmod(job_path, 0o755)
        print(f"  ✓ Updated {calc['rel_dir']}/job.sh (p={calc['partition']}, ntasks={calc['ntasks']}, mem={calc['mem']})")

    # Step 2: Rsync directories to Huk
    print("\n[Step 2/3] Syncing calculation suites to Huk cluster via rsync...")
    sync_dirs = [
        "H2_reference",
        "crcl3-1x1-h_ads-without-U",
        "crcl3-2x2-h_ads-without-U",
        "crcl3-3x3-h_ads-without-U"
    ]
    for d in sync_dirs:
        local_src = os.path.join(LOCAL_BASE, d)
        remote_dest = f"{REMOTE_HOST}:{REMOTE_BASE}/"
        cmd = ["rsync", "-avz", "--exclude=*.err", "--exclude=*.out", "--exclude=WAVECAR*", "--exclude=CHGCAR*", local_src, remote_dest]
        print(f"  Syncing {d}...")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"❌ Rsync failed for {d}: {res.stderr}")
            sys.exit(1)
    print("  ✓ All suites successfully synchronized to Huk!")

    # Step 3: Submit all jobs via SSH sbatch
    print("\n[Step 3/3] Submitting jobs to Slurm queue on Huk...")
    submitted_jobs = []
    for calc in CALCULATIONS:
        rem_dir = f"{REMOTE_BASE}/{calc['rel_dir']}"
        sbatch_cmd = f"ssh -o BatchMode=yes -o ConnectTimeout=5 {REMOTE_HOST} 'cd {rem_dir} && sbatch job.sh'"
        res = subprocess.run(sbatch_cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0 and "Submitted batch job" in res.stdout:
            job_id = res.stdout.strip().split()[-1]
            submitted_jobs.append((job_id, calc["job_name"], calc["rel_dir"], calc["partition"]))
            print(f"  ✓ [{job_id}] Submitted {calc['job_name']:16s} ({calc['rel_dir']})")
        else:
            print(f"  ❌ Failed to submit {calc['job_name']}: {res.stderr} | {res.stdout}")

    print("\n" + "=" * 80)
    print(" 🎉 SUBMISSION SUMMARY MATRIX ON HUK CLUSTER")
    print("=" * 80)
    print(f"{'Job ID':<10} {'Job Name':<18} {'Partition':<22} {'Relative Directory'}")
    print("-" * 80)
    for jid, jname, rdir, part in submitted_jobs:
        print(f"{jid:<10} {jname:<18} {part:<22} {rdir}")
    print("=" * 80)
    print(f"Total jobs submitted to Huk: {len(submitted_jobs)} / {len(CALCULATIONS)}")

if __name__ == "__main__":
    main()
