#!/usr/bin/env python3
import os
import sys
import math

def read_poscar(filepath):
    """
    Parse a VASP POSCAR/CONTCAR file.
    Returns: title, scale, lattice (3x3 list), species (list of str), counts (list of int),
             coord_type ('Direct' or 'Cartesian'), coords (list of [x, y, z])
    """
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    title = lines[0]
    scale = float(lines[1])
    lat = []
    for i in range(2, 5):
        lat.append([float(x) * scale for x in lines[i].split()])
    
    # Check if line 5 has element symbols
    parts5 = lines[5].split()
    if parts5[0].isalpha():
        species = parts5
        counts = [int(x) for x in lines[6].split()]
        idx = 7
    else:
        # Older format or no species line
        species = ["Element"] * len(parts5)
        counts = [int(x) for x in parts5]
        idx = 6
    
    # Optional Selective dynamics
    if lines[idx].lower().startswith('s'):
        idx += 1
    
    coord_type = lines[idx]
    is_direct = coord_type.lower().startswith('d')
    idx += 1
    
    total_atoms = sum(counts)
    coords = []
    for i in range(idx, idx + total_atoms):
        parts = lines[i].split()
        c = [float(parts[0]), float(parts[1]), float(parts[2])]
        coords.append(c)
    
    # Expand species per atom
    atom_species = []
    for sp, cnt in zip(species, counts):
        atom_species.extend([sp] * cnt)
        
    return {
        'title': title,
        'lattice': lat,
        'species': species,
        'counts': counts,
        'atom_species': atom_species,
        'coord_type': 'Direct' if is_direct else 'Cartesian',
        'coords': coords
    }

def frac_to_cart(fcoord, lat):
    return [
        fcoord[0] * lat[0][0] + fcoord[1] * lat[1][0] + fcoord[2] * lat[2][0],
        fcoord[0] * lat[0][1] + fcoord[1] * lat[1][1] + fcoord[2] * lat[2][1],
        fcoord[0] * lat[0][2] + fcoord[1] * lat[1][2] + fcoord[2] * lat[2][2],
    ]

def cart_to_frac(ccoord, lat):
    # Invert 3x3 lattice
    # For hexagonal/orthogonal lattice where lat[0][2]=lat[1][2]=lat[2][0]=lat[2][1]=0
    # Let's do general 3x3 determinant & inversion
    a = lat
    det = (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
          -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
          +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))
    inv = [
        [(a[1][1]*a[2][2]-a[1][2]*a[2][1])/det, (a[0][2]*a[2][1]-a[0][1]*a[2][2])/det, (a[0][1]*a[1][2]-a[0][2]*a[1][1])/det],
        [(a[1][2]*a[2][0]-a[1][0]*a[2][2])/det, (a[0][0]*a[2][2]-a[0][2]*a[2][0])/det, (a[0][2]*a[1][0]-a[0][0]*a[1][2])/det],
        [(a[1][0]*a[2][1]-a[1][1]*a[2][0])/det, (a[0][1]*a[2][0]-a[0][0]*a[2][1])/det, (a[0][0]*a[1][1]-a[0][1]*a[1][0])/det]
    ]
    return [
        ccoord[0]*inv[0][0] + ccoord[1]*inv[1][0] + ccoord[2]*inv[2][0],
        ccoord[0]*inv[0][1] + ccoord[1]*inv[1][1] + ccoord[2]*inv[2][1],
        ccoord[0]*inv[0][2] + ccoord[1]*inv[1][2] + ccoord[2]*inv[2][2]
    ]

def pbc_dist(f1, f2, lat):
    # Periodic boundary condition distance
    df = [f1[0] - f2[0], f1[1] - f2[1], f1[2] - f2[2]]
    # wrap in-plane (and out of plane, though slab has vacuum)
    df[0] -= round(df[0])
    df[1] -= round(df[1])
    # don't wrap z if slab vacuum
    dcart = frac_to_cart(df, lat)
    return math.sqrt(dcart[0]**2 + dcart[1]**2 + dcart[2]**2), dcart

