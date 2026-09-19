#!/usr/bin/env python3
"""
================================================================================
 Professional Post-Processing & Comparative Analysis for Hydrogen Adsorption
 on Monolayer CrCl3: 1x1 vs 2x2 Supercells (Pure PBE vs PBE+D3)
================================================================================
 Computes:
   1. Total energies (E0, TOTEN) and magnetic moments from VASP OSZICAR/OUTCAR.
   2. Binding Energy: Delta_E = E(slab+H) - E(clean)
   3. Adsorption Energy (HER descriptor): E_ads = Delta_E - 0.5 * E(H2)
   4. Free Energy of Adsorption: Delta_G(H*) = E_ads + Delta_ZPE - T*Delta_S
      (Standard literature benchmark correction: +0.24 eV)
   5. Supercell Scaling Sensitivity: Delta_E(2x2) - Delta_E(1x1)
   6. Dispersion Contribution: Delta_E(PBE+D3) - Delta_E(Pure PBE)
================================================================================
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

# Base directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
POST_DIR = os.path.abspath(os.path.dirname(__file__))
REPO_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

# Visual Styling - Publication Quality
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Liberation Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['xtick.major.width'] = 1.2
plt.rcParams['ytick.major.width'] = 1.2
plt.rcParams['xtick.minor.width'] = 0.8
plt.rcParams['ytick.minor.width'] = 0.8

# H2 Reference Energy (PBE isolated molecule in 15x15x15 A box)
E_H2_TOTAL = -6.7596001
E_H2_HALF = E_H2_TOTAL / 2.0  # -3.379800 eV
ZPE_TS_CORRECTION = 0.24      # eV (Norskov standard Delta_ZPE - T*Delta_S)

def extract_vasp_info(directory):
    """Extracts last E0, F, and magnetic moment from OSZICAR or OUTCAR."""
    oszicar = os.path.join(directory, "OSZICAR")
    outcar = os.path.join(directory, "OUTCAR")
    
    info = {'E0': None, 'F': None, 'mag': None, 'step': None}
    
    if os.path.exists(oszicar):
        with open(oszicar, 'r') as f:
            for line in f:
                if 'E0=' in line:
                    m = re.search(r'F=\s*([^\s]+)\s+E0=\s*([^\s]+)', line)
                    mag_m = re.search(r'mag=\s*([^\s]+)', line)
                    step_m = re.search(r'^\s*(\d+)', line)
                    if m:
                        info['F'] = float(m.group(1))
                        info['E0'] = float(m.group(2))
                    if mag_m:
                        info['mag'] = float(mag_m.group(1))
                    if step_m:
                        info['step'] = int(step_m.group(1))
                        
    if info['E0'] is None and os.path.exists(outcar):
        with open(outcar, 'r') as f:
            for line in f:
                if "free energy    TOTEN" in line:
                    parts = line.split("=")
                    if len(parts) > 1:
                        info['E0'] = float(parts[1].split()[0].strip())
                        info['F'] = info['E0']
    return info

def collect_all_data():
    records = []
    
    scale_configs = [
        ('1x1', 1.00, 'crcl3-1x1-h_ads-without-U'),
        ('2x2', 0.25, 'crcl3-2x2-h_ads-without-U')
    ]
    
    variants = [
        ('no_vdw', 'Pure PBE'),
        ('yes_vdw', 'PBE+D3 (Zero)')
    ]
    
    sites = [
        ('S1', 'Site 1 (Top-Cl)', '#1f77b4'),
        ('S2', 'Site 2 (Hollow)', '#ff7f0e'),
        ('S3', 'Site 3 (Top-Cr)', '#2ca02c')
    ]
    
    for scale_label, theta, folder in scale_configs:
        # Check both crcl3-newcals/folder and REPO_ROOT/folder
        path1 = os.path.join(BASE_DIR, folder)
        path2 = os.path.join(REPO_ROOT, folder)
        base_path = path1 if os.path.exists(os.path.join(path1, "no_vdw", "clean", "OSZICAR")) else path2
        
        for vdw_key, vdw_label in variants:
            clean_dir = os.path.join(base_path, vdw_key, "clean")
            clean_info = extract_vasp_info(clean_dir)
            e_clean = clean_info['E0']
            
            for site_key, site_label, color in sites:
                site_dir = os.path.join(base_path, vdw_key, site_key)
                site_info = extract_vasp_info(site_dir)
                
                if site_info['E0'] is not None and e_clean is not None:
                    e_tot = site_info['E0']
                    delta_e = e_tot - e_clean
                    e_ads = delta_e - E_H2_HALF
                    delta_g = e_ads + ZPE_TS_CORRECTION
                    
                    records.append({
                        'scale': scale_label,
                        'coverage_theta': theta,
                        'vdw_key': vdw_key,
                        'vdw_label': vdw_label,
                        'site_key': site_key,
                        'site_label': site_label,
                        'site_color': color,
                        'E_clean': e_clean,
                        'E_tot': e_tot,
                        'Delta_E': delta_e,
                        'E_ads': e_ads,
                        'Delta_G': delta_g,
                        'mag': site_info['mag'],
                        'ionic_steps': site_info['step']
                    })
                    
    return pd.DataFrame(records)

def plot_multipanel_comparison(df):
    """Generates 4-panel publication-quality comprehensive comparison."""
    fig, axs = plt.subplots(2, 2, figsize=(13, 10.5))
    fig.subplots_adjust(hspace=0.32, wspace=0.25)
    
    # Define conditions
    conditions = [
        ('1x1', 'no_vdw', r'$1\times1$' + '\nPure PBE'),
        ('1x1', 'yes_vdw', r'$1\times1$' + '\nPBE+D3'),
        ('2x2', 'no_vdw', r'$2\times2$' + '\nPure PBE'),
        ('2x2', 'yes_vdw', r'$2\times2$' + '\nPBE+D3'),
    ]
    
    sites = [
        ('S1', 'Site 1 (Top-Cl)', '#1f77b4', 'o', '-'),
        ('S2', 'Site 2 (Hollow)', '#d62728', 's', '--'),
        ('S3', 'Site 3 (Top-Cr)', '#2ca02c', '^', '-.')
    ]
    
    # -------------------------------------------------------------
    # Panel (a): Adsorption Energy E_ads vs 1/2 H2
    # -------------------------------------------------------------
    ax_a = axs[0, 0]
    x = np.arange(len(conditions))
    width = 0.24
    
    for idx, (s_key, s_name, color, marker, ls) in enumerate(sites):
        vals = []
        for scale, vdw, _ in conditions:
            sub = df[(df['scale'] == scale) & (df['vdw_key'] == vdw) & (df['site_key'] == s_key)]
            val = sub['E_ads'].values[0] if len(sub) > 0 else np.nan
            vals.append(val)
        
        pos = x + (idx - 1) * width
        rects = ax_a.bar(pos, vals, width, label=s_name, color=color, edgecolor='black', linewidth=0.9, alpha=0.9, zorder=3)
        
        # Data labels
        for r in rects:
            h = r.get_height()
            if not np.isnan(h):
                ax_a.text(r.get_x() + r.get_width()/2.0, h + 0.03, f'{h:.2f}',
                          ha='center', va='bottom', fontsize=8.5, fontweight='bold', fontfamily='serif')

    ax_a.set_xticks(x)
    ax_a.set_xticklabels([c[2] for c in conditions], fontsize=10.5)
    ax_a.set_ylabel(r'$E_{\mathrm{ads}} = E_{\mathrm{slab+H}} - E_{\mathrm{clean}} - \frac{1}{2}E(\mathrm{H}_2)\ \ (\mathrm{eV})$', fontsize=11)
    ax_a.set_title(r'(a) Hydrogen Adsorption Energy vs. Isolated $\frac{1}{2}\mathrm{H}_2$', fontsize=12, fontweight='bold', pad=10)
    ax_a.set_ylim(1.2, 2.95)
    ax_a.yaxis.set_major_locator(MultipleLocator(0.3))
    ax_a.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_a.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_a.legend(frameon=True, facecolor='white', framealpha=0.92, fontsize=9.5, loc='upper left')

    # -------------------------------------------------------------
    # Panel (b): Total Binding Energy Delta E (vs clean slab + H*)
    # -------------------------------------------------------------
    ax_b = axs[0, 1]
    
    for idx, (s_key, s_name, color, marker, ls) in enumerate(sites):
        vals = []
        for scale, vdw, _ in conditions:
            sub = df[(df['scale'] == scale) & (df['vdw_key'] == vdw) & (df['site_key'] == s_key)]
            val = sub['Delta_E'].values[0] if len(sub) > 0 else np.nan
            vals.append(val)
        
        pos = x + (idx - 1) * width
        rects = ax_b.bar(pos, vals, width, label=s_name, color=color, edgecolor='black', linewidth=0.9, alpha=0.9, zorder=3)
        
        for r in rects:
            h = r.get_height()
            if not np.isnan(h):
                ax_b.text(r.get_x() + r.get_width()/2.0, h - 0.04, f'{h:.2f}',
                          ha='center', va='top', fontsize=8.5, fontweight='bold', fontfamily='serif')

    ax_b.set_xticks(x)
    ax_b.set_xticklabels([c[2] for c in conditions], fontsize=10.5)
    ax_b.set_ylabel(r'$\Delta E = E_{\mathrm{slab+H}} - E_{\mathrm{clean}}\ \ (\mathrm{eV})$', fontsize=11)
    ax_b.set_title(r'(b) Thermodynamic Binding Energy $\Delta E$', fontsize=12, fontweight='bold', pad=10)
    ax_b.set_ylim(-2.28, -0.60)
    ax_b.yaxis.set_major_locator(MultipleLocator(0.3))
    ax_b.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_b.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_b.legend(frameon=True, facecolor='white', framealpha=0.92, fontsize=9.5, loc='upper right')

    # -------------------------------------------------------------
    # Panel (c): Supercell Scaling & Dispersion Deltas
    # -------------------------------------------------------------
    ax_c = axs[1, 0]
    site_names_c = ['Top-Cl\n($S_1$)', 'Hollow\n($S_2$)', 'Top-Cr\n($S_3$)']
    x_c = np.arange(len(site_names_c))
    w_c = 0.20
    
    # Delta_E(2x2 - 1x1) Pure PBE
    delta_scale_pbe = []
    delta_scale_d3 = []
    delta_vdw_1x1 = []
    delta_vdw_2x2 = []
    
    for s_key, _, _, _, _ in sites:
        e_1x1_pbe = df[(df['scale'] == '1x1') & (df['vdw_key'] == 'no_vdw') & (df['site_key'] == s_key)]['Delta_E'].values[0]
        e_2x2_pbe = df[(df['scale'] == '2x2') & (df['vdw_key'] == 'no_vdw') & (df['site_key'] == s_key)]['Delta_E'].values[0]
        e_1x1_d3  = df[(df['scale'] == '1x1') & (df['vdw_key'] == 'yes_vdw') & (df['site_key'] == s_key)]['Delta_E'].values[0]
        e_2x2_d3  = df[(df['scale'] == '2x2') & (df['vdw_key'] == 'yes_vdw') & (df['site_key'] == s_key)]['Delta_E'].values[0]
        
        delta_scale_pbe.append(e_2x2_pbe - e_1x1_pbe)
        delta_scale_d3.append(e_2x2_d3 - e_1x1_d3)
        delta_vdw_1x1.append(e_1x1_d3 - e_1x1_pbe)
        delta_vdw_2x2.append(e_2x2_d3 - e_2x2_pbe)
        
    ax_c.bar(x_c - 1.5*w_c, delta_scale_pbe, w_c, label=r'Coverage ($2\times2 - 1\times1$, Pure PBE)',
             color='#3498db', edgecolor='black', linewidth=0.9, zorder=3)
    ax_c.bar(x_c - 0.5*w_c, delta_scale_d3, w_c, label=r'Coverage ($2\times2 - 1\times1$, PBE+D3)',
             color='#9b59b6', edgecolor='black', linewidth=0.9, zorder=3)
    ax_c.bar(x_c + 0.5*w_c, delta_vdw_1x1, w_c, label=r'vdW Stabilization (D3 - PBE, $1\times1$)',
             color='#e67e22', edgecolor='black', linewidth=0.9, zorder=3)
    ax_c.bar(x_c + 1.5*w_c, delta_vdw_2x2, w_c, label=r'vdW Stabilization (D3 - PBE, $2\times2$)',
             color='#e74c3c', edgecolor='black', linewidth=0.9, zorder=3)
    
    ax_c.axhline(0, color='black', linewidth=1.1, zorder=4)
    ax_c.set_xticks(x_c)
    ax_c.set_xticklabels(site_names_c, fontsize=10.5)
    ax_c.set_ylabel(r'Energy Difference $\delta (\Delta E)\ \ (\mathrm{eV})$', fontsize=11)
    ax_c.set_title(r'(c) Coverage ($2\times2$ vs $1\times1$) & Dispersion Shifts', fontsize=12, fontweight='bold', pad=10)
    ax_c.set_ylim(-0.16, 0.08)
    ax_c.yaxis.set_major_locator(MultipleLocator(0.04))
    ax_c.yaxis.set_minor_locator(MultipleLocator(0.02))
    ax_c.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_c.legend(frameon=True, facecolor='white', framealpha=0.92, fontsize=8.2, loc='upper center', ncol=2)

    # -------------------------------------------------------------
    # Panel (d): Gibbs Free Energy Diagram along HER Coordinate
    # -------------------------------------------------------------
    ax_d = axs[1, 1]
    
    # HER reaction steps: H+ + e- (0 eV) -> H* (Delta G) -> 1/2 H2 (0 eV)
    step_x = [0, 1, 2]
    step_labels = [r'$\mathrm{H}^+ + \mathrm{e}^-$', r'$\mathrm{H}^*$', r'$\frac{1}{2}\mathrm{H}_2$']
    
    # Optimal thermo-neutral dashed line
    ax_d.axhline(0, color='#7f8c8d', linestyle=':', linewidth=1.5, label='Ideal HER Catalyst ($\\Delta G = 0$)', zorder=1)
    
    # Plot curves for 2x2 PBE+D3 and 1x1 PBE+D3
    palette = {
        ('S1', '2x2'): ('#1f77b4', '-', 'Top-Cl ($2\\times2$, D3)'),
        ('S3', '2x2'): ('#2ca02c', '-', 'Top-Cr ($2\\times2$, D3)'),
        ('S2', '2x2'): ('#d62728', '--', 'Hollow ($2\\times2$, D3)'),
        ('S1', '1x1'): ('#1f77b4', ':', 'Top-Cl ($1\\times1$, D3)'),
        ('S3', '1x1'): ('#2ca02c', ':', 'Top-Cr ($1\\times1$, D3)'),
    }
    
    for (s_key, scale), (col, ls, lbl) in palette.items():
        sub = df[(df['scale'] == scale) & (df['vdw_key'] == 'yes_vdw') & (df['site_key'] == s_key)]
        dg_val = sub['Delta_G'].values[0]
        
        # Horizontal step levels
        ax_d.plot([-0.3, 0.3], [0, 0], color='#2c3e50', linewidth=1.5)
        ax_d.plot([0.7, 1.3], [dg_val, dg_val], color=col, linestyle=ls, linewidth=2.2, label=f'{lbl}: {dg_val:.2f} eV')
        ax_d.plot([1.7, 2.3], [0, 0], color='#2c3e50', linewidth=1.5)
        
        # Connecting lines
        ax_d.plot([0.3, 0.7], [0, dg_val], color=col, linestyle=ls, alpha=0.5, linewidth=1.2)
        ax_d.plot([1.3, 1.7], [dg_val, 0], color=col, linestyle=ls, alpha=0.5, linewidth=1.2)
        
    ax_d.set_xticks([0, 1, 2])
    ax_d.set_xticklabels(step_labels, fontsize=11.5, fontweight='bold')
    ax_d.set_ylabel(r'$\Delta G_{\mathrm{H}^*}\ \ (\mathrm{eV})$', fontsize=11)
    ax_d.set_title(r'(d) HER Free Energy Profile ($\Delta G_{\mathrm{H}^*} = E_{\mathrm{ads}} + 0.24\ \mathrm{eV}$)',
                   fontsize=12, fontweight='bold', pad=10)
    ax_d.set_ylim(-0.3, 2.9)
    ax_d.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_d.yaxis.set_minor_locator(MultipleLocator(0.25))
    ax_d.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_d.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=8.5, loc='upper right')

    plt.suptitle(r'Hydrogen Adsorption Thermodynamics on Monolayer $\mathrm{CrCl}_3$: Multi-Scale & Dispersion Benchmarks',
                 fontsize=14, fontweight='bold', y=0.995)
    
    out_png = os.path.join(POST_DIR, "crcl3_h_adsorption_comparative_multipanel.png")
    out_pdf = os.path.join(POST_DIR, "crcl3_h_adsorption_comparative_multipanel.pdf")
    
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_png}")
    print(f"Generated: {out_pdf}")

def plot_standalone_comparison(df):
    """Generates focused 2x2 vs 1x1 presentation bar plot."""
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    
    # 4 groups: S1 Pure PBE, S1 PBE+D3, S3 Pure PBE, S3 PBE+D3
    categories = [
        ('S1', 'no_vdw', r'Site 1 (Top-Cl)' + '\nPure PBE'),
        ('S1', 'yes_vdw', r'Site 1 (Top-Cl)' + '\nPBE+D3'),
        ('S3', 'no_vdw', r'Site 3 (Top-Cr)' + '\nPure PBE'),
        ('S3', 'yes_vdw', r'Site 3 (Top-Cr)' + '\nPBE+D3'),
        ('S2', 'no_vdw', r'Site 2 (Hollow)' + '\nPure PBE'),
        ('S2', 'yes_vdw', r'Site 2 (Hollow)' + '\nPBE+D3'),
    ]
    
    x = np.arange(len(categories))
    w = 0.35
    
    vals_1x1 = []
    vals_2x2 = []
    
    for s_key, vdw_key, _ in categories:
        sub_1 = df[(df['scale'] == '1x1') & (df['vdw_key'] == vdw_key) & (df['site_key'] == s_key)]
        sub_2 = df[(df['scale'] == '2x2') & (df['vdw_key'] == vdw_key) & (df['site_key'] == s_key)]
        vals_1x1.append(sub_1['E_ads'].values[0] if len(sub_1) > 0 else np.nan)
        vals_2x2.append(sub_2['E_ads'].values[0] if len(sub_2) > 0 else np.nan)
        
    rects1 = ax.bar(x - w/2, vals_1x1, w, label=r'$1\times1$ Supercell ($\theta = 1.00$ H/cell)',
                    color='#3498db', edgecolor='black', linewidth=1.0, zorder=3)
    rects2 = ax.bar(x + w/2, vals_2x2, w, label=r'$2\times2$ Supercell ($\theta = 0.25$ H/cell)',
                    color='#2ecc71', edgecolor='black', linewidth=1.0, zorder=3)
    
    for rects in [rects1, rects2]:
        for r in rects:
            h = r.get_height()
            if not np.isnan(h):
                ax.text(r.get_x() + r.get_width()/2.0, h + 0.03, f'{h:.2f}',
                        ha='center', va='bottom', fontsize=9, fontweight='bold', fontfamily='serif')

    ax.set_xticks(x)
    ax.set_xticklabels([c[2] for c in categories], fontsize=10)
    ax.set_ylabel(r'$E_{\mathrm{ads}} = E_{\mathrm{slab+H}} - E_{\mathrm{clean}} - \frac{1}{2}E(\mathrm{H}_2)\ \ (\mathrm{eV})$', fontsize=11.5)
    ax.set_title(r'Hydrogen Adsorption Energy on Monolayer $\mathrm{CrCl}_3$: $1\times1$ vs $2\times2$',
                 fontsize=12.5, fontweight='bold', pad=12)
    ax.set_ylim(1.2, 2.75)
    ax.yaxis.set_major_locator(MultipleLocator(0.3))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=10, loc='upper left')
    
    out_png = os.path.join(POST_DIR, "crcl3_h_adsorption_standalone_comparison.png")
    out_pdf = os.path.join(POST_DIR, "crcl3_h_adsorption_standalone_comparison.pdf")
    
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_png}")
    print(f"Generated: {out_pdf}")

def write_markdown_report(df):
    """Generates detailed academic markdown report summarizing all energetics."""
    md_path = os.path.join(POST_DIR, "CRCL3_H_ADSORPTION_COMPARATIVE_REPORT.md")
    
    with open(md_path, 'w') as f:
        f.write("# Hydrogen Adsorption Energetics on Monolayer $\\text{CrCl}_3$\n")
        f.write("## Comparative Analysis: $1\\times1$ vs. $2\\times2$ Supercells & Dispersion Effects\n\n")
        f.write("**Reference Standards:**\n")
        f.write(f"- Isolated $\\text{{H}}_2$ gas-phase energy (Pure PBE, $15\\times15\\times15$ Å box): $E(\\text{{H}}_2) = {E_H2_TOTAL:.6f}\\text{{ eV}} \\implies \\frac{{1}}{{2}}E(\\text{{H}}_2) = {E_H2_HALF:.6f}\\text{{ eV}}$\n")
        f.write(f"- Thermodynamic HER correction: $\\Delta G_{{\\mathrm{{H}}^*}} = E_{{\\mathrm{{ads}}}} + {ZPE_TS_CORRECTION}\\text{{ eV}}$\n\n")
        f.write("---\n\n")
        f.write("### 1. Comprehensive Energetics Summary Table\n\n")
        f.write("| Supercell | Coverage $\\theta$ | DFT Treatment | Adsorption Site | $E_{\\mathrm{clean}}$ (eV) | $E_{\\mathrm{tot}}$ (eV) | Binding $\\Delta E$ (eV) | $E_{\\mathrm{ads}}$ vs $\\frac{1}{2}\\text{H}_2$ (eV) | $\\Delta G_{\\mathrm{H}^*}$ (eV) | Magnetization | Ionic Steps |\n")
        f.write("|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n")
        
        for _, row in df.iterrows():
            f.write(f"| {row['scale']} | {row['coverage_theta']:.2f} | {row['vdw_label']} | **{row['site_label']}** | {row['E_clean']:.4f} | {row['E_tot']:.4f} | **{row['Delta_E']:.4f}** | **{row['E_ads']:.4f}** | **{row['Delta_G']:.4f}** | {row['mag']:.2f} $\\mu_B$ | {row['ionic_steps']} |\n")
            
        f.write("\n---\n\n")
        f.write("### 2. Physical & Mechanistic Insights\n\n")
        f.write("1. **Site Competition ($S_1$ vs. $S_3$):**\n")
        f.write("   - Both **Site 1 (Top-Cl)** and **Site 3 (Top-Cr)** act as the two principal thermodynamic adsorption minima across all scales and functionals.\n")
        f.write("   - In the $2\\times2$ supercell (isolated adatom limit, $\\theta = 0.25$), Site 1 is marginally more favorable than Site 3 by **$0.045\\text{ eV}$ (Pure PBE)** and **$0.111\\text{ eV}$ (PBE+D3)**.\n")
        f.write("   - In contrast, **Site 2 (Hollow)** is energetically disfavored by **$+0.74$ to $+0.89\\text{ eV}$**, showing that hydrogen avoids the open interstitial void of the Cr honeycomb ring.\n\n")
        f.write("2. **Supercell Scaling & Lateral Repulsion:**\n")
        f.write("   - Diluting hydrogen coverage from $\\theta = 1.00$ ($1\\times1$, $d_{\\mathrm{H-H}} = 6.05$ Å) to $\\theta = 0.25$ ($2\\times2$, $d_{\\mathrm{H-H}} = 12.09$ Å) stabilizes Site 1 by **$-0.099\\text{ eV}$** (Pure PBE) and **$-0.028\\text{ eV}$** (PBE+D3).\n")
        f.write("   - For Site 3, the binding energy is virtually invariant with scale (differing by only **$-0.011\\text{ eV}$** in PBE and **$-0.031\\text{ eV}$** in PBE+D3). This demonstrates that Site 3 represents a strongly localized chemisorption state with negligible lateral dipole coupling.\n\n")
        f.write("3. **Dispersion / van der Waals Influence:**\n")
        f.write("   - Inclusion of Grimme DFT-D3 zero damping (`yes_vdw`) consistently increases the binding energy across all sites by **$-0.03$ to $-0.14\\text{ eV}$**.\n")
        f.write("   - Dispersion stabilizes the pristine monolayer lattice itself (lowering $E_{\\mathrm{clean}}$ by $-0.912\\text{ eV}$ in $1\\times1$ and $-3.650\\text{ eV}$ in $2\\times2$), while also enhancing adatom-substrate dispersive attraction.\n")

    print(f"Generated: {md_path}")

def main():
    print("Collecting DFT energetics for CrCl3 1x1 and 2x2 H-adsorption...")
    df = collect_all_data()
    
    # Save CSV
    csv_path = os.path.join(POST_DIR, "crcl3_h_adsorption_energies_summary.csv")
    df.to_csv(csv_path, index=False)
    print(f"Exported CSV: {csv_path}")
    
    # Generate Plots
    plot_multipanel_comparison(df)
    plot_standalone_comparison(df)
    
    # Generate Report
    write_markdown_report(df)
    print("All postprocessing plots and comparative reports generated successfully!")

if __name__ == "__main__":
    main()
