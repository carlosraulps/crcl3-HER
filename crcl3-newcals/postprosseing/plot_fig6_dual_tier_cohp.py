#!/usr/bin/env python3
"""
plot_fig6_dual_tier_cohp.py
===========================
Generates publication-quality COHP plots (-COHP vs E - E_F) for:
  1. Pure PBE baseline (crcl3-newcals/past-calculations) -> Fig6_PBE_baseline.png/.pdf
  2. Multi-site +U_all = 3.29 eV (crcl3-newcals/cohp_lobster_Uall) -> Fig6_Uall.png/.pdf and Fig6.png/.pdf

Adheres strictly to GEMINI.md Publication Anti-Collision Policy:
  - STIX math & Times New Roman typography
  - Zero-overlap legends and annotations with smart bounded cards
  - Standardized axis ranges: [-1.8, 3.8] for -COHP, [-9.0, 3.5] eV for E - E_F
"""

import os
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Liberation Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.1
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.top'] = True
plt.rcParams['ytick.right'] = True

def format_bond_latex(bond_name):
    parts = bond_name.split('-')
    formatted = []
    for p in parts:
        m = re.match(r'([A-Za-z]+)(\d+)', p)
        if m:
            el, idx = m.group(1), m.group(2)
            formatted.append(f'\\mathrm{{{el}}}_{{{idx}}}')
        else:
            formatted.append(f'\\mathrm{{{p}}}')
    return r'$' + '-'.join(formatted) + r'$'

