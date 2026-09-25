---
name: server-info
description: >-
  Comprehensive HPC multi-cluster intelligence, live node telemetry, core
  fragmentation detection, empirical turnaround optimization, automated zero-redundancy
  Slurm batch script generation and dispatch, and safeguarded multi-tier synchronization
  daemon with Git master push and continuation triggers across Iskay, Huk, Carbono, and Arch.
  Activate whenever the user asks for server specs, cluster queues, optimal job placement,
  turnaround estimations, job dispatching, or automated synchronization between clusters.
---

# ⚡ Server-Info: HPC Multi-Cluster Intelligence & Optimization Superpower

Welcome to the upgraded **Server-Info Superpower Suite**. This package provides comprehensive architecture profiles, real-time Slurm cluster telemetry, Amdahl's Law parallel sizing, empirical turnaround optimization, automated job dispatching, and a safeguarded multi-tier synchronization monitor that prevents false positives/negatives.

---

## 🚀 Quick CLI Commands

The unified `server-info` command is available directly on PATH:

| Command | Action | Description |
| :--- | :--- | :--- |
| `server-info` | **Ecosystem Overview** | Side-by-side comparison table of all 4 clusters with live reachability probe. |
| `server-info <cluster> --live` | **Cluster Telemetry** | Hardware topology, partition limits, node states, and active queues (`huk`, `carbono`, `iskay`, `arch`). |
| `server-info --decide [--steps N] [--atoms N]` | **Turnaround Matrix** | Audits node fragmentation, wait times ($T_{\text{wait}}$), and compute rates ($t_{\text{step}}$) to pick the fastest cluster. |
| `server-info --dispatch <calc_dir>` | **Meta-Scheduler Dispatch** | Automatically selects cluster, adapts Slurm script with USR1 micro-batch traps, rsyncs inputs, submits via `sbatch`, and registers in ledger. |
| `server-info --sync-check` | **Safeguarded Sync** | Verifies convergence via multi-tier validation (`OUTCAR` strings, `CONTCAR` integrity, `OSZICAR` $E_0$), syncs outputs, runs continuation hooks, and pushes to Git `master`. |
| `server-info --sync-watch [--interval N]` | **Persistent Monitor** | Runs the synchronization daemon in continuous loop. |
| `server-info --jobs` | **Ledger Audit** | Displays table of all active and completed calculations tracked in `~/.hpc_jobs_ledger.json`. |
| `server-info --advise <cluster> --atoms N` | **Job Sizing Advisor** | Calculates optimal cores, partition, memory request, and VASP `NCORE`/`KPAR` parameters. |

---

## 🌐 Supported Cluster Architectures

* **Carbono Supercomputer (`carbono`)**:
  - Academic supercomputer at UFABC (Brazil, UTC-3).
  - 14 compute nodes (`n01`–`n14`), **2,240 AMD EPYC cores**, 7.1 TB RAM.
  - Partitions: `fulereno` (MinTRES=64c, MaxTRESPU=384c), `nanotubo` (MinTRES=17c), `grafeno` (1-16c).
  - Empirical Rate: **4.14 min / ionic step** (64 cores, $2\times2$ 33-atom cell).
  - High wait times ($T_{\text{wait}} \ge 24\text{h}$) when idle cores are fragmented below single-node 64-core blocks.

* **Huk Dedicated Cluster (`huk`)**:
  - Internal dedicated cluster on LAN (`192.168.16.100`) accessed via persistent SSH socket.
  - 10 compute nodes (`huk119`–`huk128`), **296 Intel Xeon cores**, 1.6 TB RAM.
  - Partitions: `hram` (huk119, 40c, 504 GB RAM), `alto` (huk120-121, 36c), `medio` (huk122-124, 28c), `normal` (huk125-128, 24c, up to 90 days).
  - Empirical Rates: **8.50 min / step** (`alto`, 36c), **12.62 min / step** (`medio`, 28c).
  - Dedicated nodes frequently offer **$T_{\text{wait}} = 0$**, allowing same-day completions.

* **Iskay Gateway Cluster (`iskay`)**:
  - High-density gateway cluster (`192.168.16.200`).
  - 2 nodes (`iskay201`, `iskay202`), **256 cores / 742 GB RAM each** (512 cores total).
  - Ideal for large $3\times3$ supercells and massive parameter sweeps.

* **Arch Workstation (`arch`)**:
  - Local workstation for prototyping, visualization, post-processing, and desktop notifications.

---

## 🛡️ False-Positive & False-Negative Safeguards

The synchronization daemon (`hpc_sync_monitor.py`) enforces strict multi-tier verification before marking any calculation as completed:
1. **Slurm Queue Verification**: Queries `squeue -j <id>` to ensure job is no longer running (`R`), pending (`PD`), or completing (`CG`).
2. **Physical Convergence Verification**: Searches `OUTCAR` for `"reached required accuracy - stopping structural energy minimisation"` (for relaxations) or `"General timing and accounting"` (for static runs).
3. **Geometry Integrity Audit**: Verifies `CONTCAR` exists, has size $> 100$ bytes, line count $\ge 8$, and valid floating-point direct coordinates. A 0-byte or truncated `CONTCAR` is immediately flagged as `INCOMPLETE` / `CRASHED`.
4. **Energy Extraction**: Extracts final ground-state electronic energy $E_0$ and total magnetic moment from `OSZICAR`.
5. **Non-Blocking Git Synchronization**: Runs `git push` with `GIT_TERMINAL_PROMPT=0` and timeout guards to ensure unattended background execution never blocks on interactive authentication.

---

## 🔌 Model Context Protocol (MCP) Integration

The skill includes a dedicated JSON-RPC 2.0 MCP server executable at `/home/cr/.local/bin/server-info-mcp` and registered in `~/.gemini/config/mcp_config.json`:

Exposed AI Tools:
* `list_clusters()`: Master database of cluster profiles.
* `get_cluster_info(cluster_name)`: Detailed hardware, partitions, and environment.
* `get_live_telemetry(cluster_name)`: Live nodes and running jobs probe.
* `calculate_optimal_job(cluster, app, atoms, kpoints)`: Amdahl's Law sizing advisor.
* `decide_cluster(atoms, steps, calc_dir)`: Multi-factor turnaround comparison matrix.
* `dispatch_calculation(calc_dir, target_cluster, hook, dry_run)`: End-to-end automated dispatch.
* `sync_and_monitor(sync_on_completion)`: Live audit, convergence verification, and auto-sync.
* `list_tracked_jobs()`: Complete persistent ledger of calculations.
