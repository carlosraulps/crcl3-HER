#!/usr/bin/env python3
"""
================================================================================
HPC Cluster Intelligence & Superpower MCP Server (JSON-RPC 2.0 stdio)
================================================================================
Exposes HPC cluster hardware profiles, live Slurm telemetry, job sizing
advisories, multi-cluster turnaround optimization, auto-dispatch, and
safeguarded synchronization as Model Context Protocol (MCP) tools.

Tools provided:
  - list_clusters()
  - get_cluster_info(cluster_name)
  - get_live_telemetry(cluster_name)
  - calculate_optimal_job(cluster, app, atoms, kpoints, ...)
  - decide_cluster(atoms, steps, kpoints, calc_dir)
  - dispatch_calculation(calc_dir, target_cluster, continuation_hook, dry_run)
  - sync_and_monitor(sync_on_completion)
  - list_tracked_jobs()
================================================================================
"""

import sys
import os
import json
from typing import Dict, Any, Optional

# Add scripts directory to sys.path
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from job_efficiency_advisor import JobEfficiencyAdvisor
from slurm_generator import generate_sbatch
import hpc_meta_dispatcher as dispatcher
import hpc_sync_monitor as monitor


def load_clusters_db() -> Dict[str, Any]:
    base_dir = os.path.dirname(SCRIPT_DIR)
    clusters_path = os.path.join(base_dir, "resources", "clusters.json")
    if os.path.exists(clusters_path):
        with open(clusters_path, "r") as f:
            return json.load(f).get("clusters", {})
    return {}


CLUSTERS_DB = load_clusters_db()
ADVISOR = JobEfficiencyAdvisor()

TOOLS = [
    {
        "name": "list_clusters",
        "description": "Lists all available HPC clusters (Iskay, Huk, Carbono, Arch) with hardware, CPU architecture, and network access methods.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_cluster_info",
        "description": "Retrieves comprehensive architecture, hardware topology, partitions, storage paths, and module environments for a specific cluster.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "cluster_name": {"type": "string", "description": "Name of cluster (iskay, huk, carbono, arch)"}
            },
            "required": ["cluster_name"]
        }
    },
    {
        "name": "get_live_telemetry",
        "description": "Queries real-time Slurm reachability, active responding nodes, and running queue count on Huk, Carbono, or Iskay.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "cluster_name": {"type": "string", "description": "Target cluster (iskay, huk, carbono)"}
            },
            "required": ["cluster_name"]
        }
    },
    {
        "name": "calculate_optimal_job",
        "description": "Calculates optimal core allocation, partition, memory request, and VASP parallel tags (NCORE, KPAR) using Amdahl's Law.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "cluster": {"type": "string", "description": "Target cluster (iskay, huk, carbono)"},
                "app": {"type": "string", "default": "vasp", "enum": ["vasp", "siesta", "lammps", "generic"]},
                "atoms": {"type": "integer", "default": 32, "description": "Number of atoms in system"},
                "kpoints": {"type": "integer", "default": 4, "description": "Total k-points in grid"},
                "supercell": {"type": "string", "default": "custom", "enum": ["1x1", "2x2", "3x3", "custom"]},
                "walltime_days": {"type": "integer", "default": 7, "description": "Requested runtime in days"},
                "is_hybrid": {"type": "boolean", "default": False, "description": "Whether using HSE06 hybrid functional"}
            },
            "required": ["cluster"]
        }
    },
    {
        "name": "decide_cluster",
        "description": "Evaluates live node core fragmentation, queue latency, and empirical execution benchmarks across Carbono, Huk, and Iskay to recommend the cluster with minimum total turnaround time.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "atoms": {"type": "integer", "default": 33, "description": "Number of atoms"},
                "steps": {"type": "integer", "default": 40, "description": "Expected relaxation steps"},
                "calc_dir": {"type": "string", "description": "Optional local calculation directory to inspect POSCAR/INCAR"}
            }
        }
    },
    {
        "name": "dispatch_calculation",
        "description": "Automatically selects the fastest cluster (or targeted cluster), generates a tailored zero-redundancy Slurm batch script with USR1 checkpoint traps, rsyncs inputs, submits via sbatch, and registers the job in the global tracking ledger.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "calc_dir": {"type": "string", "description": "Absolute path to local calculation directory with POSCAR/INCAR/POTCAR"},
                "target_cluster": {"type": "string", "description": "Optional forced target cluster (carbono, huk, iskay)"},
                "continuation_hook": {"type": "string", "description": "Optional workflow hook to run upon completion (e.g. stage_h_on_co)"},
                "dry_run": {"type": "boolean", "default": False, "description": "Simulate dispatch without submitting"}
            },
            "required": ["calc_dir"]
        }
    },
    {
        "name": "sync_and_monitor",
        "description": "Audits all active jobs in ~/.hpc_jobs_ledger.json, verifies convergence using strict multi-tier validation (preventing false positives/negatives), rsyncs outputs back to local workspace, triggers continuation hooks, and pushes to Git master branch.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sync_on_completion": {"type": "boolean", "default": True, "description": "Whether to auto-sync outputs on convergence"}
            }
        }
    },
    {
        "name": "list_tracked_jobs",
        "description": "Returns the complete persistent ledger of active and completed calculations across all clusters.",
        "inputSchema": {"type": "object", "properties": {}}
    }
]


