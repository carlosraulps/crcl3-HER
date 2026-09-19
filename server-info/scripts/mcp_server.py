#!/usr/bin/env python3
"""
================================================================================
HPC Cluster Intelligence MCP Server (JSON-RPC 2.0 stdio)
================================================================================
Exposes HPC cluster hardware specifications, live Slurm telemetry, job sizing
advisories, and automated batch script generation as Model Context Protocol (MCP)
tools for Antigravity, Claude, and AI assistants.

Tools provided:
  - list_clusters()
  - get_cluster_info(cluster_name)
  - get_live_telemetry(cluster_name)
  - calculate_optimal_job(cluster, app, atoms, kpoints, supercell, walltime_days, hybrid)
  - generate_slurm_script(cluster, app, job_name, atoms, kpoints, supercell)
================================================================================
"""

import sys
import os
import json
import subprocess
from typing import Dict, Any

from job_efficiency_advisor import JobEfficiencyAdvisor
from slurm_generator import generate_sbatch


def load_clusters_db() -> Dict[str, Any]:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
        "description": "Lists all available HPC clusters (Iskay, Huk, Carbono, Arch) with hardware and network summaries.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_cluster_info",
        "description": "Retrieves comprehensive architecture, hardware topology, partitions, and storage limits for a specific cluster.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "cluster_name": {"type": "string", "description": "Name of the cluster (iskay, huk, carbono, arch)"}
            },
            "required": ["cluster_name"]
        }
    },
    {
        "name": "get_live_telemetry",
        "description": "Queries real-time Slurm daemon reachability, active nodes, and running queue on Iskay or Huk.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "cluster_name": {"type": "string", "description": "Target cluster (iskay or huk)"}
            },
            "required": ["cluster_name"]
        }
    },
    {
        "name": "calculate_optimal_job",
        "description": "Calculates the most efficient core count, node placement, partition, memory request, and software tuning tags (NCORE, KPAR) for a project.",
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
        "name": "generate_slurm_script",
        "description": "Generates an optimized, ready-to-run .sbatch Slurm job script tailored to the cluster and software parameters.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "cluster": {"type": "string", "description": "Target cluster (iskay, huk, carbono)"},
                "app": {"type": "string", "default": "vasp"},
                "job_name": {"type": "string", "default": "dft_calc"},
                "atoms": {"type": "integer", "default": 32},
                "kpoints": {"type": "integer", "default": 4},
                "supercell": {"type": "string", "default": "custom"}
            },
            "required": ["cluster"]
        }
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
        if c == "iskay":
            res = subprocess.run("sinfo -h -o '%N %T %c %m' 2>/dev/null", shell=True, capture_output=True, text=True)
            nodes = res.stdout.strip().splitlines()
            q_res = subprocess.run("squeue -h -t R | wc -l", shell=True, capture_output=True, text=True)
            return {"cluster": "iskay", "status": "online", "nodes_count": len(nodes), "running_jobs": int(q_res.stdout.strip() or 0)}
        elif c == "huk":
            res = subprocess.run("ssh -o BatchMode=yes -o ConnectTimeout=3 huk 'sinfo -h -o \"%N %T %c %m\"' 2>/dev/null", shell=True, capture_output=True, text=True)
            nodes = [l for l in res.stdout.strip().splitlines() if len(l.split()) >= 4]
            q_res = subprocess.run("ssh -o BatchMode=yes -o ConnectTimeout=3 huk 'squeue -h -t R | wc -l' 2>/dev/null", shell=True, capture_output=True, text=True)
            return {"cluster": "huk", "status": "online", "nodes_count": len(nodes), "running_jobs": int(q_res.stdout.strip() or 0)}
        return {"error": f"Live telemetry only supported for iskay and huk currently."}

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

    elif name == "generate_slurm_script":
        script = generate_sbatch(
            cluster=args.get("cluster", "huk"),
            app=args.get("app", "vasp"),
            job_name=args.get("job_name", "dft_calc"),
            atoms=args.get("atoms", 32),
            kpoints=args.get("kpoints", 4),
            supercell=args.get("supercell", "custom")
        )
        return {"script": script}

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
                        "serverInfo": {"name": "hpc-server-info-mcp", "version": "1.0.0"}
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
