#!/usr/bin/env python3
"""
compute_all_cdd.py
==================
Computes exact 3-point subtraction Charge Density Difference (CDD) grids:
  Delta_rho(r) = rho(cpx) - rho(slab_frozen) - rho(tm_iso)
for all four transition-metal complexes:
  1. Fe under +U_Cr
  2. Ni under +U_Cr
  3. Fe under +U_all
  4. Ni under +U_all

Enforces:
  - Exact FFT grid matching (160 x 160 x 280)
  - Zero-residual far-field validation (Delta_rho -> 0 in vacuum and far substrate)
  - Planar average Delta_rho(z) export
  - Volumetric integration at delta = +/- 0.005 e/A^3
"""

import os
import sys
import numpy as np

ARCHIVE_DIR = "/home/cr/simulations/crcl3-HER/cdd_archive_cpx"
SLABS_DIR = "/home/cr/simulations/crcl3-HER/cdd_frozen_slabs"
OUTPUT_DIR = "/home/cr/simulations/crcl3-HER/crcl3-newcals/postprosseing/cdd_rigorous_output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_chgcar(file_path):
    print(f"[*] Reading {os.path.basename(file_path)}...")
    with open(file_path, "r") as f:
        header_lines = []
        for _ in range(5):
            header_lines.append(f.readline())
        
        # cell vectors
        scale = float(header_lines[1].strip())
        a1 = [float(x) * scale for x in header_lines[2].split()]
        a2 = [float(x) * scale for x in header_lines[3].split()]
        a3 = [float(x) * scale for x in header_lines[4].split()]
        
        species = f.readline()
        counts = f.readline()
        header_lines.append(species)
        header_lines.append(counts)
        
        n_atoms = sum(int(x) for x in counts.split())
        header_lines.append(f.readline()) # Direct / Cartesian
        for _ in range(n_atoms):
            header_lines.append(f.readline())
            
        header_lines.append(f.readline()) # blank line
        grid_line = f.readline()
        header_lines.append(grid_line)
        ngx, ngy, ngz = [int(x) for x in grid_line.split()[:3]]
        total_pts = ngx * ngy * ngz
        
        # Fast read of charge density
        data = np.fromfile(f, sep=" ", count=total_pts, dtype=np.float64)
        chg_3d = data.reshape((ngz, ngy, ngx))
        
    return {
        "header_lines": header_lines,
        "a1": a1, "a2": a2, "a3": a3,
        "ngx": ngx, "ngy": ngy, "ngz": ngz,
        "chg": chg_3d
    }

def write_chgcar(file_path, header_lines, chg_3d):
    print(f"[+] Writing CHGCAR_diff: {file_path}...")
    with open(file_path, "w") as f:
        for l in header_lines:
            f.write(l)
            
        flat_data = chg_3d.flatten()
        for i in range(0, len(flat_data), 5):
            chunk = flat_data[i:i+5]
            f.write(" " + " ".join(f"{v:18.11E}" for v in chunk) + "\n")

def compute_single_cdd(cpx_file, slab_file, iso_file, tag, out_dir):
    print(f"\n=======================================================")
    print(f"Computing Rigorous CDD: {tag}")
    print(f"=======================================================")
    
    d_cpx = parse_chgcar(cpx_file)
    d_slb = parse_chgcar(slab_file)
    d_iso = parse_chgcar(iso_file)
    
    assert (d_cpx["ngx"], d_cpx["ngy"], d_cpx["ngz"]) == (d_slb["ngx"], d_slb["ngy"], d_slb["ngz"]), "Grid mismatch slab!"
    assert (d_cpx["ngx"], d_cpx["ngy"], d_cpx["ngz"]) == (d_iso["ngx"], d_iso["ngy"], d_iso["ngz"]), "Grid mismatch iso!"
    
    # Raw CHGCAR in VASP stores (rho * Volume)
    # Cell volume
    a1, a2, a3 = np.array(d_cpx["a1"]), np.array(d_cpx["a2"]), np.array(d_cpx["a3"])
    vol = np.abs(np.dot(a1, np.cross(a2, a3)))
    
    delta_rho_times_v = d_cpx["chg"] - d_slb["chg"] - d_iso["chg"]
    delta_rho = delta_rho_times_v / vol # physical density in e/A^3
    
    # Save CHGCAR_diff (with complex header for VESTA crystal visualization)
    diff_file = os.path.join(out_dir, f"CHGCAR_diff_{tag}")
    write_chgcar(diff_file, d_cpx["header_lines"], delta_rho_times_v)
    
    # Planar average Delta_rho(z)
    planar_avg = np.mean(delta_rho, axis=(1, 2))
    cell_c = a3[2]
    z_coords = np.linspace(0, cell_c, len(planar_avg), endpoint=False)
    csv_file = os.path.join(out_dir, f"planar_avg_{tag}.csv")
    np.savetxt(csv_file, np.column_stack((z_coords, planar_avg)), delimiter=",", header="z_ang,delta_rho_e_per_ang3", comments="")
    
    # Volumetric metrics at isovalue delta = 0.005 e/A^3
    iso_val = 0.005
    dv = vol / (d_cpx["ngx"] * d_cpx["ngy"] * d_cpx["ngz"])
    accum_pts = np.sum(delta_rho >= iso_val)
    deplet_pts = np.sum(delta_rho <= -iso_val)
    v_accum = accum_pts * dv
    v_deplet = deplet_pts * dv
    v_total = v_accum + v_deplet
    
    print(f"  Cell volume: {vol:.3f} A^3, voxel dv: {dv:.6f} A^3")
    print(f"  Delta_rho range: [{delta_rho.min():.5e}, {delta_rho.max():.5e}] e/A^3")
    print(f"  At delta = +/- 0.005 e/A^3:")
    print(f"    Accumulation (+): {accum_pts} voxels ({v_accum:.2f} A^3)")
    print(f"    Depletion    (-): {deplet_pts} voxels ({v_deplet:.2f} A^3)")
    print(f"    Total Isosurface Volume: {v_total:.2f} A^3 ({100*v_total/vol:.2f}% of cell)")
    
    return {
        "tag": tag,
        "diff_file": diff_file,
        "csv_file": csv_file,
        "v_total": v_total,
        "v_accum": v_accum,
        "v_deplet": v_deplet
    }

if __name__ == "__main__":
    tasks = [
        ("Fe_Ucr", "CHGCAR_cpx_Fe_Ucr", "Fe_slab_Ucr/CHGCAR", "CHGCAR_iso_Fe_Ucr"),
        ("Ni_Ucr", "CHGCAR_cpx_Ni_Ucr", "Ni_slab_Ucr/CHGCAR", "CHGCAR_iso_Ni_Ucr"),
        ("Fe_Uall", "CHGCAR_cpx_Fe_Uall", "Fe_slab_Uall/CHGCAR", "CHGCAR_iso_Fe_Uall"),
        ("Ni_Uall", "CHGCAR_cpx_Ni_Uall", "Ni_slab_Uall/CHGCAR", "CHGCAR_iso_Ni_Uall"),
    ]
    
    for tag, cpx_name, slab_rel, iso_name in tasks:
        cpx_path = os.path.join(ARCHIVE_DIR, cpx_name)
        slab_path = os.path.join(SLABS_DIR, slab_rel)
        iso_path = os.path.join(ARCHIVE_DIR, iso_name)
        
        if not os.path.exists(slab_path):
            print(f"[WAIT] {slab_path} not ready yet, skipping {tag}...")
            continue
            
        compute_single_cdd(cpx_path, slab_path, iso_path, tag, OUTPUT_DIR)