def parse_oszicar(filepath):
    if not os.path.exists(filepath):
        return []
    steps = []
    with open(filepath, 'r') as f:
        for line in f:
            if 'F=' in line:
                # e.g. 1 F= -.15808767E+03 E0= -.15808767E+03  d E =0.000000E+00
                parts = line.strip().split()
                try:
                    step_num = int(parts[0])
                    energy = float(parts[2])
                    e0 = float(parts[4])
                    steps.append({'step': step_num, 'energy': energy, 'e0': e0, 'line': line.strip()})
                except Exception:
                    pass
    return steps

def parse_outcar(filepath):
    if not os.path.exists(filepath):
        return {}
    res = {
        'converged': False,
        'energies': [],
        'forces': [],
        'ionic_steps': 0,
        'mag_moments': []
    }
    with open(filepath, 'r') as f:
        content = f.read()
    
    if "reached required accuracy" in content:
        res['converged'] = True
        
    lines = content.splitlines()
    for i, l in enumerate(lines):
        if "free energy    TOTEN  =" in l:
            try:
                e = float(l.split("=")[1].split()[0])
                res['energies'].append(e)
            except Exception:
                pass
        elif "TOTAL-FORCE (eV/Angst)" in l:
            # next line is dashed
            # following lines are coordinates and forces
            step_forces = []
            j = i + 2
            while j < len(lines) and not lines[j].startswith(" ---"):
                parts = lines[j].split()
                if len(parts) == 6:
                    step_forces.append([float(parts[0]), float(parts[1]), float(parts[2]),
                                        float(parts[3]), float(parts[4]), float(parts[5])])
                j += 1
            res['forces'].append(step_forces)
            
    res['ionic_steps'] = len(res['energies'])
    return res

