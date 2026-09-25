#!/usr/bin/env python3
"""
================================================================================
Server Info & HPC Superpower Unified CLI
================================================================================
Comprehensive cluster intelligence, hardware specs, live telemetry,
Amdahl's law sizing, turnaround optimization matrix, auto-dispatch,
and multi-cluster synchronization monitor.

Usage:
  server-info [cluster] [--live]             # Single cluster info & telemetry
  server-info all [--live]                   # Ecosystem comparison table
  server-info --decide [--dir D] [--steps N] # Turnaround decision matrix
  server-info --dispatch <calc_dir>          # Automatic selection, adapt & submit
  server-info --sync-check                   # Verify convergence & sync outputs
  server-info --sync-watch [--interval N]    # Persistent monitor daemon
  server-info --jobs                         # List tracked jobs in ledger
  server-info --advise <cluster> --atoms N   # Job efficiency & VASP NCORE/KPAR
================================================================================
"""

import sys
import os
import json
import argparse
import subprocess
from typing import Dict, Any, Optional

# Add scripts directory to sys.path
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from job_efficiency_advisor import JobEfficiencyAdvisor
from slurm_generator import generate_sbatch
import hpc_meta_dispatcher as dispatcher
import hpc_sync_monitor as monitor

# ANSI Colors
CYAN = "\033[1;36m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
MAGENTA = "\033[1;35m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


