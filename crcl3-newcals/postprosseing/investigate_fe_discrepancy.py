#!/usr/bin/env python3
"""
investigate_fe_discrepancy.py

Exhaustive scientific investigation comparing Fe adsorption calculations across:
- Caique's Pure PBE / vdW baseline (past-dirs/doped-H/adsorbed/Fe and past-dirs/adsorbed/fe)
- Tier 2 (+U_Cr = 3.29 eV): crcl3-2x2-fe_ads-with-U/yes_vdw/ (S1, S2, S3)
- Tier 3 (+U_all = 3.29 eV on Cr & Fe): crcl3-2x2-CoFeNi-vdw12-U_all3.29/adsorbed/Fe/ (clean, H_ads)

Performs:
1. Exact atomic site identification (Which site did Fe sit on: S1 Top-Cl, S2 Hollow, S3 Top-Cr?)
2. Fe-H bond length and coordinates (Did H desorb or migrate to Cl?)
3. Fe-Cl and Fe-Cr coordination environment (distortion, penetration into pore, or surface protrusion?)
4. Total energy decomposition: E(substrate), E(substrate+H), 1/2 E(H2), dE_ads, dG_H*
5. Hubbard U and spin-state differences (Cr 3d vs Fe 3d U values, local magnetization, high-spin vs low-spin)
"""

import os
import sys
import numpy as np

