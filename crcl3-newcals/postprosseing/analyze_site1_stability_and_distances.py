#!/usr/bin/env python3
"""
analyze_site1_stability_and_distances.py

Quantitative analysis of Site 1 (Top-Cl) across:
1. Hydrogen Adsorption: 1x1, 2x2, 3x3 supercells under 3 dispersion treatments:
   - Pure PBE (no_vdw)
   - PBE+D3 Zero-damping (yes_vdw)
   - PBE+D3 Becke-Johnson (yes_vdw_ivdw12)
2. Transition Metal Adsorption: 2x2 supercell for Co, Fe, Ni under Pure PBE and PBE+D3 (BJ).

Extracts:
- Direct bond distances to nearest substrate atoms.
- Verification of desorption vs chemisorption.
- Relaxation displacements from nominal initial coordinates.
- Final binding and adsorption energies.
"""

import os
import sys
import numpy as np
from ase.io import read

BASE_DIR = "/home/cr/simulations/crcl3-HER/crcl3-newcals"

def analyze_h_site1():
    print("=" * 80)
    print("PART 1: HYDROGEN ADSORPTION AT SITE 1 (Top-Cl) ACROSS 1x1, 2x2, 3x3 SUPERCELLS")
    print("=" * 80)
    
    supercells = ["1x1", "2x2", "3x3"]
    methods = [
        ("no_vdw", "Pure PBE"),
        ("yes_vdw", "PBE+D3(Zero)"),
        ("yes_vdw_ivdw12", "PBE+D3(BJ)"),
    ]
    
    results = []
    for sc in supercells:
        for m_dir, m_label in methods:
            contcar_path = os.path.join(BASE_DIR, f"crcl3-{sc}-h_ads-without-U", m_dir, "S1", "CONTCAR")
            outcar_path = os.path.join(BASE_DIR, f"crcl3-{sc}-h_ads-without-U", m_dir, "S1", "OUTCAR")
            
            if not os.path.exists(contcar_path):
                continue
                
            atoms = read(contcar_path)
            # H atom is the last atom
            h_idx = len(atoms) - 1
            h_pos = atoms.positions[h_idx]
            
            # Find distances to all Cl atoms
            cl_indices = [i for i, a in enumerate(atoms) if a.symbol == "Cl"]
            distances = []
            for cl_i in cl_indices:
                d = atoms.get_distance(h_idx, cl_i, mic=True)
                distances.append((d, cl_i))
            distances.sort()
            
            closest_d, closest_cl = distances[0]
            second_d, second_cl = distances[1]
            
            # Energy from OUTCAR
            e_tot = None
            if os.path.exists(outcar_path):
                with open(outcar_path, "r") as f:
                    for line in reversed(f.readlines()[-200:]):
                        if "free  energy   TOTEN" in line:
                            e_tot = float(line.split()[4])
                            break
            
            status = "CHEMISORBED (Covalent H-Cl)" if closest_d < 1.6 else "DESORBED"
            results.append({
                "supercell": sc,
                "method": m_label,
                "closest_d": closest_d,
                "second_d": second_d,
                "closest_cl": closest_cl,
                "e_tot": e_tot,
                "status": status
            })
            
            e_str = f"{e_tot:11.4f} eV" if e_tot is not None else "    N/A    "
            print(f"[{sc}] {m_label:15s} | d(H-Cl_{closest_cl}) = {closest_d:6.3f} Å | d(H-Cl_{second_cl}) = {second_d:6.3f} Å | E_tot = {e_str} | {status}")
            
    return results

def analyze_tm_site1():
    print("\n" + "=" * 80)
    print("PART 2: TRANSITION METAL (Co, Fe, Ni) ADSORPTION AT SITE 1 (Top-Cl) (2x2 SUPERCELL)")
    print("=" * 80)
    
    tms = [
        ("co", "Cobalt (Co)"),
        ("fe", "Iron (Fe)"),
        ("ni", "Nickel (Ni)")
    ]
    methods = [
        ("no_vdw", "Pure PBE"),
        ("yes_vdw", "PBE+D3(BJ)")
    ]
    
    results = []
    for tm_symbol, tm_name in tms:
        for m_dir, m_label in methods:
            contcar_path = os.path.join(BASE_DIR, f"crcl3-2x2-{tm_symbol}_ads-without-U", m_dir, "S1", "CONTCAR")
            outcar_path = os.path.join(BASE_DIR, f"crcl3-2x2-{tm_symbol}_ads-without-U", m_dir, "S1", "OUTCAR")
            poscar_path = os.path.join(BASE_DIR, f"crcl3-2x2-{tm_symbol}_ads-without-U", m_dir, "S1", "POSCAR")
            
            if not os.path.exists(contcar_path):
                print(f"[{tm_name}] {m_label:15s} | CONTCAR not found (Calculation pending)")
                continue
                
            atoms = read(contcar_path)
            tm_idx = len(atoms) - 1 # TM is last atom
            tm_pos = atoms.positions[tm_idx]
            
            # Initial displacement from POSCAR
            disp = None
            if os.path.exists(poscar_path):
                init_atoms = read(poscar_path)
                disp = np.linalg.norm(atoms.positions[tm_idx] - init_atoms.positions[tm_idx])
            
            # Nearest Cl atoms
            cl_indices = [i for i, a in enumerate(atoms) if a.symbol == "Cl"]
            distances_cl = []
            for cl_i in cl_indices:
                d = atoms.get_distance(tm_idx, cl_i, mic=True)
                distances_cl.append((d, cl_i))
            distances_cl.sort()
            
            # Nearest Cr atoms
            cr_indices = [i for i, a in enumerate(atoms) if a.symbol == "Cr"]
            distances_cr = []
            for cr_i in cr_indices:
                d = atoms.get_distance(tm_idx, cr_i, mic=True)
                distances_cr.append((d, cr_i))
            distances_cr.sort()
            
            # Energy from OUTCAR
            e_tot = None
            if os.path.exists(outcar_path):
                with open(outcar_path, "r") as f:
                    for line in reversed(f.readlines()[-200:]):
                        if "free  energy   TOTEN" in line:
                            e_tot = float(line.split()[4])
                            break
            
            # Coordination count within 2.5 Å
            coord_cl = [d for d, _ in distances_cl if d < 2.5]
            
            # Determine structural fate
            # S1 is top of Cl11 (atom 19)
            # S2 hollow is coordinated to 3 Cl atoms at ~2.2-2.3 Å and equidistant from 3 Cr atoms
            if len(coord_cl) == 3 and abs(coord_cl[0] - coord_cl[2]) < 0.15:
                fate = "SLID TO HOLLOW (3-fold symmetric S2)"
            elif len(coord_cl) >= 3:
                fate = f"DISTORTED 3-FOLD ({coord_cl[0]:.2f}, {coord_cl[1]:.2f}, {coord_cl[2]:.2f} Å)"
            elif len(coord_cl) == 1:
                fate = "1-FOLD ON TOP-Cl"
            else:
                fate = f"COORDINATION {len(coord_cl)}"
                
            status = "BOUND TO SURFACE" if distances_cl[0][0] < 2.5 else "DESORBED"
            
            print(f"[{tm_name:12s}] {m_label:12s} | Disp: {disp:5.2f} Å | Cl-bonds: {[round(x, 2) for x in coord_cl]} Å | Nearest Cr: {distances_cr[0][0]:.2f} Å | E: {e_tot:.3f} eV | {fate}")
            
    return results

