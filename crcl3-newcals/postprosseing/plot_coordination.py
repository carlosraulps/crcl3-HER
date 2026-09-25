import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import ase.io

# Setup paths
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
post_dir = os.path.join(base_dir, "postprosseing")
os.makedirs(post_dir, exist_ok=True)

# ----------------------------------------------------
# Matplotlib Premium Design Settings (Times New Roman)
# ----------------------------------------------------
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['mathtext.fontset'] = 'stix'

# Color palette for elements
colors = {
    'Cr': '#85c1e9',  # Light Blue
    'Cl': '#82e0aa',  # Light Green
    'Co': '#e74c3c',  # Vibrant Red
    'Fe': '#e67e22',  # Warm Orange
    'Ni': '#9b59b6'   # Distinct Purple
}

# Increased atom sizes for high-res visibility
sizes = {
    'Cr': 900,
    'Cl': 800,
    'Co': 1100
}

def get_local_cluster(atoms, center_idx, cl_cutoff=3.0, cr_cutoff=4.0):
    """Extract coordinates of the center atom and its neighbors using minimum image convention."""
    cell = atoms.get_cell()
    pos = atoms.get_positions()
    center_pos = pos[center_idx]
    
    # Calculate relative positions with minimum image convention
    rel_pos = pos - center_pos
    rel_pos = np.dot(rel_pos, np.linalg.inv(cell))
    rel_pos = (rel_pos + 0.5) % 1.0 - 0.5
    rel_pos = np.dot(rel_pos, cell)
    
    # Identify neighbors
    dists = np.linalg.norm(rel_pos, axis=1)
    
    cl_neighbors = []
    cr_neighbors = []
    
    for i, d in enumerate(dists):
        if i == center_idx:
            continue
        symbol = atoms[i].symbol
        if symbol == 'Cl' and d < cl_cutoff:
            cl_neighbors.append((i + 1, rel_pos[i], d))  # 1-indexed
        elif symbol == 'Cr' and d < cr_cutoff:
            cr_neighbors.append((i + 1, rel_pos[i], d))  # 1-indexed
            
    return rel_pos[center_idx], cl_neighbors, cr_neighbors

def group_projection_points(points, indices_2d, threshold=0.3):
    """
    Groups points that are close to each other in a specific 2D projection.
    points: list of tuples (idx, 3D_rel_pos, distance)
    indices_2d: tuple of indices for projection (e.g. (0, 1) for XY, (0, 2) for XZ)
    """
    grouped = []
    used = set()
    
    # Project to 2D
    projected = []
    for idx, p, d in points:
        projected.append((idx, np.array([p[indices_2d[0]], p[indices_2d[1]]]), d, p))
        
    for i in range(len(projected)):
        if i in used:
            continue
        idx_i, pos_2d_i, d_i, pos_3d_i = projected[i]
        cluster = [projected[i]]
        used.add(i)
        
        for j in range(i+1, len(projected)):
            if j in used:
                continue
            idx_j, pos_2d_j, d_j, pos_3d_j = projected[j]
            dist_2d = np.linalg.norm(pos_2d_i - pos_2d_j)
            if dist_2d < threshold:
                cluster.append(projected[j])
                used.add(j)
                
        if len(cluster) == 1:
            label = f"Cl$_{{{cluster[0][0]}}}$"
            mean_pos_2d = cluster[0][1]
            mean_pos_3d = cluster[0][3]
            mean_d = cluster[0][2]
        else:
            idxs = sorted([c[0] for c in cluster])
            idx_str = ",".join(map(str, idxs))
            label = f"Cl$_{{{idx_str}}}$"
            mean_pos_2d = np.mean([c[1] for c in cluster], axis=0)
            mean_pos_3d = np.mean([c[3] for c in cluster], axis=0)
            mean_d = np.mean([c[2] for c in cluster])
            
        grouped.append((label, mean_pos_2d, mean_pos_3d, mean_d))
        
    return grouped

def draw_text_with_outline(ax, x, y, text, color, size=11, weight='bold', is_white_bg=False):
    """Draws text on the axes with a thick outline to prevent background overlaps."""
    t = ax.text(x, y, text, ha='center', va='center', fontsize=size, fontweight=weight, color=color, zorder=10)
    if is_white_bg:
        outline_color = 'black'
    else:
        outline_color = 'white'
    t.set_path_effects([path_effects.withStroke(linewidth=3, foreground=outline_color)])
    return t

def setup_ax_limits_and_labels(ax, title, xlabel, ylabel, all_coords_2d):
    """Sets titles, labels, grids, aspect ratios, and safe window margins."""
    ax.set_title(title, fontsize=13, fontweight='bold', pad=10)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.grid(True, linestyle=':', alpha=0.5, zorder=0)
    
    # Calculate margins to avoid clipping circles
    xs = [p[0] for p in all_coords_2d]
    ys = [p[1] for p in all_coords_2d]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    
    padding = 0.8  # Ångström margin around outer atoms
    ax.set_xlim(xmin - padding, xmax + padding)
    ax.set_ylim(ymin - padding, ymax + padding)
    ax.set_aspect('equal', 'box')

