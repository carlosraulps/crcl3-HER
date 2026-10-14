#!/usr/bin/env python3
"""
generate_fig_s1_coordination.py
===============================
Generates publication-quality Figure S1 (Local Coordination Geometries & Bond Distances)
for:
  1. Single-site +U_Cr (U_Cr = 3.29 eV, U_TM = 0.0 eV) -> new_sup_fig_1_Ucr.png/.pdf
  2. Multi-site +U_all (U_Cr = U_TM = 3.29 eV) -> new_sup_fig_1_Uall.png/.pdf

Adheres strictly to GEMINI.md Publication Anti-Collision Policy:
  - STIX math & Times New Roman typography
  - Collision-free bond distance annotations
  - Matched 2-row layout: Top row: (a) Co, (b) Fe; Bottom row: (c) Ni
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from ase.io import read

# Typography setup
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['mathtext.fontset'] = 'stix'

COLORS = {
    'Cr': '#85c1e9',   # Light Blue
    'Cl': '#82e0aa',   # Light Green
    'Co': '#e74c3c',   # Vibrant Red
    'Fe': '#e67e22',   # Warm Orange
    'Ni': '#9b59b6'    # Distinct Purple
}

SIZES = {'Cr': 380, 'Cl': 340, 'TM': 460}

def get_local_cluster(atoms, tm_symbol, cl_cutoff=3.2, cr_cutoff=4.2):
    """Extract coordinates of the TM center and its Cl/Cr neighbors using minimum image convention."""
    tm_indices = [i for i, a in enumerate(atoms) if a.symbol == tm_symbol]
    if not tm_indices:
        # Fallback to atom 33 (0-indexed 32)
        tm_idx = 32
    else:
        tm_idx = tm_indices[0]
        
    cell = atoms.get_cell()
    pos = atoms.get_positions()
    center_pos = pos[tm_idx]
    
    rel_pos = pos - center_pos
    rel_pos = np.dot(rel_pos, np.linalg.inv(cell))
    rel_pos = (rel_pos + 0.5) % 1.0 - 0.5
    rel_pos = np.dot(rel_pos, cell)
    
    dists = np.linalg.norm(rel_pos, axis=1)
    
    cl_neighbors = []
    cr_neighbors = []
    
    for i, d in enumerate(dists):
        if i == tm_idx:
            continue
        sym = atoms[i].symbol
        if sym == 'Cl' and d < cl_cutoff:
            cl_neighbors.append((i + 1, rel_pos[i], d))
        elif sym == 'Cr' and d < cr_cutoff:
            cr_neighbors.append((i + 1, rel_pos[i], d))
            
    # Sort Cl neighbors by distance
    cl_neighbors.sort(key=lambda x: x[2])
    return rel_pos[tm_idx], cl_neighbors, cr_neighbors

def group_projection_points(points, indices_2d, threshold=0.35):
    """Group points that project closely in 2D."""
    grouped = []
    used = set()
    projected = [(idx, np.array([p[indices_2d[0]], p[indices_2d[1]]]), d, p) for idx, p, d in points]
    
    for i in range(len(projected)):
        if i in used:
            continue
        cluster = [projected[i]]
        used.add(i)
        for j in range(i + 1, len(projected)):
            if j in used:
                continue
            if np.linalg.norm(projected[i][1] - projected[j][1]) < threshold:
                cluster.append(projected[j])
                used.add(j)
                
        if len(cluster) == 1:
            lbl = f"Cl$_{{{cluster[0][0]}}}$"
            mean_2d = cluster[0][1]
            mean_3d = cluster[0][3]
            mean_d = cluster[0][2]
        else:
            idxs = sorted([c[0] for c in cluster])
            lbl = f"Cl$_{{{','.join(map(str, idxs))}}}$"
            mean_2d = np.mean([c[1] for c in cluster], axis=0)
            mean_3d = np.mean([c[3] for c in cluster], axis=0)
            mean_d = np.mean([c[2] for c in cluster])
        grouped.append((lbl, mean_2d, mean_3d, mean_d))
    return grouped

def draw_subpanel(ax, atoms, tm_symbol, mode, view_type):
    """Draw a single subpanel (Top XY or Side XZ)."""
    center_pos, cl_list, cr_list = get_local_cluster(atoms, tm_symbol)
    proj_idx = (0, 1) if view_type == 'XY' else (0, 2)
    tm_2d = center_pos[[proj_idx[0], proj_idx[1]]]
    
    all_pts = [tm_2d]
    
    # 1. Background Cr atoms
    for idx, p, d in cr_list:
        p2 = p[[proj_idx[0], proj_idx[1]]]
        ax.scatter(p2[0], p2[1], s=SIZES['Cr'], color=COLORS['Cr'], edgecolors='#555555', alpha=0.45, zorder=1)
        t = ax.text(p2[0], p2[1], f"Cr$_{{{idx}}}$", ha='center', va='center', fontsize=8, color='#2c3e50', zorder=2)
        t.set_path_effects([path_effects.withStroke(linewidth=2, foreground='white')])
        all_pts.append(p2)
        
    # 2. Cl ligands and bond lines
    grouped_cl = group_projection_points(cl_list, proj_idx)
    for lbl, p2, p3, d in grouped_cl:
        ax.scatter(p2[0], p2[1], s=SIZES['Cl'], color=COLORS['Cl'], edgecolors='#1e8449', linewidth=1.2, zorder=3)
        t = ax.text(p2[0], p2[1], lbl, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#145a32', zorder=4)
        t.set_path_effects([path_effects.withStroke(linewidth=2.2, foreground='white')])
        
        # Bond line
        ax.plot([center_pos[proj_idx[0]], p3[proj_idx[0]]], [center_pos[proj_idx[1]], p3[proj_idx[1]]],
                color='#333333', linestyle='--', linewidth=1.2, zorder=2)
        
        # Bond distance annotation (only on Top View XY to prevent visual crowding)
        if view_type == 'XY':
            mid = 0.5 * (tm_2d + p2)
            offset = 0.16 if p2[1] >= tm_2d[1] else -0.18
            t_dist = ax.text(mid[0], mid[1] + offset, f"{d:.2f} Å", ha='center', va='center',
                             fontsize=8.5, fontweight='bold', color='#111111', zorder=5)
            t_dist.set_path_effects([path_effects.withStroke(linewidth=2.5, foreground='white')])
            
        all_pts.append(p2)
        
    # 3. Central TM atom
    ax.scatter(tm_2d[0], tm_2d[1], s=SIZES['TM'], color=COLORS[tm_symbol], edgecolors='#111111', linewidth=1.4, zorder=6)
    t_tm = ax.text(tm_2d[0], tm_2d[1], f"{tm_symbol}$_{{33}}$", ha='center', va='center',
                   fontsize=9.5, fontweight='bold', color='white', zorder=7)
    t_tm.set_path_effects([path_effects.withStroke(linewidth=2.5, foreground='black')])
    
    # Axis formatting
    ax.set_title(f"{tm_symbol} {mode.capitalize()} - {'Top View (XY)' if view_type=='XY' else 'Side View (XZ)'}",
                 fontsize=10, fontweight='bold', pad=6)
    ax.set_xlabel("X (Å)", fontsize=9)
    ax.set_ylabel("Y (Å)" if view_type=='XY' else "Z (Å)", fontsize=9)
    ax.grid(True, linestyle=':', alpha=0.55, zorder=0)
    
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    pad = 0.75
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(min(ys) - pad, max(ys) + pad)
    ax.set_aspect('equal', 'box')

def generate_figure(tier_name, struct_dict, out_prefix):
    """Renders the full composite Fig S1 with 3 bounded panels (a, b, c)."""
    fig = plt.figure(figsize=(15.5, 13.5), dpi=300)
    
    # Layout using GridSpec:
    # Row 0: Panel (a) Co [2x2] and Panel (b) Fe [2x2]
    # Row 1: Panel (c) Ni [2x2] centered
    gs = fig.add_gridspec(2, 4, height_ratios=[1, 1], hspace=0.28, wspace=0.25)
    
    # Panel (a) Co: gs[0, 0:2]
    sub_gs_a = gs[0, 0:2].subgridspec(2, 2, hspace=0.26, wspace=0.22)
    ax_a_xy = fig.add_subplot(sub_gs_a[0, 0])
    ax_e_xy = fig.add_subplot(sub_gs_a[0, 1])
    ax_a_xz = fig.add_subplot(sub_gs_a[1, 0])
    ax_e_xz = fig.add_subplot(sub_gs_a[1, 1])
    
    draw_subpanel(ax_a_xy, struct_dict['Co']['ads'], 'Co', 'Adsorbed', 'XY')
    draw_subpanel(ax_e_xy, struct_dict['Co']['emb'], 'Co', 'Embedded', 'XY')
    draw_subpanel(ax_a_xz, struct_dict['Co']['ads'], 'Co', 'Adsorbed', 'XZ')
    draw_subpanel(ax_e_xz, struct_dict['Co']['emb'], 'Co', 'Embedded', 'XZ')
    
    # Panel (b) Fe: gs[0, 2:4]
    sub_gs_b = gs[0, 2:4].subgridspec(2, 2, hspace=0.26, wspace=0.22)
    ax_b_a_xy = fig.add_subplot(sub_gs_b[0, 0])
    ax_b_e_xy = fig.add_subplot(sub_gs_b[0, 1])
    ax_b_a_xz = fig.add_subplot(sub_gs_b[1, 0])
    ax_b_e_xz = fig.add_subplot(sub_gs_b[1, 1])
    
    draw_subpanel(ax_b_a_xy, struct_dict['Fe']['ads'], 'Fe', 'Adsorbed', 'XY')
    draw_subpanel(ax_b_e_xy, struct_dict['Fe']['emb'], 'Fe', 'Embedded', 'XY')
    draw_subpanel(ax_b_a_xz, struct_dict['Fe']['ads'], 'Fe', 'Adsorbed', 'XZ')
    draw_subpanel(ax_b_e_xz, struct_dict['Fe']['emb'], 'Fe', 'Embedded', 'XZ')
    
    # Panel (c) Ni: gs[1, 1:3] (Centered)
    sub_gs_c = gs[1, 1:3].subgridspec(2, 2, hspace=0.26, wspace=0.22)
    ax_c_a_xy = fig.add_subplot(sub_gs_c[0, 0])
    ax_c_e_xy = fig.add_subplot(sub_gs_c[0, 1])
    ax_c_a_xz = fig.add_subplot(sub_gs_c[1, 0])
    ax_c_e_xz = fig.add_subplot(sub_gs_c[1, 1])
    
    draw_subpanel(ax_c_a_xy, struct_dict['Ni']['ads'], 'Ni', 'Adsorbed', 'XY')
    draw_subpanel(ax_c_e_xy, struct_dict['Ni']['emb'], 'Ni', 'Embedded', 'XY')
    draw_subpanel(ax_c_a_xz, struct_dict['Ni']['ads'], 'Ni', 'Adsorbed', 'XZ')
    draw_subpanel(ax_c_e_xz, struct_dict['Ni']['emb'], 'Ni', 'Embedded', 'XZ')
    
    # Add overarching panel letters and outer dashed bounding box for each panel
    for label, cell in [('(a)', gs[0, 0:2]), ('(b)', gs[0, 2:4]), ('(c)', gs[1, 1:3])]:
        pos = cell.get_position(fig)
        pad_x = 0.012
        pad_y = 0.014
        rect = plt.Rectangle(
            (pos.x0 - pad_x, pos.y0 - pad_y),
            pos.width + 2 * pad_x, pos.height + 2 * pad_y,
            edgecolor='#222222', facecolor='none', linestyle='--', linewidth=1.2,
            transform=fig.transFigure, clip_on=False
        )
        fig.add_artist(rect)
        fig.text(pos.x0 - pad_x, pos.y0 + pos.height + pad_y + 0.008, label,
                 fontsize=22, fontweight='bold', va='bottom', ha='left')
    
    png_path = f"{out_prefix}.png"
    pdf_path = f"{out_prefix}.pdf"
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    plt.savefig(pdf_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[✓] {tier_name} Fig S1 generated: {png_path} and {pdf_path}")

def main():
    base = "/Volumes/KingstonSSD/Krojects/Kresearch/crlcl3-CoFeNi-HER/crcl3-newcals"
    acs_fig_dir = "/Volumes/KingstonSSD/Krojects/Kresearch/crlcl3-CoFeNi-HER/ACS_version/ACS_resubmission/figure"
    os.makedirs(acs_fig_dir, exist_ok=True)
    
    # 1. Single-Site +U_Cr (U_Cr = 3.29 eV)
    structs_ucr = {}
    for tm in ['Co', 'Fe', 'Ni']:
        ads_p = os.path.join(base, f"cohp_lobster_Ucr/adsorbed/{tm}/POSCAR")
        emb_p = os.path.join(base, f"cohp_lobster_Ucr/embedded/{tm}/POSCAR")
        structs_ucr[tm] = {'ads': read(ads_p), 'emb': read(emb_p)}
        
    generate_figure("+U_Cr (Single-Site)", structs_ucr, os.path.join(acs_fig_dir, "new_sup_fig_1_Ucr"))
    
    # 2. Multi-Site +U_all (U_all = 3.29 eV)
    structs_uall = {}
    for tm in ['Co', 'Fe', 'Ni']:
        ads_p = os.path.join(base, f"crcl3-2x2-CoFeNi-vdw12-U_all3.29/adsorbed/{tm}/clean/CONTCAR")
        emb_p = os.path.join(base, f"crcl3-2x2-CoFeNi-vdw12-U_all3.29/embedded/{tm}/clean/CONTCAR")
        structs_uall[tm] = {'ads': read(ads_p), 'emb': read(emb_p)}
        
    generate_figure("+U_all (Multi-Site)", structs_uall, os.path.join(acs_fig_dir, "new_sup_fig_1_Uall"))
    
    # Also sync into main ACS_version/figure
    main_fig_dir = "/Volumes/KingstonSSD/Krojects/Kresearch/crlcl3-CoFeNi-HER/ACS_version/figure"
    for ext in ['png', 'pdf']:
        os.system(f"cp {acs_fig_dir}/new_sup_fig_1_Ucr.{ext} {main_fig_dir}/new_sup_fig_1_Ucr.{ext}")
        os.system(f"cp {acs_fig_dir}/new_sup_fig_1_Uall.{ext} {main_fig_dir}/new_sup_fig_1_Uall.{ext}")
        
    # By default, link new_sup_fig_1.png to Ucr (or user's preferred tier)
    os.system(f"cp {acs_fig_dir}/new_sup_fig_1_Ucr.png {acs_fig_dir}/new_sup_fig_1.png")
    os.system(f"cp {acs_fig_dir}/new_sup_fig_1_Ucr.png {main_fig_dir}/new_sup_fig_1.png")
    print("[✓] All Fig S1 files successfully generated and synchronized across ACS submission folders.")

if __name__ == "__main__":
    main()
