#!/usr/bin/env python3
# plot_dbc_vs_deltag.py
# Publication-quality plot of d-band center vs. hydrogen adsorption free energy (dG_H).

import os
import re
import numpy as np
import matplotlib.pyplot as plt
from pymatgen.io.vasp import Vasprun
from pymatgen.electronic_structure.core import OrbitalType, Spin

# Setup relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # crcl3-newcals/

# ----------------- Data Parsing Functions -----------------

def parse_final_energy(outcar_path):
    """Parses the final energy without entropy from OUTCAR."""
    if not os.path.exists(outcar_path):
        raise FileNotFoundError(f"Missing OUTCAR: {outcar_path}")
    energy = None
    with open(outcar_path, 'r') as f:
        for line in f:
            match = re.search(r'energy\s+without\s+entropy\s*=\s*([-\d\.]+)', line)
            if match:
                energy = float(match.group(1))
    if energy is None:
        raise ValueError(f"Could not parse energy from {outcar_path}")
    return energy

def get_d_band_center(xml_path):
    """Calculates the d-band center of the transition metal (up to Fermi level)."""
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"Missing vasprun.xml: {xml_path}")
        
    v = Vasprun(xml_path)
    structure = v.final_structure
    
    # Find the transition metal
    tm_site = None
    for site in structure:
        if site.species_string in ["Co", "Fe", "Ni"]:
            tm_site = site
            break
            
    if tm_site is None:
        raise ValueError(f"No transition metal (Co, Fe, Ni) found in structure: {xml_path}")
        
    complete_dos = v.complete_dos
    spd_dos = complete_dos.get_site_spd_dos(tm_site)
    d_dos = spd_dos[OrbitalType.d]
    
    # Energies relative to Fermi level
    energies = d_dos.energies - d_dos.efermi
    
    # Sum spin channels
    dos_values = np.zeros_like(energies)
    if Spin.up in d_dos.densities:
        dos_values += d_dos.densities[Spin.up]
    if Spin.down in d_dos.densities:
        dos_values += d_dos.densities[Spin.down]
        
    # Integrate up to Fermi level (E <= 0)
    mask = energies <= 0
    e_masked = energies[mask]
    dos_masked = dos_values[mask]
    
    # Use trapezoid (new numpy version) or fallback to trapz
    try:
        integral_dos = np.trapezoid(dos_masked, e_masked)
        integral_e_dos = np.trapezoid(e_masked * dos_masked, e_masked)
    except AttributeError:
        integral_dos = np.trapz(dos_masked, e_masked)
        integral_e_dos = np.trapz(e_masked * dos_masked, e_masked)
        
    if integral_dos == 0:
        return 0.0
    return integral_e_dos / integral_dos

# ----------------- Main Plotting Script -----------------

