---
name: server-info
description: >-
  Comprehensive HPC cluster intelligence, hardware topology, live telemetry,
  and scientific job optimization advisor for Iskay, Huk, Carbono, Arch, and future
  clusters. Activate this skill whenever the user asks for server specs, cluster info
  (e.g., '/server-info <cluster>'), optimal node/core/memory allocations, Slurm batch script
  generation, or efficient job placement for physics, DFT (VASP, SIESTA), ML, or general compute.
---

# ⚡ Server-Info: HPC Multi-Cluster Intelligence & Optimization Skill

Welcome to the **Server-Info Skill**. This tool suite provides deep architecture profiles, live Slurm cluster telemetry, and scientific job efficiency algorithms for high-performance computing clusters accessible in this environment.

---

## 🚀 Quick Commands & Capabilities

| Goal | Command / Action | Description |
| :--- | :--- | :--- |
| **Inspect Cluster** | `python3 scripts/server_info.py <cluster> --live` | Returns hardware topology, partition limits, and live Slurm status. |
| **Cluster Overview** | `python3 scripts/server_info.py all --live` | Displays side-by-side comparison across all 4 clusters. |
| **Job Sizing Advisor** | `python3 scripts/job_efficiency_advisor.py <cluster> --app vasp --atoms <N>` | Calculates optimal cores, memory, partition, `NCORE`, and `KPAR`. |
| **Generate Batch Script** | `python3 scripts/slurm_generator.py --cluster <cluster> --app vasp --atoms <N> -o job.sbatch` | Generates ready-to-run `.sbatch` script tailored to target hardware. |

---

## 🌐 Supported Cluster Profiles

* [**Iskay (`iskay`)**](./resources/profiles/iskay.json): 2 high-density compute nodes (`iskay201`, `iskay202`), **256 cores / 742 GB RAM each** (512 cores total), direct subprocess driver, full internet access.
* [**Huk (`huk`)**](./resources/profiles/huk.json): 10 dedicated nodes (`huk119`–`huk128`), **296 cores / 1,642 GB RAM total**. Internal isolated cluster on LAN (`192.168.16.100`), access via persistent ControlMaster SSH socket. Features specialized partitions (`hram`, `alto`, `medio`, `normal`).
* [**Carbono (`carbono`)**](./resources/profiles/carbono.json): UFABC academic supercomputer in Brazil (UTC-3). Lmod module environment (`module load vasp`, etc.).
* [**Arch Workstation (`arch`)**](./resources/profiles/arch.json): Local development and post-processing machine with desktop notifications, Qtile integration, and visualization tools.

Detailed comparison table: [Cluster Cheat Sheet](./references/cluster_cheat_sheet.md)

---

## 🔬 Scientific Job Optimization Protocol

When a user asks how to configure or submit a calculation (VASP, SIESTA, LAMMPS, or general MPI):

### Step 1: Query Target Hardware & Queue State
Run the live inspector to determine current node availability:
```bash
python3 scripts/server_info.py <cluster> --live
```

### Step 2: Calculate Optimal Job Parameters
Run the efficiency advisor with system size (atom count, k-points, supercell):
```bash
# Example: 32-atom VASP calculation on Huk:
python3 scripts/job_efficiency_advisor.py huk --app vasp --atoms 32 --kpoints 8
```
The advisor evaluates:
1. **Memory Ceiling & OOM Buffer**: Estimates peak electronic memory + 20% safety margin.
2. **Partition Selection**:
   - Systems $>115\text{ GB}$ or hybrid functionals (HSE06) $\rightarrow$ **`hram` (huk119, 504 GB)**.
   - Fast turnaround relaxations $\rightarrow$ **`alto` (36 cores, 7d limit)**.
   - Long ionic runs $\rightarrow$ **`medio` (30d)** or **`normal` (90d)**.
3. **Core Sizing & Amdahl's Law**: Prevents allocating 64+ cores when communication latency causes speedup to plateau below 50% efficiency.
4. **VASP `INCAR` Tags**:
   - `KPAR`: Divisor of total k-points.
   - `NCORE`: $4$, $6$, or $8$ (matching socket core divisors, never $1$).

### Step 3: Generate the Submission Script
Generate the customized `.sbatch` script directly:
```bash
python3 scripts/slurm_generator.py --cluster huk --app vasp --job-name crcl3_2x2 --atoms 32 -o job.sbatch
```

### Step 4: Validate Pre-Submission
Review against the [Pre-Submission Checklist](./references/submission_protocol.md) before executing `sbatch`.

---

## 📚 Technical References

* [**VASP HPC Tuning Guide**](./references/vasp_hpc_optimization.md): In-depth parallelization mechanics (`NCORE`, `KPAR`, plane-waves, memory scaling per atom).
* [**Slurm Scheduling Efficiency Guide**](./references/slurm_efficiency_guide.md): CPU core pinning (`--cpu-bind=cores`), NUMA socket penalties, hyperthreading vs physical cores, Amdahl's Law derivations.
* [**Submission Protocol Runbook**](./references/submission_protocol.md): Pre-flight check, dry-run testing procedures, and post-submission monitoring.
* [**Cluster Database Registry**](./resources/clusters.json): JSON schema and registry database for all clusters.

---

## 🔌 Model Context Protocol (MCP) Server Integration

This skill includes a built-in JSON-RPC 2.0 MCP server for direct AI tool calling:
```bash
# Run standalone stdio MCP server:
python3 scripts/mcp_server.py
```
Exposes tools:
* `list_clusters()`
* `get_cluster_info(cluster_name)`
* `get_live_telemetry(cluster_name)`
* `calculate_optimal_job(cluster, app, atoms, kpoints, ...)`
* `generate_slurm_script(cluster, app, job_name, ...)`