def parse_poscar(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    if not lines:
        return None
    
    title = lines[0]
    scale = float(lines[1])
    lattice = np.array([[float(x) for x in lines[i].split()] for i in range(2, 5)]) * scale
    
    parts5 = lines[5].split()
    try:
        counts = [int(x) for x in parts5]
        species = title.split()
        coord_line_idx = 6
    except ValueError:
        species = parts5
        counts = [int(x) for x in lines[6].split()]
        coord_line_idx = 7
        
    mode = lines[coord_line_idx]
    if mode.lower().startswith('s'):
        coord_line_idx += 1
        mode = lines[coord_line_idx]
        
    is_direct = mode.lower().startswith('d') or mode.lower().startswith('direct')
    coord_start = coord_line_idx + 1
    total_atoms = sum(counts)
    atom_types = []
    for sp, cnt in zip(species, counts):
        atom_types.extend([sp] * cnt)
        
    coords = []
    for i in range(coord_start, coord_start + total_atoms):
        if i >= len(lines):
            break
        parts = lines[i].split()
        coords.append([float(parts[0]), float(parts[1]), float(parts[2])])
        
    coords = np.array(coords)
    cart_coords = np.dot(coords, lattice) if is_direct else coords
    frac_coords = coords if is_direct else np.dot(cart_coords, np.linalg.inv(lattice))
    
    return {
        'title': title,
        'lattice': lattice,
        'species': species,
        'counts': counts,
        'total_atoms': total_atoms,
        'atom_types': atom_types,
        'cart_coords': cart_coords,
        'frac_coords': frac_coords
    }

def get_min_pbc_dist(pos1, pos2, lattice):
    diff = pos1 - pos2
    inv_lat = np.linalg.inv(lattice)
    frac_diff = np.dot(diff, inv_lat)
    frac_diff -= np.round(frac_diff)
    return np.linalg.norm(np.dot(frac_diff, lattice))

def analyze_system(dir_path, name):
    print("\n" + "="*85)
    print(f"  SYSTEM: {name}")
    print(f"  Directory: {dir_path}")
    print("="*85)
    
    if not os.path.exists(dir_path):
        print("  [ERROR] Directory not found!")
        return None
        
    # Read INCAR
    incar_p = os.path.join(dir_path, 'INCAR')
    incar_tags = {}
    if os.path.exists(incar_p):
        with open(incar_p, 'r') as f:
            for l in f:
                l_strip = l.strip()
                if l_strip and not l_strip.startswith('#') and '=' in l_strip:
                    k, v = l_strip.split('=', 1)
                    incar_tags[k.strip().upper()] = v.split('#')[0].strip()
                    
    print("  [INCAR Parameters]")
    print(f"    LDAU   = {incar_tags.get('LDAU', 'Default (False)')}")
    print(f"    LDAUL  = {incar_tags.get('LDAUL', 'None')}")
    print(f"    LDAUU  = {incar_tags.get('LDAUU', 'None')}")
    print(f"    MAGMOM = {incar_tags.get('MAGMOM', 'None')}")
    print(f"    IVDW   = {incar_tags.get('IVDW', '0 (No vdW)')}")
    print(f"    ENCUT  = {incar_tags.get('ENCUT', 'Default')} eV")
    
    # Read CONTCAR or POSCAR
    cont_p = os.path.join(dir_path, 'CONTCAR')
    pos_p = os.path.join(dir_path, 'POSCAR')
    st = parse_poscar(cont_p) if (os.path.exists(cont_p) and os.path.getsize(cont_p) > 50) else parse_poscar(pos_p)
    
    if not st:
        print("  [ERROR] No structure file found!")
        return None
        
    types = st['atom_types']
    coords = st['cart_coords']
    lat = st['lattice']
    
    fe_indices = [i for i, t in enumerate(types) if t.lower() == 'fe']
    h_indices  = [i for i, t in enumerate(types) if t.lower() == 'h']
    cr_indices = [i for i, t in enumerate(types) if t.lower() == 'cr']
    cl_indices = [i for i, t in enumerate(types) if t.lower() == 'cl']
    
    print(f"\n  [Composition] Formula: {st['species']} = {st['counts']} (Total {st['total_atoms']} atoms)")
    
    # Parse Energy and Magnetization
    e0 = None
    mag = None
    osz_p = os.path.join(dir_path, 'OSZICAR')
    if os.path.exists(osz_p):
        with open(osz_p, 'r') as f:
            for l in reversed(f.readlines()):
                if 'E0=' in l:
                    parts = l.split()
                    for idx, p in enumerate(parts):
                        if p.startswith('E0='):
                            e0 = float(parts[idx+1] if p == 'E0=' else p.split('=')[1])
                        if p.startswith('mag='):
                            mag = float(parts[idx+1] if p == 'mag=' else p.split('=')[1])
                    break
                    
    out_p = os.path.join(dir_path, 'OUTCAR')
    converged = False
    fe_local_mag = None
    h_local_mag = None
    if os.path.exists(out_p):
        with open(out_p, 'r', errors='ignore') as f:
            out_lines = f.readlines()
        converged = any('reached required accuracy' in l for l in out_lines)
        
        # Parse local magnetic moments
        mag_table = False
        atom_mags = []
        for l in reversed(out_lines):
            if 'magnetization (x)' in l or 'total and magnetization' in l:
                mag_table = True
                continue
            if mag_table:
                if 'ion' in l:
                    break
                p = l.split()
                if len(p) >= 5 and p[0].isdigit():
                    try:
                        atom_mags.append((int(p[0]), float(p[4])))
                    except ValueError:
                        pass
        atom_mags.reverse()
        if atom_mags and fe_indices:
            fe_local_mag = atom_mags[fe_indices[0]][1] if fe_indices[0] < len(atom_mags) else None
        if atom_mags and h_indices:
            h_local_mag = atom_mags[h_indices[0]][1] if h_indices[0] < len(atom_mags) else None
            
    print(f"\n  [Electronic & Magnetic Ground State]")
    print(f"    E0 (Ground Energy)  = {e0:.6f} eV" if e0 is not None else "    E0 = N/A")
    print(f"    Total Magnetization = {mag:.3f} mu_B" if mag is not None else "    Total Mag = N/A")
    print(f"    Fe Local Moment     = {fe_local_mag:.3f} mu_B" if fe_local_mag is not None else "    Fe Local Mag = N/A")
    print(f"    H Local Moment      = {h_local_mag:.3f} mu_B" if h_local_mag is not None else "    H Local Mag = N/A")
    print(f"    VASP Converged      = {converged}")
    
    # Geometric Coordinates and Site Diagnostics
    if fe_indices:
        fe_pos = coords[fe_indices[0]]
        fe_frac = st['frac_coords'][fe_indices[0]]
        cl_z = [coords[ci][2] for ci in cl_indices]
        cr_z = [coords[cri][2] for cri in cr_indices]
        top_cl_z = np.mean([z for z in cl_z if z > np.median(cl_z)])
        mid_cr_z = np.mean(cr_z)
        
        # Distances to nearest atoms
        cl_dists = sorted([get_min_pbc_dist(fe_pos, coords[ci], lat) for ci in cl_indices])
        cr_dists = sorted([get_min_pbc_dist(fe_pos, coords[cri], lat) for cri in cr_indices])
        
        print(f"\n  [Fe Coordination & Site Geometry]")
        print(f"    Fe Direct (Frac):  [{fe_frac[0]:.4f}, {fe_frac[1]:.4f}, {fe_frac[2]:.4f}]")
        print(f"    Fe Cart (x,y,z):   [{fe_pos[0]:.3f}, {fe_pos[1]:.3f}, {fe_pos[2]:.3f}] A")
        print(f"    Fe-Cl nearest (3): {cl_dists[:3]} A")
        print(f"    Fe-Cr nearest (3): {cr_dists[:3]} A")
        print(f"    Fe Height above top Cl layer: {fe_pos[2] - top_cl_z:+.3f} A")
        print(f"    Fe Height relative to Cr layer: {fe_pos[2] - mid_cr_z:+.3f} A")
        
        # Determine Site Classification:
        if abs(fe_pos[2] - mid_cr_z) < 1.0:
            site_name = "Embedded (Pore / in-plane hollow)"
        elif cr_dists[0] < 2.7:
            site_name = "S3 (Top-Cr surface site)"
        elif cl_dists[0] < 2.3:
            site_name = "S1 (Top-Cl surface site)"
        else:
            site_name = "S2 (Hollow above surface)"
        print(f"    => SITE IDENTIFICATION: {site_name}")
        
    if h_indices:
        h_pos = coords[h_indices[0]]
        h_frac = st['frac_coords'][h_indices[0]]
        print(f"\n  [Hydrogen (H) Adsorption Diagnostics]")
        print(f"    H Direct (Frac):   [{h_frac[0]:.4f}, {h_frac[1]:.4f}, {h_frac[2]:.4f}]")
        print(f"    H Cart (x,y,z):    [{h_pos[0]:.3f}, {h_pos[1]:.3f}, {h_pos[2]:.3f}] A")
        
        if fe_indices:
            fe_h = get_min_pbc_dist(fe_pos, h_pos, lat)
            print(f"    *** d(Fe - H) = {fe_h:.4f} A ***")
            if fe_h < 1.75:
                print("    -> Physical Status: CHEMICALLY BOUND to Fe (Fe-H covalent single bond)")
            elif fe_h < 2.5:
                print("    -> Physical Status: WEAK INTERACTION / TRANSITION STATE")
            else:
                print("    -> Physical Status: DESORBED / DETACHED INTO VACUUM (d > 2.5 A)")
                
        h_cl = sorted([get_min_pbc_dist(h_pos, coords[ci], lat) for ci in cl_indices])
        print(f"    d(H - Cl) nearest 3: {h_cl[:3]} A")
        if h_cl[0] < 1.4:
            print("    *** WARNING: H HAS TRANSFERRED TO FORM HCl ON SUBSTRATE! ***")
            
    return {
        'name': name,
        'e0': e0,
        'mag': mag,
        'fe_local_mag': fe_local_mag,
        'converged': converged,
        'has_h': len(h_indices) > 0,
        'fe_h_dist': get_min_pbc_dist(fe_pos, h_pos, lat) if (fe_indices and h_indices) else None,
        'fe_cl_dist': cl_dists[0] if fe_indices else None,
        'fe_cr_dist': cr_dists[0] if fe_indices else None,
        'fe_z_rel': fe_pos[2] - top_cl_z if fe_indices else None
    }

def main():
    print("="*85)
    print("   CRCL3-FE ADSORPTION FORENSIC AUDIT: TIER 1 vs TIER 2 vs TIER 3")
    print("="*85)
    
    calcs = [
        # Past Caique Reference (Tier 1: Pure PBE)
        ('/home/cr/simulations/crcl3-HER/past-dirs/adsorbed/fe', 'Caique Past Fe_ads Clean (Pure PBE)'),
        ('/home/cr/simulations/crcl3-HER/past-dirs/doped-H/adsorbed/Fe', 'Caique Past Fe_ads + H (Pure PBE)'),
        
        # Tier 2 (+U_Cr only, U_Fe=0)
        ('/home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-fe_ads-with-U/yes_vdw/clean', 'Tier 2 (+U_Cr) Substrate Baseline (Clean CrCl3)'),
        ('/home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-fe_ads-with-U/yes_vdw/S1', 'Tier 2 (+U_Cr) Fe_ads S1 (Site 1 Clean)'),
        ('/home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-fe_ads-with-U/yes_vdw/S2', 'Tier 2 (+U_Cr) Fe_ads S2 (Site 2 Clean)'),
        ('/home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-fe_ads-with-U/yes_vdw/S3', 'Tier 2 (+U_Cr) Fe_ads S3 (Site 3 Clean)'),
        
        # Tier 3 (+U_all: U_Cr=3.29, U_Fe=3.29)
        ('/home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/adsorbed/Fe/clean', 'Tier 3 (+U_all) Fe_ads Clean (New Suite)'),
        ('/home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/adsorbed/Fe/H_ads', 'Tier 3 (+U_all) Fe_ads + H (New Suite)'),
        
        # Embedded Fe for comparison
        ('/home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/embedded/Fe/clean', 'Tier 3 (+U_all) Fe_emb Clean'),
        ('/home/cr/simulations/crcl3-HER/crcl3-newcals/crcl3-2x2-CoFeNi-vdw12-U_all3.29/embedded/Fe/H_ads', 'Tier 3 (+U_all) Fe_emb + H'),
    ]
    
    results = {}
    for p, n in calcs:
        r = analyze_system(p, n)
        if r:
            results[n] = r
            
    print("\n" + "="*85)
    print("   THERMODYNAMIC COMPARATIVE SUMMARY & RECONCILIATION")
    print("="*85)
    
    # 1/2 E(H2) references
    e_h2_half = -3.3857 # from standard benchmark (-6.7714 / 2)
    corr = 0.18 # Caique Fe ZPE-TdS correction
    
    # Caique Past PBE:
    e_past_cln = results.get('Caique Past Fe_ads Clean (Pure PBE)', {}).get('e0')
    e_past_h   = results.get('Caique Past Fe_ads + H (Pure PBE)', {}).get('e0')
    if e_past_cln and e_past_h:
        eads_past = e_past_h - e_past_cln - (-3.3798)
        dg_past = eads_past + corr
        print(f"1. Caique Pure PBE: E_cln={e_past_cln:.3f}, E_H={e_past_h:.3f} => E_ads={eads_past:+.3f} eV, dG={dg_past:+.3f} eV")
        
    # Tier 3:
    e_t3_cln = results.get('Tier 3 (+U_all) Fe_ads Clean (New Suite)', {}).get('e0')
    e_t3_h   = results.get('Tier 3 (+U_all) Fe_ads + H (New Suite)', {}).get('e0')
    if e_t3_cln and e_t3_h:
        eads_t3 = e_t3_h - e_t3_cln - e_h2_half
        dg_t3 = eads_t3 + 0.256 # standard correction or corr
        print(f"2. Tier 3 (+U_all): E_cln={e_t3_cln:.3f}, E_H={e_t3_h:.3f} => E_ads={eads_t3:+.3f} eV, dG={dg_t3:+.3f} eV (with +0.256 eV corr)")
        print(f"   Tier 3 (+U_all) with Caique corr (+0.18 eV): dG = {eads_t3 + 0.18:+.3f} eV")
        
    # Tier 2 Analysis:
    print("\n3. Tier 2 (+U_Cr) Investigation:")
    e_t2_s1 = results.get('Tier 2 (+U_Cr) Fe_ads S1 (Site 1 Clean)', {}).get('e0')
    e_t2_s3 = results.get('Tier 2 (+U_Cr) Fe_ads S3 (Site 3 Clean)', {}).get('e0')
    print(f"   Tier 2 Fe_ads S1 (Clean): E0 = {e_t2_s1} eV")
    print(f"   Tier 2 Fe_ads S3 (Clean): E0 = {e_t2_s3} eV")
    print("   Note: Tier 2 (+U_Cr) lacked an explicit relaxed Fe_ads + H calculation!")

if __name__ == '__main__':
    main()