def handle_tool_call(name: str, args: Dict[str, Any]) -> Any:
    if name == "list_clusters":
        summary = {}
        for cname, cinfo in CLUSTERS_DB.items():
            summary[cname] = {
                "name": cinfo.get("name"),
                "role": cinfo.get("role"),
                "cores": cinfo.get("hardware_summary", {}).get("total_cores"),
                "ram_gb": cinfo.get("hardware_summary", {}).get("total_ram_gb"),
                "access": cinfo.get("network", {}).get("access_method"),
                "has_internet": cinfo.get("network", {}).get("has_internet")
            }
        return summary

    elif name == "get_cluster_info":
        c = args.get("cluster_name", "").lower()
        if c in CLUSTERS_DB:
            return CLUSTERS_DB[c]
        return {"error": f"Cluster '{c}' not found. Available: {list(CLUSTERS_DB.keys())}"}

    elif name == "get_live_telemetry":
        c = args.get("cluster_name", "").lower()
        from server_info import ServerInfoCLI
        cli = ServerInfoCLI()
        return cli.get_live_status(c)

    elif name == "calculate_optimal_job":
        return ADVISOR.advise(
            cluster=args.get("cluster", "huk"),
            app=args.get("app", "vasp"),
            atoms=args.get("atoms", 32),
            kpoints=args.get("kpoints", 4),
            supercell=args.get("supercell", "custom"),
            walltime_days=args.get("walltime_days", 7),
            is_hybrid=args.get("is_hybrid", False)
        )

    elif name == "decide_cluster":
        calc_dir = args.get("calc_dir")
        if calc_dir and os.path.exists(calc_dir):
            calc_info = dispatcher.inspect_calculation_dir(calc_dir)
        else:
            calc_info = {
                "name": "MCP Query",
                "atoms": args.get("atoms", 33),
                "steps": args.get("steps", 40),
                "kpoints": 4,
                "supercell": "2x2" if args.get("atoms", 33) <= 40 else "3x3",
                "has_u": False,
                "u_val": 0.0
            }
        matrix = dispatcher.compute_turnaround_matrix(calc_info)
        return {
            "evaluations": matrix["evaluations"],
            "recommended_winner": matrix["winner"]
        }

    elif name == "dispatch_calculation":
        calc_dir = args.get("calc_dir")
        target_cluster = args.get("target_cluster")
        hook = args.get("continuation_hook")
        dry_run = args.get("dry_run", False)
        return dispatcher.dispatch_calculation(
            calc_dir,
            target_cluster=target_cluster,
            continuation_hook=hook,
            dry_run=dry_run
        )

    elif name == "sync_and_monitor":
        sync_on_completion = args.get("sync_on_completion", True)
        stats = monitor.process_ledger_jobs(sync_on_completion=sync_on_completion)
        return {"status": "SUCCESS", "stats": stats, "ledger": monitor.load_ledger()}

    elif name == "list_tracked_jobs":
        return monitor.load_ledger()

    return {"error": f"Unknown tool: {name}"}


def main():
    """Simple JSON-RPC 2.0 loop over stdin/stdout for MCP clients."""
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "hpc-server-info-mcp", "version": "2.0.0"}
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": TOOLS}
                }
            elif method == "tools/call":
                params = req.get("params", {})
                tname = params.get("name")
                targs = params.get("arguments", {})
                res_content = handle_tool_call(tname, targs)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(res_content, indent=2)}]
                    }
                }
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method {method} not found"}
                }

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
