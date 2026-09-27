#!/usr/bin/env python3
"""
plot_pristine_crcl3_u_comparison.py

Generates publication-quality comparative figures illustrating the fundamental effect
of Hubbard U (U = 3.29 eV) and van der Waals dispersion (DFT-D3) on pristine monolayer CrCl3:
  Panel (a): Electronic Band Gap Opening (Spin-Up and Spin-Down Channels: Pure PBE vs PBE+D3 vs PBE+D3+U)
  Panel (b): Octahedral Structural Dilation (Cr-Cl bond length and Monolayer Thickness h)
  Panel (c): Cohesive Energetics per Formula Unit & Dispersion Energy Breakdown
  Panel (d): Magnetic Moment & Supercell Size Convergence (1x1, 2x2, 3x3)

Equipped with smart_plot_optimizer collision prevention & adaptive headroom.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

# Ensure script dir in path for smart_plot_optimizer
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from smart_plot_optimizer import (
    expand_headroom_for_annotations,
    auto_stagger_bar_labels,
    resolve_text_overlaps
)

# Styling adhering to publication guidelines
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Liberation Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['xtick.major.width'] = 1.2
plt.rcParams['ytick.major.width'] = 1.2
plt.rcParams['xtick.minor.width'] = 0.8
plt.rcParams['ytick.minor.width'] = 0.8

def create_pristine_figure():
    fig, axs = plt.subplots(2, 2, figsize=(13.5, 11))
    fig.subplots_adjust(hspace=0.32, wspace=0.28)
    
    bbox_props = dict(boxstyle='round,pad=0.25', facecolor='white', edgecolor='#cccccc', alpha=0.92, linewidth=0.8)
    
    # -------------------------------------------------------------
    # Panel (a): Band Gap Opening (Majority & Minority Spin Channels)
    # -------------------------------------------------------------
    ax_a = axs[0, 0]
    methods = ['Pure PBE\n(No vdW, $U=0$)', 'PBE+D3\n(vdW, $U=0$)', 'PBE+D3+$U$\n($U=3.29\\,\\mathrm{eV}$)']
    x = np.arange(len(methods))
    w = 0.35
    
    # Band gaps (eV) from VASP eigenvalue calculations:
    # Pure PBE: Spin-1 = 1.762 eV, Spin-2 = 3.334 eV
    # PBE+D3:   Spin-1 = 1.771 eV, Spin-2 = 3.345 eV
    # PBE+D3+U: Spin-1 = 2.582 eV, Spin-2 = 4.149 eV
    gap_spin1 = [1.762, 1.771, 2.582]
    gap_spin2 = [3.334, 3.345, 4.149]
    
    bars_s1 = ax_a.bar(x - w/2, gap_spin1, width=w, color='#3498db', edgecolor='black', linewidth=1.2, label='Majority Spin ($E_g^{\\uparrow}$)', alpha=0.9, zorder=3)
    bars_s2 = ax_a.bar(x + w/2, gap_spin2, width=w, color='#9b59b6', edgecolor='black', linewidth=1.2, label='Minority Spin ($E_g^{\\downarrow}$)', alpha=0.9, zorder=3)
    
    # Annotations with adaptive staggering
    for rect, val in zip(bars_s1, gap_spin1):
        ax_a.text(rect.get_x() + rect.get_width()/2.0, rect.get_height() + 0.08,
                  f'{val:.2f} eV', ha='center', va='bottom', fontsize=9.0, fontweight='bold',
                  color='#1a5276', bbox=bbox_props, zorder=5)
        
    for rect, val in zip(bars_s2, gap_spin2):
        ax_a.text(rect.get_x() + rect.get_width()/2.0, rect.get_height() + 0.08,
                  f'{val:.2f} eV', ha='center', va='bottom', fontsize=9.0, fontweight='bold',
                  color='#5b2c6f', bbox=bbox_props, zorder=5)
        
    # Band gap opening badge - placed with ample clearance in upper center-left
    delta_eg = gap_spin1[2] - gap_spin1[1]
    pct = (delta_eg / gap_spin1[1]) * 100.0
    ax_a.annotate(f'Hubbard Gap Opening:\n$\\Delta E_g = +{delta_eg:.2f}\\,\\mathrm{{eV}}$ (+{pct:.1f}%)',
                  xy=(x[2] - w/2, gap_spin1[2]), xytext=(x[1] - 0.25, 4.25),
                  arrowprops=dict(arrowstyle="->", color='#c0392b', lw=1.5, connectionstyle="arc3,rad=-0.15"),
                  fontsize=8.5, fontweight='bold', color='#c0392b', bbox=bbox_props, zorder=6)
    
    ax_a.set_ylabel('Electronic Band Gap $E_g$ (eV)', fontsize=11, fontweight='bold')
    ax_a.set_title('(a) Electronic Band Gap Opening via On-Site Coulomb $U$', fontsize=11.5, fontweight='bold', pad=10)
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(methods, fontsize=9.5)
    ax_a.set_ylim(0, 5.2)
    ax_a.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax_a.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)
    ax_a.legend(frameon=True, facecolor='white', edgecolor='#cccccc', framealpha=0.95, loc='upper left', fontsize=9.5)

    # -------------------------------------------------------------
    # Panel (b): Octahedral Geometric Dilation (d(Cr-Cl) & Thickness)
    # -------------------------------------------------------------
    ax_b = axs[0, 1]
    # Metrics:
    # d(Cr-Cl): Pure PBE = 2.3568 A, PBE+D3 = 2.3530 A, PBE+D3+U = 2.3761 A
    # Thickness h: Pure PBE = 2.6714 A, PBE+D3 = 2.6546 A, PBE+D3+U = 2.7107 A
    d_cr_cl = [2.3568, 2.3530, 2.3761]
    thickness = [2.6714, 2.6546, 2.7107]
    
    bars_d = ax_b.bar(x - w/2, d_cr_cl, width=w, color='#1abc9c', edgecolor='black', linewidth=1.2, label='$d(\\mathrm{Cr-Cl})$ Bond Length (Å)', alpha=0.9, zorder=3)
    bars_h = ax_b.bar(x + w/2, thickness, width=w, color='#e67e22', edgecolor='black', linewidth=1.2, label='Monolayer Thickness $h$ (Å)', alpha=0.9, zorder=3)
    
    for rect, val in zip(bars_d, d_cr_cl):
        ax_b.text(rect.get_x() + rect.get_width()/2.0, rect.get_height() + 0.03,
                  f'{val:.4f} Å', ha='center', va='bottom', fontsize=8.5, fontweight='bold',
                  color='#0e6251', bbox=bbox_props, zorder=5)
        
    for rect, val in zip(bars_h, thickness):
        ax_b.text(rect.get_x() + rect.get_width()/2.0, rect.get_height() + 0.03,
                  f'{val:.4f} Å', ha='center', va='bottom', fontsize=8.5, fontweight='bold',
                  color='#7e5109', bbox=bbox_props, zorder=5)
        
    # Structural expansion callout card placed cleanly in top center-right
    ax_b.text(0.68, 0.94,
              'Hubbard $U$ Structural Effect:\n'
              '• $d(\\mathrm{Cr-Cl})$ expands: $+0.023\\,\\mathrm{\\AA}$ (+1.0%)\n'
              '• Layer thickness $h$ dilates: $+0.056\\,\\mathrm{\\AA}$ (+2.1%)\n'
              '• $3d$ localization reduces covalent back-bonding',
              transform=ax_b.transAxes, fontsize=8.2, va='top', ha='center',
              bbox=dict(boxstyle='round,pad=0.35', facecolor='#fef9e7', edgecolor='#f39c12', alpha=0.95),
              zorder=6)
    
    ax_b.set_ylabel('Structural Distance (Å)', fontsize=11, fontweight='bold')
    ax_b.set_title('(b) Octahedral Lattice Relaxation & Cage Dilation', fontsize=11.5, fontweight='bold', pad=10)
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(methods, fontsize=9.5)
    ax_b.set_ylim(2.15, 3.15)
    ax_b.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax_b.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)
    ax_b.legend(frameon=True, facecolor='white', edgecolor='#cccccc', framealpha=0.95, loc='upper left', fontsize=9.5)

    # -------------------------------------------------------------
    # Panel (c): Cohesive Energetics per Formula Unit & vdW Breakdown
    # -------------------------------------------------------------
    ax_c = axs[1, 0]
    # Energies per formula unit (eV/f.u.):
    # Pure PBE = -19.5359 eV/f.u.
    # PBE+D3   = -20.2634 eV/f.u.  (vdW adds -0.7275 eV/f.u.)
    # PBE+D3+U = -18.4130 eV/f.u.  (Coulomb U penalty +1.8504 eV/f.u.)
    e_fu = [-19.5359, -20.2634, -18.4130]
    bar_c = ax_c.bar(x, e_fu, width=0.45, color=['#7f8c8d', '#2980b9', '#c0392b'],
                     edgecolor='black', linewidth=1.2, alpha=0.9, zorder=3)
    
    for rect, val in zip(bar_c, e_fu):
        ax_c.text(rect.get_x() + rect.get_width()/2.0, val - 0.40,
                  f'{val:.4f}\neV/f.u.', ha='center', va='top', fontsize=9.0, fontweight='bold',
                  color='white' if val < -19.0 else '#2c3e50',
                  bbox=dict(boxstyle='round,pad=0.2', facecolor='#2c3e50', edgecolor='none', alpha=0.85),
                  zorder=5)
        
    # Dispersion energy bracket
    ax_c.annotate('vdW Stabilization\n$\\Delta E_{\\mathrm{disp}} = -0.73\\,\\mathrm{eV/f.u.}$',
                  xy=(1, -20.2634), xytext=(0.3, -21.4),
                  arrowprops=dict(arrowstyle="->", color='#2980b9', lw=1.5),
                  fontsize=8.5, fontweight='bold', color='#1f618d', bbox=bbox_props, zorder=6)
    
    # Hubbard penalty bracket
    ax_c.annotate('Hubbard $+U$ Shift\n$\\Delta E_U = +1.85\\,\\mathrm{eV/f.u.}$',
                  xy=(2, -18.4130), xytext=(1.4, -17.2),
                  arrowprops=dict(arrowstyle="->", color='#c0392b', lw=1.5),
                  fontsize=8.5, fontweight='bold', color='#922b21', bbox=bbox_props, zorder=6)
    
    ax_c.set_ylabel('Total Energy per F.U. (eV/f.u.)', fontsize=11, fontweight='bold')
    ax_c.set_title('(c) Ground-State Energetics & Dispersion Contribution', fontsize=11.5, fontweight='bold', pad=10)
    ax_c.set_xticks(x)
    ax_c.set_xticklabels(methods, fontsize=9.5)
    ax_c.set_ylim(-22.2, -16.0)
    ax_c.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax_c.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)

    # -------------------------------------------------------------
    # Panel (d): Magnetic Robustness & Supercell Size Invariance
    # -------------------------------------------------------------
    ax_d = axs[1, 1]
    # Supercell sizes: 1x1, 2x2, 3x3
    supercells = ['Primitive $1\\times1$\n(2 Cr atoms)', 'Supercell $2\\times2$\n(8 Cr atoms)', 'Supercell $3\\times3$\n(18 Cr atoms)']
    x_sc = np.arange(len(supercells))
    
    # Per-Cr magnetic moment (mu_B / Cr)
    mag_per_cr = [3.000, 3.000, 3.000]
    # Total cell magnetization (mu_B)
    tot_mag = [6.000, 24.000, 54.000]
    
    ax_d2 = ax_d.twinx()
    
    line1 = ax_d.plot(x_sc, mag_per_cr, marker='s', markersize=9, linewidth=2.0, color='#e74c3c', label='Cr Spin Moment ($3.00\\,\\mu_B$/atom)', zorder=4)
    line2 = ax_d2.plot(x_sc, tot_mag, marker='o', markersize=9, linewidth=2.0, color='#2c3e50', linestyle='--', label='Total Cell Magnetization ($M_{\\mathrm{tot}}$)', zorder=4)
    
    for i, (m, t) in enumerate(zip(mag_per_cr, tot_mag)):
        ax_d.text(x_sc[i], m + 0.12, f'{m:.2f} $\\mu_B$', ha='center', va='bottom', fontsize=9.0, fontweight='bold', color='#c0392b', bbox=bbox_props, zorder=6)
        ax_d2.text(x_sc[i], t - 4.5, f'{t:.0f} $\\mu_B$', ha='center', va='top', fontsize=9.0, fontweight='bold', color='#2c3e50', bbox=bbox_props, zorder=6)
        
    ax_d.set_ylabel('Local Moment per Cr ($\\mu_B$ / atom)', fontsize=11, fontweight='bold', color='#c0392b')
    ax_d2.set_ylabel('Total Supercell Moment ($\\mu_B$)', fontsize=11, fontweight='bold', color='#2c3e50')
    ax_d.tick_params(axis='y', labelcolor='#c0392b')
    ax_d2.tick_params(axis='y', labelcolor='#2c3e50')
    ax_d.set_title('(d) High-Spin $S=3/2$ Magnetism & Size Scaling', fontsize=11.5, fontweight='bold', pad=10)
    ax_d.set_xticks(x_sc)
    ax_d.set_xticklabels(supercells, fontsize=9.5)
    ax_d.set_ylim(2.5, 3.6)
    ax_d2.set_ylim(0, 65)
    ax_d.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)
    
    # Combined legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax_d.legend(lines, labels, frameon=True, facecolor='white', edgecolor='#cccccc', framealpha=0.95, loc='upper left', fontsize=9.0)

    # Save outputs
    out_png = os.path.join(SCRIPT_DIR, 'pristine_crcl3_u_comparison.png')
    out_pdf = os.path.join(SCRIPT_DIR, 'pristine_crcl3_u_comparison.pdf')
    plt.savefig(out_png, dpi=350, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()
    
    print(f"Generated pristine CrCl3 comparison plot:")
    print(f"  PNG: {out_png}")
    print(f"  PDF: {out_pdf}")

if __name__ == '__main__':
    create_pristine_figure()
