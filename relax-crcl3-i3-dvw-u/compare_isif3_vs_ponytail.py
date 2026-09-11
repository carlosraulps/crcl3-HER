#!/usr/bin/env python3
"""
compare_isif3_vs_ponytail.py
Compares the relaxed structural parameters, stress tensors, energies, and monolayer thickness
between:
1. Original ISIF = 2 (fixed in-plane bulk cell a = 6.0485 A)
2. Ponytail Zero-Stress EOS prediction (a_0(U) = 5.9802 + 0.0210 * U)
3. New ISIF = 3 with LATTICE_CONSTRAINTS = .TRUE. .TRUE. .FALSE. (freed a,b, fixed c)
"""

import os
import math
import numpy as np

def parse_poscar_lattice(poscar_path):
    if not os.path.exists(poscar_path) or os.path.getsize(poscar_path) == 0:
        return None
    with open(poscar_path) as f:
        lines = [line.strip() for line in f if line.strip()]
    scale = float(lines[1])
    v1 = [float(x) * scale for x in lines[2].split()[:3]]
    v2 = [float(x) * scale for x in lines[3].split()[:3]]
    v3 = [float(x) * scale for x in lines[4].split()[:3]]
    
    a = math.sqrt(sum(x**2 for x in v1))
    b = math.sqrt(sum(x**2 for x in v2))
    c = math.sqrt(sum(x**2 for x in v3))
    
    dot_ab = sum(x*y for x, y in zip(v1, v2))
    gamma = math.degrees(math.acos(dot_ab / (a * b)))
    
    # Parse atoms and compute geometry
    species = lines[5].split()
    counts = [int(x) for x in lines[6].split()]
    is_direct = "d" in lines[7].lower() or "direct" in lines[7].lower()
    
    coords = []
    line_idx = 8
    total_atoms = sum(counts)
    for i in range(total_atoms):
        parts = [float(x) for x in lines[line_idx + i].split()[:3]]
        coords.append(parts)
        
    cr_coords = coords[:counts[0]]
    cl_coords = coords[counts[0]:counts[0]+counts[1]]
    
    cell_matrix = np.array([v1, v2, v3])
    if is_direct:
        cr_cart = np.dot(cr_coords, cell_matrix)
        cl_cart = np.dot(cl_coords, cell_matrix)
    else:
        cr_cart = np.array(cr_coords)
        cl_cart = np.array(cl_coords)
        
    # Vertical thickness d_z
    cr_z_mean = np.mean(cr_cart[:, 2])
    top_cl = cl_cart[cl_cart[:, 2] > cr_z_mean]
    bot_cl = cl_cart[cl_cart[:, 2] < cr_z_mean]
    d_z = np.mean(top_cl[:, 2]) - np.mean(bot_cl[:, 2])
    
    # Cr-Cl bond length (first coordination shell)
    cr0 = cr_cart[0]
    cr_cl_dists = []
    for cl in cl_cart:
        min_d = 1e9
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                disp = cl + dx * np.array(v1) + dy * np.array(v2) - cr0
                d = np.linalg.norm(disp)
                if d < min_d:
                    min_d = d
        if min_d < 2.6:
            cr_cl_dists.append(min_d)
            
    avg_bond = np.mean(cr_cl_dists) if cr_cl_dists else float('nan')
    
    return {
        "a": a, "b": b, "c": c, "gamma": gamma,
        "d_z": d_z, "d_Cr_Cl": avg_bond,
        "v1": v1, "v2": v2, "v3": v3
    }

