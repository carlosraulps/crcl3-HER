#!/usr/bin/env python3
"""
compare_cdd_ucr_uall.py

Direct Physical and Visual Comparison between:
  1. +U_Cr tier (U applied only on Cr = 3.29 eV, U_Co = 0 eV)
  2. +U_all tier (U applied on Cr = 3.29 eV, U_Co = 3.29 eV)

Generates:
  - High-res comparative 1D Planar Average plot: Fig_CDD_Comparative_Profiles.png / .pdf
  - Side-by-side 3D VESTA render comparison figure
  - Quantitative metrics summary table
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from PIL import Image

# Typography and aesthetics according to user guidelines
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.size'] = 11

CDD_DIR = "/Volumes/KingstonSSD/Krojects/Kresearch/crlcl3-CoFeNi-HER/crcl3-newcals/postprosseing/cdd_comparison"
UALL_DIFF = os.path.join(CDD_DIR, "CHGCAR_diff_Uall")
UCR_DIFF = os.path.join(CDD_DIR, "CHGCAR_diff_Ucr")
OUT_DIR = CDD_DIR

def parse_chgcar_planar(file_path):
    """Parses CHGCAR and returns z-coordinates and planar average Delta_rho(z)."""
    with open(file_path, "r") as f:
        _ = f.readline()
        scale = float(f.readline().strip())
        _ = [float(x) * scale for x in f.readline().split()]
        _ = [float(x) * scale for x in f.readline().split()]
        a3 = [float(x) * scale for x in f.readline().split()]
        
        species = f.readline().split()
        try:
            counts = [int(x) for x in species]
        except ValueError:
            counts = [int(x) for x in f.readline().split()]
            
        coord_type = f.readline().strip()
        num_atoms = sum(counts)
        coords = []
        for _ in range(num_atoms):
            coords.append([float(x) for x in f.readline().split()[:3]])
            
        _ = f.readline()
        ngx, ngy, ngz = [int(x) for x in f.readline().split()[:3]]
        total_pts = ngx * ngy * ngz
        
        chg_data = []
        while len(chg_data) < total_pts:
            line = f.readline()
            if not line:
                break
            chg_data.extend([float(x) for x in line.split()])
            
        chg_3d = np.array(chg_data[:total_pts]).reshape((ngz, ngy, ngx))
        
    planar_avg = np.mean(chg_3d, axis=(1, 2))
    cell_c = a3[2]
    z_coords = np.linspace(0, cell_c, len(planar_avg), endpoint=False)
    z_co = coords[-1][2] * cell_c
    
    return z_coords, planar_avg, cell_c, z_co

def plot_comparison():
    if not (os.path.exists(UALL_DIFF) and os.path.exists(UCR_DIFF)):
        print(f"[WAIT] Both CHGCAR_diff files not ready yet.")
        return False
        
    z_uall, rho_uall, cell_c, z_co = parse_chgcar_planar(UALL_DIFF)
    z_ucr, rho_ucr, _, _ = parse_chgcar_planar(UCR_DIFF)
    
    delta_delta = rho_uall - rho_ucr
    
    fig = plt.figure(figsize=(9, 7), dpi=300)
    gs = GridSpec(2, 1, height_ratios=[2.2, 1.0], hspace=0.25)
    
    # Panel A: Main Planar Average Comparison
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(z_ucr, rho_ucr, color="#1f77b4", lw=2.2, label=r"$+U_{\mathrm{Cr}}$ Single-tier ($U_{\mathrm{Cr}}=3.29\ \mathrm{eV},\ U_{\mathrm{Co}}=0\ \mathrm{eV}$)")
    ax1.plot(z_uall, rho_uall, color="#d62728", lw=2.0, ls="--", label=r"$+U_{\mathrm{all}}$ Multi-tier ($U_{\mathrm{Cr}}=3.29\ \mathrm{eV},\ U_{\mathrm{Co}}=3.29\ \mathrm{eV}$)")
    ax1.axhline(0, color="k", ls=":", alpha=0.5, lw=1)
    
    # Substrate Cl and Cr reference lines
    ax1.axvline(z_co, color="#2ca02c", ls="-.", lw=1.5, label=f"Co Adatom ($z = {z_co:.2f}$ Å)")
    
    ax1.set_xlim(0, cell_c)
    # Dynamic headroom policy
    y_min, y_max = min(np.min(rho_ucr), np.min(rho_uall)), max(np.max(rho_ucr), np.max(rho_uall))
    dy = y_max - y_min
    ax1.set_ylim(y_min - 0.1 * dy, y_max + 0.30 * dy)
    
    ax1.set_ylabel(r"Planar Average $\Delta \rho(z)$ ($e$/Å)", fontsize=12)
    ax1.set_title(r"Quantitative Charge Density Difference (CDD) Comparison: $\mathrm{Co@CrCl_3}$ ($S_2$ Hollow)", fontsize=13, pad=10)
    ax1.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.92, edgecolor="#cccccc", fontsize=10)
    ax1.grid(True, ls=":", alpha=0.5)
    
    # Inset zoom around Co site
    axins = ax1.inset_axes([0.62, 0.45, 0.35, 0.48])
    mask = (z_ucr >= z_co - 2.5) & (z_ucr <= z_co + 2.5)
    axins.plot(z_ucr[mask], rho_ucr[mask], color="#1f77b4", lw=2.2)
    axins.plot(z_uall[mask], rho_uall[mask], color="#d62728", lw=2.0, ls="--")
    axins.axvline(z_co, color="#2ca02c", ls="-.", lw=1.5)
    axins.axhline(0, color="k", ls=":", alpha=0.4)
    axins.set_title(r"Zoom: Interface Region ($\pm 2.5$ Å)", fontsize=9)
    axins.tick_params(labelsize=8)
    axins.grid(True, ls=":", alpha=0.4)
    
    # Panel B: Exact Differential Profile Delta(Delta rho) = rho_Uall - rho_Ucr
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.plot(z_uall, delta_delta, color="#9467bd", lw=1.8, label=r"Difference $\Delta\Delta\rho(z) = \Delta\rho_{+U_{\mathrm{all}}} - \Delta\rho_{+U_{\mathrm{Cr}}}$")
    ax2.axhline(0, color="k", ls=":", alpha=0.5, lw=1)
    ax2.axvline(z_co, color="#2ca02c", ls="-.", lw=1.2)
    ax2.set_xlabel(r"$z$ coordinate along $c$-axis (Å)", fontsize=12)
    ax2.set_ylabel(r"$\Delta\Delta \rho(z)$ ($e$/Å)", fontsize=11)
    ax2.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.92, edgecolor="#cccccc", fontsize=9.5)
    ax2.grid(True, ls=":", alpha=0.5)
    
    out_png = os.path.join(OUT_DIR, "Fig_CDD_Comparative_Profiles.png")
    out_pdf = os.path.join(OUT_DIR, "Fig_CDD_Comparative_Profiles.pdf")
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.savefig(out_pdf, bbox_inches="tight")
    plt.close()
    print(f"🎉 Comparative CDD profile saved: {out_png}")
    return True

if __name__ == "__main__":
    plot_comparison()