def main():
    # 1. Parse H2 reference energy
    try:
        e_h2 = parse_final_energy(os.path.join(BASE_DIR, "H2_ref/OUTCAR"))
        half_e_h2 = e_h2 / 2.0
    except Exception as e:
        print(f"Error parsing H2 reference: {e}")
        return
        
    metals = ["Co", "Fe", "Ni"]
    
    # Series containers
    ads_dbc = []
    ads_dg = []
    
    emb_dbc = []
    emb_dg = []
    
    print("Collecting calculation data...")
    
    # Parse Adsorbed systems
    for tm in metals:
        try:
            e_doped = parse_final_energy(os.path.join(BASE_DIR, f"adsorbed/{tm.lower()}/OUTCAR"))
            e_doped_h = parse_final_energy(os.path.join(BASE_DIR, f"doped-H/adsorbed/{tm}/OUTCAR"))
            dbc = get_d_band_center(os.path.join(BASE_DIR, f"adsorbed/{tm.lower()}/vasprun.xml"))
            
            de_h = e_doped_h - e_doped - half_e_h2
            dg_h = de_h + 0.24  # standard ZPE and entropy correction
            
            ads_dbc.append(dbc)
            ads_dg.append(dg_h)
            print(f"  adsorbed/{tm}: dbc = {dbc:.4f} eV, dG_H = {dg_h:.4f} eV")
        except Exception as e:
            print(f"  Error parsing adsorbed/{tm}: {e}")
            
    # Parse Embedded systems
    for tm in metals:
        try:
            e_doped = parse_final_energy(os.path.join(BASE_DIR, f"embedded/{tm.lower()}/OUTCAR"))
            e_doped_h = parse_final_energy(os.path.join(BASE_DIR, f"doped-H/embeded/{tm}/OUTCAR"))
            dbc = get_d_band_center(os.path.join(BASE_DIR, f"embedded/{tm.lower()}/vasprun.xml"))
            
            de_h = e_doped_h - e_doped - half_e_h2
            dg_h = de_h + 0.24  # standard ZPE and entropy correction
            
            emb_dbc.append(dbc)
            emb_dg.append(dg_h)
            print(f"  embedded/{tm}: dbc = {dbc:.4f} eV, dG_H = {dg_h:.4f} eV")
        except Exception as e:
            print(f"  Error parsing embedded/{tm}: {e}")
            
    # Convert to arrays for regression fitting
    ads_dbc = np.array(ads_dbc)
    ads_dg = np.array(ads_dg)
    emb_dbc = np.array(emb_dbc)
    emb_dg = np.array(emb_dg)
    
    # 2. Design and Create Plot
    plt.figure(figsize=(7.5, 6), dpi=300)
    
    # Color system (premium slate dark/light scheme)
    color_ads = "#1f77b4"  # Premium Steel Blue
    color_emb = "#ff7f0e"  # Premium Coral Orange
    
    # Plot ideal HER region (shaded area around 0.0 to 0.2 eV)
    plt.axhspan(-0.1, 0.2, color="#2ca02c", alpha=0.08, label="Ideal HER Active Window", zorder=1)
    plt.axhline(0, color="gray", linestyle="--", linewidth=1.0, alpha=0.5, zorder=2)
    
    # Fit linear regressions
    if len(ads_dbc) > 1:
        slope_ads, intercept_ads = np.polyfit(ads_dbc, ads_dg, 1)
        r_ads = np.corrcoef(ads_dbc, ads_dg)[0, 1]
        x_fit_ads = np.linspace(min(ads_dbc)-0.1, max(ads_dbc)+0.1, 100)
        y_fit_ads = slope_ads * x_fit_ads + intercept_ads
        plt.plot(x_fit_ads, y_fit_ads, color=color_ads, linestyle="-.", linewidth=1.5, alpha=0.7, 
                 label=f"Adsorbed Fit ($R^2$ = {r_ads**2:.3f})")
                 
    if len(emb_dbc) > 1:
        slope_emb, intercept_emb = np.polyfit(emb_dbc, emb_dg, 1)
        r_emb = np.corrcoef(emb_dbc, emb_dg)[0, 1]
        x_fit_emb = np.linspace(min(emb_dbc)-0.1, max(emb_dbc)+0.1, 100)
        y_fit_emb = slope_emb * x_fit_emb + intercept_emb
        plt.plot(x_fit_emb, y_fit_emb, color=color_emb, linestyle="-.", linewidth=1.5, alpha=0.7, 
                 label=f"Embedded Fit ($R^2$ = {r_emb**2:.3f})")
                 
    # Plot data points
    plt.scatter(ads_dbc, ads_dg, color=color_ads, edgecolor="black", s=110, marker="o", 
                linewidth=1.2, label="Adsorbed TM", zorder=5)
    plt.scatter(emb_dbc, emb_dg, color=color_emb, edgecolor="black", s=110, marker="s", 
                linewidth=1.2, label="Embedded TM", zorder=5)
                
    # Custom offsets for annotations to prevent overlaps (x_offset, y_offset)
    offsets_ads = {
        "Co": (0, -22),   # below the point
        "Fe": (0, 10),    # above the point
        "Ni": (-22, -5),  # to the left of the point
    }
    offsets_emb = {
        "Co": (0, 10),    # above the point
        "Fe": (0, 10),    # above the point
        "Ni": (0, 10),    # above the point
    }
                
    # Annotate points with chemical elements
    for i, tm in enumerate(metals):
        if i < len(ads_dbc):
            off = offsets_ads.get(tm, (0, 10))
            plt.annotate(tm, (ads_dbc[i], ads_dg[i]), textcoords="offset points", 
                         xytext=off, ha='center', va='bottom', fontsize=11, fontweight="bold",
                         bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", lw=0.5, alpha=0.85), zorder=6)
        if i < len(emb_dbc):
            off = offsets_emb.get(tm, (0, 10))
            plt.annotate(tm, (emb_dbc[i], emb_dg[i]), textcoords="offset points", 
                         xytext=off, ha='center', va='bottom', fontsize=11, fontweight="bold",
                         bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", lw=0.5, alpha=0.85), zorder=6)
                         
    # Labels & Title
    plt.xlabel("$d$-Band Center, $\\varepsilon_d$ ($E - E_{\\mathrm{F}}$, eV)", fontsize=13, fontweight="bold", labelpad=8)
    plt.ylabel("Hydrogen Adsorption Free Energy, $\\Delta G_{\\mathrm{H}}$ (eV)", fontsize=13, fontweight="bold", labelpad=8)
    plt.title("Descriptors: $d$-Band Center vs. $\\Delta G_{\\mathrm{H}}$ on $\\mathrm{CrCl_3}$", fontsize=14, fontweight="bold", pad=15)
    
    # Adjust plot limits to give headroom and prevent cutoff of labels
    plt.ylim(-0.2, 2.2)
    
    # Axes style
    ax = plt.gca()
    ax.tick_params(labelsize=11, width=1.2)
    for spine in ax.spines.values():
        spine.set_linewidth(1.2)
        
    plt.grid(True, linestyle=":", alpha=0.6, zorder=0)
    plt.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="gray", framealpha=0.9, fontsize=10.5)

    
    # Save figure
    output_png = os.path.join(SCRIPT_DIR, "dbc_vs_deltag.png")
    plt.tight_layout()
    plt.savefig(output_png, dpi=300)
    print(f"Plot saved successfully to: {output_png}")

if __name__ == "__main__":
    main()