# Co index is 33 (0-indexed 32 in python) for all systems
co_idx = 32
tms_names = ['Co', 'Fe', 'Ni']

# Create 3 rows (one per TM) and 4 columns (Ads-Top, Ads-Side, Emb-Top, Emb-Side)
fig, axes = plt.subplots(3, 4, figsize=(20, 15.5))

for r, tm in enumerate(tms_names):
    # Load POSCAR files
    ads = ase.io.read(os.path.join(base_dir, f'adsorbed/{tm.lower()}/POSCAR'))
    emb = ase.io.read(os.path.join(base_dir, f'embedded/{tm.lower()}/POSCAR'))
    
    ads_co_pos, ads_cl, ads_cr = get_local_cluster(ads, co_idx, cl_cutoff=3.0, cr_cutoff=4.0)
    emb_co_pos, emb_cl, emb_cr = get_local_cluster(emb, co_idx, cl_cutoff=3.0, cr_cutoff=4.0)
    
    # ------------------
    # Adsorbed - Column 0 (XY) & 1 (XZ)
    # ------------------
    ads_co_xy = ads_co_pos[[0, 1]]
    ads_co_xz = ads_co_pos[[0, 2]]
    
    # Col 0: Top View XY
    ax = axes[r, 0]
    all_pts_xy = [ads_co_xy]
    # Plot Cr background
    for idx, p, d in ads_cr:
        ax.scatter(p[0], p[1], s=sizes['Cr'], color=colors['Cr'], edgecolors='black', alpha=0.4, zorder=1)
        draw_text_with_outline(ax, p[0], p[1], f"Cr$_{{{idx}}}$", color='black', size=9.5, weight='normal')
        all_pts_xy.append(p[[0, 1]])
    # Group Cl neighbors
    grouped_cl_xy = group_projection_points(ads_cl, (0, 1))
    for label, pos_2d, pos_3d, d in grouped_cl_xy:
        ax.scatter(pos_2d[0], pos_2d[1], s=sizes['Cl'], color=colors['Cl'], edgecolors='black', zorder=2)
        draw_text_with_outline(ax, pos_2d[0], pos_2d[1], label, color='black', size=11)
        ax.plot([ads_co_pos[0], pos_3d[0]], [ads_co_pos[1], pos_3d[1]], color='black', linestyle='--', linewidth=1.5, zorder=1)
        mid = 0.5 * (ads_co_xy + pos_2d)
        t = ax.text(mid[0], mid[1] + 0.15, f"{d:.2f} Å", ha='center', va='center', fontsize=9.5, fontweight='bold', color='black', zorder=4)
        t.set_path_effects([path_effects.withStroke(linewidth=2.5, foreground='white')])
        all_pts_xy.append(pos_2d)
    # Plot TM (Co, Fe, or Ni)
    ax.scatter(ads_co_xy[0], ads_co_xy[1], s=sizes['Co'], color=colors[tm], edgecolors='black', zorder=3)
    draw_text_with_outline(ax, ads_co_xy[0], ads_co_xy[1], f"{tm}$_{{{co_idx+1}}}$", color='white', size=11, is_white_bg=True)
    
    setup_ax_limits_and_labels(ax, f"{tm} Adsorbed - Top View (XY)", "X (Å)", "Y (Å)", all_pts_xy)
    
    # Col 1: Side View XZ
    ax = axes[r, 1]
    all_pts_xz = [ads_co_xz]
    for idx, p, d in ads_cr:
        ax.scatter(p[0], p[2], s=sizes['Cr'], color=colors['Cr'], edgecolors='black', alpha=0.4, zorder=1)
        draw_text_with_outline(ax, p[0], p[2], f"Cr$_{{{idx}}}$", color='black', size=9.5, weight='normal')
        all_pts_xz.append(p[[0, 2]])
    grouped_cl_xz = group_projection_points(ads_cl, (0, 2))
    for label, pos_2d, pos_3d, d in grouped_cl_xz:
        ax.scatter(pos_2d[0], pos_2d[1], s=sizes['Cl'], color=colors['Cl'], edgecolors='black', zorder=2)
        draw_text_with_outline(ax, pos_2d[0], pos_2d[1], label, color='black', size=11)
        ax.plot([ads_co_pos[0], pos_3d[0]], [ads_co_pos[2], pos_3d[2]], color='black', linestyle='--', linewidth=1.5, zorder=1)
        all_pts_xz.append(pos_2d)
    ax.scatter(ads_co_xz[0], ads_co_xz[1], s=sizes['Co'], color=colors[tm], edgecolors='black', zorder=3)
    draw_text_with_outline(ax, ads_co_xz[0], ads_co_xz[1], f"{tm}$_{{{co_idx+1}}}$", color='white', size=11, is_white_bg=True)
    
    setup_ax_limits_and_labels(ax, f"{tm} Adsorbed - Side View (XZ)", "X (Å)", "Z (Å)", all_pts_xz)
    
    # ------------------
    # Embedded - Column 2 (XY) & 3 (XZ)
    # ------------------
    emb_co_xy = emb_co_pos[[0, 1]]
    emb_co_xz = emb_co_pos[[0, 2]]
    
    # Col 2: Top View XY
    ax = axes[r, 2]
    all_pts_emb_xy = [emb_co_xy]
    for idx, p, d in emb_cr:
        ax.scatter(p[0], p[1], s=sizes['Cr'], color=colors['Cr'], edgecolors='black', alpha=0.4, zorder=1)
        draw_text_with_outline(ax, p[0], p[1], f"Cr$_{{{idx}}}$", color='black', size=9.5, weight='normal')
        all_pts_emb_xy.append(p[[0, 1]])
    grouped_emb_cl_xy = group_projection_points(emb_cl, (0, 1))
    for label, pos_2d, pos_3d, d in grouped_emb_cl_xy:
        ax.scatter(pos_2d[0], pos_2d[1], s=sizes['Cl'], color=colors['Cl'], edgecolors='black', zorder=2)
        draw_text_with_outline(ax, pos_2d[0], pos_2d[1], label, color='black', size=11)
        ax.plot([emb_co_pos[0], pos_3d[0]], [emb_co_pos[1], pos_3d[1]], color='black', linestyle='--', linewidth=1.5, zorder=1)
        mid = 0.5 * (emb_co_xy + pos_2d)
        # Stagger offsets slightly to avoid overlaps
        y_offset = 0.18 if pos_2d[1] > 0 else -0.22
        t = ax.text(mid[0], mid[1] + y_offset, f"{d:.2f} Å", ha='center', va='center', fontsize=9.5, fontweight='bold', color='black', zorder=4)
        t.set_path_effects([path_effects.withStroke(linewidth=2.5, foreground='white')])
        all_pts_emb_xy.append(pos_2d)
    ax.scatter(emb_co_xy[0], emb_co_xy[1], s=sizes['Co'], color=colors[tm], edgecolors='black', zorder=3)
    draw_text_with_outline(ax, emb_co_xy[0], emb_co_xy[1], f"{tm}$_{{{co_idx+1}}}$", color='white', size=11, is_white_bg=True)
    
    setup_ax_limits_and_labels(ax, f"{tm} Embedded - Top View (XY)", "X (Å)", "Y (Å)", all_pts_emb_xy)
    
    # Col 3: Side View XZ
    ax = axes[r, 3]
    all_pts_emb_xz = [emb_co_xz]
    for idx, p, d in emb_cr:
        ax.scatter(p[0], p[2], s=sizes['Cr'], color=colors['Cr'], edgecolors='black', alpha=0.4, zorder=1)
        draw_text_with_outline(ax, p[0], p[2], f"Cr$_{{{idx}}}$", color='black', size=9.5, weight='normal')
        all_pts_emb_xz.append(p[[0, 2]])
    grouped_emb_cl_xz = group_projection_points(emb_cl, (0, 2))
    for label, pos_2d, pos_3d, d in grouped_emb_cl_xz:
        ax.scatter(pos_2d[0], pos_2d[1], s=sizes['Cl'], color=colors['Cl'], edgecolors='black', zorder=2)
        draw_text_with_outline(ax, pos_2d[0], pos_2d[1], label, color='black', size=11)
        ax.plot([emb_co_pos[0], pos_3d[0]], [emb_co_pos[2], pos_3d[2]], color='black', linestyle='--', linewidth=1.5, zorder=1)
        all_pts_emb_xz.append(pos_2d)
    ax.scatter(emb_co_xz[0], emb_co_xz[1], s=sizes['Co'], color=colors[tm], edgecolors='black', zorder=3)
    draw_text_with_outline(ax, emb_co_xz[0], emb_co_xz[1], f"{tm}$_{{{co_idx+1}}}$", color='white', size=11, is_white_bg=True)
    
    setup_ax_limits_and_labels(ax, f"{tm} Embedded - Side View (XZ)", "X (Å)", "Z (Å)", all_pts_emb_xz)

