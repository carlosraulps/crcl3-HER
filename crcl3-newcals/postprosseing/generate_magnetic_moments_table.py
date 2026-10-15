#!/usr/bin/env python3
"""
Generate publication-quality Table Figure of Pristine Monolayer CrCl3 Magnetic Moments
by Chemical Species and Functional/Hubbard U Benchmarks.

Outputs:
 - crcl3-newcals/postprosseing/images-juan/01_Fig1_Pristine_Monolayer/table_pristine_magnetic_moments.png
 - crcl3-newcals/postprosseing/images-juan/01_Fig1_Pristine_Monolayer/table_pristine_magnetic_moments.pdf
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Set matplotlib parameters for publication-quality rendering
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['mathtext.fontset'] = 'dejavusans'

fig = plt.figure(figsize=(14.5, 11.2), dpi=300)
ax = fig.add_subplot(111)
ax.axis('off')

# Color palette (Nord / Nature Materials style)
bg_color = '#ffffff'
header_bg = '#1e293b'         # Deep Slate Blue
header_fg = '#ffffff'
accent_gold = '#f59e0b'       # Warm Gold for optimal U*
highlight_bg = '#fef3c7'      # Light amber for U* row
alt_row_bg = '#f8fafc'        # Subtle slate tint
text_main = '#0f172a'         # Dark navy/slate text
text_muted = '#475569'
border_color = '#cbd5e1'
cr_color = '#0284c7'          # Sky blue for Cr
cl_color = '#16a34a'          # Emerald green for Cl

fig.patch.set_facecolor(bg_color)

# ==============================================================================
# Title & Header Banner
# ==============================================================================
y_pos = 0.96

# Top category badge
badge_box = patches.FancyBboxPatch(
    (0.04, y_pos - 0.005), 0.28, 0.028,
    boxstyle="round,pad=0.005,rounding_size=0.01",
    facecolor='#0284c7', edgecolor='none'
)
ax.add_patch(badge_box)
ax.text(0.18, y_pos + 0.009, 'PRISTINE MONOLAYER CrCl₃', 
        color='#ffffff', fontsize=10.5, fontweight='bold', ha='center', va='center')

ax.text(0.34, y_pos + 0.009, 'First-Principles Electronic Structure & Magnetism',
        color=text_muted, fontsize=10.5, fontstyle='italic', va='center')

y_pos -= 0.038
ax.text(0.04, y_pos, 'Magnetic Moments by Chemical Species & Benchmark Tiers', 
        color=text_main, fontsize=17, fontweight='bold', va='top')

y_pos -= 0.024
ax.text(0.04, y_pos, 'Spin-resolved sphere projections (LORBIT = 11, Wigner-Seitz radii) across Pure PBE and Hubbard $U$ tiers ($0 \\leq U \\leq 6$ eV)',
        color=text_muted, fontsize=10.0, va='top')

# ==============================================================================
# Section 1: Detailed Species Breakdown Table (Optimal PBE+D3+U_Cr Tier)
# ==============================================================================
y_pos -= 0.038

# Section title
ax.text(0.04, y_pos, 'TABLE 1: Atomic Site Magnetic Moments by Chemical Species ($2\\times 2$ Supercell, $U_{\\mathrm{Cr}} = 3.29$ eV)',
        color='#0f172a', fontsize=11.5, fontweight='bold', va='top')

y_pos -= 0.022

# Table 1 Header
col_x = [0.04, 0.13, 0.24, 0.35, 0.43, 0.51, 0.59, 0.69, 0.81, 0.96]
headers_1 = [
    'Chemical\nSpecies',
    'Atoms / Cell\n($2\\times 2$)',
    'Formal Valence\n& Configuration',
    'Local Site\nSymmetry',
    '$m_s$\n($\\mu_{\\mathrm{B}}$)',
    '$m_p$\n($\\mu_{\\mathrm{B}}$)',
    '$m_d$\n($\\mu_{\\mathrm{B}}$)',
    '$m_{\\mathrm{tot}}$ / Atom\n($\\mu_{\\mathrm{B}}$)',
    'Sublattice Total\n($\\mu_{\\mathrm{B}}$)',
    'Local Spin\nCoupling'
]

row_h = 0.036
header_rect = patches.Rectangle((0.04, y_pos - row_h), 0.92, row_h, facecolor=header_bg, edgecolor='none')
ax.add_patch(header_rect)

for i in range(len(col_x) - 1):
    mid_x = (col_x[i] + col_x[i+1]) / 2.0
    ax.text(mid_x, y_pos - row_h/2.0, headers_1[i],
            color=header_fg, fontsize=8.8, fontweight='bold', ha='center', va='center')

y_pos -= row_h

# Table 1 Rows
data_1 = [
    ['Cr (Chromium)', '8', 'Cr³⁺ ($3d^3, t_{2g}^3 e_g^0$)', 'Octahedral ($D_{3d}$)', '+0.031', '+0.039', '+3.047', '+3.117', '+24.936', 'Ferromagnetic (↑↑)'],
    ['Cl (Chlorine)', '24', 'Cl⁻ ($3s^2 3p^6$)', 'Bridging ($C_{2v}$)', '-0.001', '-0.063', '0.000', '-0.064', '-1.536', 'Antiparallel (↓↓)'],
    ['Interstitial / Delocalized', '--', 'Delocalized spin density', 'Inter-atomic space', '--', '--', '--', '--', '+0.600', 'Parallel (↑↑)'],
    ['Unit Cell Total (1×1)', '2 Cr + 6 Cl', 'Formula unit: CrCl₃', 'Honeycomb (P-31m)', '+0.060', '-0.300', '+6.094', '+3.000 / f.u.', '+6.000', 'FM Ground State'],
    ['Supercell Total (2×2)', '8 Cr + 24 Cl', '8 formula units (Cr₈Cl₂₄)', 'Supercell (P-31m)', '+0.216', '-1.196', '+24.372', '+3.000 / f.u.', '+24.000', 'Strict Integer Moment']
]

for row_idx, r in enumerate(data_1):
    is_summary = (row_idx >= 3)
    bg = '#e2e8f0' if row_idx == 4 else ('#f1f5f9' if row_idx == 3 else (alt_row_bg if row_idx % 2 == 1 else '#ffffff'))
    
    r_rect = patches.Rectangle((0.04, y_pos - row_h), 0.92, row_h, facecolor=bg, edgecolor=border_color, linewidth=0.5)
    ax.add_patch(r_rect)
    
    for c_idx in range(len(col_x) - 1):
        mid_x = (col_x[c_idx] + col_x[c_idx+1]) / 2.0
        val = r[c_idx]
        
        # Color coding
        fweight = 'bold' if (is_summary or c_idx == 0 or c_idx == 7 or c_idx == 8) else 'normal'
        tcolor = text_main
        if c_idx == 0:
            if 'Cr' in val and not is_summary:
                tcolor = '#0284c7'
            elif 'Cl' in val and not is_summary:
                tcolor = '#16a34a'
        elif c_idx == 7 or c_idx == 8:
            if '-' in val:
                tcolor = '#dc2626' # Red for negative Cl moment
            elif '+' in val and not is_summary:
                tcolor = '#0369a1' # Blue for positive Cr moment
            elif is_summary:
                tcolor = '#0f172a'
        
        ax.text(mid_x, y_pos - row_h/2.0, val,
                color=tcolor, fontsize=8.6 if not is_summary else 8.9, fontweight=fweight, ha='center', va='center')
        
    y_pos -= row_h

# ==============================================================================
# Section 2: Functional & Hubbard U Benchmark Table
# ==============================================================================
y_pos -= 0.040

ax.text(0.04, y_pos, 'TABLE 2: Methodological Benchmark Across Hubbard $U_{\\mathrm{Cr}}$ Parameter Sweep ($0 \\leq U \\leq 6$ eV)',
        color='#0f172a', fontsize=11.5, fontweight='bold', va='top')

y_pos -= 0.022

col_x2 = [0.04, 0.16, 0.24, 0.34, 0.44, 0.54, 0.64, 0.73, 0.82, 0.96]
headers_2 = [
    'Methodological\nFunctional Tier',
    'Hubbard $U_{\\mathrm{Cr}}$\n(eV)',
    'Cr-$3d$ ($m_d$)\n($\\mu_{\\mathrm{B}}$)',
    'Cr Total ($m_{\\mathrm{Cr}}$)\n($\\mu_{\\mathrm{B}}$)',
    'Cl-$3p$ ($m_p$)\n($\\mu_{\\mathrm{B}}$)',
    'Cl Total ($m_{\\mathrm{Cl}}$)\n($\\mu_{\\mathrm{B}}$)',
    '$M_{\\mathrm{tot}}$ / Cell\n($\\mu_{\\mathrm{B}}$)',
    'Band Gap $E_g$\n(eV)',
    'Physical Description\n& Electronic Status'
]

row_h2 = 0.033
header_rect2 = patches.Rectangle((0.04, y_pos - row_h2), 0.92, row_h2, facecolor=header_bg, edgecolor='none')
ax.add_patch(header_rect2)

for i in range(len(col_x2) - 1):
    mid_x = (col_x2[i] + col_x2[i+1]) / 2.0
    ax.text(mid_x, y_pos - row_h2/2.0, headers_2[i],
            color=header_fg, fontsize=8.6, fontweight='bold', ha='center', va='center')

y_pos -= row_h2

# Table 2 Rows
data_2 = [
    ['Pure PBE Baseline', '0.00', '+2.841', '+2.908', '-0.022', '-0.022', '3.00 / f.u.', '1.50 (dir)', 'Underestimated gap, high covalency'],
    ['PBE+D3 (No U)', '0.00', '+2.841', '+2.908', '-0.022', '-0.022', '3.00 / f.u.', '1.50 (dir)', 'vdW included; identical local moments'],
    ['PBE+D3+$U_{\\mathrm{Cr}}$', '1.00', '+2.907', '+2.975', '-0.035', '-0.036', '3.00 / f.u.', '1.82 (dir)', 'Initial $d$-electron localization'],
    ['PBE+D3+$U_{\\mathrm{Cr}}$', '2.00', '+2.971', '+3.040', '-0.048', '-0.049', '3.00 / f.u.', '2.18 (dir)', 'Progressive gap widening'],
    ['PBE+D3+$U_{\\mathrm{Cr}}$', '3.00', '+3.033', '+3.103', '-0.060', '-0.062', '3.00 / f.u.', '2.48 (dir)', 'Approaching optimal lattice compliance'],
    ['PBE+D3+$U_{\\mathrm{Cr}}$ ★ Optimal', '3.29', '+3.047', '+3.117', '-0.063', '-0.064', '3.00 / f.u.', '2.56 (dir)', 'Matches experimental $a_0 = 6.056$ Å & LR'],
    ['PBE+D3+$U_{\\mathrm{Cr}}$', '4.00', '+3.094', '+3.165', '-0.073', '-0.075', '3.00 / f.u.', '2.59 (dir)', 'Saturating gap opening'],
    ['PBE+D3+$U_{\\mathrm{Cr}}$', '5.00', '+3.153', '+3.226', '-0.086', '-0.088', '3.00 / f.u.', '2.68 (dir)', 'Strongly localized limit'],
    ['PBE+D3+$U_{\\mathrm{Cr}}$', '6.00', '+3.211', '+3.285', '-0.098', '-0.100', '3.00 / f.u.', '2.77 (dir)', 'Upper correlation bound']
]

for row_idx, r in enumerate(data_2):
    is_opt = ('★' in r[0])
    bg = highlight_bg if is_opt else (alt_row_bg if row_idx % 2 == 1 else '#ffffff')
    border_w = 1.6 if is_opt else 0.5
    bcolor = accent_gold if is_opt else border_color
    
    r_rect = patches.Rectangle((0.04, y_pos - row_h2), 0.92, row_h2, facecolor=bg, edgecolor=bcolor, linewidth=border_w)
    ax.add_patch(r_rect)
    
    for c_idx in range(len(col_x2) - 1):
        mid_x = (col_x2[c_idx] + col_x2[c_idx+1]) / 2.0
        val = r[c_idx]
        
        fweight = 'bold' if is_opt or c_idx == 0 else 'normal'
        tcolor = text_main
        if is_opt and c_idx == 0:
            tcolor = '#b45309' # Dark amber
        elif c_idx == 3: # Cr total
            tcolor = '#0369a1'
        elif c_idx == 5: # Cl total
            tcolor = '#dc2626'
            
        ax.text(mid_x, y_pos - row_h2/2.0, val,
                color=tcolor, fontsize=8.4, fontweight=fweight, ha='center', va='center')
        
    y_pos -= row_h2

# ==============================================================================
# Section 3: Physical Insights & Summary Cards
# ==============================================================================
y_pos -= 0.034

card_w = 0.293
card_h = 0.125
card_spacing = 0.020

# Card 1: Cr3+ Local Moment Origin
c1_x = 0.04
c1_box = patches.FancyBboxPatch(
    (c1_x, y_pos - card_h), card_w, card_h,
    boxstyle="round,pad=0.008,rounding_size=0.012",
    facecolor='#f0f9ff', edgecolor='#bae6fd', linewidth=1.2
)
ax.add_patch(c1_box)
ax.text(c1_x + 0.012, y_pos - 0.016, '①  Cr³⁺ Local Moment ($3d^3$)', color='#0369a1', fontsize=9.5, fontweight='bold', va='top')
txt_c1 = (
    "• Octahedral ligand field ($D_{3d}$) splits $3d$ levels into\n"
    "  an occupied $t_{2g}^3 (\\uparrow\\uparrow\\uparrow)$ triplet and empty $e_g^0$ doublet.\n"
    "• High-spin $S = 3/2$ produces $3.000\\,\\mu_{\\mathrm{B}}$ formal spin.\n"
    "• Projected Wigner-Seitz moment: $+3.117\\,\\mu_{\\mathrm{B}}$\n"
    "  (98% localized in $3d$ manifold: $m_d = 3.047\\,\\mu_{\\mathrm{B}}$)."
)
ax.text(c1_x + 0.012, y_pos - 0.038, txt_c1, color='#0c4a6e', fontsize=7.8, va='top', linespacing=1.35)

# Card 2: Cl- Superexchange & Negative Polarization
c2_x = c1_x + card_w + card_spacing
c2_box = patches.FancyBboxPatch(
    (c2_x, y_pos - card_h), card_w, card_h,
    boxstyle="round,pad=0.008,rounding_size=0.012",
    facecolor='#f0fdf4', edgecolor='#bbf7d0', linewidth=1.2
)
ax.add_patch(c2_box)
ax.text(c2_x + 0.012, y_pos - 0.016, '②  Cl⁻ Negative Spin Polarization', color='#15803d', fontsize=9.5, fontweight='bold', va='top')
txt_c2 = (
    "• Ligand Cl⁻ ($3p^6$) exhibits net negative polarization\n"
    "  opposite to Cr: $m_{\\mathrm{tot}}(\\mathrm{Cl}) = -0.064\\,\\mu_{\\mathrm{B}}$.\n"
    "• Arises from Goodenough–Kanamori superexchange\n"
    "  and covalent virtual hopping between Cr-$3d$ and Cl-$3p$.\n"
    "• High symmetry: all 24 Cl atoms in $2\\times 2$ are equivalent\n"
    "  and carry identical negative polarization."
)
ax.text(c2_x + 0.012, y_pos - 0.038, txt_c2, color='#14532d', fontsize=7.8, va='top', linespacing=1.35)

# Card 3: Exact Integer Cell Magnetization
c3_x = c2_x + card_w + card_spacing
c3_box = patches.FancyBboxPatch(
    (c3_x, y_pos - card_h), card_w, card_h,
    boxstyle="round,pad=0.008,rounding_size=0.012",
    facecolor='#fefce8', edgecolor='#fef08a', linewidth=1.2
)
ax.add_patch(c3_box)
ax.text(c3_x + 0.012, y_pos - 0.016, '③  Integer Integer Total Magnetization', color='#a16207', fontsize=9.5, fontweight='bold', va='top')
txt_c3 = (
    "• Total cell moment is strictly integer:\n"
    "  $M_{\\mathrm{tot}} = 24.000\\,\\mu_{\\mathrm{B}}$ ($2\\times 2$, 8 f.u.) = $3.000\\,\\mu_{\\mathrm{B}}/\\mathrm{f.u.}$\n"
    "• Ferromagnetic insulator ground state with integer\n"
    "  valence band filling and clean gap to empty states.\n"
    "• Interstitial space carries $+0.60\\,\\mu_{\\mathrm{B}}$ background\n"
    "  balancing local Cr core and Cl ligand projections."
)
ax.text(c3_x + 0.012, y_pos - 0.038, txt_c3, color='#713f12', fontsize=7.8, va='top', linespacing=1.35)

# ==============================================================================
# Save Figure to Destination Folders
# ==============================================================================
out_dirs = [
    '/home/cr/simulations/crcl3-HER/crcl3-newcals/postprosseing/images-juan/01_Fig1_Pristine_Monolayer',
    '/home/cr/simulations/crcl3-HER/crcl3-newcals/postprosseing/images-juan'
]

for d in out_dirs:
    os.makedirs(d, exist_ok=True)
    png_path = os.path.join(d, 'table_pristine_magnetic_moments.png')
    pdf_path = os.path.join(d, 'table_pristine_magnetic_moments.pdf')
    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor=bg_color)
    plt.savefig(pdf_path, bbox_inches='tight', facecolor=bg_color)
    print(f'Successfully saved: {png_path}')
    print(f'Successfully saved: {pdf_path}')

plt.close()
print("Done!")