class ServerInfoCLI:
    def __init__(self):
        base_dir = os.path.dirname(SCRIPT_DIR)
        self.clusters_file = os.path.join(base_dir, "resources", "clusters.json")
        self.profiles_dir = os.path.join(base_dir, "resources", "profiles")
        self.clusters = self.load_clusters()

    def load_clusters(self) -> Dict[str, Any]:
        if os.path.exists(self.clusters_file):
            try:
                with open(self.clusters_file, "r") as f:
                    return json.load(f).get("clusters", {})
            except Exception:
                pass
        return {}

    def get_live_status(self, cluster_name: str) -> Dict[str, Any]:
        c = cluster_name.lower()
        res = {"reachable": False, "nodes": 0, "queue": 0, "node_summary": "N/A"}

        if c == "iskay":
            raw = dispatcher.run_ssh("iskay", "sinfo -h -o '%N %T %c %m'")
            if raw:
                lines = raw.strip().splitlines()
                res["reachable"] = True
                res["nodes"] = len(lines)
                sq = dispatcher.run_ssh("iskay", "squeue -h -t R | wc -l")
                res["queue"] = int(sq.strip()) if sq and sq.strip().isdigit() else 0
                res["node_summary"] = ", ".join([f"{l.split()[0]} ({l.split()[1]})" for l in lines[:4]])
        elif c == "huk":
            raw = dispatcher.run_ssh("huk", "sinfo -h -o '%N %T %c %m'")
            if raw:
                lines = [l for l in raw.strip().splitlines() if len(l.split()) >= 4]
                res["reachable"] = True
                res["nodes"] = len(lines)
                sq = dispatcher.run_ssh("huk", "squeue -h -t R | wc -l")
                res["queue"] = int(sq.strip()) if sq and sq.strip().isdigit() else 0
                res["node_summary"] = ", ".join([f"{l.split()[0]} ({l.split()[1]})" for l in lines[:6]])
        elif c == "carbono":
            raw = dispatcher.run_ssh("carbono", "sinfo -h -o '%N %T %c %m'")
            if raw:
                lines = [l for l in raw.strip().splitlines() if len(l.split()) >= 4]
                res["reachable"] = True
                res["nodes"] = len(lines)
                sq = dispatcher.run_ssh("carbono", "squeue -h -t R | wc -l")
                res["queue"] = int(sq.strip()) if sq and sq.strip().isdigit() else 0
                res["node_summary"] = ", ".join([f"{l.split()[0]} ({l.split()[1]})" for l in lines[:6]])
        return res

    def print_single_cluster(self, cname: str, live: bool = False):
        c = cname.lower()
        data = self.clusters.get(c)
        if not data:
            print(f"❌ Cluster '{cname}' not found. Available: {', '.join(self.clusters.keys())}")
            return

        hw = data.get("hardware_summary", {})
        net = data.get("network", {})
        slurm = data.get("slurm", {})

        print("=" * 70)
        print(f" 🖥️  HPC SERVER PROFILE · [{data.get('name', cname.upper())}]")
        print("=" * 70)
        print(f"• Role            : {data.get('role', 'N/A')}")
        print(f"• Network Host    : {net.get('hostname', net.get('ip', 'N/A'))} (Internet: {'YES' if net.get('has_internet') else 'NO (LAN Isolated)'})")
        print(f"• Access Protocol : {net.get('access_method', 'SSH')}")
        print(f"• Slurm Mode      : {slurm.get('mode', 'N/A')} ({slurm.get('version', 'N/A')})")
        print("-" * 70)
        print(f"⚙️  Hardware Summary:")
        print(f"   - Active Nodes  : {hw.get('nodes_count', 'N/A')} nodes ({hw.get('node_prefix', '')}*)")
        print(f"   - Cores / Node  : {hw.get('cores_per_node', 'N/A')} cores (Total: {hw.get('total_cores', 'N/A')})")
        print(f"   - RAM / Node    : {hw.get('ram_per_node_gb', 'N/A')} GB (Total: {hw.get('total_ram_gb', 'N/A')} GB)")
        print(f"   - CPU Model     : {hw.get('cpu_model', 'N/A')}")

        parts = data.get("partitions_detail")
        if parts:
            print("-" * 70)
            print("📑 Partitions & Policies:")
            for pname, pinfo in parts.items():
                print(f"   • [{pname.upper()}] {pinfo.get('cores_per_node')} cores | {pinfo.get('ram_gb')} GB RAM | Max: {pinfo.get('max_walltime_days')} days")
                print(f"     ↳ Best for: {pinfo.get('best_for')}")

        rec = data.get("recommended_workloads", [])
        if rec:
            print("-" * 70)
            print("🎯 Recommended Workloads:")
            for r in rec:
                print(f"   • {r}")

        if live:
            print("-" * 70)
            print("📡 Live Telemetry Query:")
            tele = self.get_live_status(c)
            if tele["reachable"]:
                print(f"   🟢 Slurm Daemon : REACHABLE & ACTIVE")
                print(f"   • Active Nodes : {tele['nodes']} nodes responding")
                print(f"   • Running Jobs : {tele['queue']} jobs executing in queue")
                print(f"   • Nodes Sample : {tele['node_summary']}")
            else:
                print(f"   🔴 Slurm Daemon : UNREACHABLE / OFFLINE")

        print("=" * 70)

    def print_all(self, live: bool = False):
        print("=" * 82)
        print(f" 🌐 HIGH-PERFORMANCE COMPUTING CLUSTER ECOSYSTEM OVERVIEW")
        print("=" * 82)
        print(f"{'Cluster':<12} {'Nodes':<8} {'Total Cores':<14} {'Total RAM':<14} {'Internet':<10} {'Access'}")
        print("-" * 82)
        for cname, cinfo in self.clusters.items():
            hw = cinfo.get("hardware_summary", {})
            net = cinfo.get("network", {})
            nodes = str(hw.get("nodes_count", "1"))
            cores = str(hw.get("total_cores", "N/A"))
            ram = f"{hw.get('total_ram_gb', 'N/A')} GB" if hw.get('total_ram_gb') else "N/A"
            inet = "YES" if net.get("has_internet") else "NO (LAN)"
            access = net.get("access_method", "SSH")
            print(f"{cinfo.get('name', cname):<12} {nodes:<8} {cores:<14} {ram:<14} {inet:<10} {access}")

        print("=" * 82)
        if live:
            print("\n📡 Live Reachability Probe:")
            for cname in ["huk", "carbono", "iskay"]:
                tele = self.get_live_status(cname)
                status = "🟢 ONLINE" if tele["reachable"] else "🔴 OFFLINE"
                print(f" • {cname.upper():<8} : {status} ({tele['nodes']} nodes, {tele['queue']} active jobs)")
            print("=" * 82)