def analyze_system(calc_dir, name):
    print("=" * 80)
    print(f"ANALYZING: {name} in {calc_dir}")
    print("=" * 80)
    
    poscar_path = os.path.join(calc_dir, "POSCAR")
    contcar_path = os.path.join(calc_dir, "CONTCAR")
    outcar_path = os.path.join(calc_dir, "OUTCAR")
    oszicar_path = os.path.join(calc_dir, "OSZICAR")
    
    if not os.path.exists(poscar_path):
        print(f"ERROR: POSCAR not found at {poscar_path}")
        return None
    
    pos = read_poscar(poscar_path)
    has_contcar = os.path.exists(contcar_path) and os.path.getsize(contcar_path) > 0
    cont = read_poscar(contcar_path) if has_contcar else None
    
    outcar = parse_outcar(outcar_path)
    oszicar = parse_oszicar(oszicar_path)
    
    print(f"Convergence status: {'CONVERGED' if outcar.get('converged') else 'STOPPED/RUNNING'}")
    print(f"Total ionic steps in OSZICAR: {len(oszicar)}")
    if oszicar:
        print(f"Last Energy (OSZICAR): {oszicar[-1]['energy']:.6f} eV")
    
    # Identify H atom (typically the last atom)
    h_idx = -1
    for idx, sp in enumerate(pos['atom_species']):
        if sp.upper() == 'H':
            h_idx = idx
            break
            
    if h_idx == -1:
        print(f"No H atom found in POSCAR species ({pos['species']})!")
        return None
        
    print(f"H atom index: {h_idx+1} (1-based)")
    
    lat = pos['lattice']
    pos_h_frac = pos['coords'][h_idx]
    pos_h_cart = frac_to_cart(pos_h_frac, lat) if pos['coord_type'] == 'Direct' else pos_h_frac
    if pos['coord_type'] != 'Direct':
        pos_h_frac = cart_to_frac(pos_h_cart, lat)
        
    print(f"\nINITIAL POSCAR:")
    print(f"  H fractional: [{pos_h_frac[0]:.6f}, {pos_h_frac[1]:.6f}, {pos_h_frac[2]:.6f}]")
    print(f"  H Cartesian : [{pos_h_cart[0]:.6f}, {pos_h_cart[1]:.6f}, {pos_h_cart[2]:.6f}] A")
    
    # Substrate atoms in POSCAR
    cr_pos_carts = []
    cl_pos_carts = []
    cr_pos_fracs = []
    cl_pos_fracs = []
    for i, (sp, coord) in enumerate(zip(pos['atom_species'], pos['coords'])):
        if i == h_idx:
            continue
        c_frac = coord if pos['coord_type'] == 'Direct' else cart_to_frac(coord, lat)
        c_cart = frac_to_cart(c_frac, lat)
        if sp.upper().startswith('CR'):
            cr_pos_fracs.append((i+1, c_frac))
            cr_pos_carts.append((i+1, c_cart))
        elif sp.upper().startswith('CL'):
            cl_pos_fracs.append((i+1, c_frac))
            cl_pos_carts.append((i+1, c_cart))
            
    cr_z_avg_init = sum(c[1][2] for c in cr_pos_carts) / len(cr_pos_carts)
    cl_z_all_init = [c[1][2] for c in cl_pos_carts]
    # top Cl atoms are those with z > cr_z_avg
    top_cl_init = [c for c in cl_pos_carts if c[1][2] > cr_z_avg_init]
    top_cl_z_avg_init = sum(c[1][2] for c in top_cl_init) / len(top_cl_init)
    
    print(f"  Initial Substrate Planes:")
    print(f"    Cr average z    : {cr_z_avg_init:.4f} A")
    print(f"    Top-Cl average z: {top_cl_z_avg_init:.4f} A (d_z above Cr = {top_cl_z_avg_init - cr_z_avg_init:.4f} A)")
    print(f"    Initial H height above top-Cl: {pos_h_cart[2] - top_cl_z_avg_init:.4f} A")
    print(f"    Initial H height above Cr    : {pos_h_cart[2] - cr_z_avg_init:.4f} A")

    # If CONTCAR exists, analyze final position and displacement
    if cont:
        cont_lat = cont['lattice']
        cont_h_frac = cont['coords'][h_idx]
        cont_h_cart = frac_to_cart(cont_h_frac, cont_lat) if cont['coord_type'] == 'Direct' else cont_h_frac
        if cont['coord_type'] != 'Direct':
            cont_h_frac = cart_to_frac(cont_h_cart, cont_lat)
            
        print(f"\nFINAL CONTCAR (Relaxed / Latest geometry):")
        print(f"  H fractional: [{cont_h_frac[0]:.6f}, {cont_h_frac[1]:.6f}, {cont_h_frac[2]:.6f}]")
        print(f"  H Cartesian : [{cont_h_cart[0]:.6f}, {cont_h_cart[1]:.6f}, {cont_h_cart[2]:.6f}] A")
        
        # Calculate displacement of H
        # Use pbc_dist between initial frac and final frac
        h_disp_tot, h_disp_cart = pbc_dist(cont_h_frac, pos_h_frac, cont_lat)
        dx = h_disp_cart[0]
        dy = h_disp_cart[1]
        dz = h_disp_cart[2]
        d_xy = math.sqrt(dx**2 + dy**2)
        
        print(f"\nH DISPLACEMENT (Movement during relaxation):")
        print(f"  Total 3D displacement |dr| : {h_disp_tot:.4f} A")
        print(f"  Lateral displacement dr_xy : {d_xy:.4f} A")
        print(f"  Vertical displacement dz   : {dz:.4f} A (positive = moved upward/away, negative = moved downward/inward)")
        print(f"  Displacement vector (dx,dy,dz): ({dx:.4f}, {dy:.4f}, {dz:.4f}) A")
        
        # Relaxed substrate planes and neighbors
        cont_cr_carts = []
        cont_cl_carts = []
        cont_cr_fracs = []
        cont_cl_fracs = []
        
        # Substrate atom displacements
        sub_disps = []
        for i, (sp, coord) in enumerate(zip(cont['atom_species'], cont['coords'])):
            if i == h_idx:
                continue
            cf = coord if cont['coord_type'] == 'Direct' else cart_to_frac(coord, cont_lat)
            pf = pos['coords'][i] if pos['coord_type'] == 'Direct' else cart_to_frac(pos['coords'][i], lat)
            disp_mag, disp_c = pbc_dist(cf, pf, cont_lat)
            sub_disps.append((disp_mag, i+1, sp, disp_c))
            
            cc = frac_to_cart(cf, cont_lat)
            if sp.upper().startswith('CR'):
                cont_cr_fracs.append((i+1, cf))
                cont_cr_carts.append((i+1, cc))
            elif sp.upper().startswith('CL'):
                cont_cl_fracs.append((i+1, cf))
                cont_cl_carts.append((i+1, cc))
                
        sub_disps.sort(key=lambda x: x[0], reverse=True)
        print(f"\nSUBSTRATE PERTURBATIONS:")
        print(f"  Top 3 most displaced substrate atoms:")
        for mag, aid, sp, dc in sub_disps[:3]:
            print(f"    Atom {aid} ({sp}): |dr| = {mag:.4f} A, dz = {dc[2]:.4f} A")
            
        cont_cr_z_avg = sum(c[1][2] for c in cont_cr_carts) / len(cont_cr_carts)
        cont_top_cl = [c for c in cont_cl_carts if c[1][2] > cont_cr_z_avg]
        cont_top_cl_z_avg = sum(c[1][2] for c in cont_top_cl) / len(cont_top_cl)
        
        print(f"\nFINAL SUBSTRATE PLANES:")
        print(f"  Cr average z    : {cont_cr_z_avg:.4f} A")
        print(f"  Top-Cl average z: {cont_top_cl_z_avg:.4f} A")
        print(f"  Final H height above top-Cl: {cont_h_cart[2] - cont_top_cl_z_avg:.4f} A")
        print(f"  Final H height above Cr    : {cont_h_cart[2] - cont_cr_z_avg:.4f} A")

        # Distances to all Cl and Cr atoms from final H
        cl_distances = []
        for aid, cf in cont_cl_fracs:
            dist, dcart = pbc_dist(cont_h_frac, cf, cont_lat)
            cl_distances.append((dist, aid, dcart, cf))
        cl_distances.sort(key=lambda x: x[0])
        
        cr_distances = []
        for aid, cf in cont_cr_fracs:
            dist, dcart = pbc_dist(cont_h_frac, cf, cont_lat)
            cr_distances.append((dist, aid, dcart, cf))
        cr_distances.sort(key=lambda x: x[0])
        
        print(f"\nCOORDINATION & WHERE H IS STAYING:")
        print(f"  Nearest Cl atoms:")
        for dist, aid, dcart, cf in cl_distances[:4]:
            cart_cl = frac_to_cart(cf, cont_lat)
            print(f"    Atom {aid} (Cl): distance = {dist:.4f} A (dx={dcart[0]:.3f}, dy={dcart[1]:.3f}, dz={dcart[2]:.3f} A; Cl z={cart_cl[2]:.3f} A)")
            
        print(f"  Nearest Cr atoms:")
        for dist, aid, dcart, cf in cr_distances[:3]:
            cart_cr = frac_to_cart(cf, cont_lat)
            print(f"    Atom {aid} (Cr): distance = {dist:.4f} A (dx={dcart[0]:.3f}, dy={dcart[1]:.3f}, dz={dcart[2]:.3f} A; Cr z={cart_cr[2]:.3f} A)")
            
        # Bond angles around H
        # Angle H - Nearest Cl - Nearest Cr
        # or Angle Cl - H - Cl
        nearest_cl_aid = cl_distances[0][1]
        nearest_cl_cart = frac_to_cart(cl_distances[0][3], cont_lat)
        nearest_cr_aid = cr_distances[0][1]
        nearest_cr_cart = frac_to_cart(cr_distances[0][3], cont_lat)
        
        # Vector Cl -> H:
        v_cl_h = cl_distances[0][2] # from H to Cl, so invert for Cl to H:
        v_cl_h = [-v_cl_h[0], -v_cl_h[1], -v_cl_h[2]]
        
        # Vector Cr -> H:
        v_cr_h = [-cr_distances[0][2][0], -cr_distances[0][2][1], -cr_distances[0][2][2]]
        
        # Angle with surface normal (z-axis: [0, 0, 1])
        # cos(theta) = dz / dist
        tilt_from_z_cl = math.degrees(math.acos(min(max(v_cl_h[2] / cl_distances[0][0], -1.0), 1.0)))
        tilt_from_z_cr = math.degrees(math.acos(min(max(v_cr_h[2] / cr_distances[0][0], -1.0), 1.0)))
        print(f"\nGEOMETRIC ORIENTATION:")
        print(f"  Bond axis to nearest Cl{nearest_cl_aid} tilt from surface normal (+z): {tilt_from_z_cl:.2f}°")
        print(f"  Bond axis to nearest Cr{nearest_cr_aid} tilt from surface normal (+z): {tilt_from_z_cr:.2f}°")

    # Trajectory from OUTCAR forces and positions if available
    if outcar.get('forces'):
        print(f"\nIONIC RELAXATION TRAJECTORY (Step-by-Step for H atom):")
        print(f"  Step |    E_tot (eV)    |   H_z (A)   | F_x (eV/A) | F_y (eV/A) | F_z (eV/A) | |F_H| (eV/A) | Max |F_all|")
        print(f"  -----+------------------+-------------+------------+------------+------------+--------------+------------")
        for s_idx, f_table in enumerate(outcar['forces']):
            if h_idx < len(f_table):
                hf = f_table[h_idx]
                h_fmag = math.sqrt(hf[3]**2 + hf[4]**2 + hf[5]**2)
                max_f = max(math.sqrt(row[3]**2 + row[4]**2 + row[5]**2) for row in f_table)
                e_val = outcar['energies'][s_idx] if s_idx < len(outcar['energies']) else 0.0
                print(f"  {s_idx+1:4d} | {e_val:16.6f} | {hf[2]:11.4f} | {hf[3]:10.4f} | {hf[4]:10.4f} | {hf[5]:10.4f} | {h_fmag:12.4f} | {max_f:10.4f}")

    return {
        'name': name,
        'converged': outcar.get('converged', False),
        'pos': pos,
        'cont': cont,
        'h_disp_tot': h_disp_tot if cont else 0.0,
        'h_disp_cart': h_disp_cart if cont else [0,0,0],
        'cl_distances': cl_distances if cont else [],
        'cr_distances': cr_distances if cont else [],
        'energy': oszicar[-1]['energy'] if oszicar else None,
        'ionic_steps': len(oszicar)
    }