def parse_outcar(outcar_path):
    if not os.path.exists(outcar_path) or os.path.getsize(outcar_path) == 0:
        return None
    toten = None
    stress = None
    timing = None
    n_ionic = 0
    with open(outcar_path, 'r', errors='ignore') as f:
        for line in f:
            if "free  energy   TOTEN" in line:
                parts = line.split()
                toten = float(parts[-2])
                n_ionic += 1
            if "in kB" in line:
                parts = line.split()
                try:
                    stress = [float(x) for x in parts[2:8]]
                except:
                    pass
            if "Elapsed time (sec):" in line:
                parts = line.split()
                timing = float(parts[-1])
            
    return {
        "toten": toten,
        "stress": stress,
        "n_ionic": n_ionic,
        "elapsed_sec": timing
    }

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ref_dir = os.path.dirname(base_dir)
    
    print("=" * 105)
    print(" 🔬 COMPREHENSIVE COMPARISON: ISIF=2 vs EOS vs ISIF=3 LATTICE_CONSTRAINTS")
    print("=" * 105)
    print(f"{'U (eV)':<6} | {'Method':<22} | {'a (A)':<8} | {'c (A)':<8} | {'gamma':<7} | {'d_z (A)':<8} | {'d(Cr-Cl)':<8} | {'E0 (eV)':<11} | {'sigma_xx (kB)':<12}")
    print("-" * 105)
    
    u_vals = [0, 4]
    for u in u_vals:
        # 1. ISIF=2 baseline
        ref_p = os.path.join(ref_dir, f"U_{u}", "CONTCAR")
        ref_o = os.path.join(ref_dir, f"U_{u}", "OUTCAR")
        ref_geom = parse_poscar_lattice(ref_p)
        ref_out = parse_outcar(ref_o)
        
        if ref_geom and ref_out:
            s_xx = f"{ref_out['stress'][0]:.1f}" if ref_out['stress'] else "N/A"
            print(f"{u:<6.1f} | {'ISIF=2 (fixed bulk a)':<22} | {ref_geom['a']:<8.4f} | {ref_geom['c']:<8.4f} | {ref_geom['gamma']:<7.2f} | {ref_geom['d_z']:<8.4f} | {ref_geom['d_Cr_Cl']:<8.4f} | {ref_out['toten']:<11.5f} | {s_xx:<12}")
            
        # 2. Ponytail Zero-Stress Prediction
        a_eos = 5.9802 + 0.0210 * u
        print(f"{u:<6.1f} | {'Ponytail Zero-Stress':<22} | {a_eos:<8.4f} | {17.6700:<8.4f} | {120.00:<7.2f} | {'-':<8} | {'-':<8} | {'-':<11} | {'0.0':<12}")
        
        # 3. New ISIF=3 LATTICE_CONSTRAINTS
        new_dir = os.path.join(base_dir, f"U_{u}")
        new_p = os.path.join(new_dir, "CONTCAR")
        scratch_p = f"/home/cr/scratch_vasp/test_isif3/U_{u}/CONTCAR"
        if (not os.path.exists(new_p) or os.path.getsize(new_p) == 0) and os.path.exists(scratch_p):
            new_p = scratch_p
            
        new_o = os.path.join(new_dir, "OUTCAR")
        scratch_o = f"/home/cr/scratch_vasp/test_isif3/U_{u}/OUTCAR"
        if (not os.path.exists(new_o) or os.path.getsize(new_o) == 0) and os.path.exists(scratch_o):
            new_o = scratch_o
                
        new_geom = parse_poscar_lattice(new_p)
        new_out = parse_outcar(new_o)
        
        if new_geom and new_out and new_out['toten'] is not None:
            s_xx = f"{new_out['stress'][0]:.1f}" if new_out['stress'] else "N/A"
            print(f"{u:<6.1f} | {'ISIF=3 LAT_CONSTR':<22} | {new_geom['a']:<8.4f} | {new_geom['c']:<8.4f} | {new_geom['gamma']:<7.2f} | {new_geom['d_z']:<8.4f} | {new_geom['d_Cr_Cl']:<8.4f} | {new_out['toten']:<11.5f} | {s_xx:<12}")
        else:
            print(f"{u:<6.1f} | {'ISIF=3 LAT_CONSTR':<22} | {'Running...':<8} | {'-':<8} | {'-':<7} | {'-':<8} | {'-':<8} | {'-':<11} | {'-':<12}")
        print("-" * 105)

if __name__ == "__main__":
    main()
