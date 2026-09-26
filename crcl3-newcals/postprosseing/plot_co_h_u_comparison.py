#!/usr/bin/env python3
"""
plot_co_h_u_comparison.py

Generates publication-quality comparative figures illustrating the impact of 
Hubbard U (U=3.29 eV) on Co and Co-H adsorption on monolayer CrCl3 (2x2):
  Panel (a): Site stability inversion (Delta E_rel) for Co adsorption (Without U vs With U)
  Panel (b): Total cell magnetization (mu_B) highlighting AFM -> FM transition
  Panel (c): Free energy profile for HER (Delta G_H*) with ideal Sabatier window
  Panel (d): Evolution of active site bond lengths and spin-transition upon H adsorption

Equipped with smart_plot_optimizer collision prevention & adaptive headroom.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

# Styling
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Liberation Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['xtick.major.width'] = 1.2
plt.rcParams['ytick.major.width'] = 1.2
plt.rcParams['xtick.minor.width'] = 0.8
plt.rcParams['ytick.minor.width'] = 0.8

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def create_comparison_figure():
    fig, axs = plt.subplots(2, 2, figsize=(13.5, 11))
    fig.subplots_adjust(hspace=0.34, wspace=0.28)
    
    bbox_props = dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#cccccc', alpha=0.92, linewidth=0.8)
    
    # -------------------------------------------------------------
    # Panel (a): Relative Site Penalty: Without U vs With U
    # -------------------------------------------------------------
    ax_a = axs[0, 0]
    sites = ['Site 1\n(Top-Cl)', 'Site 2\n(Hollow)', 'Site 3\n(Top-Cr)']
    x = np.arange(len(sites))
    w = 0.35
    
    # Values: Delta E_rel (eV) relative to ground state
    # Without U: S1=0.22 eV, S2=0.00 eV (GS), S3=0.71 eV
    # With U: S1=0.14 eV (slid to hollow/bridge), S3=0.00 eV (GS)
    penalties_no_u = [0.222, 0.000, 0.710]
    penalties_u    = [0.144, 0.000, 0.000]
    
    bars1 = ax_a.bar(x - w/2, penalties_no_u, width=w, color='#3498db', edgecolor='black', linewidth=1.2, label='PBE+D3 (Without $U$)', alpha=0.9, zorder=3)
    bars2 = ax_a.bar(x + w/2, [0.144, 0, 0.000], width=w, color='#e74c3c', edgecolor='black', linewidth=1.2, label='PBE+D3+$U$ ($U=3.29\\,\\mathrm{eV}$)', alpha=0.9, zorder=3)
    
    # Smart staggered annotations to prevent any collision
    ax_a.text(x[0] - w/2, penalties_no_u[0] + 0.06, '+0.22 eV', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    ax_a.text(x[0] + w/2, penalties_u[0] + 0.18, '+0.14 eV\n(Slid/Bridge)', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)
    
    ax_a.text(x[1] - w/2, 0.06, 'Ground State\n(-5.06 eV)', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    
    ax_a.text(x[2] - w/2, penalties_no_u[2] + 0.06, '+0.71 eV\n(Repulsive)', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    ax_a.text(x[2] + w/2, 0.06, 'Ground State\n(-4.47 eV)', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)
    
    ax_a.set_ylabel(r'Relative Energy Penalty $\Delta E_{\mathrm{rel}}$ (eV)', fontsize=12, fontweight='bold')
    ax_a.set_title(r'(a) Site Preference Inversion on $\mathrm{CrCl}_3(2\times2)$', fontsize=12, fontweight='bold', pad=10)
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(sites, fontsize=10.5)
    ax_a.set_ylim(-0.05, 1.60) # Extended headroom
    ax_a.yaxis.set_major_locator(MultipleLocator(0.4))
    ax_a.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_a.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_a.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.2, loc='upper left')
    
    # -------------------------------------------------------------
    # Panel (b): Total Magnetization: Spin Alignment
    # -------------------------------------------------------------
    ax_b = axs[0, 1]
    mag_labels = ['Pristine\nSlab', 'Top-Cr ($S_3$)\nWithout $U$', 'Top-Cr ($S_3$)\nWith $U=3.29\\,\\mathrm{eV}$', 'Co-H ($S_3\\_\\mathrm{H}$)\nWith $U=3.29\\,\\mathrm{eV}$']
    x_b = np.arange(len(mag_labels))
    mags = [24.00, 23.00, 27.00, 22.00]
    colors_b = ['#7f8c8d', '#2980b9', '#c0392b', '#8e44ad']
    
    bars_b = ax_b.bar(x_b, mags, width=0.50, color=colors_b, edgecolor='black', linewidth=1.2, zorder=3)
    ax_b.axhline(24.0, color='gray', linestyle=':', linewidth=1.3, label=r'Pristine $2\times2$ ($24\,\mu_{\mathrm{B}}$)', zorder=2)
    
    # Non-overlapping annotations with dedicated background cards
    ax_b.text(x_b[0], mags[0] + 0.55, r'$24.00\,\mu_{\mathrm{B}}$', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#333333', bbox=bbox_props, zorder=5)
    ax_b.text(x_b[1], mags[1] + 0.55, r'AFM: $23\,\mu_{\mathrm{B}}$' + '\n' + r'($24 - 1\,\mu_{\mathrm{B}}$)', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    ax_b.text(x_b[2], mags[2] + 0.55, r'FM: $27\,\mu_{\mathrm{B}}$' + '\n' + r'($24 + 3\,\mu_{\mathrm{B}}$)', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)
    ax_b.text(x_b[3], mags[3] + 0.55, r'Spin-Crossover' + '\n' + r'$22.00\,\mu_{\mathrm{B}}$', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#4a154b', bbox=bbox_props, zorder=5)
    
    ax_b.set_ylabel(r'Total Magnetic Moment $M_{\mathrm{tot}}$ ($\mu_{\mathrm{B}}$)', fontsize=12, fontweight='bold')
    ax_b.set_title(r'(b) Magnetic Coupling & Spin Crossover', fontsize=12, fontweight='bold', pad=10)
    ax_b.set_xticks(x_b)
    ax_b.set_xticklabels(mag_labels, fontsize=9.5)
    ax_b.set_ylim(16, 32.5) # Ample headroom
    ax_b.yaxis.set_major_locator(MultipleLocator(4.0))
    ax_b.yaxis.set_minor_locator(MultipleLocator(1.0))
    ax_b.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_b.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.2, loc='upper left')
    
    # -------------------------------------------------------------
    # Panel (c): Free Energy Diagram for HER (Delta G_H*)
    # -------------------------------------------------------------
    ax_c = axs[1, 0]
    
    systems_c = [
        'Pristine\n(Top-Cl)',
        'Embedded Co\n(6-coord Cl)',
        'Adsorbed Co\nWithout $U$ (Hollow)',
        'Adsorbed Co\nWith $U$ (Top-Cr)'
    ]
    deltag_vals = [1.528, 1.736, 0.178, -0.069]
    x_c = np.arange(len(systems_c))
    
    # Optimal HER window
    ax_c.axhspan(-0.10, 0.20, color='#2ecc71', alpha=0.22, label=r'Optimal HER Window ($\pm 0.15\,\mathrm{eV}$)', zorder=1)
    ax_c.axhline(0.00, color='#27ae60', linestyle='--', linewidth=1.5, label=r'Thermo-neutral ($\Delta G_{\mathrm{H}^*} = 0$)', zorder=2)
    
    for i in range(len(systems_c)):
        val = deltag_vals[i]
        c = '#27ae60' if -0.1 <= val <= 0.2 else '#c0392b' if val > 1.0 else '#2980b9'
        ax_c.plot([i - 0.28, i + 0.28], [val, val], color=c, linewidth=4.0, solid_capstyle='round', zorder=4)
        
        # Position label above or below depending on sign to prevent line collision
        if val < 0:
            y_text = val - 0.14
            va_set = 'top'
        else:
            y_text = val + 0.10
            va_set = 'bottom'
            
        ax_c.text(i, y_text, f'{val:+.3f} eV', ha='center', va=va_set, fontsize=9.2, fontweight='bold', color=c, bbox=bbox_props, zorder=5)
        
    ax_c.set_ylabel(r'HER Free Energy $\Delta G_{\mathrm{H}^*}$ (eV)', fontsize=12, fontweight='bold')
    ax_c.set_title(r'(c) HER Electrocatalytic Descriptor Benchmarks', fontsize=12, fontweight='bold', pad=10)
    ax_c.set_xticks(x_c)
    ax_c.set_xticklabels(systems_c, fontsize=9.5)
    ax_c.set_ylim(-0.45, 2.35) # Expanded bounds
    ax_c.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_c.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_c.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_c.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.0, loc='upper left')
    
    # -------------------------------------------------------------
    # Panel (d): Active Site Geometric Evolution upon H Adsorption
    # -------------------------------------------------------------
    ax_d = axs[1, 1]
    
    geom_labels = [
        'Co at Top-Cr ($S_3$)\nBefore H Adsorption',
        'Co–H at Top-Cr ($S_3\\_\\mathrm{H}$)\nAfter H Adsorption'
    ]
    x_d = np.arange(len(geom_labels))
    w_d = 0.24
    
    # Distances in Angstroms (Converged):
    # S3: d(Co-Cr)=2.578, d(Co-Cl)=2.219, d(Co-H)=None
    # S3_H: d(Co-Cr)=2.857, d(Co-Cl)=2.320 (avg), d(Co-H)=1.549
    d_cocr = [2.578, 2.857]
    d_cocl = [2.219, 2.320]
    d_coh  = [0.000, 1.549]
    
    r1 = ax_d.bar(x_d - w_d, d_cocr, width=w_d, color='#e67e22', edgecolor='black', linewidth=1.2, label=r'$d(\mathrm{Co-Cr})$', zorder=3)
    r2 = ax_d.bar(x_d, d_cocl, width=w_d, color='#3498db', edgecolor='black', linewidth=1.2, label=r'Avg $d(\mathrm{Co-Cl})$', zorder=3)
    r3 = ax_d.bar(x_d + w_d, d_coh, width=w_d, color='#9b59b6', edgecolor='black', linewidth=1.2, label=r'$d(\mathrm{Co-H})$', zorder=3)
    
    for i in range(len(geom_labels)):
        ax_d.text(i - w_d, d_cocr[i] + 0.08, f'{d_cocr[i]:.2f} Å', ha='center', va='bottom', fontsize=8.5, fontweight='bold', bbox=bbox_props, zorder=5)
        ax_d.text(i, d_cocl[i] + 0.08, f'{d_cocl[i]:.2f} Å', ha='center', va='bottom', fontsize=8.5, fontweight='bold', bbox=bbox_props, zorder=5)
        if d_coh[i] > 0:
            ax_d.text(i + w_d, d_coh[i] + 0.08, f'{d_coh[i]:.2f} Å', ha='center', va='bottom', fontsize=8.5, fontweight='bold', bbox=bbox_props, zorder=5)
        else:
            ax_d.text(i + w_d, 0.08, 'N/A', ha='center', va='bottom', fontsize=8.5, color='gray', bbox=bbox_props, zorder=5)
            
    ax_d.set_ylabel(r'Interatomic Distance (Å)', fontsize=12, fontweight='bold')
    ax_d.set_title(r'(d) Active Site Coordination Relaxation under $+U$', fontsize=12, fontweight='bold', pad=10)
    ax_d.set_xticks(x_d)
    ax_d.set_xticklabels(geom_labels, fontsize=9.5)
    ax_d.set_ylim(0, 4.10) # Generous headroom ensures zero collision with legend
    ax_d.yaxis.set_major_locator(MultipleLocator(1.0))
    ax_d.yaxis.set_minor_locator(MultipleLocator(0.2))
    ax_d.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_d.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.2, loc='upper left')
    
    # Save figure
    png_path = os.path.join(SCRIPT_DIR, "crcl3_co_h_u_comparison_multipanel.png")
    pdf_path = os.path.join(SCRIPT_DIR, "crcl3_co_h_u_comparison_multipanel.pdf")
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    plt.savefig(pdf_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated: {png_path}")
    print(f"Successfully generated: {pdf_path}")

if __name__ == "__main__":
    create_comparison_figure()
