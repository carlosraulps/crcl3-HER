#!/usr/bin/env python3
"""
================================================================================
Automated SLURM Submission Script Generator
================================================================================
Generates customized, performance-tuned .sbatch scripts for VASP, SIESTA,
LAMMPS, and Python/ML jobs on Iskay, Huk, and Carbono.

Usage:
    python3 slurm_generator.py --cluster huk --app vasp --job-name crcl3_opt --atoms 32 --output job.sbatch
================================================================================
"""

import sys
import os
import argparse
from job_efficiency_advisor import JobEfficiencyAdvisor


def generate_sbatch(
    cluster: str,
    app: str = "vasp",
    job_name: str = "dft_calc",
    atoms: int = 32,
    kpoints: int = 4,
    supercell: str = "custom",
    walltime_days: int = 7,
    is_hybrid: bool = False,
    custom_command: str = ""
) -> str:
    advisor = JobEfficiencyAdvisor()
    advice = advisor.advise(
        cluster=cluster,
        app=app,
        atoms=atoms,
        kpoints=kpoints,
        supercell=supercell,
        walltime_days=walltime_days,
        is_hybrid=is_hybrid
    )

    partition = advice.get("recommended_partition", "normal")
    cores = advice.get("allocated_cores", 16)
    nodes = advice.get("nodes", 1)
    mem_gb = advice.get("memory_request_gb", 32)
    ncore = advice.get("vasp_ncore", 4)
    kpar = advice.get("vasp_kpar", 1)

    c = cluster.lower()
    days_str = f"{walltime_days}-00:00:00"

    script = [
        "#!/bin/bash",
        f"#SBATCH --job-name={job_name}",
        f"#SBATCH --partition={partition}",
        f"#SBATCH --nodes={nodes}",
        f"#SBATCH --ntasks={cores}",
        f"#SBATCH --time={days_str}",
        f"#SBATCH --mem={mem_gb}G",
        f"#SBATCH --output={job_name}_%j.out",
        f"#SBATCH --error={job_name}_%j.err",
    ]

    # Cluster-specific tuning directives
    if c in ("iskay", "iskay201", "iskay202"):
        script.extend([
            "#SBATCH --cpu-bind=cores",
            "",
            "# --- Iskay Execution Environment ---",
            "export OMP_NUM_THREADS=1",
            "export MKL_NUM_THREADS=1",
            "ulimit -s unlimited",
        ])
    elif c == "huk":
        script.extend([
            "",
            "# --- Huk Execution Environment ---",
            "export OMP_NUM_THREADS=1",
            "export MKL_NUM_THREADS=1",
            "ulimit -s unlimited",
        ])
    elif c == "carbono":
        script.extend([
            "",
            "# --- Carbono UFABC Environment ---",
            "module load python",
            "module load vasp 2>/dev/null || module load intel openmpi",
            "export OMP_NUM_THREADS=1",
            "ulimit -s unlimited",
        ])

    script.append("")
    script.append("# --- Diagnostic Metadata ---")
    script.append('echo "Starting Slurm Job: $SLURM_JOB_ID on $(hostname)"')
    script.append('echo "Allocated Nodes: $SLURM_NODELIST ($SLURM_NTASKS cores)"')
    script.append('echo "Start Time: $(date)"')
    script.append("")

    # Application execution template
    if app == "vasp":
        script.extend([
            "# --- VASP Electronic/Ionic Minimization ---",
            f"# Recommended INCAR parameters for this allocation:",
            f"#   NCORE = {ncore}",
            f"#   KPAR  = {kpar}",
            "",
            'if grep -q "NCORE" INCAR 2>/dev/null; then',
            f'    sed -i "s/.*NCORE.*/ NCORE = {ncore}/" INCAR',
            "else",
            f'    echo " NCORE = {ncore}" >> INCAR',
            "fi",
            "",
            'if grep -q "KPAR" INCAR 2>/dev/null; then',
            f'    sed -i "s/.*KPAR.*/ KPAR = {kpar}/" INCAR',
            "else",
            f'    echo " KPAR = {kpar}" >> INCAR',
            "fi",
            "",
            "# Execute VASP via MPI",
            custom_command or "mpirun -np $SLURM_NTASKS vasp_std"
        ])
    elif app == "siesta":
        script.extend([
            "# --- SIESTA Electronic Structure ---",
            "export OMP_NUM_THREADS=1",
            custom_command or "mpirun -np $SLURM_NTASKS siesta < input.fdf > output.out"
        ])
    else:
        script.extend([
            "# --- Generic Command Execution ---",
            custom_command or "srun ./my_binary"
        ])

    script.append("")
    script.append('echo "Job Completed At: $(date)"')
    return "\n".join(script) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Tailored SLURM Submission Script Generator")
    parser.add_argument("--cluster", default="huk", choices=["iskay", "huk", "carbono"], help="Target HPC cluster")
    parser.add_argument("--app", default="vasp", choices=["vasp", "siesta", "generic"], help="Software package")
    parser.add_argument("--job-name", default="dft_relax", help="Slurm job name")
    parser.add_argument("--atoms", type=int, default=32, help="Number of atoms in system")
    parser.add_argument("--kpoints", type=int, default=4, help="Total k-points")
    parser.add_argument("--supercell", default="custom", choices=["1x1", "2x2", "3x3", "custom"])
    parser.add_argument("--walltime-days", type=int, default=7, help="Walltime limit in days")
    parser.add_argument("--hybrid", action="store_true", help="Using hybrid functional HSE06")
    parser.add_argument("--output", "-o", default=None, help="Save to file instead of stdout")

    args = parser.parse_args()

    sbatch_content = generate_sbatch(
        cluster=args.cluster,
        app=args.app,
        job_name=args.job_name,
        atoms=args.atoms,
        kpoints=args.kpoints,
        supercell=args.supercell,
        walltime_days=args.walltime_days,
        is_hybrid=args.hybrid
    )

    if args.output:
        with open(args.output, "w") as f:
            f.write(sbatch_content)
        print(f"✅ Generated tailored Slurm submission script: {args.output}")
    else:
        print(sbatch_content)


if __name__ == "__main__":
    main()
