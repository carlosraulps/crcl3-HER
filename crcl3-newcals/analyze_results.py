import os
import re
import numpy as np
from pymatgen.io.lobster import Doscar, Icohplist

# Define directories
DEST_BASE = "/Users/apple/Research/abc/paper-adaptation/crcl3-newcals"
systems = ["adsorbed/co", "adsorbed/fe", "adsorbed/ni", 
           "embedded/co", "embedded/fe", "embedded/ni"]

def get_band_center(energies, dos_values):
    """Calculates the band center given energy array and DOS array."""
    # Only integrate up to Fermi level (E=0 in LOBSTER DOSCAR)
    mask = energies <= 0
    e_masked = energies[mask]
    dos_masked = dos_values[mask]
    
    integral_dos = np.trapz(dos_masked, e_masked)
    if integral_dos == 0:
        return 0.0
    integral_e_dos = np.trapz(e_masked * dos_masked, e_masked)
    return integral_e_dos / integral_dos

def parse_lobsterin_for_indices(lobsterin_path):
    tm_idx = None
    cl_indices = []
    with open(lobsterin_path, 'r') as f:
        for line in f:
            if line.startswith("cohpBetweenAtom"):
                # cohpBetweenAtom 26 and 12
                match = re.search(r"cohpBetweenAtom\s+(\d+)\s+and\s+(\d+)", line)
                if match:
                    idx1, idx2 = int(match.group(1)), int(match.group(2))
                    if tm_idx is None:
                        tm_idx = idx1
                    if idx2 not in cl_indices:
                        cl_indices.append(idx2)
    return tm_idx, cl_indices

def main():
    print(f"{'System':<15} | {'TM d-band (up, dn, tot)':<30} | {'Cl p-band (up, dn, tot)':<30} | {'Delta (p-d)':<12} | {'ICOHP (TM-Cl, TM-Cr)':<20}")
    print("-" * 125)
    
    for name in systems:
        sys_dir = os.path.join(DEST_BASE, name)
        doscar_path = os.path.join(sys_dir, "DOSCAR.lobster")
        icohplist_path = os.path.join(sys_dir, "ICOHPLIST.lobster")
        lobsterin_path = os.path.join(sys_dir, "lobsterin")
        
        if not os.path.exists(doscar_path):
            print(f"{name:<15} | No data (job not run yet?)")
            continue
            
        # Parse lobsterin to get TM and neighbor indices
        tm_idx, neighbor_indices = parse_lobsterin_for_indices(lobsterin_path)
        
        # We need POSCAR to distinguish Cl from Cr among neighbors
        from ase.io import read
        poscar_path = os.path.join(sys_dir, "POSCAR")
        atoms = read(poscar_path)
        
        cl_neighbors = []
        cr_neighbors = []
        for n_idx in neighbor_indices:
            symbol = atoms[n_idx - 1].symbol  # LOBSTER is 1-indexed
            if symbol == "Cl":
                cl_neighbors.append(n_idx)
            elif symbol == "Cr":
                cr_neighbors.append(n_idx)
        
        # Read DOSCAR.lobster
        try:
            doscar = Doscar(doscar_path)
            energies = doscar.energies  # E - Ef
            
            # TM d-band center
            # doscar.pdos is a list, 0-indexed for atoms (i.e. pdos[0] is atom 1)
            tm_pdos = doscar.pdos[tm_idx - 1]
            
            # Sum d orbitals: dxy, dyz, dz2, dxz, dx2-y2
            d_orbitals = [k for k in tm_pdos.keys() if k.startswith("d")]
            
            d_up = np.zeros_like(energies)
            d_dn = np.zeros_like(energies)
            for orb in d_orbitals:
                d_up += tm_pdos[orb]["1"]  # Spin up
                d_dn += tm_pdos[orb]["-1"] # Spin down
                
            d_center_up = get_band_center(energies, d_up)
            d_center_dn = get_band_center(energies, d_dn)
            
            # Total weighted d-band center
            int_d_up = np.trapz(d_up[energies <= 0], energies[energies <= 0])
            int_d_dn = np.trapz(d_dn[energies <= 0], energies[energies <= 0])
            if (int_d_up + int_d_dn) > 0:
                d_center_tot = (d_center_up * int_d_up + d_center_dn * int_d_dn) / (int_d_up + int_d_dn)
            else:
                d_center_tot = 0.0
                
            # Cl p-band center
            p_up = np.zeros_like(energies)
            p_dn = np.zeros_like(energies)
            for cl_idx in cl_neighbors:
                cl_pdos = doscar.pdos[cl_idx - 1]
                p_orbitals = [k for k in cl_pdos.keys() if k.startswith("p")]
                for orb in p_orbitals:
                    p_up += cl_pdos[orb]["1"]
                    p_dn += cl_pdos[orb]["-1"]
                    
            p_center_up = get_band_center(energies, p_up)
            p_center_dn = get_band_center(energies, p_dn)
            
            int_p_up = np.trapz(p_up[energies <= 0], energies[energies <= 0])
            int_p_dn = np.trapz(p_dn[energies <= 0], energies[energies <= 0])
            if (int_p_up + int_p_dn) > 0:
                p_center_tot = (p_center_up * int_p_up + p_center_dn * int_p_dn) / (int_p_up + int_p_dn)
            else:
                p_center_tot = 0.0
                
            delta_pd = abs(d_center_tot - p_center_tot)
            
            # Parse ICOHPLIST
            tm_cl_sum = 0.0
            tm_cl_count = 0
            tm_cr_sum = 0.0
            tm_cr_count = 0
            
            with open(icohplist_path, 'r') as f:
                lines = f.readlines()
                for line in lines[1:]: # Skip header
                    parts = line.split()
                    if len(parts) >= 8:
                        a1 = parts[1]
                        a2 = parts[2]
                        if str(tm_idx) in a1 or str(tm_idx) in a2:
                            icohp_tot = float(parts[4]) + float(parts[5]) # spin polarized
                            if "Cl" in a1 or "Cl" in a2:
                                tm_cl_sum += icohp_tot
                                tm_cl_count += 1
                            elif "Cr" in a1 or "Cr" in a2:
                                tm_cr_sum += icohp_tot
                                tm_cr_count += 1
                                
            avg_tm_cl = tm_cl_sum / tm_cl_count if tm_cl_count > 0 else 0.0
            avg_tm_cr = tm_cr_sum / tm_cr_count if tm_cr_count > 0 else 0.0
            
            print(f"{name:<15} | {d_center_up:5.2f}, {d_center_dn:5.2f}, {d_center_tot:5.2f} | {p_center_up:5.2f}, {p_center_dn:5.2f}, {p_center_tot:5.2f} | {delta_pd:5.2f} | {avg_tm_cl:5.2f}, {avg_tm_cr:5.2f}")
            
        except Exception as e:
            print(f"{name:<15} | Error parsing results: {e}")

if __name__ == "__main__":
    main()