plt.suptitle(r"Coordination Geometries for Transition Metal (TM)-doped Monolayer $\mathrm{CrCl_3}$", fontsize=18, fontweight='bold', y=0.99)
plt.tight_layout()
save_path = os.path.join(post_dir, "coordination_schematics.png")
plt.savefig(save_path, dpi=300)
plt.close()
print(f"Coordination schematics saved to {save_path}")

# =============================================================================
# MANIM 3D ANIMATION
# =============================================================================
# To run this, execute: ~/venvs/manim/bin/python3 plot_coordination.py --animate
import sys

# Prevent Matplotlib from blocking or re-running if imported by manim
try:
    from manim import *
    HAS_MANIM = True
except ImportError:
    HAS_MANIM = False

if HAS_MANIM:
    class Coordination3DAnimation(ThreeDScene):
        def construct(self):
            # Camera orientation setup
            self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES)
            self.begin_ambient_camera_rotation(rate=0.15)
            
            # Master Title
            master_title = Text("3D Coordination Geometries (CrCl3 Monolayer)", font="Times New Roman", weight=BOLD).scale(0.6).to_corner(UL)
            self.add_fixed_in_frame_mobjects(master_title)
            
            # Sequence: Adsorbed Co, Fe, Ni -> Embedded Co, Fe, Ni
            systems = [
                ('adsorbed', 'Co', 'Adsorbed Co System'),
                ('adsorbed', 'Fe', 'Adsorbed Fe System'),
                ('adsorbed', 'Ni', 'Adsorbed Ni System'),
                ('embedded', 'Co', 'Embedded Co System'),
                ('embedded', 'Fe', 'Embedded Fe System'),
                ('embedded', 'Ni', 'Embedded Ni System'),
            ]
            
            co_idx = 32  # 1-indexed atom 33
            
            sub_title = None
            
            for state, tm, label in systems:
                # Update Subtitle
                new_sub = Text(label, font="Times New Roman", color=colors[tm]).scale(0.55).next_to(master_title, DOWN, aligned_edge=LEFT)
                self.add_fixed_in_frame_mobjects(new_sub)
                
                if sub_title is not None:
                    self.remove(sub_title)
                sub_title = new_sub
                
                # Load structural data
                poscar_path = os.path.join(base_dir, f"{state}/{tm.lower()}/POSCAR")
                atoms = ase.io.read(poscar_path)
                center_pos, cl_neighbors, cr_neighbors = get_local_cluster(atoms, co_idx, cl_cutoff=3.0, cr_cutoff=4.0)
                
                # Colors
                c_tm = colors[tm]
                c_cl = colors['Cl']
                c_cr = '#b2bec3'  # Soft subtle grey/slate for background Cr
                
                group = VGroup()
                
                # 1. Central TM Sphere
                tm_sphere = Sphere(radius=0.38, color=c_tm).move_to(ORIGIN)
                tm_sphere.set_color(c_tm)
                group.add(tm_sphere)
                
                # TM 3D Label
                tm_lbl = Text(f"{tm}33", font="Times New Roman", weight=BOLD).scale(0.35).move_to(ORIGIN + UP*0.55 + RIGHT*0.1)
                group.add(tm_lbl)
                
                # 2. Cl Neighbor Spheres, Bonds & Labels
                for idx, pos, d in cl_neighbors:
                    cl_sp = Sphere(radius=0.28, color=c_cl).move_to(pos)
                    bond = Line3D(start=ORIGIN, end=pos, color=WHITE, thickness=0.015)
                    cl_lbl = Text(f"Cl{idx}", font="Times New Roman").scale(0.28).move_to(pos + pos/np.linalg.norm(pos)*0.4)
                    group.add(cl_sp, bond, cl_lbl)
                
                # 3. Soft Background Cr Spheres (Transparent & Soft Grey)
                for idx, pos, d in cr_neighbors:
                    cr_sp = Sphere(radius=0.32, color=c_cr).move_to(pos)
                    cr_sp.set_opacity(0.35)
                    group.add(cr_sp)
                
                # Fade in the current system
                self.play(FadeIn(group), run_time=1.5)
                self.wait(2)
                
                # Fade out current system before next
                self.play(FadeOut(group), run_time=1.0)
            
            if sub_title is not None:
                self.remove(sub_title)
            
            # Final message
            final_txt = Text("Coordination Environment Complete", font="Times New Roman").scale(0.6)
            self.add_fixed_in_frame_mobjects(final_txt)
            self.play(FadeIn(final_txt))
            self.wait(2)

if __name__ == "__main__":
    if "--animate" in sys.argv:
        import subprocess
        print("Rendering 3D animation with Manim (Quality: 720p @ 30fps)...")
        manim_bin = os.path.expanduser("~/venvs/manim/bin/manim")
        # Run Manim directly on this file (-pqm specifies 720p at 30fps)
        subprocess.run([manim_bin, "-pqm", __file__, "Coordination3DAnimation"])
        print("Animation rendered successfully in media/ folder!")