def main():
    parser = argparse.ArgumentParser(description="Unified HPC Server-Info & Superpower Manager")
    parser.add_argument("cluster", nargs="?", default=None, help="Cluster name (iskay, huk, carbono, arch, or all)")
    parser.add_argument("--live", action="store_true", help="Query live Slurm status via LAN/SSH")
    parser.add_argument("--all", action="store_true", help="Display ecosystem overview table")

    # Superpower Operations
    parser.add_argument("--decide", action="store_true", help="Run multi-cluster turnaround optimization decision matrix")
    parser.add_argument("--dispatch", type=str, metavar="DIR", help="Directory of calculation to automatically adapt, sync & dispatch")
    parser.add_argument("--target", type=str, help="Force target cluster for dispatch (carbono, huk, iskay)")
    parser.add_argument("--hook", type=str, help="Continuation hook to execute upon convergence")
    parser.add_argument("--steps", type=int, default=40, help="Estimated ionic steps for decision matrix")
    parser.add_argument("--atoms", type=int, default=33, help="Atom count for decision matrix")
    parser.add_argument("--dir", type=str, help="Calculation directory to inspect for decision matrix")
    parser.add_argument("--dry-run", action="store_true", help="Simulate dispatch without submitting")

    # Synchronization & Lifecycle
    parser.add_argument("--sync-check", "--sync", action="store_true", dest="sync_check", help="Verify convergence and sync outputs for all tracked jobs")
    parser.add_argument("--sync-watch", action="store_true", help="Run persistent synchronization monitor daemon")
    parser.add_argument("--interval", type=int, default=60, help="Polling interval in seconds for --sync-watch")
    parser.add_argument("--jobs", "--ledger", action="store_true", dest="show_jobs", help="Display tracked jobs ledger")
    parser.add_argument("--init-existing", action="store_true", help="Auto-discover active cluster jobs into ledger")

    # Job Sizing Advisor
    parser.add_argument("--advise", action="store_true", help="Run Amdahl's law job sizing advisor")
    parser.add_argument("--app", default="vasp", help="Target scientific package (vasp, siesta, lammps)")
    parser.add_argument("--kpoints", type=int, default=4, help="K-points count for sizing advisor")

    args = parser.parse_args()
    cli = ServerInfoCLI()

    # Route based on arguments
    if args.dispatch:
        dispatcher.dispatch_calculation(args.dispatch, target_cluster=args.target, continuation_hook=args.hook, dry_run=args.dry_run)
    elif args.decide:
        if args.dir:
            calc_info = dispatcher.inspect_calculation_dir(args.dir)
        else:
            calc_info = {
                "name": "User Query",
                "atoms": args.atoms,
                "steps": args.steps,
                "kpoints": args.kpoints,
                "supercell": "2x2" if args.atoms <= 40 else "3x3",
                "has_u": False,
                "u_val": 0.0
            }
        matrix = dispatcher.compute_turnaround_matrix(calc_info)
        dispatcher.print_decision_report(matrix)
    elif args.sync_watch:
        print(f"{BOLD}{GREEN}Starting HPC Synchronization Daemon (Interval: {args.interval}s)...{RESET}")
        try:
            while True:
                monitor.process_ledger_jobs(sync_on_completion=True)
                import time
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nStopped daemon.")
    elif args.sync_check:
        monitor.process_ledger_jobs(sync_on_completion=True)
    elif args.init_existing:
        monitor.main()
    elif args.show_jobs:
        ledger = monitor.load_ledger()
        if not ledger:
            print(f"{YELLOW}No jobs currently recorded in ledger ({monitor.LEDGER_PATH}).{RESET}")
        else:
            monitor.process_ledger_jobs(sync_on_completion=False)
    elif args.advise:
        advisor = JobEfficiencyAdvisor()
        res = advisor.advise(
            cluster=args.cluster or "huk",
            app=args.app,
            atoms=args.atoms,
            kpoints=args.kpoints
        )
        print(json.dumps(res, indent=2))
    elif args.all or (args.cluster and args.cluster.lower() == "all"):
        cli.print_all(live=args.live)
    elif args.cluster:
        cli.print_single_cluster(args.cluster, live=args.live)
    else:
        # Default: print all ecosystem with live reachability probe
        cli.print_all(live=True)


if __name__ == "__main__":
    main()
