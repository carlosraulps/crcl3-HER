#!/usr/bin/env python3
"""
plot_co_h_u_comparison.py

Generates publication-quality comparative figures illustrating the impact of 
Hubbard U (single-site U_Cr vs multi-site U_all = 3.29 eV) on Co and Co-H adsorption
on monolayer CrCl3 (2x2):
  Panel (a): Site stability inversion (Delta E_rel) for Co adsorption (Without U vs With U)
  Panel (b): Total cell magnetization (mu_B) highlighting AFM -> FM and spin crossover
  Panel (c): Free energy profile for HER (Delta G_H*) with ideal Sabatier window across tiers
  Panel (d): Active site coordination relaxation and interatomic bond lengths

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
from smart_plot_optimizer import resolve_text_overlaps

def create_comparison_figure():
    fig, axs = plt.subplots(2, 2, figsize=(14.0, 11.5))
    fig.subplots_adjust(hspace=0.34, wspace=0.28)
    
    bbox_props = dict(boxstyle='round,pad=0.22', facecolor='white', edgecolor='#cccccc', alpha=0.94, linewidth=0.8)
    
    # -------------------------------------------------------------
    # Panel (a): Relative Site Penalty: Without U vs With U
    # -------------------------------------------------------------
    ax_a = axs[0, 0]
    sites = ['Site 1\n(Top-Cl)', 'Site 2\n(Hollow)', 'Site 3\n(Top-Cr)']
    x = np.arange(len(sites))
    w = 0.35
    
    # Values: Delta E_rel (eV) relative to ground state
    penalties_no_u = [0.222, 0.000, 0.710]
    penalties_u    = [0.000, 0.076, 0.671]
    
    bars1 = ax_a.bar(x - w/2, penalties_no_u, width=w, color='#3498db', edgecolor='black', linewidth=1.2, label='PBE+D3 (Without $U$)', alpha=0.9, zorder=3)
    bars2 = ax_a.bar(x + w/2, penalties_u, width=w, color='#e74c3c', edgecolor='black', linewidth=1.2, label='PBE+D3+$U_{\\mathrm{Cr}}$ ($3.29\\,\\mathrm{eV}$)', alpha=0.9, zorder=3)
    
    t1 = ax_a.text(x[0] - w/2, penalties_no_u[0] + 0.08, '+0.22 eV', ha='center', va='bottom', fontsize=8.2, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    t2 = ax_a.text(x[0] + w/2, 0.06, 'Ground State\n(-5.14 eV, Slid)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)
    
    t3 = ax_a.text(x[1] - w/2, 0.06, 'Ground State\n(-5.06 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    t4 = ax_a.text(x[1] + w/2, 0.36, '+0.08 eV\n(-5.06 eV)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)
    ax_a.plot([x[1] + w/2, x[1] + w/2], [penalties_u[1], 0.35], color='#781f1f', linestyle=':', linewidth=1.1, zorder=4)
    
    t5 = ax_a.text(x[2] - w/2, penalties_no_u[2] + 0.22, '+0.71 eV\n(Repulsive)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#1f4e78', bbox=bbox_props, zorder=5)
    ax_a.plot([x[2] - w/2, x[2] - w/2], [penalties_no_u[2], penalties_no_u[2] + 0.20], color='#1f4e78', linestyle=':', linewidth=1.1, zorder=4)
    t6 = ax_a.text(x[2] + w/2, penalties_u[2] + 0.06, '+0.67 eV\n(Active Site S3)', ha='center', va='bottom', fontsize=8.0, fontweight='bold', color='#781f1f', bbox=bbox_props, zorder=5)
    
    resolve_text_overlaps(fig, ax_a, [t1, t2, t3, t4, t5, t6])
    
    ax_a.set_ylabel(r'Relative Energy Penalty $\Delta E_{\mathrm{rel}}$ (eV)', fontsize=12, fontweight='bold')
    ax_a.set_title(r'(a) Co Adsorption Site Preference on $\mathrm{CrCl}_3(2\times2)$', fontsize=12, fontweight='bold', pad=10)
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(sites, fontsize=10.5)
    ax_a.set_ylim(-0.05, 1.60)
    ax_a.yaxis.set_major_locator(MultipleLocator(0.4))
    ax_a.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_a.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_a.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.2, loc='upper left')
    
    # -------------------------------------------------------------
    # Panel (b): Total Magnetization: Spin Alignment across Tiers
    # -------------------------------------------------------------
    ax_b = axs[0, 1]
    mag_labels = [
        'Pristine\nSlab',
        'Top-Cr\nNo $U$',
        'Top-Cr\n$+U_{\\mathrm{Cr}}$',
        'Co–H\n$+U_{\\mathrm{Cr}}$',
        'Top-Cr\n$+U_{\\mathrm{all}}$',
        'Co–H\n$+U_{\\mathrm{all}}$'
    ]
    x_b = np.arange(len(mag_labels))
    mags = [24.00, 23.00, 27.00, 22.00, 27.00, 28.00]
    colors_b = ['#7f8c8d', '#2980b9', '#c0392b', '#8e44ad', '#16a085', '#27ae60']
    
    bars_b = ax_b.bar(x_b, mags, width=0.52, color=colors_b, edgecolor='black', linewidth=1.2, zorder=3)
    ax_b.axhline(24.0, color='gray', linestyle=':', linewidth=1.3, label=r'Pristine $2\times2$ ($24\,\mu_{\mathrm{B}}$)', zorder=2)
    
    texts_b = []
    for i, m in enumerate(mags):
        t = ax_b.text(x_b[i], m + 0.55, f'{m:.1f} $\\mu_{{\\mathrm{{B}}}}$', ha='center', va='bottom', fontsize=8.0, fontweight='bold', bbox=bbox_props, zorder=5)
        texts_b.append(t)
        
    resolve_text_overlaps(fig, ax_b, texts_b)
    
    ax_b.set_ylabel(r'Total Magnetic Moment $M_{\mathrm{tot}}$ ($\mu_{\mathrm{B}}$)', fontsize=12, fontweight='bold')
    ax_b.set_title(r'(b) Magnetic Moments across Methodological Tiers', fontsize=12, fontweight='bold', pad=10)
    ax_b.set_xticks(x_b)
    ax_b.set_xticklabels(mag_labels, fontsize=9.0)
    ax_b.set_ylim(16, 33.0)
    ax_b.yaxis.set_major_locator(MultipleLocator(4.0))
    ax_b.yaxis.set_minor_locator(MultipleLocator(1.0))
    ax_b.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_b.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=9.0, loc='upper left')
    
    # -------------------------------------------------------------
    # Panel (c): Free Energy Diagram for HER (Delta G_H*)
    # -------------------------------------------------------------
    ax_c = axs[1, 0]
    
    systems_c = [
        'Pristine\n(Top-Cl)',
        'Co (emb)\n$+U_{\\mathrm{Cr}}$',
        'Co (emb)\n$+U_{\\mathrm{all}}$',
        'Co (ads)\nNo $U$',
        'Co (ads)\n$+U_{\\mathrm{Cr}}$',
        r'$\mathbf{Co\ (ads)}$' + '\n' + r'$\mathbf{+U_{\mathrm{all}}}$'
    ]
    deltag_vals = [1.528, 1.375, 1.389, 0.178, -0.069, 0.065]
    x_c = np.arange(len(systems_c))
    
    ax_c.axhspan(-0.15, 0.20, color='#2ecc71', alpha=0.20, label=r'Optimal HER Window ($|\Delta G| \leq 0.15\,\mathrm{eV}$)', zorder=1)
    ax_c.axhline(0.00, color='#27ae60', linestyle='--', linewidth=1.4, label=r'Thermo-neutral ($\Delta G_{\mathrm{H}^*} = 0$)', zorder=2)
    
    for i in range(len(systems_c)):
        val = deltag_vals[i]
        if -0.15 <= val <= 0.20:
            c = '#27ae60' if val > 0 else '#1e8449'
            lw = 4.8 if i == 5 else 3.8
        else:
            c = '#c0392b' if val > 1.0 else '#2980b9'
            lw = 3.8
            
        ax_c.plot([i - 0.28, i + 0.28], [val, val], color=c, linewidth=lw, solid_capstyle='round', zorder=4)
        
        y_text = val - 0.16 if val < 0 else val + 0.10
        va_set = 'top' if val < 0 else 'bottom'
        badge_style = dict(boxstyle='round,pad=0.25', facecolor='#e8f8f5', edgecolor='#27ae60', alpha=0.95, linewidth=1.2) if i == 5 else bbox_props
        
        ax_c.text(i, y_text, f'{val:+.3f} eV', ha='center', va=va_set, fontsize=8.8, fontweight='bold', color=c, bbox=badge_style, zorder=5)
        
    ax_c.set_ylabel(r'HER Free Energy $\Delta G_{\mathrm{H}^*}$ (eV)', fontsize=12, fontweight='bold')
    ax_c.set_title(r'(c) Co HER Descriptor Benchmarks ($+U_{\mathrm{Cr}}$ vs $+U_{\mathrm{all}}$)', fontsize=12, fontweight='bold', pad=10)
    ax_c.set_xticks(x_c)
    ax_c.set_xticklabels(systems_c, fontsize=8.8)
    ax_c.set_ylim(-0.45, 2.10)
    ax_c.yaxis.set_major_locator(MultipleLocator(0.5))
    ax_c.yaxis.set_minor_locator(MultipleLocator(0.1))
    ax_c.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_c.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=8.8, loc='upper left')
    
    # -------------------------------------------------------------
    # Panel (d): Active Site Geometric Evolution upon H Adsorption
    # -------------------------------------------------------------
    ax_d = axs[1, 1]
    
    geom_labels = [
        'Co (Top-Cr)\n$+U_{\\mathrm{Cr}}$ Clean',
        'Co–H (Top-Cr)\n$+U_{\\mathrm{Cr}}$ +H',
        'Co (Top-Cr)\n$+U_{\\mathrm{all}}$ Clean',
        'Co–H (Top-Cr)\n$+U_{\\mathrm{all}}$ +H'
    ]
    x_d = np.arange(len(geom_labels))
    w_d = 0.24
    
    # Converged interatomic distances:
    # +U_Cr: S3 clean (d_Cr=2.58, d_Cl=2.22), S3_H (d_Cr=2.86, d_Cl=2.32, d_H=1.55)
    # +U_all: S3 clean (d_Cr=2.75, d_Cl=2.30), S3_H (d_Cr=3.02, d_Cl=2.34, d_H=1.55)
    d_cocr = [2.578, 2.857, 2.754, 3.024]
    d_cocl = [2.219, 2.320, 2.303, 2.341]
    d_coh  = [0.000, 1.549, 0.000, 1.551]
    
    r1 = ax_d.bar(x_d - w_d, d_cocr, width=w_d, color='#e67e22', edgecolor='black', linewidth=1.1, label=r'$d(\mathrm{Co-Cr})$', zorder=3)
    r2 = ax_d.bar(x_d,       d_cocl, width=w_d, color='#3498db', edgecolor='black', linewidth=1.1, label=r'Avg $d(\mathrm{Co-Cl})$', zorder=3)
    r3 = ax_d.bar(x_d + w_d, d_coh,  width=w_d, color='#9b59b6', edgecolor='black', linewidth=1.1, label=r'$d(\mathrm{Co-H})$', zorder=3)
    
    for i in range(len(geom_labels)):
        ax_d.text(i - w_d, d_cocr[i] + 0.08, f'{d_cocr[i]:.2f} Å', ha='center', va='bottom', fontsize=7.8, fontweight='bold', bbox=bbox_props, zorder=5)
        ax_d.text(i,       d_cocl[i] + 0.08, f'{d_cocl[i]:.2f} Å', ha='center', va='bottom', fontsize=7.8, fontweight='bold', bbox=bbox_props, zorder=5)
        if d_coh[i] > 0:
            ax_d.text(i + w_d, d_coh[i] + 0.08, f'{d_coh[i]:.2f} Å', ha='center', va='bottom', fontsize=7.8, fontweight='bold', bbox=bbox_props, zorder=5)
        else:
            ax_d.text(i + w_d, 0.08, 'N/A', ha='center', va='bottom', fontsize=7.6, color='gray', bbox=bbox_props, zorder=5)
            
    ax_d.set_ylabel(r'Interatomic Distance (Å)', fontsize=12, fontweight='bold')
    ax_d.set_title(r'(d) Active Site Coordination Relaxation ($+U_{\mathrm{Cr}}$ vs $+U_{\mathrm{all}}$)', fontsize=12, fontweight='bold', pad=10)
    ax_d.set_xticks(x_d)
    ax_d.set_xticklabels(geom_labels, fontsize=8.6)
    ax_d.set_ylim(0, 4.25)
    ax_d.yaxis.set_major_locator(MultipleLocator(1.0))
    ax_d.yaxis.set_minor_locator(MultipleLocator(0.2))
    ax_d.grid(True, axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax_d.legend(frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', fontsize=8.8, loc='upper left')
    
    # Save figure
    png_path = os.path.join(SCRIPT_DIR, "crcl3_co_h_u_comparison_multipanel.png")
    pdf_path = os.path.join(SCRIPT_DIR, "crcl3_co_h_u_comparison_multipanel.pdf")
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    plt.savefig(pdf_path, bbox_inches='tight')
    plt.close()
    print(f"Successfully generated: {png_path}")
    print(f"Successfully generated: {pdf_path}")

if __name__ == "__main__":
    create_comparison_figure()
