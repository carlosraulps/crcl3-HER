#!/usr/bin/env python3
"""
analyze_lattice_and_forces.py
=============================
Author: Antigravity Assistant
Purpose: Analyze real-space and reciprocal-space lattice vectors,
         stress tensors, and atomic displacements (with minimum image convention)
         for all converged and running calculations in crcl3-1x1, 2x2, 3x3.
"""

import os
import sys
import math
import glob

def dot(u, v):
    return sum(x*y for x, y in zip(u, v))

def cross(u, v):
    return [
        u[1]*v[2] - u[2]*v[1],
        u[2]*v[0] - u[0]*v[2],
        u[0]*v[1] - u[1]*v[0]
    ]

def norm(v):
    return math.sqrt(dot(v, v))

def angle(u, v):
    denom = norm(u) * norm(v)
    if denom < 1e-12:
        return 0.0
    cos_val = max(-1.0, min(1.0, dot(u, v) / denom))
    return math.degrees(math.acos(cos_val))

def cell_volume(a1, a2, a3):
    return abs(dot(a1, cross(a2, a3)))

def reciprocal_vectors(a1, a2, a3):
    V = dot(a1, cross(a2, a3))
    if abs(V) < 1e-12:
        return [0,0,0], [0,0,0], [0,0,0], 0.0
    b1 = [2.0 * math.pi * x / V for x in cross(a2, a3)]
    b2 = [2.0 * math.pi * x / V for x in cross(a3, a1)]
    b3 = [2.0 * math.pi * x / V for x in cross(a1, a2)]
    return b1, b2, b3, abs(V)

