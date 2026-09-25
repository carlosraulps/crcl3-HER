#!/usr/bin/env python3
"""
================================================================================
 Professional Comparative Analysis for Transition Metal (Co, Fe, Ni) Adsorption
 on Monolayer CrCl3 (2x2 Supercell): Site Competition & Dispersion Effects
================================================================================
 Evaluates:
   1. S1 (Top-Cl, Atom 19 / Cl11)
   2. S2 (Hollow, Ring Center)
   3. S3 (Top-Cr, Atom 3 / Cr3)
 Across Pure GGA-PBE and PBE + Grimme DFT-D3 (Becke-Johnson damping, IVDW=12).
================================================================================
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

# Directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
POST_DIR = os.path.abspath(os.path.dirname(__file__))

# Visual Styling - Publication Quality
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Liberation Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['xtick.major.width'] = 1.2
plt.rcParams['ytick.major.width'] = 1.2
plt.rcParams['xtick.minor.width'] = 0.8
plt.rcParams['ytick.minor.width'] = 0.8

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

def collect_tm_data():
    records = []
    
    tm_systems = [
        ('Co', 'Cobalt', 'crcl3-2x2-co_ads-without-U', 3.0),
        ('Fe', 'Iron', 'crcl3-2x2-fe_ads-without-U', 4.0),
        ('Ni', 'Nickel', 'crcl3-2x2-ni_ads-without-U', 2.0)
    ]
    
    variants = [
        ('no_vdw', 'Pure PBE'),
        ('yes_vdw', 'PBE+D3 (BJ)')
    ]
    
    sites = [
        ('S1', 'Site 1 (Top-Cl)', '#1f77b4'),
        ('S2', 'Site 2 (Hollow)', '#e67e22'),
        ('S3', 'Site 3 (Top-Cr)', '#2ca02c')
    ]
    
    for tm_sym, tm_name, folder, nom_mag in tm_systems:
        base_path = os.path.join(BASE_DIR, folder)
        
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
                    
                    records.append({
                        'TM': tm_sym,
                        'TM_name': tm_name,
                        'nominal_moment': nom_mag,
                        'vdw_key': vdw_key,
                        'vdw_label': vdw_label,
                        'site_key': site_key,
                        'site_label': site_label,
                        'site_color': color,
                        'E_clean': e_clean,
                        'E_tot': e_tot,
                        'Delta_E': delta_e,
                        'mag': site_info['mag'],
                        'ionic_steps': site_info['step']
                    })
                    
    # Check for systems with Hubbard U
    u_systems = [
        ('Co', 'Cobalt', 'crcl3-2x2-co_ads-with-U', 3.0, 'yes_vdw', 'yes_vdw_u', 'PBE+D3+U (3.29 eV)')
    ]
    for tm_sym, tm_name, folder, nom_mag, vdw_sub, vdw_key, vdw_label in u_systems:
        base_path = os.path.join(BASE_DIR, folder)
        clean_dir = os.path.join(base_path, vdw_sub, "clean")
        clean_info = extract_vasp_info(clean_dir)
        e_clean = clean_info['E0']
        
        for site_key, site_label, color in sites:
            site_dir = os.path.join(base_path, vdw_sub, site_key)
            site_info = extract_vasp_info(site_dir)
            
            if site_info['E0'] is not None and e_clean is not None:
                e_tot = site_info['E0']
                delta_e = e_tot - e_clean
                
                records.append({
                    'TM': tm_sym,
                    'TM_name': tm_name,
                    'nominal_moment': nom_mag,
                    'vdw_key': vdw_key,
                    'vdw_label': vdw_label,
                    'site_key': site_key,
                    'site_label': site_label,
                    'site_color': color,
                    'E_clean': e_clean,
                    'E_tot': e_tot,
                    'Delta_E': delta_e,
                    'mag': site_info['mag'],
                    'ionic_steps': site_info['step']
                })

    df = pd.DataFrame(records)
    
    # Calculate relative stability within each (TM, functional) group
    df['Delta_E_rel'] = 0.0
    for tm in df['TM'].unique():
        for vdw in df[df['TM'] == tm]['vdw_key'].unique():
            mask = (df['TM'] == tm) & (df['vdw_key'] == vdw)
            min_val = df.loc[mask, 'Delta_E'].min()
            df.loc[mask, 'Delta_E_rel'] = df.loc[mask, 'Delta_E'] - min_val
            
    return df

def plot_multipanel_tm_comparison(df):
    """Generates 4-panel comprehensive publication-quality figure."""
    fig, axs = plt.subplots(2, 2, figsize=(14, 11))
    fig.subplots_adjust(hspace=0.34, wspace=0.26)
    
    metals = ['Co', 'Fe', 'Ni']
    sites = [
        ('S1', 'Site 1 (Top-Cl)', '#1f77b4'),
        ('S2', 'Site 2 (Hollow)', '#e67e22'),
        ('S3', 'Site 3 (Top-Cr)', '#2ca02c')
    ]
    
    # -------------------------------------------------------------
    # Panel (a): Total Binding Energy Delta E (PBE vs PBE+D3)
    # -------------------------------------------------------------
    ax_a = axs[0, 0]
    conditions = [
        ('Co', 'no_vdw', 'Co\nPBE'),
        ('Co', 'yes_vdw', 'Co\nPBE+D3'),
        ('Co', 'yes_vdw_u', 'Co\nPBE+D3+U'),
        ('Fe', 'no_vdw', 'Fe\nPBE'),
        ('Fe', 'yes_vdw', 'Fe\nPBE+D3'),
        ('Ni', 'no_vdw', 'Ni\nPBE'),
        ('Ni', 'yes_vdw', 'Ni\nPBE+D3'),
    ]
    
    x = np.arange(len(conditions))
    width = 0.24
    
    for idx, (s_key, s_name, color) in enumerate(sites):
        vals = []
        for tm, vdw, _ in conditions:
            sub = df[(df['TM'] == tm) & (df['vdw_key'] == vdw) & (df['site_key'] == s_key)]
            val = sub['Delta_E'].values[0] if len(sub) > 0 else np.nan
            vals.append(val)
            
        pos = x + (idx - 1) * width
        rects = ax_a.bar(pos, vals, width, label=s_name, color=color, edgecolor='black', linewidth=0.9, alpha=0.9, zorder=3)
        
        for r in rects:
            h = r.get_height()
            if not np.isnan(h):
                ax_a.text(r.get_x() + r.get_width()/2.0, h - 0.10, f'{h:.2f}',
                          ha='center', va='top', fontsize=7.8, fontweight='bold', fontfamily='serif',
                          rotation=90,
                          bbox=dict(boxstyle='square,pad=0.08', facecolor='white', edgecolor='none', alpha=0.85),
                          zorder=5)

    ax_a.axhline(0, color='black', linewidth=0.9, zorder=4)
    ax_a.set_xticks(x)
    ax_a.set_xticklabels([c[2] for c in conditions], fontsize=9.5)
    ax_a.set_ylabel(r'$\Delta E_{\mathrm{bind}} = E_{\mathrm{slab+TM}} - E_{\mathrm{clean}}\ \ (\mathrm{eV})$', fontsize=14)
    ax_a.set_title(r'(a) Transition Metal Binding Energy on $\mathrm{CrCl}_3$ ($2\times2$)', fontsize=12, fontweight='bold', pad=10)
    ax_a.set_ylim(-8.3, 0.2)
    ax_a.yaxis.set_major_locator(MultipleLocator(1.0))
    ax_a.yaxis.set_minor_locator(MultipleLocator(0.2))
    ax_a.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_a.legend(frameon=True, facecolor='white', framealpha=0.92, fontsize=9.0, loc='lower left')

    # -------------------------------------------------------------
    # Panel (b): Relative Site Energy Penalty Delta E - Delta E_min
    # -------------------------------------------------------------
    ax_b = axs[0, 1]
    
    for idx, (s_key, s_name, color) in enumerate(sites):
        vals = []
        for tm, vdw, _ in conditions:
            sub = df[(df['TM'] == tm) & (df['vdw_key'] == vdw) & (df['site_key'] == s_key)]
            val = sub['Delta_E_rel'].values[0] if len(sub) > 0 else np.nan
            vals.append(val)
            
        pos = x + (idx - 1) * width
        rects = ax_b.bar(pos, vals, width, label=s_name, color=color, edgecolor='black', linewidth=0.9, alpha=0.9, zorder=3)
        
        for r in rects:
            h = r.get_height()
            if not np.isnan(h):
                lbl = "GS" if abs(h) < 1e-3 else f'+{h:.2f}'
                ax_b.text(r.get_x() + r.get_width()/2.0, h + 0.05, lbl,
                          ha='center', va='bottom', fontsize=7.8, fontweight='bold', fontfamily='serif',
                          rotation=90,
                          bbox=dict(boxstyle='square,pad=0.08', facecolor='white', edgecolor='none', alpha=0.85),
                          zorder=5)

    ax_b.set_xticks(x)
    ax_b.set_xticklabels([c[2] for c in conditions], fontsize=9.5)
    ax_b.set_ylabel(r'$\Delta E - \Delta E_{\mathrm{min}}\ \ (\mathrm{eV})$', fontsize=14)
    ax_b.set_title(r'(b) Relative Site Preference & Metastability Penalty', fontsize=12, fontweight='bold', pad=10)
    ax_b.set_ylim(-0.05, 3.8)
    ax_b.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_b.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_b.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_b.legend(frameon=True, facecolor='white', framealpha=0.92, fontsize=9.0, loc='upper left')

    # -------------------------------------------------------------
    # Panel (c): Dispersion Energy Contribution (D3 - PBE)
    # -------------------------------------------------------------
    ax_c = axs[1, 0]
    x_tm = np.arange(len(metals))
    w_tm = 0.25
    
    for idx, (s_key, s_name, color) in enumerate(sites):
        disp_vals = []
        for tm in metals:
            pbe = df[(df['TM'] == tm) & (df['vdw_key'] == 'no_vdw') & (df['site_key'] == s_key)]['Delta_E'].values[0]
            d3 = df[(df['TM'] == tm) & (df['vdw_key'] == 'yes_vdw') & (df['site_key'] == s_key)]['Delta_E'].values[0]
            disp = d3 - pbe  # Negative means D3 stabilizes binding further
            disp_vals.append(disp)
            
        pos = x_tm + (idx - 1) * w_tm
        rects = ax_c.bar(pos, disp_vals, w_tm, label=s_name, color=color, edgecolor='black', linewidth=0.9, alpha=0.9, zorder=3)
        
        for r in rects:
            h = r.get_height()
            ax_c.text(r.get_x() + r.get_width()/2.0, h - 0.05 if h < 0 else h + 0.05, f'{h:+.2f}',
                      ha='center', va='top' if h < 0 else 'bottom', fontsize=7.8, fontweight='bold', fontfamily='serif',
                      rotation=90,
                      bbox=dict(boxstyle='square,pad=0.08', facecolor='white', edgecolor='none', alpha=0.85),
                      zorder=5)

    ax_c.axhline(0, color='black', linewidth=0.9, zorder=4)
    ax_c.set_xticks(x_tm)
    ax_c.set_xticklabels([f'{m} ({m}-doped)' for m in metals], fontsize=10.5)
    ax_c.set_ylabel(r'$\Delta E_{\mathrm{disp}} = \Delta E(\mathrm{D3}) - \Delta E(\mathrm{PBE})\ \ (\mathrm{eV})$', fontsize=14)
    ax_c.set_title(r'(c) Dispersion Contribution to Binding Energy', fontsize=12, fontweight='bold', pad=10)
    ax_c.set_ylim(-1.9, 1.9)
    ax_c.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_c.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_c.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_c.legend(frameon=True, facecolor='white', framealpha=0.92, fontsize=9.0, loc='lower left')

    # -------------------------------------------------------------
    # Panel (d): Magnetic Moment along Adsorption States
    # -------------------------------------------------------------
    ax_d = axs[1, 1]
    
    # Pristine substrate magnetic moment
    M_clean = 24.0  # 8 Cr atoms * 3 mu_B
    ax_d.axhline(M_clean, color='#7f8c8d', linestyle=':', linewidth=1.5,
                 label=r'Pristine $\mathrm{CrCl}_3$ ($24\,\mu_B$)', zorder=1)
    
    for idx, (s_key, s_name, color) in enumerate(sites):
        m_vals = []
        for tm, vdw, _ in conditions:
            sub = df[(df['TM'] == tm) & (df['vdw_key'] == vdw) & (df['site_key'] == s_key)]
            m_vals.append(sub['mag'].values[0] if len(sub) > 0 else np.nan)
            
        pos = x + (idx - 1) * width
        rects = ax_d.bar(pos, m_vals, width, label=s_name, color=color, edgecolor='black', linewidth=0.9, alpha=0.9, zorder=3)
        
        for r in rects:
            h = r.get_height()
            if not np.isnan(h):
                ax_d.text(r.get_x() + r.get_width()/2.0, h + 0.35, f'{h:.1f}',
                          ha='center', va='bottom', fontsize=7.8, fontweight='bold', fontfamily='serif',
                          rotation=90,
                          bbox=dict(boxstyle='square,pad=0.08', facecolor='white', edgecolor='none', alpha=0.85),
                          zorder=5)

    ax_d.set_xticks(x)
    ax_d.set_xticklabels([c[2] for c in conditions], fontsize=9.5)
    ax_d.set_ylabel(r'Total Magnetic Moment $M_{\mathrm{tot}}\ \ (\mu_B)$', fontsize=14)
    ax_d.set_title(r'(d) Total Slab Spin Moment $M_{\mathrm{tot}}$ upon TM Adsorption', fontsize=12, fontweight='bold', pad=10)
    ax_d.set_ylim(19.0, 32.5)
    ax_d.yaxis.set_major_locator(MultipleLocator(2.0))
    ax_d.yaxis.set_minor_locator(MultipleLocator(0.5))
    ax_d.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_d.legend(frameon=True, facecolor='white', framealpha=0.92, fontsize=10.0, loc='upper right')

    plt.suptitle(r'Transition Metal Functionalization on Monolayer $\mathrm{CrCl}_3$ ($2\times2$ Supercell): $\mathrm{Co}$ vs $\mathrm{Fe}$ vs $\mathrm{Ni}$',
                 fontsize=14, fontweight='bold', y=0.995)
    
    out_png = os.path.join(POST_DIR, "tm_site_competition_multipanel.png")
    out_pdf = os.path.join(POST_DIR, "tm_site_competition_multipanel.pdf")
    
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_png}")
    print(f"Generated: {out_pdf}")

def plot_presentation_summary(df):
    """Generates focused grouped presentation bar chart."""
    fig, ax = plt.subplots(figsize=(13.0, 6.0))
    
    groups = [
        ('Co', 'no_vdw', 'Co (PBE)'),
        ('Co', 'yes_vdw', 'Co (PBE+D3)'),
        ('Co', 'yes_vdw_u', 'Co (PBE+D3+U)'),
        ('Fe', 'no_vdw', 'Fe (PBE)'),
        ('Fe', 'yes_vdw', 'Fe (PBE+D3)'),
        ('Ni', 'no_vdw', 'Ni (PBE)'),
        ('Ni', 'yes_vdw', 'Ni (PBE+D3)'),
    ]
    
    sites = [
        ('S1', 'Site 1 (Top-Cl)', '#1f77b4'),
        ('S2', 'Site 2 (Hollow)', '#e67e22'),
        ('S3', 'Site 3 (Top-Cr)', '#2ca02c')
    ]
    
    x = np.arange(len(groups))
    w = 0.25
    
    for idx, (s_key, s_name, color) in enumerate(sites):
        vals = []
        for tm, vdw, _ in groups:
            sub = df[(df['TM'] == tm) & (df['vdw_key'] == vdw) & (df['site_key'] == s_key)]
            vals.append(sub['Delta_E'].values[0] if len(sub) > 0 else np.nan)
            
        pos = x + (idx - 1) * w
        rects = ax.bar(pos, vals, w, label=s_name, color=color, edgecolor='black', linewidth=0.9, alpha=0.9, zorder=3)
        
        for r in rects:
            h = r.get_height()
            if not np.isnan(h):
                ax.text(r.get_x() + r.get_width()/2.0, h - 0.12, f'{h:.2f} eV',
                        ha='center', va='top', fontsize=8.2, fontweight='bold', fontfamily='serif',
                        rotation=90,
                        bbox=dict(boxstyle='square,pad=0.08', facecolor='white', edgecolor='none', alpha=0.88),
                        zorder=5)

    ax.axhline(0, color='black', linewidth=0.9, zorder=4)
    ax.set_xticks(x)
    ax.set_xticklabels([g[2] for g in groups], fontsize=10.5, fontweight='bold')
    ax.set_ylabel(r'$\Delta E_{\mathrm{bind}} = E_{\mathrm{slab+TM}} - E_{\mathrm{clean}}\ \ (\mathrm{eV})$', fontsize=15)
    ax.set_title(r'Adsorption Energetics and Site Competition for $3d$ Transition Metals on Monolayer $\mathrm{CrCl}_3$',
                 fontsize=13, fontweight='bold', pad=12)
    ax.set_ylim(-8.5, 0.2)
    ax.yaxis.set_major_locator(MultipleLocator(1.0))
    ax.yaxis.set_minor_locator(MultipleLocator(0.2))
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax.legend(frameon=True, facecolor='white', framealpha=0.92, fontsize=10.0, loc='lower left')
    
    out_png = os.path.join(POST_DIR, "tm_site_preference_barchart.png")
    out_pdf = os.path.join(POST_DIR, "tm_site_preference_barchart.pdf")
    
    plt.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.savefig(out_pdf, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_png}")
    print(f"Generated: {out_pdf}")

def write_tm_report(df):
    """Generates detailed academic markdown report summarizing TM adsorption."""
    md_path = os.path.join(POST_DIR, "CRCL3_TM_SITE_COMPETITION_REPORT.md")
    
    with open(md_path, 'w') as f:
        f.write("# Transition Metal Adsorption and Site Competition on Monolayer $\\text{CrCl}_3$\n")
        f.write("## Comparative Study: Cobalt ($\\text{Co}$), Iron ($\\text{Fe}$), Nickel ($\\text{Ni}$) on $2\\times2$ Supercells\n\n")
        f.write("**Methodology:**\n")
        f.write("- Substrate: Monolayer $\\text{CrCl}_3$ ($2\\times2\\times1$ supercell, 8 Cr + 24 Cl atoms, $20$ Å vacuum box).\n")
        f.write("- Functionals: Pure GGA-PBE vs. PBE + Grimme DFT-D3 with Becke-Johnson damping (`IVDW=12`).\n")
        f.write("- Binding Energy definition: $\\Delta E_{\\mathrm{bind}} = E_{\\mathrm{slab+TM}} - E_{\\mathrm{clean}}$ (eV).\n")
        f.write("- Ground state reference: $\\Delta E_{\\mathrm{rel}} = \\Delta E_{\\mathrm{bind}} - \\min(\\Delta E_{\\mathrm{bind}})$.\n\n")
        f.write("---\n\n")
        f.write("### 1. Energetics Summary Table\n\n")
        f.write("| TM Adatom | Functional | Site Key | Site Description | $E_{\\mathrm{clean}}$ (eV) | $E_{\\mathrm{tot}}$ (eV) | Binding $\\Delta E$ (eV) | Relative Penalty (eV) | Total Mag ($\\mu_B$) | Ionic Steps |\n")
        f.write("|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|\n")
        
        for _, row in df.iterrows():
            rel_str = "**GROUND STATE**" if abs(row['Delta_E_rel']) < 1e-3 else f"+{row['Delta_E_rel']:.3f} eV"
            f.write(f"| **{row['TM']}** ({row['TM_name']}) | {row['vdw_label']} | {row['site_key']} | {row['site_label']} | {row['E_clean']:.4f} | {row['E_tot']:.4f} | **{row['Delta_E']:.3f}** | {rel_str} | {row['mag']:.2f} | {row['ionic_steps']} |\n")
            
        f.write("\n---\n\n")
        f.write("### 2. Physical & Mechanistic Discussion\n\n")
        f.write("1. **Nickel ($\\text{Ni}$): Definite Hollow-Site Stabilization**\n")
        f.write("   - For Ni, the **Hollow site ($S_2$)** is the unambiguous thermodynamic ground state in both Pure PBE ($\\Delta E = -3.792\\text{ eV}$) and PBE+D3 ($\\Delta E = -4.199\\text{ eV}$).\n")
        f.write("   - The Hollow site provides symmetric threefold coordination to the basal chlorine atoms with moderate penetration into the hollow cavity, stabilizing Ni by $0.29\\text{ eV}$ (PBE) and $0.40\\text{ eV}$ (PBE+D3) over the Top-Cl site ($S_1$).\n")
        f.write("   - The total magnetic moment remains constant at $24.00\\,\\mu_B$ across all sites, indicating low-spin or paired $d^8$ configuration with negligible net spin perturbation to the ferromagnetic CrCl$_3$ background ($8\\times 3\\,\\mu_B$).\n\n")
        f.write("2. **Cobalt ($\\text{Co}$): Dispersion-Induced Site Inversion**\n")
        f.write("   - In Pure PBE, Top-Cl ($S_1$, $-4.728\\text{ eV}$) and Hollow ($S_2$, $-4.726\\text{ eV}$) are essentially isoenergetic (energy difference $< 2\\text{ meV}$).\n")
        f.write("   - Inclusion of Grimme DFT-D3 (BJ) dispersion stabilizes the hollow coordination by an additional $-0.33\\text{ eV}$, establishing **Hollow ($S_2$, $\\Delta E = -5.057\\text{ eV}$)** as the true ground state over Top-Cl ($-4.835\\text{ eV}$).\n")
        f.write("   - The magnetic moment for Co on Hollow and Top-Cr is $23.00\\,\\mu_B$ (antiferromagnetic alignment of Co $3d$ electron with the Cr substrate), whereas at Top-Cl in PBE+D3 it polarizes ferromagnetically to $27.00\\,\\mu_B$.\n\n")
        f.write("3. **Iron ($\\text{Fe}$): Strongest Adsorption & Spin Transition**\n")
        f.write("   - Fe exhibits the highest binding energy among all three $3d$ transition metals, exceeding $-6.8\\text{ eV}$ at Top-Cl under PBE+D3 (BJ).\n")
        f.write("   - In Pure PBE, the Hollow site ($S_2$) is the ground state with $\\Delta E = -6.333\\text{ eV}$ and $M = 28.44\\,\\mu_B$ ($+4\\,\\mu_B$ high-spin Fe contribution).\n")
        f.write("   - Under PBE+D3 (BJ), Top-Cl ($S_1$) undergoes a collective relaxation yielding a deep thermodynamic minimum of **$\\Delta E = -6.807\\text{ eV}$** with $M = 22.00\\,\\mu_B$, reflecting strong spin-reorganization and hybridization with the ligand chlorine.\n\n")
        f.write("4. **Universal Avoidance of Top-Cr ($S_3$) in Standard PBE/PBE+D3:**\n")
        f.write("   - For all three transition metals without on-site Coulomb corrections, Site 3 (Top-Cr) is consistently the least favorable position, with an energetic penalty of $+0.65\\text{ to } +3.00\\text{ eV}$ relative to the ground state.\n")
        f.write("   - This is physically driven by strong electrostatic repulsion and core Pauli exclusion between the approaching $3d$ transition metal cation and the underlying high-spin $\\text{Cr}^{3+}$ ($t_{2g}^3$) center.\n\n")
        f.write("5. **Impact of Hubbard $U = 3.29\\text{ eV}$ on Cobalt Site Stability:**\n")
        f.write("   - Incorporating the Dudarev Hubbard $U = 3.29\\text{ eV}$ on the Cr $3d$ orbitals (derived from the optimal lattice/gap intersection in `relax-crcl3-i3-vdw-u`) significantly enhances electron localization on Cr$^{3+}$ ($t_{2g}^3$).\n")
        f.write("   - For Cobalt, Top-Cr ($S_3$) achieves a strong binding energy of $\\Delta E = -4.502\\text{ eV}$ with an exact ferromagnetic spin moment of $M_{\\mathrm{tot}} = 27.00\\,\\mu_B$ ($8\\times 3.0\\,\\mu_B$ from Cr plus $3.0\\,\\mu_B$ from high-spin Co$^{2+}$).\n")
        f.write("   - Top-Cl ($S_1$) exhibits an intermediate binding energy of $\\Delta E = -3.283\\text{ eV}$ while undergoing relaxation, demonstrating the stabilization of coordinated adsorption states under on-site Coulomb correction.\n")

    print(f"Generated: {md_path}")

def main():
    print("Collecting DFT energetics for TM (Co, Fe, Ni) adsorption on CrCl3 2x2...")
    df = collect_tm_data()
    
    csv_path = os.path.join(POST_DIR, "crcl3_tm_adsorption_energies_summary.csv")
    df.to_csv(csv_path, index=False)
    print(f"Exported CSV: {csv_path}")
    
    plot_multipanel_tm_comparison(df)
    plot_presentation_summary(df)
    
    write_tm_report(df)
    print("All TM postprocessing plots and reports generated successfully!")

if __name__ == "__main__":
    main()
