#!/usr/bin/env python3
"""
================================================================================
Server Info & Multi-Cluster Inspector CLI
================================================================================
Inspects hardware specs, memory topologies, Slurm partitions, and live cluster
telemetry for Iskay, Huk, Carbono, and Arch.

Usage:
    python3 server_info.py [cluster_name] [--live] [--all]
    python3 server_info.py huk --live
    python3 server_info.py all
================================================================================
"""

import sys
import os
import json
import argparse
import subprocess
from typing import Dict, Any, Optional


def run_cmd(cmd: str, timeout: int = 8) -> Tuple_out:
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return res.returncode == 0, res.stdout.strip()
    except Exception as e:
        return False, str(e)


Tuple_out = tuple[bool, str]


class ServerInfoCLI:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
            ok, sinfo_out = run_cmd("sinfo -h -o '%N %T %c %m' 2>/dev/null")
            if ok and sinfo_out:
                lines = sinfo_out.splitlines()
                res["reachable"] = True
                res["nodes"] = len(lines)
                _, sq_out = run_cmd("squeue -h -t R | wc -l")
                res["queue"] = int(sq_out) if sq_out.isdigit() else 0
                res["node_summary"] = ", ".join([f"{l.split()[0]} ({l.split()[1]})" for l in lines[:4]])
        elif c == "huk":
            ok, sinfo_out = run_cmd("ssh -o BatchMode=yes -o ConnectTimeout=4 huk 'sinfo -h -o \"%N %T %c %m\"' 2>/dev/null")
            if ok and sinfo_out:
                lines = [l for l in sinfo_out.splitlines() if len(l.split()) >= 4]
                res["reachable"] = True
                res["nodes"] = len(lines)
                _, sq_out = run_cmd("ssh -o BatchMode=yes -o ConnectTimeout=4 huk 'squeue -h -t R | wc -l' 2>/dev/null")
                res["queue"] = int(sq_out) if sq_out.isdigit() else 0
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

        print("=" * 68)
        print(f" 🖥️  HPC SERVER PROFILE · [{data.get('name', cname.upper())}]")
        print("=" * 68)
        print(f"• Role            : {data.get('role', 'N/A')}")
        print(f"• Network Host    : {net.get('hostname', net.get('ip', 'N/A'))} (Internet: {'YES' if net.get('has_internet') else 'NO (LAN Isolated)'})")
        print(f"• Access Protocol : {net.get('access_method', 'SSH')}")
        print(f"• Slurm Mode      : {slurm.get('mode', 'N/A')} ({slurm.get('version', 'N/A')})")
        print("-" * 68)
        print(f"⚙️  Hardware Summary:")
        print(f"   - Active Nodes  : {hw.get('nodes_count', 'N/A')} nodes ({hw.get('node_prefix', '')}*)")
        print(f"   - Cores / Node  : {hw.get('cores_per_node', 'N/A')} cores (Total: {hw.get('total_cores', 'N/A')})")
        print(f"   - RAM / Node    : {hw.get('ram_per_node_gb', 'N/A')} GB (Total: {hw.get('total_ram_gb', 'N/A')} GB)")
        print(f"   - CPU Model     : {hw.get('cpu_model', 'N/A')}")

        parts = data.get("partitions_detail")
        if parts:
            print("-" * 68)
            print("📑 Partitions & Policies:")
            for pname, pinfo in parts.items():
                print(f"   • [{pname.upper()}] {pinfo.get('cores_per_node')} cores | {pinfo.get('ram_gb')} GB RAM | Max: {pinfo.get('max_walltime_days')} days")
                print(f"     ↳ Best for: {pinfo.get('best_for')}")

        rec = data.get("recommended_workloads", [])
        if rec:
            print("-" * 68)
            print("🎯 Recommended Workloads:")
            for r in rec:
                print(f"   • {r}")

        if live:
            print("-" * 68)
            print("📡 Live Telemetry Query:")
            tele = self.get_live_status(c)
            if tele["reachable"]:
                print(f"   🟢 Slurm Daemon : REACHABLE & ACTIVE")
                print(f"   • Active Nodes : {tele['nodes']} nodes responding")
                print(f"   • Running Jobs : {tele['queue']} jobs executing in queue")
                print(f"   • Nodes Sample : {tele['node_summary']}")
            else:
                print(f"   🔴 Slurm Daemon : UNREACHABLE / OFFLINE")

        print("=" * 68)

    def print_all(self, live: bool = False):
        print("=" * 78)
        print(f" 🌐 HIGH-PERFORMANCE COMPUTING CLUSTER ECOSYSTEM OVERVIEW")
        print("=" * 78)
        print(f"{'Cluster':<12} {'Nodes':<8} {'Total Cores':<14} {'Total RAM':<14} {'Internet':<10} {'Access'}")
        print("-" * 78)
        for cname, cinfo in self.clusters.items():
            hw = cinfo.get("hardware_summary", {})
            net = cinfo.get("network", {})
            nodes = str(hw.get("nodes_count", "1"))
            cores = str(hw.get("total_cores", "N/A"))
            ram = f"{hw.get('total_ram_gb', 'N/A')} GB" if hw.get('total_ram_gb') else "N/A"
            inet = "YES" if net.get("has_internet") else "NO (LAN)"
            access = net.get("access_method", "SSH")
            print(f"{cinfo.get('name', cname):<12} {nodes:<8} {cores:<14} {ram:<14} {inet:<10} {access}")

        print("=" * 78)
        if live:
            print("\n📡 Live Reachability Probe:")
            for cname in ["iskay", "huk"]:
                tele = self.get_live_status(cname)
                status = "🟢 ONLINE" if tele["reachable"] else "🔴 OFFLINE"
                print(f" • {cname.upper():<8} : {status} ({tele['nodes']} nodes, {tele['queue']} active jobs)")
            print("=" * 78)


def main():
    parser = argparse.ArgumentParser(description="HPC Cluster Profile & Specification CLI")
    parser.add_argument("cluster", nargs="?", default="all", help="Cluster name (iskay, huk, carbono, arch, or all)")
    parser.add_argument("--live", action="store_true", help="Query live Slurm status via LAN/SSH")
    parser.add_argument("--all", action="store_true", help="Display ecosystem overview table")

    args = parser.parse_args()
    cli = ServerInfoCLI()

    if args.all or args.cluster.lower() == "all":
        cli.print_all(live=args.live)
    else:
        cli.print_single_cluster(args.cluster, live=args.live)


if __name__ == "__main__":
    main()