def plot_cohp_suite(mode_dir, out_prefix, title_suffix):
    systems_config = [
        ('adsorbed', 'co', 'Co', 'Adsorbed'), ('adsorbed', 'fe', 'Fe', 'Adsorbed'), ('adsorbed', 'ni', 'Ni', 'Adsorbed'),
        ('embedded', 'co', 'Co', 'Embedded'), ('embedded', 'fe', 'Fe', 'Embedded'), ('embedded', 'ni', 'Ni', 'Embedded')
    ]
    
    results = {}
    for mode, tm_folder, tm_name, label in systems_config:
        p1 = os.path.join(mode_dir, mode, tm_folder, 'COHPCAR.lobster')
        p2 = os.path.join(mode_dir, mode, tm_name, 'COHPCAR.lobster')
        cohp_file = p1 if os.path.exists(p1) else p2
        if not os.path.exists(cohp_file):
            print(f'Warning: {cohp_file} not found')
            continue
            
        with open(cohp_file, 'r') as f:
            cohp_lines = f.readlines()
            
        header = cohp_lines[1].split()
        num_bonds = int(header[0])
        is_spin = int(header[1]) == 2
        n_pts = int(header[2])
        
        bonds = []
        data_start = 0
        for idx in range(2, len(cohp_lines)):
            parts = cohp_lines[idx].split()
            if len(parts) > 0:
                try:
                    float(parts[0])
                    data_start = idx
                    break
                except ValueError:
                    pass
            bonds.append(cohp_lines[idx].strip())
            
        data = []
        for idx in range(data_start, data_start + n_pts):
            data.append([float(x) for x in cohp_lines[idx].split()])
        data = np.array(data)
        
        energies = data[:, 0]
        cohp_curves = {}
        icohps = []
        
        for i in range(1, len(bonds)):
            match = re.search(r'No\.(\d+):(.*)->(.*)\((.*)\)', bonds[i])
            if match:
                b_num = int(match.group(1))
                at1 = match.group(2).strip()
                at2 = match.group(3).strip()
                dist = float(match.group(4))
                
                a1_num = re.search(r'\d+', at1).group()
                a2_num = re.search(r'\d+', at2).group()
                
                if a1_num == '33' or a2_num == '33':
                    if is_spin:
                        c1 = 4 * b_num + 1
                        i1 = 4 * b_num + 2
                        c2 = 4 * b_num + 3
                        i2 = 4 * b_num + 4
                        cohp_tot = data[:, c1] + data[:, c2]
                        icohp_tot = data[:, i1] + data[:, i2]
                    else:
                        cohp_tot = data[:, 2 * b_num + 1]
                        icohp_tot = data[:, 2 * b_num + 2]
                        
                    fermi_idx = np.argmin(np.abs(energies))
                    b_label = f'{at1}-{at2}' if not at1.startswith('Co') and not at1.startswith('Fe') and not at1.startswith('Ni') else f'{at2}-{at1}'
                    cohp_curves[b_label] = cohp_tot
                    icohps.append((b_label, icohp_tot[fermi_idx], dist))
                    
        key = f'{mode}_{tm_name}'
        results[key] = {
            'tm': tm_name, 'mode': label,
            'energies': energies, 'curves': cohp_curves, 'icohps': icohps
        }

    fig, axes = plt.subplots(2, 3, figsize=(13.2, 8.4), sharex=True, sharey=True)
    color_cycles = {
        'Co': ['#1f77b4', '#41b6c4', '#225ea8', '#081d58', '#006d2c', '#74c476'],
        'Fe': ['#d95f02', '#e7298a', '#e6ab02', '#a6761d', '#666666', '#d95f0e'],
        'Ni': ['#7570b3', '#984ea3', '#bcbddc', '#54278f', '#807dba', '#3f007d']
    }
    
    panel_labels = [['(a)', '(b)', '(c)'], ['(d)', '(e)', '(f)']]
    tms = ['Co', 'Fe', 'Ni']
    
    for row_idx, mode in enumerate(['adsorbed', 'embedded']):
        for col_idx, tm in enumerate(tms):
            ax = axes[row_idx, col_idx]
            key = f'{mode}_{tm}'
            if key not in results:
                continue
            res = results[key]
            energies = res['energies']
            curves = res['curves']
            
            ax.axvline(0, color='#888888', linestyle='--', linewidth=0.8, alpha=0.7)
            ax.axhline(0, color='#111111', linestyle='--', linewidth=1.1, alpha=0.85)
            
            c_list = color_cycles[tm]
            for i, (b_name, curve) in enumerate(curves.items()):
                col = c_list[i % len(c_list)]
                ax.plot(-curve, energies, label=format_bond_latex(b_name),
                        color=col, linewidth=1.6, alpha=0.9)
                        
            p_lbl = panel_labels[row_idx][col_idx]
            m_txt = 'Surface Adsorbed' if mode == 'adsorbed' else 'Embedded Pore'
            ax.text(0.04, 0.94, f'{p_lbl} {tm} ({m_txt})',
                    transform=ax.transAxes, fontsize=12, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                             edgecolor='#cccccc', alpha=0.92, linewidth=0.7))
                             
            ax.legend(loc='lower left', frameon=True, facecolor='white',
                      framealpha=0.92, fontsize=9.5, borderpad=0.35,
                      handlelength=1.2, labelspacing=0.25)
            ax.set_ylim(-9.0, 3.5)
            ax.set_xlim(-1.8, 3.8)

    for col in range(3):
        axes[1, col].set_xlabel(r'$-\mathrm{COHP}$', fontsize=13, fontweight='bold')
    for row in range(2):
        axes[row, 0].set_ylabel(r'$E - E_{\mathrm{F}}\ (\mathrm{eV})$', fontsize=13, fontweight='bold')
        
    title_tex = r'Crystal Orbital Hamilton Populations ($-\mathrm{COHP}$) of $\mathrm{TM-Cl}$ Bonds (' + title_suffix + r')'
    fig.suptitle(title_tex, fontsize=14.5, fontweight='bold', y=0.985)
    plt.tight_layout()
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    post_png = os.path.join(script_dir, f'{out_prefix}.png')
    post_pdf = os.path.join(script_dir, f'{out_prefix}.pdf')
    plt.savefig(post_png, dpi=300)
    plt.savefig(post_pdf)
    plt.close()
    print(f'Generated: {post_png} and {post_pdf}')
    
    # Sync to ACS resubmission figure directory
    acs_fig_dir = os.path.abspath(os.path.join(script_dir, '../../ACS_version/ACS_resubmission/figure'))
    if os.path.exists(acs_fig_dir):
        import shutil
        shutil.copy2(post_png, os.path.join(acs_fig_dir, f'{out_prefix}.png'))
        shutil.copy2(post_pdf, os.path.join(acs_fig_dir, f'{out_prefix}.pdf'))
        if out_prefix == 'Fig6_Uall':
            shutil.copy2(post_png, os.path.join(acs_fig_dir, 'Fig6.png'))
            shutil.copy2(post_pdf, os.path.join(acs_fig_dir, 'Fig6.pdf'))
            print('Synced to Fig6.png/Fig6.pdf in ACS resubmission directory.')

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.abspath(os.path.join(script_dir, '..'))
    
    # 1. PBE Baseline
    past_dir = os.path.join(base_dir, 'past-calculations')
    plot_cohp_suite(past_dir, 'Fig6_PBE_baseline', r'Pure PBE Baseline')

    # 2. U_all
    uall_dir = os.path.join(base_dir, 'cohp_lobster_Uall')
    plot_cohp_suite(uall_dir, 'Fig6_Uall', r'$+U_{\mathrm{all}} = 3.29\,\mathrm{eV}$')
