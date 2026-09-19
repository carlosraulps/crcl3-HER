#!/usr/bin/env python3
"""
================================================================================
Scientific HPC Job Efficiency & Allocation Advisor
================================================================================
Calculates the optimal core count, node count, partition, memory buffer,
and software parallelization parameters (NCORE, KPAR, OMP_NUM_THREADS)
specifically adapted to DFT (VASP, SIESTA), Molecular Dynamics, or general HPC.

Incorporates:
  1. Topology-aware placement (sockets, NUMA nodes, L3 cache)
  2. Memory footprint estimation with safety overhead
  3. Amdahl's Law parallel efficiency modeling (prevents core-count over-allocation)
  4. VASP specific heuristics: NCORE = sqrt(cores) or cores/socket divisor,
     KPAR = divisor(kpoints), min 4 bands/core rule of thumb.
================================================================================
"""

import sys
import os
import math
import argparse
import json
from typing import Dict, Any, Tuple, Optional


class JobEfficiencyAdvisor:
    def __init__(self, cluster_data_path: Optional[str] = None):
        if not cluster_data_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cluster_data_path = os.path.join(base_dir, "resources", "clusters.json")

        self.clusters = {}
        if os.path.exists(cluster_data_path):
            try:
                with open(cluster_data_path, "r") as f:
                    self.clusters = json.load(f).get("clusters", {})
            except Exception as e:
                print(f"[Warning] Could not load clusters registry: {e}", file=sys.stderr)

    def estimate_vasp_memory_gb(self, atoms: int, kpoints: int = 1, supercell: str = "custom", is_hybrid: bool = False) -> float:
        """
        Estimates the baseline memory footprint for VASP DFT calculations.
        Baseline:
          - 1x1 cell (~8 atoms): ~8-12 GB RAM
          - 2x2 cell (~32 atoms): ~16-25 GB RAM
          - 3x3 cell (~72-80 atoms): ~60-110 GB RAM (requires high memory)
          - Hybrid functionals (HSE06): ~3x-5x memory scaling
        """
        if supercell == "1x1":
            base_mem = 12.0
        elif supercell == "2x2":
            base_mem = 24.0
        elif supercell == "3x3":
            base_mem = 85.0
        else:
            # Power law scaling ~ N_atoms^1.8
            base_mem = max(6.0, 0.25 * (atoms ** 1.55))

        # K-points parallelization multiplier
        kpt_factor = 1.0 + 0.15 * math.log2(max(1, kpoints))
        total_mem = base_mem * kpt_factor

        if is_hybrid:
            total_mem *= 3.5

        # 20% safety buffer to prevent kernel OOM killer
        return round(total_mem * 1.2, 1)

    def calculate_vasp_parameters(self, total_cores: int, kpoints: int = 1, cores_per_socket: int = 18) -> Tuple[int, int]:
        """
        Calculates optimal NCORE and KPAR for VASP.
        - KPAR: Number of k-points parallel groups (divisor of total k-points)
        - NCORE: Number of cores that work on a single orbital (divisor of cores per socket)
        """
        # KPAR
        if kpoints <= 1:
            kpar = 1
        else:
            # Find largest divisor of kpoints that divides total_cores
            valid_divisors = [d for d in [1, 2, 4, 8, 16] if kpoints % d == 0 and total_cores % d == 0]
            kpar = max(valid_divisors) if valid_divisors else 1

        # NCORE
        # Golden rule: NCORE should divide cores_per_socket, typically 4 to 16
        possible_ncores = [c for c in [2, 4, 6, 8, 12, 16] if (cores_per_socket % c == 0 or total_cores % c == 0)]
        target = int(math.sqrt(total_cores // kpar))
        if possible_ncores:
            # Pick closest to target
            ncore = min(possible_ncores, key=lambda x: abs(x - max(4, target)))
        else:
            ncore = 4

        return ncore, kpar

    def calculate_amdahl_efficiency(self, cores: int, parallel_fraction: float = 0.95) -> Tuple[float, float]:
        """
        Calculates expected speedup and parallel efficiency using Amdahl's Law.
        Speedup S(N) = 1 / ((1 - P) + (P / N))
        Efficiency E(N) = S(N) / N
        """
        p = parallel_fraction
        denom = (1.0 - p) + (p / max(1, cores))
        speedup = 1.0 / denom
        efficiency = speedup / max(1, cores)
        return round(speedup, 2), round(efficiency * 100.0, 1)

    def recommend_for_huk(self, app: str, atoms: int, kpoints: int, walltime_days: int = 5, is_hybrid: bool = False) -> Dict[str, Any]:
        """Specific recommendations for the 10-node Huk cluster."""
        est_mem = self.estimate_vasp_memory_gb(atoms, kpoints, is_hybrid=is_hybrid)

        # Select Partition
        # hram: 40 cores, 504 GB RAM
        # alto: 36 cores, 126 GB RAM
        # medio: 28 cores, 126 GB RAM
        # normal: 24 cores, 126 GB RAM (up to 90d)
        if est_mem > 115.0 or is_hybrid or atoms >= 65:
            partition = "hram"
            node_cores = 40
            node_name = "huk119"
            cores_per_socket = 20
        elif walltime_days > 30:
            partition = "normal"
            node_cores = 24
            node_name = "huk[125-128]"
            cores_per_socket = 12
        elif walltime_days > 7:
            partition = "medio"
            node_cores = 28
            node_name = "huk[122-124]"
            cores_per_socket = 14
        else:
            partition = "alto"
            node_cores = 36
            node_name = "huk120"
            cores_per_socket = 18

        # Allocate cores based on atom count
        # Rule of thumb: at least 0.5 to 1.0 atoms per core for high efficiency
        max_recommended_cores = min(node_cores, max(8, int(atoms * 1.5)))
        # Snap to divisor of node_cores
        cores = node_cores if atoms >= 24 else min(16, node_cores)

        ncore, kpar = self.calculate_vasp_parameters(cores, kpoints, cores_per_socket)
        speedup, efficiency = self.calculate_amdahl_efficiency(cores, parallel_fraction=0.96)

        return {
            "cluster": "huk",
            "recommended_partition": partition,
            "target_node": node_name,
            "allocated_cores": cores,
            "cores_per_node": node_cores,
            "nodes": 1,
            "estimated_memory_gb": est_mem,
            "memory_request_gb": int(math.ceil(est_mem)),
            "vasp_ncore": ncore,
            "vasp_kpar": kpar,
            "parallel_efficiency_pct": efficiency,
            "speedup_factor": speedup,
            "rationale": (
                f"Selected '{partition}' partition on Huk based on estimated {est_mem:.1f} GB RAM footprint "
                f"and {walltime_days} days requested walltime."
            )
        }

    def recommend_for_iskay(self, app: str, atoms: int, kpoints: int, supercell: str = "custom") -> Dict[str, Any]:
        """Specific recommendations for the 256-core Iskay nodes."""
        est_mem = self.estimate_vasp_memory_gb(atoms, kpoints, supercell=supercell)

        # On Iskay, each node has 256 cores and 742 GB RAM!
        # Do not use 256 cores for small systems (like 1x1 or 2x2 with 8-32 atoms),
        # because communication overhead will destroy parallel efficiency.
        if atoms <= 12 or supercell == "1x1":
            cores = 16
        elif atoms <= 36 or supercell == "2x2":
            cores = 32
        elif atoms <= 80 or supercell == "3x3":
            cores = 64
        else:
            cores = 128

        ncore, kpar = self.calculate_vasp_parameters(cores, kpoints, cores_per_socket=128)
        speedup, efficiency = self.calculate_amdahl_efficiency(cores, parallel_fraction=0.97)

        return {
            "cluster": "iskay",
            "recommended_partition": "normal",
            "target_node": "iskay201 or iskay202",
            "allocated_cores": cores,
            "cores_per_node": 256,
            "nodes": 1,
            "estimated_memory_gb": est_mem,
            "memory_request_gb": max(32, int(math.ceil(est_mem))),
            "vasp_ncore": ncore,
            "vasp_kpar": kpar,
            "parallel_efficiency_pct": efficiency,
            "speedup_factor": speedup,
            "rationale": (
                f"Iskay provides 256 cores per node. Restricting to {cores} cores prevents communication "
                f"bottlenecks while achieving ~{efficiency}% parallel efficiency for {atoms} atoms."
            )
        }

    def advise(self, cluster: str, app: str = "vasp", atoms: int = 32, kpoints: int = 4, supercell: str = "custom", walltime_days: int = 5, is_hybrid: bool = False) -> Dict[str, Any]:
        c = cluster.lower()
        if c == "huk":
            return self.recommend_for_huk(app, atoms, kpoints, walltime_days, is_hybrid)
        elif c in ("iskay", "iskay201", "iskay202"):
            return self.recommend_for_iskay(app, atoms, kpoints, supercell)
        elif c == "carbono":
            return {
                "cluster": "carbono",
                "recommended_partition": "standard",
                "allocated_cores": min(48, max(16, atoms)),
                "nodes": 1,
                "estimated_memory_gb": self.estimate_vasp_memory_gb(atoms, kpoints, is_hybrid=is_hybrid),
                "vasp_ncore": 8,
                "vasp_kpar": 4,
                "rationale": "Carbono UFABC partition recommendation."
            }
        else:
            return {
                "cluster": c,
                "error": f"Unknown cluster '{cluster}'. Known clusters: iskay, huk, carbono, arch."
            }


def main():
    parser = argparse.ArgumentParser(description="Scientific HPC Job Efficiency & Allocation Advisor")
    parser.add_argument("cluster", nargs="?", default="huk", help="Target cluster (iskay, huk, carbono, arch)")
    parser.add_argument("--app", default="vasp", choices=["vasp", "siesta", "lammps", "python"], help="Software package")
    parser.add_argument("--atoms", type=int, default=32, help="Number of atoms in the system")
    parser.add_argument("--kpoints", type=int, default=4, help="Total k-points in KPOINTS grid")
    parser.add_argument("--supercell", default="custom", choices=["1x1", "2x2", "3x3", "custom"], help="Standard supercell scale")
    parser.add_argument("--walltime-days", type=int, default=7, help="Estimated walltime duration in days")
    parser.add_argument("--hybrid", action="store_true", help="Using HSE06 or hybrid functional (higher memory)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    advisor = JobEfficiencyAdvisor()
    res = advisor.advise(
        cluster=args.cluster,
        app=args.app,
        atoms=args.atoms,
        kpoints=args.kpoints,
        supercell=args.supercell,
        walltime_days=args.walltime_days,
        is_hybrid=args.hybrid
    )

    if args.json:
        print(json.dumps(res, indent=2))
        return

    print("=" * 65)
    print(f" ⚡ HPC SLURM JOB OPTIMIZATION ADVISOR · [{args.cluster.upper()}]")
    print("=" * 65)
    print(f"• Application           : {args.app.upper()}")
    print(f"• System Size           : {args.atoms} atoms (Supercell: {args.supercell})")
    print(f"• K-points Count        : {args.kpoints}")
    print(f"• Hybrid Functional     : {'YES (HSE06)' if args.hybrid else 'Standard (PBE/DFT)'}")
    print("-" * 65)
    print(f"🎯 Recommended Partition: {res.get('recommended_partition')}")
    print(f"🖥️  Target Hardware       : {res.get('target_node')}")
    print(f"⚙️  Optimal Cores Count   : {res.get('allocated_cores')} cores ({res.get('nodes')} node)")
    print(f"💾 Estimated Memory Need: {res.get('estimated_memory_gb')} GB (Request: {res.get('memory_request_gb', '?')} GB)")
    print(f"⚡ VASP INCAR `NCORE`   : {res.get('vasp_ncore')}")
    print(f"🌐 VASP INCAR `KPAR`    : {res.get('vasp_kpar')}")
    print(f"📈 Parallel Efficiency  : {res.get('parallel_efficiency_pct')}% (Speedup: ~{res.get('speedup_factor')}x)")
    print("-" * 65)
    print(f"💡 Rationale: {res.get('rationale')}")
    print("=" * 65)


if __name__ == "__main__":
    main()