def main():
    root = "/home/juan/Carlos/crcl3-2x2-h_ads-without-U"
    calcs = [
        ("no_vdw / S1 (top-Cl)", os.path.join(root, "no_vdw", "S1")),
        ("no_vdw / S3 (top-Cr)", os.path.join(root, "no_vdw", "S3")),
        ("yes_vdw / S1 (top-Cl)", os.path.join(root, "yes_vdw", "S1")),
        ("yes_vdw / S3 (top-Cr)", os.path.join(root, "yes_vdw", "S3")),
    ]
    
    clean_novdw_pos = os.path.join(root, "no_vdw", "clean")
    clean_yesvdw_pos = os.path.join(root, "yes_vdw", "clean")
    
    e_clean_novdw = parse_oszicar(os.path.join(clean_novdw_pos, "OSZICAR"))[-1]['energy']
    e_clean_yesvdw = parse_oszicar(os.path.join(clean_yesvdw_pos, "OSZICAR"))[-1]['energy']
    e_h2_novdw = -6.75960012
    e_h2_half_novdw = e_h2_novdw / 2.0
    
    print("=" * 80)
    print("REFERENCE ENERGIES:")
    print(f"Clean 2x2 slab (no_vdw) : {e_clean_novdw:.6f} eV")
    print(f"Clean 2x2 slab (yes_vdw): {e_clean_yesvdw:.6f} eV")
    print(f"H2 molecule (no_vdw)   : {e_h2_novdw:.6f} eV (1/2 E = {e_h2_half_novdw:.6f} eV)")
    print("=" * 80)
    
    results = {}
    for name, path in calcs:
        res = analyze_system(path, name)
        results[name] = res

if __name__ == "__main__":
    main()