def parse_poscar(filepath):
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return None
    with open(filepath, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    if len(lines) < 8:
        return None
    comment = lines[0]
    scale = float(lines[1])
    a1 = [float(x) * scale for x in lines[2].split()[:3]]
    a2 = [float(x) * scale for x in lines[3].split()[:3]]
    a3 = [float(x) * scale for x in lines[4].split()[:3]]
    
    line5_parts = lines[5].split()
    if line5_parts[0].isalpha():
        species = line5_parts
        counts = [int(x) for x in lines[6].split()]
        coord_start = 7
    else:
        species = ['Cr', 'Cl', 'H']
        counts = [int(x) for x in line5_parts]
        coord_start = 6

    is_selective = False
    if 'select' in lines[coord_start].lower():
        is_selective = True
        coord_start += 1
    
    coord_type = lines[coord_start].lower()
    coord_start += 1
    is_direct = ('dir' in coord_type)
    
    total_atoms = sum(counts)
    atom_types = []
    for sp, cnt in zip(species, counts):
        atom_types.extend([sp] * cnt)
        
    direct_coords = []
    cart_coords = []
    for i in range(total_atoms):
        idx = coord_start + i
        if idx >= len(lines):
            break
        parts = lines[idx].split()
        if len(parts) >= 3:
            u, v, w = float(parts[0]), float(parts[1]), float(parts[2])
            if is_direct:
                direct_coords.append((u, v, w))
                rx = u*a1[0] + v*a2[0] + w*a3[0]
                ry = u*a1[1] + v*a2[1] + w*a3[1]
                rz = u*a1[2] + v*a2[2] + w*a3[2]
                cart_coords.append((rx, ry, rz))
            else:
                cart_coords.append((u*scale, v*scale, w*scale))
                direct_coords.append((u, v, w))
            
    return {
        'comment': comment,
        'a1': a1, 'a2': a2, 'a3': a3,
        'species': species,
        'counts': counts,
        'atom_types': atom_types,
        'direct_coords': direct_coords,
        'cart_coords': cart_coords
    }

def parse_outcar(filepath):
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return None
    stress = None
    ext_pressure = None
    energy = None
    mag = None
    max_force = None
    n_ionic_steps = 0
    is_converged = False
    
    with open(filepath, 'r', errors='ignore') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if 'reached required accuracy - stopping structural energy minimisation' in line:
            is_converged = True
        if 'in kB' in line:
            parts = line.split()
            if len(parts) >= 7:
                try:
                    stress = [float(p) for p in parts[2:8]]
                except:
                    pass
        if 'external pressure =' in line:
            parts = line.split()
            try:
                ext_pressure = float(parts[3])
            except:
                pass
        if 'free  energy   TOTEN' in line:
            n_ionic_steps += 1
            parts = line.split()
            try:
                energy = float(parts[4])
            except:
                pass
        if 'number of electron ' in line and 'magnetization' in line:
            parts = line.split()
            try:
                mag = float(parts[-1])
            except:
                pass
        if 'POSITION                                       TOTAL-FORCE (eV/Angst)' in line:
            forces = []
            j = i + 2
            while j < len(lines):
                fl = lines[j].strip()
                if '---' in fl:
                    break
                p = fl.split()
                if len(p) >= 6:
                    fx, fy, fz = float(p[3]), float(p[4]), float(p[5])
                    forces.append(math.sqrt(fx*fx + fy*fy + fz*fz))
                j += 1
            if forces:
                max_force = max(forces)
                
    return {
        'stress': stress,
        'ext_pressure': ext_pressure,
        'energy': energy,
        'mag': mag,
        'max_force': max_force,
        'n_ionic_steps': n_ionic_steps,
        'is_converged': is_converged
    }

def analyze_system(dirpath):
    poscar_path = os.path.join(dirpath, 'POSCAR')
    contcar_path = os.path.join(dirpath, 'CONTCAR')
    outcar_path = os.path.join(dirpath, 'OUTCAR')
    
    pos = parse_poscar(poscar_path)
    if not pos:
        return None
    
    cont = parse_poscar(contcar_path)
    out = parse_outcar(outcar_path)
    
    a1, a2, a3 = pos['a1'], pos['a2'], pos['a3']
    a_len, b_len, c_len = norm(a1), norm(a2), norm(a3)
    alpha = angle(a2, a3)
    beta  = angle(a1, a3)
    gamma = angle(a1, a2)
    V_real = cell_volume(a1, a2, a3)
    
    b1, b2, b3, _ = reciprocal_vectors(a1, a2, a3)
    b1_len, b2_len, b3_len = norm(b1), norm(b2), norm(b3)
    b_alpha = angle(b2, b3)
    b_beta  = angle(b1, b3)
    b_gamma = angle(b1, b2)
    
    delta_a, delta_b, delta_c = 0.0, 0.0, 0.0
    delta_V = 0.0
    delta_b1, delta_b2, delta_b3 = 0.0, 0.0, 0.0
    max_disp = 0.0
    h_info = None
    
    if cont and cont['cart_coords']:
        ca1, ca2, ca3 = cont['a1'], cont['a2'], cont['a3']
        ca_len, cb_len, cc_len = norm(ca1), norm(ca2), norm(ca3)
        cV = cell_volume(ca1, ca2, ca3)
        delta_a = ca_len - a_len
        delta_b = cb_len - b_len
        delta_c = cc_len - c_len
        delta_V = cV - V_real
        
        cb1, cb2, cb3, _ = reciprocal_vectors(ca1, ca2, ca3)
        delta_b1 = norm(cb1) - b1_len
        delta_b2 = norm(cb2) - b2_len
        delta_b3 = norm(cb3) - b3_len
        
        min_len = min(len(pos['direct_coords']), len(cont['direct_coords']))
        disps = []
        for i in range(min_len):
            pu, pv, pw = pos['direct_coords'][i]
            cu, cv, cw = cont['direct_coords'][i]
            du = cu - pu
            du -= round(du)
            dv = cv - pv
            dv -= round(dv)
            dw = cw - pw
            dw -= round(dw)
            dx = du*a1[0] + dv*a2[0] + dw*a3[0]
            dy = du*a1[1] + dv*a2[1] + dw*a3[1]
            dz = du*a1[2] + dv*a2[2] + dw*a3[2]
            d = math.sqrt(dx*dx + dy*dy + dz*dz)
            disps.append(d)
            if pos['atom_types'][i] == 'H':
                c_cart = cont['cart_coords'][i]
                min_cr_dist = 999.0
                min_cl_dist = 999.0
                for j in range(min_len):
                    if j == i:
                        continue
                    cj_cart = cont['cart_coords'][j]
                    # minimum image distance
                    t_du = cont['direct_coords'][j][0] - cu
                    t_du -= round(t_du)
                    t_dv = cont['direct_coords'][j][1] - cv
                    t_dv -= round(t_dv)
                    t_dw = cont['direct_coords'][j][2] - cw
                    t_dw -= round(t_dw)
                    tdx = t_du*a1[0] + t_dv*a2[0] + t_dw*a3[0]
                    tdy = t_du*a1[1] + t_dv*a2[1] + t_dw*a3[1]
                    tdz = t_du*a1[2] + t_dv*a2[2] + t_dw*a3[2]
                    dist = math.sqrt(tdx*tdx + tdy*tdy + tdz*tdz)
                    if pos['atom_types'][j] == 'Cr' and dist < min_cr_dist:
                        min_cr_dist = dist
                    elif pos['atom_types'][j] == 'Cl' and dist < min_cl_dist:
                        min_cl_dist = dist
                h_info = {
                    'delta_xyz': (dx, dy, dz),
                    'delta_norm': d,
                    'delta_z': dz,
                    'd_Cr': min_cr_dist,
                    'd_Cl': min_cl_dist
                }
        if disps:
            max_disp = max(disps)
            
    return {
        'dir': dirpath,
        'a_len': a_len, 'b_len': b_len, 'c_len': c_len,
        'alpha': alpha, 'beta': beta, 'gamma': gamma,
        'V_real': V_real,
        'b1_len': b1_len, 'b2_len': b2_len, 'b3_len': b3_len,
        'b_alpha': b_alpha, 'b_beta': b_beta, 'b_gamma': b_gamma,
        'delta_a': delta_a, 'delta_b': delta_b, 'delta_c': delta_c,
        'delta_V': delta_V,
        'delta_b1': delta_b1, 'delta_b2': delta_b2, 'delta_b3': delta_b3,
        'max_disp': max_disp,
        'h_info': h_info,
        'outcar': out
    }

def main():
    base_dirs = [
        '/home/juan/Carlos/crcl3-1x1-h_ads-without-U',
        '/home/juan/Carlos/crcl3-2x2-h_ads-without-U'
    ]
    
    results = []
    for b in base_dirs:
        if not os.path.exists(b):
            continue
        for v in ['no_vdw', 'yes_vdw']:
            v_dir = os.path.join(b, v)
            if not os.path.exists(v_dir):
                continue
            for s in ['clean', 'S1', 'S2', 'S3']:
                s_dir = os.path.join(v_dir, s)
                if os.path.exists(s_dir):
                    data = analyze_system(s_dir)
                    if data:
                        results.append((b, v, s, data))
                        
    print("="*124)
    print(f"{'CRCL3 LATTICE PARAMETERS, RECIPROCAL LATTICE & RELAXATION AUDIT':^124}")
    print("="*124)
    print(f"{'Cell / Variant / Site':<28} | {'Real a, b, c (A)':<18} | {'Recip |b1|,|b2|,|b3| (1/A)':<24} | {'ISIF=2 dL (A)':<16} | {'P (kB)':<8} | {'Fmax (eV/A)':<11} | {'Status'}")
    print("-" * 124)
    
    for b, v, s, d in results:
        cell_label = "1x1" if "1x1" in b else "2x2"
        tag = f"{cell_label} {v} {s}"
        real_str = f"{d['a_len']:.3f}, {d['b_len']:.3f}, {d['c_len']:.1f}"
        recip_str = f"{d['b1_len']:.4f}, {d['b2_len']:.4f}, {d['b3_len']:.4f}"
        dl_str = f"{d['delta_a']:+.1e}, {d['delta_b']:+.1e}"
        
        p_str = "--"
        f_str = "--"
        status = "PENDING"
        if d['outcar']:
            if d['outcar']['ext_pressure'] is not None:
                p_str = f"{d['outcar']['ext_pressure']:+.2f}"
            if d['outcar']['max_force'] is not None:
                f_str = f"{d['outcar']['max_force']:.4f}"
            if d['outcar']['is_converged']:
                status = "CONVERGED"
            elif d['outcar']['n_ionic_steps'] > 0:
                status = f"RUN (Step {d['outcar']['n_ionic_steps']})"
            else:
                status = "RUN (Step 1 SCF)"
        print(f"{tag:<28} | {real_str:<18} | {recip_str:<24} | {dl_str:<16} | {p_str:<8} | {f_str:<11} | {status}")
        
    print("\n" + "="*124)
    print(f"{'HYDROGEN ADSORPTION & ATOMIC RELAXATION DETAILS (MINIMUM IMAGE CONVENTION)':^124}")
    print("="*124)
    print(f"{'Cell / Variant / Site':<28} | {'MaxDisp (A)':<12} | {'H Disp (A)':<12} | {'H dz (A)':<12} | {'d(Cr-H) (A)':<12} | {'d(Cl-H) (A)':<12}")
    print("-" * 124)
    for b, v, s, d in results:
        if s == 'clean':
            continue
        cell_label = "1x1" if "1x1" in b else "2x2"
        tag = f"{cell_label} {v} {s}"
        max_d_str = f"{d['max_disp']:.4f}" if d['max_disp'] > 0 else "--"
        h = d['h_info']
        if h:
            h_disp_str = f"{h['delta_norm']:.4f}"
            h_dz_str   = f"{h['delta_z']:+.4f}"
            cr_dist_str = f"{h['d_Cr']:.4f}" if h['d_Cr'] < 900 else "--"
            cl_dist_str = f"{h['d_Cl']:.4f}" if h['d_Cl'] < 900 else "--"
        else:
            h_disp_str, h_dz_str, cr_dist_str, cl_dist_str = "--", "--", "--", "--"
        print(f"{tag:<28} | {max_d_str:<12} | {h_disp_str:<12} | {h_dz_str:<12} | {cr_dist_str:<12} | {cl_dist_str:<12}")
    print("="*124)

if __name__ == '__main__':
    main()
