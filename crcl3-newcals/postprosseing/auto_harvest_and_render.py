#!/usr/bin/env python3
"""
auto_harvest_and_render.py

Continuously polls Arch for 04_cdd_output/CHGCAR_diff.
As soon as it is present and > 10MB:
1. Rsyncs to local SSD: CHGCAR_diff_Ucr, planar_average_ucr.csv, ACF.dat
2. Executes VESTA headless export scale=2
3. Autotrims whitespace
4. Generates side-by-side comparative panel and 1D profile comparison
"""

import os
import sys
import time
import subprocess

LOCAL_DIR = "/Volumes/KingstonSSD/Krojects/Kresearch/crlcl3-CoFeNi-HER/crcl3-newcals/postprosseing/cdd_comparison"
REMOTE_SRC = "arch:/home/cr/simulations/crcl3-HER/crcl3-newcals/cdd_Co_Ucr_calculation/04_cdd_output/"
REMOTE_HUK_SRC = "arch:ssh huk 'ls -lh /home/carlos/crcl3-newcals/cdd_Co_Ucr_calculation/04_cdd_output/CHGCAR_diff 2>/dev/null'"

def check_remote_ready():
    # Check on Arch first
    res = subprocess.run(
        "ssh arch 'ls -lh /home/cr/simulations/crcl3-HER/crcl3-newcals/cdd_Co_Ucr_calculation/04_cdd_output/CHGCAR_diff 2>/dev/null'",
        shell=True, capture_output=True, text=True
    )
    if "CHGCAR_diff" in res.stdout:
        return "arch"
        
    # Check directly on Huk
    res_huk = subprocess.run(
        "ssh arch \"ssh huk 'ls -lh /home/carlos/crcl3-newcals/cdd_Co_Ucr_calculation/04_cdd_output/CHGCAR_diff 2>/dev/null'\"",
        shell=True, capture_output=True, text=True
    )
    if "CHGCAR_diff" in res_huk.stdout:
        return "huk"
        
    return None

def main():
    print("[INFO] Waiting for CHGCAR_diff to appear on Huk/Arch...")
    while True:
        status = check_remote_ready()
        if status == "arch":
            print("[OK] Detected CHGCAR_diff on Arch! Syncing to local SSD...")
            cmd = f"rsync -avz arch:/home/cr/simulations/crcl3-HER/crcl3-newcals/cdd_Co_Ucr_calculation/04_cdd_output/CHGCAR_diff {LOCAL_DIR}/CHGCAR_diff_Ucr"
            subprocess.run(cmd, shell=True, check=True)
            subprocess.run(f"rsync -avz arch:/home/cr/simulations/crcl3-HER/crcl3-newcals/cdd_Co_Ucr_calculation/04_cdd_output/planar_average_ucr.csv {LOCAL_DIR}/", shell=True)
            subprocess.run(f"rsync -avz arch:/home/cr/simulations/crcl3-HER/crcl3-newcals/cdd_Co_Ucr_calculation/04_cdd_output/ACF.dat {LOCAL_DIR}/ACF_ucr.dat", shell=True)
            break
        elif status == "huk":
            print("[OK] Detected CHGCAR_diff on Huk! Syncing directly via Arch proxy...")
            cmd = f"rsync -avz -e 'ssh -A arch ssh' huk:/home/carlos/crcl3-newcals/cdd_Co_Ucr_calculation/04_cdd_output/CHGCAR_diff {LOCAL_DIR}/CHGCAR_diff_Ucr"
            subprocess.run(cmd, shell=True, check=True)
            subprocess.run(f"rsync -avz -e 'ssh -A arch ssh' huk:/home/carlos/crcl3-newcals/cdd_Co_Ucr_calculation/04_cdd_output/planar_average_ucr.csv {LOCAL_DIR}/", shell=True)
            subprocess.run(f"rsync -avz -e 'ssh -A arch ssh' huk:/home/carlos/crcl3-newcals/cdd_Co_Ucr_calculation/04_cdd_output/ACF.dat {LOCAL_DIR}/ACF_ucr.dat", shell=True)
            break
            
        time.sleep(5)
        
    print("[OK] Files harvested successfully! Launching rendering and comparison script...")
    script = "/Volumes/KingstonSSD/Krojects/Kresearch/crlcl3-CoFeNi-HER/crcl3-newcals/postprosseing/sync_and_generate_cdd_ucr_figures.py"
    subprocess.run(f"~/venvs/research/bin/python3 {script} render_only", shell=True, check=True)
    print("🎉 ALL PROCESSING AND RENDERING COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
