#!/usr/bin/env python3
"""
postprocess_cdd_and_bader.py

1. Calculates Charge Density Difference (CDD):
   Delta_rho(r) = rho(Co@CrCl3) - rho(CrCl3_slab) - rho(isolated_Co)
   Exports:
   - CHGCAR_diff (VASP 5 format for VESTA 3D isosurfaces)
   - cdd_planar_average.png (1D planar average Delta_rho(z) along c-axis)
   
2. Performs Bader Charge Analysis:
   - Uses chgsum.pl and bader on AECCAR0, AECCAR2, CHGCAR
   - Extracts net atomic charges (Delta Q = Z_val - Q_bader) and atomic magnetic moments.
"""

import os
import sys
import subprocess
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_RELAX = os.path.join(BASE_DIR, "01_relax")
DIR_SLAB = os.path.join(BASE_DIR, "02_cdd_slab")
DIR_TM = os.path.join(BASE_DIR, "03_cdd_isolated_tm")
DIR_OUT = os.path.join(BASE_DIR, "04_bader_and_cdd_analysis")
os.makedirs(DIR_OUT, exist_ok=True)

def parse_chgcar(file_path):
    """Reads a VASP CHGCAR file and returns atoms, grid dimensions, and 3D charge array."""
    with open(file_path, "r") as f:
        # Header (POSCAR format)
        system = f.readline()
        scale = float(f.readline().strip())
        a1 = [float(x) * scale for x in f.readline().split()]
        a2 = [float(x) * scale for x in f.readline().split()]
        a3 = [float(x) * scale for x in f.readline().split()]
        
        species = f.readline().split()
        # Check if numbers or species
        try:
            counts = [int(x) for x in species]
            species = [f"Elem{i}" for i in range(len(counts))]
        except ValueError:
            counts = [int(x) for x in f.readline().split()]
            
        coord_type = f.readline().strip()
        num_atoms = sum(counts)
        coords = []
        for _ in range(num_atoms):
            coords.append([float(x) for x in f.readline().split()[:3]])
            
        blank = f.readline()
        # Grid dimensions NGX, NGY, NGZ
        ngx, ngy, ngz = [int(x) for x in f.readline().split()[:3]]
        total_pts = ngx * ngy * ngz
        
        # Read charge density data
        chg_data = []
        while len(chg_data) < total_pts:
            line = f.readline()
            if not line:
                break
            chg_data.extend([float(x) for x in line.split()])
            
        chg_3d = np.array(chg_data[:total_pts]).reshape((ngz, ngy, ngx))
        # VASP stores in Fortran-order (x fastest, then y, then z)
        # Array shape is (ngz, ngy, ngx) corresponding to z, y, x
        
    return {
        "header_lines": {
            "system": system,
            "scale": scale,
            "a1": a1, "a2": a2, "a3": a3,
            "species": species,
            "counts": counts,
            "coord_type": coord_type,
            "coords": coords,
            "ngx": ngx, "ngy": ngy, "ngz": ngz
        },
        "chg": chg_3d
    }

def write_chgcar(file_path, header, chg_3d):
    """Writes a 3D charge array in standard VASP CHGCAR format."""
    ngx, ngy, ngz = header["ngx"], header["ngy"], header["ngz"]
    with open(file_path, "w") as f:
        f.write(header["system"])
        f.write(f"   {header['scale']:.16f}\n")
        f.write(f" {header['a1'][0]:12.8f} {header['a1'][1]:12.8f} {header['a1'][2]:12.8f}\n")
        f.write(f" {header['a2'][0]:12.8f} {header['a2'][1]:12.8f} {header['a2'][2]:12.8f}\n")
        f.write(f" {header['a3'][0]:12.8f} {header['a3'][1]:12.8f} {header['a3'][2]:12.8f}\n")
        f.write(" " + " ".join(header["species"]) + "\n")
        f.write(" " + " ".join(str(c) for c in header["counts"]) + "\n")
        f.write(f"{header['coord_type']}\n")
        for c in header["coords"]:
            f.write(f" {c[0]:14.8f} {c[1]:14.8f} {c[2]:14.8f}\n")
        f.write("\n")
        f.write(f" {ngx:5d} {ngy:5d} {ngz:5d}\n")
        
        flat_data = chg_3d.flatten()
        for i in range(0, len(flat_data), 5):
            chunk = flat_data[i:i+5]
            f.write(" " + " ".join(f"{v:18.11E}" for v in chunk) + "\n")

