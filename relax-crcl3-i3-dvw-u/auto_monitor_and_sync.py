#!/usr/bin/env python3
"""
auto_monitor_and_sync.py
Monitors active SLURM jobs for relax-crcl3-i3-dvw-u, syncs completed results from scratch,
updates 3-panel lattice_vs_u and crcl3_bandgap_benchmarks_reviewer figures,
and creates the final zip archive when all 7 calculations complete.
"""

import os
import subprocess
import shutil
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRATCH_ROOT = "/home/cr/scratch_vasp/relax-crcl3-i3-dvw-u"
PYTHON_ENV = "/home/cr/.local/share/mamba/envs/vasp-env/bin/python"
U_VALUES = [0, 1, 2, 3, 4, 5, 6]

def check_and_sync():
    all_done = True
    completed_count = 0
    print("Checking status of U = 0 .. 6 eV calculations...")
    for u in U_VALUES:
        u_str = f"U_{u}"
        target_dir = os.path.join(BASE_DIR, u_str)
        scratch_dir = os.path.join(SCRATCH_ROOT, u_str)
        
        target_outcar = os.path.join(target_dir, "OUTCAR")
        scratch_outcar = os.path.join(scratch_dir, "OUTCAR")
        
        # Check if completed in scratch
        if os.path.exists(scratch_outcar):
            with open(scratch_outcar, "r", errors="ignore") as f:
                content = f.read()
            if "General timing and accounting" in content:
                # Sync files to target_dir
                for fname in ["OUTCAR", "CONTCAR", "EIGENVAL", "DOSCAR", "vasprun.xml", "OSZICAR", "vasp_run.log"]:
                    src = os.path.join(scratch_dir, fname)
                    dst = os.path.join(target_dir, fname)
                    if os.path.exists(src):
                        shutil.copyfile(src, dst)
                        
        if os.path.exists(target_outcar):
            with open(target_outcar, "r", errors="ignore") as f:
                content = f.read()
            if "General timing and accounting" in content:
                completed_count += 1
                print(f"  [{u_str}] ✅ Completed")
                continue
                
        all_done = False
        # Check if running in SLURM
        squeue_out = subprocess.run(["squeue", "-h", "-o", "%j %T %M"], capture_output=True, text=True).stdout
        job_name = f"CrCl3_i3_U_{u}"
        status = "Pending"
        for line in squeue_out.splitlines():
            if job_name in line:
                parts = line.split()
                status = f"{parts[1]} ({parts[2]})"
                break
        print(f"  [{u_str}] ⏳ {status}")
        
    print(f"\nProgress: {completed_count}/7 completed.")
    
    # Re-run plotting scripts
    print("\nUpdating publication figures...")
    subprocess.run([PYTHON_ENV, os.path.join(BASE_DIR, "plot_lattice_vs_u.py")], check=True)
    subprocess.run([PYTHON_ENV, os.path.join(BASE_DIR, "plot_bandgap_vs_u.py")], check=True)
    subprocess.run([PYTHON_ENV, os.path.join(BASE_DIR, "plot_bandgap_vs_u_benchmarks.py")], check=True)
    
    if all_done:
        print("\nAll 7 calculations complete! Packaging relax-crcl3-i3-dvw-u.zip...")
        zip_scratch = "/home/cr/scratch_vasp/relax-crcl3-i3-dvw-u.zip"
        zip_target = os.path.join(os.path.dirname(BASE_DIR), "relax-crcl3-i3-dvw-u.zip")
        artifact_zip = "/home/cr/.gemini/antigravity-cli/brain/571b6713-67da-45af-93c4-78b56dc763ef/relax-crcl3-i3-dvw-u.zip"
        
        with zipfile.ZipFile(zip_scratch, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for root, dirs, files in os.walk(BASE_DIR):
                if "__pycache__" in root:
                    continue
                for f in files:
                    if f.endswith((".pyc", ".DS_Store")):
                        continue
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, os.path.dirname(BASE_DIR))
                    zf.write(full_p, arcname=rel_p)
                    
        shutil.copyfile(zip_scratch, zip_target)
        shutil.copyfile(zip_scratch, artifact_zip)
        print(f"Archive successfully generated at: {zip_target}")

if __name__ == "__main__":
    check_and_sync()