def analyze_co_with_u():
    import re
    print("\n" + "=" * 80)
    print("PART 3: COBALT (Co) ADSORPTION WITH HUBBARD U = 3.29 eV (SITE 1 vs SITE 3)")
    print("=" * 80)
    
    sites = [
        ("S1", "Site 1 (Top-Cl)"),
        ("S3", "Site 3 (Top-Cr)")
    ]
    
    clean_oszicar = os.path.join(BASE_DIR, "crcl3-2x2-co_ads-with-U", "yes_vdw", "clean", "OSZICAR")
    e_clean = None
    if os.path.exists(clean_oszicar):
        with open(clean_oszicar, "r") as f:
            for line in f:
                if "E0=" in line:
                    m = re.search(r'E0=\s*([^\s]+)', line)
                    if m:
                        e_clean = float(m.group(1))
                        
    for s_key, s_name in sites:
        site_dir = os.path.join(BASE_DIR, "crcl3-2x2-co_ads-with-U", "yes_vdw", s_key)
        contcar_path = os.path.join(site_dir, "CONTCAR")
        outcar_path = os.path.join(site_dir, "OUTCAR")
        poscar_path = os.path.join(site_dir, "POSCAR")
        oszicar_path = os.path.join(site_dir, "OSZICAR")
        
        if not os.path.exists(contcar_path):
            print(f"[{s_name:18s}] CONTCAR not found")
            continue
            
        atoms = read(contcar_path)
        co_idx = len(atoms) - 1 # Co is last atom
        
        # Initial displacement from POSCAR
        disp = None
        if os.path.exists(poscar_path):
            init_atoms = read(poscar_path)
            disp = np.linalg.norm(atoms.positions[co_idx] - init_atoms.positions[co_idx])
            
        # Nearest Cl atoms
        cl_indices = [i for i, a in enumerate(atoms) if a.symbol == "Cl"]
        distances_cl = []
        for cl_i in cl_indices:
            d = atoms.get_distance(co_idx, cl_i, mic=True)
            distances_cl.append((d, cl_i))
        distances_cl.sort()
        
        # Nearest Cr atoms
        cr_indices = [i for i, a in enumerate(atoms) if a.symbol == "Cr"]
        distances_cr = []
        for cr_i in cr_indices:
            d = atoms.get_distance(co_idx, cr_i, mic=True)
            distances_cr.append((d, cr_i))
        distances_cr.sort()
        
        # Energy & Mag from OSZICAR
        e_tot = None
        mag = None
        if os.path.exists(oszicar_path):
            with open(oszicar_path, "r") as f:
                for line in f:
                    if "E0=" in line:
                        m = re.search(r'E0=\s*([^\s]+)', line)
                        mag_m = re.search(r'mag=\s*([^\s]+)', line)
                        if m:
                            e_tot = float(m.group(1))
                        if mag_m:
                            mag = float(mag_m.group(1))
                            
        delta_e = (e_tot - e_clean) if (e_tot and e_clean) else None
        delta_str = f"{delta_e:.3f} eV" if delta_e is not None else "N/A"
        
        coord_cl = [d for d, _ in distances_cl if d < 2.5]
        status = "BOUND TO SURFACE" if distances_cl[0][0] < 2.5 else "DESORBED"
        mag_str = f"{mag:.2f} muB" if mag is not None else "N/A"
        print(f"[{s_name:18s}] Disp: {disp:5.2f} Å | Cl-bonds: {[round(x, 2) for x in coord_cl]} Å | Nearest Cr: {distances_cr[0][0]:.2f} Å | E_tot: {e_tot:.3f} eV | Delta_E: {delta_str} | Mag: {mag_str} | {status}")

if __name__ == "__main__":
    analyze_h_site1()
    analyze_tm_site1()
    analyze_co_with_u()
