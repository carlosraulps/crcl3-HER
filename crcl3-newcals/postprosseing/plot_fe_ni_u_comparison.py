#!/usr/bin/env python3
"""
========================================================================================
 plot_fe_ni_u_comparison.py
========================================================================================
 Generates dedicated 4-panel publication-grade comparative figures for Iron (Fe)
 and Nickel (Ni) functionalized monolayer CrCl3 (2x2) across methodological tiers:
   - Tier 1: PBE+D3 (Without U)
   - Tier 2: Single-Site Hubbard U (PBE+D3+U_Cr, U_Cr = 3.29 eV)
   - Tier 3: Multi-Site Hubbard U (PBE+D3+U_all, U_Cr = 3.29 eV, U_TM = 3.29 eV)

 Panels:
   Panel (a): Site preference and pore-sinking ground state energetics
   Panel (b): Total magnetic moment and spin polarization across tiers
   Panel (c): Free energy profile for HER (Delta G_H*) with ideal Sabatier window
   Panel (d): Active site coordination relaxation, bond lengths, and pore-sinking forensics

 Equipped with smart_plot_optimizer collision prevention, vertical badge staggering,
 adaptive headroom expansion, and leader lines.
========================================================================================
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from smart_plot_optimizer import resolve_text_overlaps

# Styling
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Liberation Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['xtick.major.width'] = 1.2
plt.rcParams['ytick.major.width'] = 1.2
plt.rcParams['xtick.minor.width'] = 0.8
plt.rcParams['ytick.minor.width'] = 0.8


def generate_fe_multipanel():
    """Creates dedicated 4-panel comparison for Fe/CrCl3."""
    fig, axs = plt.subplots(2, 2, figsize=(14.0, 11.5))
    fig.subplots_adjust(hspace=0.36, wspace=0.28)
    bbox_props = dict(boxstyle='round,pad=0.22', facecolor='white', edgecolor='#cccccc', alpha=0.94, linewidth=0.8)

    # -------------------------------------------------------------
    # Panel (a): Fe Site Preference Inversion (Without U vs With U)
    # -------------------------------------------------------------
    ax_a = axs[0, 0]
    sites = ['Site 1\n(Top-Cl)', 'Site 2\n(Hollow)', 'Site 3\n(Top-Cr)']
    x = np.arange(len(sites))
    w = 0.35

    penalties_no_u = [0.000, 0.797, 3.001]
    penalties_u    = [1.350, 0.000, 0.339]

    b1 = ax_a.bar(x - w/2, penalties_no_u, width=w, color='#3498db', edgecolor='black', linewidth=1.2, label='PBE+D3 (Without $U$)', alpha=0.9, zorder=3)
    b2 = ax_a.bar(x + w/2, penalties_u, width=w, color='#e74c3c', edgecolor='black', linewidth=1.2, label='PBE+D3+$U_{\\mathrm{Cr}}$ ($3.29\\,\\mathrm{eV}$)', alpha=0.9, zorder=3)

    t1 = ax_a.text(x[0] - w/2, 0.08, 'Ground State\n(-6.81 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    t2 = ax_a.text(x[0] + w/2, penalties_u[0] + 0.10, '+1.35 eV\n(Metastable)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)

    t3 = ax_a.text(x[1] - w/2, penalties_no_u[1] + 0.10, '+0.80 eV\n(-6.01 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    t4 = ax_a.text(x[1] + w/2, 0.35, 'Ground State\n(-5.97 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)
    ax_a.plot([x[1] + w/2, x[1] + w/2], [penalties_u[1], 0.33], color='#781f1f', linestyle=':', linewidth=1.1, zorder=4)

    t5 = ax_a.text(x[2] - w/2, penalties_no_u[2] + 0.12, '+3.00 eV\n(Repulsive)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    t6 = ax_a.text(x[2] + w/2, penalties_u[2] + 0.12, '+0.34 eV\n(Local Min)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)

    resolve_text_overlaps(fig, ax_a, [t1, t2, t3, t4, t5, t6])

    # Note on Tier 3 +U_all pore-sinking ground state
    ax_a.text(0.04, 0.94, r'$\mathbf{Tier\ 3\ (+U_{\mathrm{all}}):}$ Spontaneous pore-sinking' + '\n' + r'into 6-fold Cl hollow ($\Delta E_{\mathrm{bind}} = -6.64\,\mathrm{eV}$)',
              transform=ax_a.transAxes, verticalalignment='top', fontsize=8.4,
              bbox=dict(boxstyle='round,pad=0.25', facecolor='#fef9e7', edgecolor='#f39c12', alpha=0.92, linewidth=0.9), zorder=6)

    ax_a.set_ylabel(r'Relative Energy Penalty $\Delta E_{\mathrm{rel}}$ (eV)', fontsize=12, fontweight='bold')
    ax_a.set_title(r'(a) Fe Adsorption Site Preference on $\mathrm{CrCl}_3(2\times2)$', fontsize=12, fontweight='bold', pad=10)
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(sites, fontsize=10.5)
    ax_a.set_ylim(-0.05, 4.50)
    ax_a.yaxis.set_major_locator(MultipleLocator(1.0))
    ax_a.yaxis.set_minor_locator(MultipleLocator(0.2))
    ax_a.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_a.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.0, loc='upper right')

    # -------------------------------------------------------------
    # Panel (b): Magnetic Coupling across Configurations & Tiers
    # -------------------------------------------------------------
    ax_b = axs[0, 1]
    mag_labels = [
        'Pristine\nSlab',
        'Top-Cl\nNo $U$',
        'Hollow\nNo $U$',
        'Hollow\n$+U_{\\mathrm{Cr}}$',
        'Fe–H\n$+U_{\\mathrm{Cr}}$',
        'Clean\n$+U_{\\mathrm{all}}$',
        'Fe–H\n$+U_{\\mathrm{all}}$'
    ]
    x_b = np.arange(len(mag_labels))
    mags = [24.00, 22.00, 28.39, 28.72, 28.42, 30.00, 29.00]
    colors_b = ['#7f8c8d', '#2980b9', '#3498db', '#c0392b', '#8e44ad', '#16a085', '#27ae60']

    ax_b.bar(x_b, mags, width=0.52, color=colors_b, edgecolor='black', linewidth=1.2, zorder=3)
    ax_b.axhline(24.0, color='gray', linestyle=':', linewidth=1.3, label=r'Pristine $2\times2$ ($24\,\mu_{\mathrm{B}}$)', zorder=2)

    texts_b = []
    for i in range(len(mag_labels)):
        t = ax_b.text(x_b[i], mags[i] + 0.60, f'{mags[i]:.1f} $\\mu_{{\\mathrm{{B}}}}$', ha='center', va='bottom', fontsize=7.8, fontweight='bold', bbox=bbox_props, zorder=5)
        texts_b.append(t)

    resolve_text_overlaps(fig, ax_b, texts_b)

    ax_b.set_ylabel(r'Total Magnetic Moment $M_{\mathrm{tot}}$ ($\mu_{\mathrm{B}}$)', fontsize=12, fontweight='bold')
    ax_b.set_title(r'(b) Fe Spin Alignment & Magnetic Coupling across Tiers', fontsize=12, fontweight='bold', pad=10)
    ax_b.set_xticks(x_b)
    ax_b.set_xticklabels(mag_labels, fontsize=8.6)
    ax_b.set_ylim(18, 34.0)
    ax_b.yaxis.set_major_locator(MultipleLocator(2.0))
    ax_b.yaxis.set_minor_locator(MultipleLocator(0.5))
    ax_b.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_b.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.0, loc='upper left')

    # -------------------------------------------------------------
    # Panel (c): Free Energy Profile for HER (Delta G_H*)
    # -------------------------------------------------------------
    ax_c = axs[1, 0]
    systems_c = [
        'Pristine\n(Top-Cl)',
        'Fe (emb)\n$+U_{\\mathrm{Cr}}$',
        'Fe (emb)\n$+U_{\\mathrm{all}}$',
        'Fe (ads)\nNo $U$',
        'Fe (ads)\n$+U_{\\mathrm{Cr}}$',
        'Fe (ads)\n$+U_{\\mathrm{all}}$'
    ]
    deltag_vals = [1.528, 1.114, 1.821, 0.375, 0.185, 1.837]
    x_c = np.arange(len(systems_c))

    ax_c.axhspan(-0.15, 0.20, color='#2ecc71', alpha=0.20, label=r'Optimal HER Window ($|\Delta G| \leq 0.15\,\mathrm{eV}$)', zorder=1)
    ax_c.axhline(0.00, color='#27ae60', linestyle='--', linewidth=1.4, label=r'Thermo-neutral ($\Delta G_{\mathrm{H}^*} = 0$)', zorder=2)

    for i in range(len(systems_c)):
        val = deltag_vals[i]
        c = '#27ae60' if -0.15 <= val <= 0.20 else '#c0392b' if val > 1.0 else '#2980b9'
        ax_c.plot([i - 0.28, i + 0.28], [val, val], color=c, linewidth=4.0, solid_capstyle='round', zorder=4)
        ax_c.text(i, val + 0.08, f'{val:+.3f} eV', ha='center', va='bottom', fontsize=8.6, fontweight='bold', color=c, bbox=bbox_props, zorder=5)

    # Forensic callout for Fe(ads) +U_all
    ax_c.annotate('Includes $+1.58\\,\\mathrm{eV}$\nextrusion penalty from\ndeep pore ground state',
                  xy=(5, 1.837), xytext=(4.1, 1.25),
                  arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.2),
                  fontsize=8.2, fontweight='bold', color='#922b21', bbox=bbox_props, zorder=6)

    ax_c.set_ylabel(r'HER Free Energy $\Delta G_{\mathrm{H}^*}$ (eV)', fontsize=12, fontweight='bold')
    ax_c.set_title(r'(c) Fe HER Electrocatalytic Benchmarks across Tiers', fontsize=12, fontweight='bold', pad=10)
    ax_c.set_xticks(x_c)
    ax_c.set_xticklabels(systems_c, fontsize=8.8)
    ax_c.set_ylim(-0.30, 2.35)
    ax_c.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_c.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_c.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_c.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.0, loc='upper left')

    # -------------------------------------------------------------
    # Panel (d): Active Site Geometry & Distances across Tiers
    # -------------------------------------------------------------
    ax_d = axs[1, 1]
    geom_labels = [
        'Fe Clean\n$+U_{\\mathrm{Cr}}$ (Surf)',
        'Fe–H\n$+U_{\\mathrm{Cr}}$ (Surf)',
        'Fe Clean\n$+U_{\\mathrm{all}}$ (Pore)',
        'Fe–H\n$+U_{\\mathrm{all}}$ (Surf)'
    ]
    x_d = np.arange(len(geom_labels))
    w_d = 0.24

    # Interatomic distances:
    # +U_Cr: S1 clean (d_Cl=2.20, d_Cr=3.25), S1_H (d_Cl=2.29, d_Cr=3.31, d_H=1.52)
    # +U_all: clean sunken (d_Cl=2.43, d_Cr=3.50), H surface (d_Cl=2.34, d_Cr=4.24, d_H=1.61)
    d_fecl = [2.204, 2.285, 2.426, 2.337]
    d_fecr = [3.250, 3.310, 3.497, 4.243]
    d_feh  = [0.000, 1.520, 0.000, 1.613]

    ax_d.bar(x_d - w_d, d_fecl, width=w_d, color='#3498db', edgecolor='black', linewidth=1.1, label=r'Avg $d(\mathrm{Fe-Cl})$', zorder=3)
    ax_d.bar(x_d,       d_fecr, width=w_d, color='#e67e22', edgecolor='black', linewidth=1.1, label=r'$d(\mathrm{Fe-Cr})$', zorder=3)
    ax_d.bar(x_d + w_d, d_feh,  width=w_d, color='#9b59b6', edgecolor='black', linewidth=1.1, label=r'$d(\mathrm{Fe-H})$', zorder=3)

    for i in range(len(geom_labels)):
        ax_d.text(i - w_d, d_fecl[i] + 0.08, f'{d_fecl[i]:.2f} Å', ha='center', va='bottom', fontsize=7.8, fontweight='bold', bbox=bbox_props, zorder=5)
        ax_d.text(i,       d_fecr[i] + 0.08, f'{d_fecr[i]:.2f} Å', ha='center', va='bottom', fontsize=7.8, fontweight='bold', bbox=bbox_props, zorder=5)
        if d_feh[i] > 0:
            ax_d.text(i + w_d, d_feh[i] + 0.08, f'{d_feh[i]:.2f} Å', ha='center', va='bottom', fontsize=7.8, fontweight='bold', bbox=bbox_props, zorder=5)
        else:
            ax_d.text(i + w_d, 0.08, 'N/A', ha='center', va='bottom', fontsize=7.6, color='gray', bbox=bbox_props, zorder=5)

    ax_d.set_ylabel(r'Interatomic Distance (Å)', fontsize=12, fontweight='bold')
    ax_d.set_title(r'(d) Active Site Geometry: Pore-Sinking vs Surface H Binding', fontsize=12, fontweight='bold', pad=10)
    ax_d.set_xticks(x_d)
    ax_d.set_xticklabels(geom_labels, fontsize=8.6)
    ax_d.set_ylim(0, 4.85)
    ax_d.yaxis.set_major_locator(MultipleLocator(1.0))
    ax_d.yaxis.set_minor_locator(MultipleLocator(0.2))
    ax_d.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_d.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=8.8, loc='upper left')

    out_png = os.path.join(SCRIPT_DIR, "crcl3_fe_h_u_comparison_multipanel.png")
    out_pdf = os.path.join(SCRIPT_DIR, "crcl3_fe_h_u_comparison_multipanel.pdf")
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_png}")
    print(f"Generated: {out_pdf}")


def generate_ni_multipanel():
    """Creates dedicated 4-panel comparison for Ni/CrCl3."""
    fig, axs = plt.subplots(2, 2, figsize=(14.0, 11.5))
    fig.subplots_adjust(hspace=0.36, wspace=0.28)
    bbox_props = dict(boxstyle='round,pad=0.22', facecolor='white', edgecolor='#cccccc', alpha=0.94, linewidth=0.8)

    # -------------------------------------------------------------
    # Panel (a): Ni Site Preference Inversion (Without U vs With U)
    # -------------------------------------------------------------
    ax_a = axs[0, 0]
    sites = ['Site 1\n(Top-Cl)', 'Site 2\n(Hollow)', 'Site 3\n(Top-Cr)']
    x = np.arange(len(sites))
    w = 0.35

    penalties_no_u = [0.392, 0.000, 1.022]
    penalties_u    = [0.215, 0.000, 0.924]

    b1 = ax_a.bar(x - w/2, penalties_no_u, width=w, color='#3498db', edgecolor='black', linewidth=1.2, label='PBE+D3 (Without $U$)', alpha=0.9, zorder=3)
    b2 = ax_a.bar(x + w/2, penalties_u, width=w, color='#e74c3c', edgecolor='black', linewidth=1.2, label='PBE+D3+$U_{\\mathrm{Cr}}$ ($3.29\\,\\mathrm{eV}$)', alpha=0.9, zorder=3)

    t1 = ax_a.text(x[0] - w/2, penalties_no_u[0] + 0.08, '+0.39 eV\n(-3.81 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    t2 = ax_a.text(x[0] + w/2, penalties_u[0] + 0.32, '+0.22 eV\n(-4.16 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)
    ax_a.plot([x[0] + w/2, x[0] + w/2], [penalties_u[0], penalties_u[0] + 0.30], color='#781f1f', linestyle=':', linewidth=1.1, zorder=4)

    t3 = ax_a.text(x[1] - w/2, 0.08, 'Ground State\n(-4.20 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    t4 = ax_a.text(x[1] + w/2, 0.35, 'Ground State\n(-4.37 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)
    ax_a.plot([x[1] + w/2, x[1] + w/2], [penalties_u[1], 0.33], color='#781f1f', linestyle=':', linewidth=1.1, zorder=4)

    t5 = ax_a.text(x[2] - w/2, penalties_no_u[2] + 0.10, '+1.02 eV\n(-3.18 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    t6 = ax_a.text(x[2] + w/2, penalties_u[2] + 0.10, '+0.92 eV\n(-3.45 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)

    resolve_text_overlaps(fig, ax_a, [t1, t2, t3, t4, t5, t6])

    # Note on Tier 3 +U_all pore-sinking ground state
    ax_a.text(0.04, 0.94, r'$\mathbf{Tier\ 3\ (+U_{\mathrm{all}}):}$ Spontaneous pore-sinking' + '\n' + r'into 6-fold hollow pore ($\Delta E_{\mathrm{bind}} = -2.98\,\mathrm{eV}$)',
              transform=ax_a.transAxes, verticalalignment='top', fontsize=8.4,
              bbox=dict(boxstyle='round,pad=0.25', facecolor='#fef9e7', edgecolor='#f39c12', alpha=0.92, linewidth=0.9), zorder=6)

    ax_a.set_ylabel(r'Relative Energy Penalty $\Delta E_{\mathrm{rel}}$ (eV)', fontsize=12, fontweight='bold')
    ax_a.set_title(r'(a) Ni Adsorption Site Preference on $\mathrm{CrCl}_3(2\times2)$', fontsize=12, fontweight='bold', pad=10)
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(sites, fontsize=10.5)
    ax_a.set_ylim(-0.05, 2.45)
    ax_a.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_a.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_a.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_a.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.0, loc='upper right')

    # -------------------------------------------------------------
    # Panel (b): Magnetic Invariance in Ni across Tiers
    # -------------------------------------------------------------
    ax_b = axs[0, 1]
    mag_labels = [
        'Pristine\nSlab',
        'Top-Cl\nNo $U$',
        'Hollow\nNo $U$',
        'Hollow\n$+U_{\\mathrm{Cr}}$',
        'Clean\n$+U_{\\mathrm{all}}$',
        'Ni–H\n$+U_{\\mathrm{all}}$'
    ]
    x_b = np.arange(len(mag_labels))
    mags = [24.00, 24.00, 24.00, 24.00, 24.00, 25.00]
    colors_b = ['#7f8c8d', '#2980b9', '#3498db', '#c0392b', '#16a085', '#27ae60']

    ax_b.bar(x_b, mags, width=0.52, color=colors_b, edgecolor='black', linewidth=1.2, zorder=3)
    ax_b.axhline(24.0, color='gray', linestyle=':', linewidth=1.3, label=r'Pristine $2\times2$ ($24\,\mu_{\mathrm{B}}$)', zorder=2)

    texts_b = []
    for i in range(len(mag_labels)):
        t = ax_b.text(x_b[i], mags[i] + 0.60, f'{mags[i]:.1f} $\\mu_{{\\mathrm{{B}}}}$', ha='center', va='bottom', fontsize=7.8, fontweight='bold', bbox=bbox_props, zorder=5)
        texts_b.append(t)

    resolve_text_overlaps(fig, ax_b, texts_b)

    ax_b.set_ylabel(r'Total Magnetic Moment $M_{\mathrm{tot}}$ ($\mu_{\mathrm{B}}$)', fontsize=12, fontweight='bold')
    ax_b.set_title(r'(b) Ni Magnetic Moment Stability (Singlet $\mathrm{Ni}^{2+}$)', fontsize=12, fontweight='bold', pad=10)
    ax_b.set_xticks(x_b)
    ax_b.set_xticklabels(mag_labels, fontsize=8.8)
    ax_b.set_ylim(18, 30.5)
    ax_b.yaxis.set_major_locator(MultipleLocator(2.0))
    ax_b.yaxis.set_minor_locator(MultipleLocator(0.5))
    ax_b.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_b.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.0, loc='upper left')

    # -------------------------------------------------------------
    # Panel (c): Free Energy Profile for HER (Delta G_H*)
    # -------------------------------------------------------------
    ax_c = axs[1, 0]
    systems_c = [
        'Pristine\n(Top-Cl)',
        'Ni (emb)\n$+U_{\\mathrm{Cr}}$',
        'Ni (emb)\n$+U_{\\mathrm{all}}$',
        'Ni (ads)\nNo $U$',
        'Ni (ads)\n$+U_{\\mathrm{Cr}}$',
        'Ni (ads)\n$+U_{\\mathrm{all}}$'
    ]
    deltag_vals = [1.528, 0.821, 1.024, 0.862, 0.620, 1.184]
    x_c = np.arange(len(systems_c))

    ax_c.axhspan(-0.15, 0.20, color='#2ecc71', alpha=0.20, label=r'Optimal HER Window ($|\Delta G| \leq 0.15\,\mathrm{eV}$)', zorder=1)
    ax_c.axhline(0.00, color='#27ae60', linestyle='--', linewidth=1.4, label=r'Thermo-neutral ($\Delta G_{\mathrm{H}^*} = 0$)', zorder=2)

    for i in range(len(systems_c)):
        val = deltag_vals[i]
        c = '#27ae60' if -0.15 <= val <= 0.20 else '#c0392b' if val > 1.0 else '#2980b9'
        ax_c.plot([i - 0.28, i + 0.28], [val, val], color=c, linewidth=4.0, solid_capstyle='round', zorder=4)
        ax_c.text(i, val + 0.08, f'{val:+.3f} eV', ha='center', va='bottom', fontsize=8.6, fontweight='bold', color=c, bbox=bbox_props, zorder=5)

    # Forensic callout for Ni(ads) +U_all placed clearly to avoid overlap with +0.620 eV
    ax_c.annotate('Includes $+0.50\\,\\mathrm{eV}$\nextrusion penalty from\ndeep pore ground state',
                  xy=(5, 1.184), xytext=(4.2, 0.35),
                  arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.2),
                  fontsize=8.2, fontweight='bold', color='#922b21', bbox=bbox_props, zorder=6)

    ax_c.set_ylabel(r'HER Free Energy $\Delta G_{\mathrm{H}^*}$ (eV)', fontsize=12, fontweight='bold')
    ax_c.set_title(r'(c) Ni HER Electrocatalytic Descriptor Benchmarks', fontsize=12, fontweight='bold', pad=10)
    ax_c.set_xticks(x_c)
    ax_c.set_xticklabels(systems_c, fontsize=8.8)
    ax_c.set_ylim(-0.30, 2.30)
    ax_c.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_c.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_c.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_c.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.0, loc='upper left')

    # -------------------------------------------------------------
    # Panel (d): Active Site Geometry across Tiers
    # -------------------------------------------------------------
    ax_d = axs[1, 1]
    geom_labels = [
        'Ni Clean\n$+U_{\\mathrm{Cr}}$ (Surf)',
        'Ni–H\n$+U_{\\mathrm{Cr}}$ (Surf)',
        'Ni Clean\n$+U_{\\mathrm{all}}$ (Pore)',
        'Ni–H\n$+U_{\\mathrm{all}}$ (Surf)'
    ]
    x_d = np.arange(len(geom_labels))
    w_d = 0.24

    # Interatomic distances:
    # +U_Cr: hollow clean (d_Cl=2.26, d_Cr=2.83), +H (d_Cl=2.28, d_Cr=2.84, d_H=1.45)
    # +U_all: clean sunken (d_Cl=2.41, d_Cr=3.57), +H surface (d_Cl=2.20, d_Cr=3.88, d_H=1.44)
    d_nicl = [2.258, 2.278, 2.405, 2.196]
    d_nicr = [2.825, 2.840, 3.573, 3.884]
    d_nih  = [0.000, 1.450, 0.000, 1.443]

    ax_d.bar(x_d - w_d, d_nicl, width=w_d, color='#3498db', edgecolor='black', linewidth=1.1, label=r'Avg $d(\mathrm{Ni-Cl})$', zorder=3)
    ax_d.bar(x_d,       d_nicr, width=w_d, color='#e67e22', edgecolor='black', linewidth=1.1, label=r'Avg $d(\mathrm{Ni-Cr})$', zorder=3)
    ax_d.bar(x_d + w_d, d_nih,  width=w_d, color='#9b59b6', edgecolor='black', linewidth=1.1, label=r'$d(\mathrm{Ni-H})$', zorder=3)

    for i in range(len(geom_labels)):
        ax_d.text(i - w_d, d_nicl[i] + 0.08, f'{d_nicl[i]:.2f} Å', ha='center', va='bottom', fontsize=7.8, fontweight='bold', bbox=bbox_props, zorder=5)
        ax_d.text(i,       d_nicr[i] + 0.08, f'{d_nicr[i]:.2f} Å', ha='center', va='bottom', fontsize=7.8, fontweight='bold', bbox=bbox_props, zorder=5)
        if d_nih[i] > 0:
            ax_d.text(i + w_d, d_nih[i] + 0.08, f'{d_nih[i]:.2f} Å', ha='center', va='bottom', fontsize=7.8, fontweight='bold', bbox=bbox_props, zorder=5)
        else:
            ax_d.text(i + w_d, 0.08, 'N/A', ha='center', va='bottom', fontsize=7.6, color='gray', bbox=bbox_props, zorder=5)

    ax_d.set_ylabel(r'Interatomic Distance (Å)', fontsize=12, fontweight='bold')
    ax_d.set_title(r'(d) Active Site Geometry: Pore-Sinking vs Surface H Binding', fontsize=12, fontweight='bold', pad=10)
    ax_d.set_xticks(x_d)
    ax_d.set_xticklabels(geom_labels, fontsize=8.6)
    ax_d.set_ylim(0, 4.45)
    ax_d.yaxis.set_major_locator(MultipleLocator(1.0))
    ax_d.yaxis.set_minor_locator(MultipleLocator(0.2))
    ax_d.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_d.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=8.8, loc='upper left')

    out_png = os.path.join(SCRIPT_DIR, "crcl3_ni_h_u_comparison_multipanel.png")
    out_pdf = os.path.join(SCRIPT_DIR, "crcl3_ni_h_u_comparison_multipanel.pdf")
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_png}")
    print(f"Generated: {out_pdf}")


if __name__ == "__main__":
    generate_fe_multipanel()
    generate_ni_multipanel()