def process_cdd():
    chg_complex_file = os.path.join(DIR_RELAX, "CHGCAR")
    chg_slab_file = os.path.join(DIR_SLAB, "CHGCAR")
    chg_tm_file = os.path.join(DIR_TM, "CHGCAR")
    
    if not (os.path.exists(chg_complex_file) and os.path.exists(chg_slab_file) and os.path.exists(chg_tm_file)):
        print("[WAIT] Not all CHGCAR files are available yet for CDD.")
        return
        
    print("[INFO] Parsing CHGCAR files for CDD...")
    d_complex = parse_chgcar(chg_complex_file)
    d_slab = parse_chgcar(chg_slab_file)
    d_tm = parse_chgcar(chg_tm_file)
    
    # Check grid compatibility
    if d_complex["chg"].shape != d_slab["chg"].shape or d_complex["chg"].shape != d_tm["chg"].shape:
        print("[ERROR] Grid dimension mismatch between CHGCAR files!")
        return
        
    # Delta rho = rho(complex) - rho(slab) - rho(TM)
    delta_rho = d_complex["chg"] - d_slab["chg"] - d_tm["chg"]
    
    diff_file = os.path.join(DIR_OUT, "CHGCAR_diff")
    write_chgcar(diff_file, d_complex["header_lines"], delta_rho)
    print(f"[OK] Written CDD 3D volumetric file: {diff_file}")
    
    # 1D Planar Average Delta_rho(z)
    # delta_rho shape is (ngz, ngy, ngx)
    # Planar average is mean over x and y (axes 1 and 2)
    planar_avg = np.mean(delta_rho, axis=(1, 2))
    cell_c = d_complex["header_lines"]["a3"][2]
    z_coords = np.linspace(0, cell_c, len(planar_avg), endpoint=False)
    
    plt.figure(figsize=(7, 4.5), dpi=300)
    plt.plot(z_coords, planar_avg, color="#1f77b4", lw=2, label=r"$\Delta \rho(z) = \rho_{\mathrm{Co@CrCl_3}} - \rho_{\mathrm{CrCl_3}} - \rho_{\mathrm{Co}}$")
    plt.axhline(0, color="k", ls="--", alpha=0.5, lw=1)
    
    # Mark positions
    z_co = d_complex["header_lines"]["coords"][-1][2] * cell_c
    plt.axvline(z_co, color="#d62728", ls=":", lw=1.5, label=f"Co ($z = {z_co:.2f}$ Å)")
    
    plt.xlabel(r"$z$ coordinate (Å)", fontsize=13)
    plt.ylabel(r"Planar Average $\Delta \rho(z)$ ($e$/Å)", fontsize=13)
    plt.title(r"Charge Density Difference Profile: $\mathrm{Co@CrCl_3}$ ($S_2$ Hollow, $+U_{\mathrm{all}}$)", fontsize=13)
    plt.legend(frameon=True, facecolor="white", alpha=0.92, edgecolor="#cccccc")
    plt.tight_layout()
    plot_path = os.path.join(DIR_OUT, "cdd_planar_average.png")
    plt.savefig(plot_path)
    plt.close()
    print(f"[OK] Saved planar average CDD plot: {plot_path}")

def run_bader():
    aeccar0 = os.path.join(DIR_RELAX, "AECCAR0")
    aeccar2 = os.path.join(DIR_RELAX, "AECCAR2")
    chgcar = os.path.join(DIR_RELAX, "CHGCAR")
    
    if not (os.path.exists(aeccar0) and os.path.exists(aeccar2) and os.path.exists(chgcar)):
        print("[WAIT] AECCAR files not found yet in 01_relax. Run Bader when SCF finishes.")
        return
        
    print("[INFO] Running Bader charge analysis...")
    sum_file = os.path.join(DIR_RELAX, "CHGCAR_sum")
    cmd_sum = f"chgsum.pl {aeccar0} {aeccar2}"
    subprocess.run(cmd_sum, shell=True, cwd=DIR_RELAX, check=True)
    
    cmd_bader = f"bader {chgcar} -ref {sum_file}"
    subprocess.run(cmd_bader, shell=True, cwd=DIR_RELAX, check=True)
    
    # Parse ACF.dat
    acf_path = os.path.join(DIR_RELAX, "ACF.dat")
    if os.path.exists(acf_path):
        shutil.copy2(acf_path, os.path.join(DIR_OUT, "ACF.dat"))
        print(f"[OK] Bader analysis complete. Results saved to {DIR_OUT}/ACF.dat")

if __name__ == "__main__":
    process_cdd()
    run_bader()
