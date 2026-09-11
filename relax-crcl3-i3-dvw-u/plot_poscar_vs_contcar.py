#!/usr/bin/env python3
# /// script
# dependencies = [
#   "matplotlib",
#   "numpy",
# ]
# ///
"""
plot_poscar_vs_contcar.py

Comprehensive comparative analysis of CrCl3 monolayer structural parameters:
Pre-Relaxation (POSCAR) vs Post-Relaxation (CONTCAR) across Hubbard U (0..6 eV),
including step-by-step OUTCAR relaxation trajectories, stress tensors, and
crystallographic symmetry justification for exact hexagonal isotropy (a == b).
"""

import os
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Styling
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "legend.fontsize": 8.5,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "axes.linewidth": 1.0,
    "xtick.major.size": 4.0,
    "ytick.major.size": 4.0,
})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def parse_geo(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]
    scale = float(lines[1])
    v1 = np.array([float(x) for x in lines[2].split()[:3]]) * scale
    v2 = np.array([float(x) for x in lines[3].split()[:3]]) * scale
    v3 = np.array([float(x) for x in lines[4].split()[:3]]) * scale
    a = np.linalg.norm(v1)
    b = np.linalg.norm(v2)
    c = np.linalg.norm(v3)
    gamma = np.degrees(np.arccos(np.clip(np.dot(v1, v2) / (a * b), -1.0, 1.0)))
    
    counts = [int(x) for x in lines[6].split()]
    coords = []
    for i in range(8, 8 + sum(counts)):
        coords.append([float(x) for x in lines[i].split()[:3]])
    
    lat = np.array([v1, v2, v3])
    cart = np.dot(coords, lat)
    cr_z = np.mean(cart[:counts[0], 2])
    top_cl = cart[counts[0]:, 2][cart[counts[0]:, 2] > cr_z]
    bot_cl = cart[counts[0]:, 2][cart[counts[0]:, 2] < cr_z]
    d_z = np.mean(top_cl) - np.mean(bot_cl)
    
    # Cr-Cl bond length
    cr0 = cart[0]
    bonds = []
    for cl in cart[counts[0]:]:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                disp = cl + dx * v1 + dy * v2 - cr0
                d = np.linalg.norm(disp)
                if d < 2.6:
                    bonds.append(d)
    avg_bond = np.mean(bonds)
    return {
        "a": a, "b": b, "c": c, "gamma": gamma,
        "d_z": d_z, "bond": avg_bond
    }

def parse_outcar_steps(outcar_path):
    with open(outcar_path) as f:
        lines = f.readlines()
    steps = []
    for i, l in enumerate(lines):
        if "VOLUME and BASIS-vectors are now :" in l:
            v1_line = lines[i+5].split()
            v2_line = lines[i+6].split()
            v3_line = lines[i+7].split()
            v1 = [float(x) for x in v1_line[:3]]
            v2 = [float(x) for x in v2_line[:3]]
            v3 = [float(x) for x in v3_line[:3]]
            a = (sum(x**2 for x in v1))**0.5
            b = (sum(x**2 for x in v2))**0.5
            c = (sum(x**2 for x in v3))**0.5
            
            s_xx, s_yy, s_zz = 0, 0, 0
            for j in range(max(0, i-35), min(len(lines), i+35)):
                if "in kB" in lines[j]:
                    parts = lines[j].split()
                    s_xx, s_yy, s_zz = float(parts[2]), float(parts[3]), float(parts[4])
                    break
            steps.append({
                "a": a, "b": b, "c": c,
                "s_xx": s_xx, "s_yy": s_yy, "s_zz": s_zz
            })
    return steps

u_vals = list(range(7))
data_pre = []
data_post = []
all_trajectories = {}

for u in u_vals:
    d = os.path.join(BASE_DIR, f"U_{u}")
    pos_p = os.path.join(d, "POSCAR")
    cont_p = os.path.join(d, "CONTCAR")
    out_p = os.path.join(d, "OUTCAR")
    
    geo_pre = parse_geo(pos_p)
    geo_post = parse_geo(cont_p)
    steps = parse_outcar_steps(out_p)
    
    data_pre.append(geo_pre)
    data_post.append(geo_post)
    all_trajectories[u] = steps

# Extract arrays
a_pre = [d["a"] for d in data_pre]
b_pre = [d["b"] for d in data_pre]
a_post = [d["a"] for d in data_post]
b_post = [d["b"] for d in data_post]
c_post = [d["c"] for d in data_post]
gamma_post = [d["gamma"] for d in data_post]
dz_pre = [d["d_z"] for d in data_pre]
dz_post = [d["d_z"] for d in data_post]
bond_pre = [d["bond"] for d in data_pre]
bond_post = [d["bond"] for d in data_post]

delta_a = np.array(a_post) - np.array(a_pre)
s_xx_pre = [all_trajectories[u][0]["s_xx"] for u in u_vals]
s_xx_post = [all_trajectories[u][-1]["s_xx"] for u in u_vals]

# --- PLOTTING 6-PANEL FIGURE ---
fig, axes = plt.subplots(2, 3, figsize=(16, 10.5), dpi=300)
((ax1, ax2, ax3), (ax4, ax5, ax6)) = axes

# Panel 1: POSCAR vs CONTCAR (a & b vs U)
ax1.plot(u_vals, a_pre, 'k--', marker='o', label=r'Initial $a_{\mathrm{pre}}$ (POSCAR)', alpha=0.6)
ax1.plot(u_vals, a_post, color='#1f77b4', marker='s', linewidth=2.0, label=r'Relaxed $a_{\mathrm{post}}$ (CONTCAR)')
ax1.plot(u_vals, b_post, color='#d62728', marker='^', linestyle=':', linewidth=1.5, label=r'Relaxed $b_{\mathrm{post}}$ (CONTCAR)')

# Literature references
ax1.axhline(6.056, color='#2ca02c', linestyle='-.', linewidth=1.3, label='Webster 2018 / Luo 2020 (6.056 Å)')
ax1.axhline(5.985, color='#9467bd', linestyle=':', linewidth=1.3, label='Gao 2018 (5.985 Å)')
ax1.axhline(5.959, color='#8c564b', linestyle='--', linewidth=1.1, label='Bulk Dillon 1966 (5.959 Å)')

for x, y in zip(u_vals, a_post):
    ax1.annotate(f"{y:.4f}", (x, y), textcoords="offset points", xytext=(0, 7),
                 ha='center', fontsize=8.5, fontweight='bold', color='#1f77b4')

ax1.set_xlabel(r'Hubbard $U_{\mathrm{eff}}$ on Cr-$3d$ (eV)')
ax1.set_ylabel(r'In-Plane Lattice Parameters $a, b$ (Å)')
ax1.set_title(r'(a) Lattice $a, b$: Pre- vs. Post-Relaxation', fontweight='bold')
ax1.grid(True, linestyle='--', alpha=0.45)
ax1.legend(loc='lower right', framealpha=0.92, fontsize=8)
ax1.set_ylim(5.94, 6.13)

# Panel 2: Cell Change Delta a vs U
colors = ['#1f77b4' if da > 0 else '#d62728' for da in delta_a]
bars = ax2.bar(u_vals, delta_a, color=colors, width=0.55, edgecolor='black', linewidth=0.8, alpha=0.85)
ax2.axhline(0.0, color='black', linewidth=1.0)
for bar, da in zip(bars, delta_a):
    height = bar.get_height()
    y_pos = height + (0.003 if height >= 0 else -0.008)
    ax2.annotate(f"{da:+.4f} Å", (bar.get_x() + bar.get_width()/2, y_pos),
                 ha='center', fontsize=8.5, fontweight='bold', color='black')

ax2.text(0.5, -0.045, "Contraction\n(reduces initial cell)", color='#d62728', fontsize=9.5, fontweight='bold', ha='center')
ax2.text(4.5, 0.035, "Expansion\n(relieves d-orbital repulsion)", color='#1f77b4', fontsize=9.5, fontweight='bold', ha='center')
ax2.set_xlabel(r'Hubbard $U_{\mathrm{eff}}$ on Cr-$3d$ (eV)')
ax2.set_ylabel(r'$\Delta a = a_{\mathrm{post}} - a_{\mathrm{pre}}$ (Å)')
ax2.set_title(r'(b) In-Plane Vector Shift $\Delta a(U)$', fontweight='bold')
ax2.grid(True, linestyle='--', alpha=0.45)
ax2.set_ylim(-0.07, 0.07)

# Panel 3: OUTCAR Relaxation Trajectories a(step)
cmap = plt.get_cmap('plasma')
for idx, u in enumerate(u_vals):
    traj = all_trajectories[u]
    steps_x = list(range(1, len(traj) + 1))
    a_steps = [s["a"] for s in traj]
    color = cmap(idx / 6.0)
    ax3.plot(steps_x, a_steps, marker='o', markersize=5, linewidth=1.8, color=color, label=f'U = {u} eV ({len(traj)} steps)')

ax3.set_xlabel('Ionic Relaxation Step')
ax3.set_ylabel(r'In-Plane Lattice Vector $a$ (Å)')
ax3.set_title(r'(c) Step-by-Step Trajectory $a(\mathrm{step})$ from OUTCAR', fontweight='bold')
ax3.grid(True, linestyle='--', alpha=0.45)
ax3.legend(loc='center right', framealpha=0.9, fontsize=8)

# Panel 4: In-Plane Stress Tensor sigma_xx (Pre vs Post)
width = 0.35
x_indices = np.array(u_vals)
rects1 = ax4.bar(x_indices - width/2, s_xx_pre, width, label=r'Initial Stress $\sigma_{xx}$ (Pre)', color='#e377c2', alpha=0.8, edgecolor='black')
rects2 = ax4.bar(x_indices + width/2, s_xx_post, width, label=r'Final Stress $\sigma_{xx}$ (Post)', color='#2ca02c', alpha=0.85, edgecolor='black')

ax4.axhline(0.0, color='black', linewidth=0.8)
for x, y in zip(x_indices + width/2, s_xx_post):
    ax4.annotate(f"{y:.2f}", (x, y), textcoords="offset points", xytext=(0, 4 if y >= 0 else -10),
                 ha='center', fontsize=8, fontweight='bold', color='#2ca02c')

ax4.set_xlabel(r'Hubbard $U_{\mathrm{eff}}$ on Cr-$3d$ (eV)')
ax4.set_ylabel(r'In-Plane Stress Component $\sigma_{xx} = \sigma_{yy}$ (kB)')
ax4.set_title(r'(d) In-Plane Stress Minimization ($\sigma_{xx}$)', fontweight='bold')
ax4.grid(True, linestyle='--', alpha=0.45)
ax4.legend(loc='upper left', framealpha=0.92, fontsize=8.5)
ax4.set_ylim(-7.0, 8.0)

# Panel 5: Monolayer Thickness dz and Bond Length
ax5.plot(u_vals, dz_post, marker='s', color='#ff7f0e', linewidth=2.0, label=r'Post $d_z(\mathrm{Cl-Cl})$')
ax5.axhline(dz_pre[0], color='#ff7f0e', linestyle='--', label=r'Pre $d_z(\mathrm{Cl-Cl})$ (2.700 Å)', alpha=0.6)
ax5.plot(u_vals, bond_post, marker='^', color='#17becf', linewidth=2.0, label=r'Post $d(\mathrm{Cr-Cl})$')
ax5.axhline(bond_pre[0], color='#17becf', linestyle='--', label=r'Pre $d(\mathrm{Cr-Cl})$ (2.375 Å)', alpha=0.6)

# Add literature points
ax5.plot(0, 2.352, marker='*', markersize=10, color='red', label='Luo 2020: 2.352 Å (U=0)')
ax5.plot(0, 2.357, marker='x', markersize=8, color='blue', label='Webster 2018: 2.357 Å (U=0)')

for x, y in zip(u_vals, dz_post):
    ax5.annotate(f"{y:.3f}", (x, y), textcoords="offset points", xytext=(0, 6),
                 ha='center', fontsize=8, color='#ff7f0e')

ax5.set_xlabel(r'Hubbard $U_{\mathrm{eff}}$ on Cr-$3d$ (eV)')
ax5.set_ylabel('Internal Distances (Å)')
ax5.set_title(r'(e) Vertical Thickness $d_z$ & $\mathrm{Cr-Cl}$ Bond Length', fontweight='bold')
ax5.grid(True, linestyle='--', alpha=0.45)
ax5.legend(loc='center left', framealpha=0.92, fontsize=8)
ax5.set_ylim(2.32, 2.76)

# Panel 6: Crystallographic Symmetry Explanation
ax6.axis('off')
explanation_lines = [
    r"$\mathbf{Crystallographic\ Proof:\ Why}\ a \equiv b\ \mathbf{in\ Monolayer}\ \mathrm{CrCl}_3$",
    "",
    r"$\bullet\ \mathbf{Space\ Group:}\ P\bar{3}1m\ \mathrm{(No.\ 162)},\ \mathrm{Point\ Group}\ D_{3d}\ (\bar{3}m)$",
    r"$\bullet\ \mathbf{C_3\ Rotational\ Symmetry:}\ \mathrm{3-fold\ rotation\ axis\ }\parallel z$",
    r"   $\rightarrow\ \mathbf{a}_1\ \mathrm{and}\ \mathbf{a}_2\ \mathrm{are\ symmetry-equivalent:}\ |\mathbf{a}_1| \equiv |\mathbf{a}_2| \Leftrightarrow a \equiv b$",
    r"   $\rightarrow\ \mathrm{Inter-axis\ angle\ is\ strictly\ }\gamma = 120.000^\circ$",
    r"   $\rightarrow\ \mathrm{Stress\ tensor\ is\ strictly\ isotropic:\ }\sigma_{xx} \equiv \sigma_{yy},\ \sigma_{xy} \equiv 0$",
    "",
    r"$\mathbf{Coordinate\ System\ Representation:}$",
    r"$\mathbf{1.\ Hexagonal\ Primitive\ Cell\ (Our\ Work,\ Webster,\ Luo):}$",
    r"   $\mathbf{a}_1 = (a, 0, 0),\ \mathbf{a}_2 = (-a/2, a\sqrt{3}/2, 0)$",
    r"   $\rightarrow\ a = b \approx 6.056\ \mathrm{\AA},\ \gamma = 120^\circ\ (2\ \mathrm{Cr},\ 6\ \mathrm{Cl}\ \mathrm{atoms})$",
    "",
    r"$\mathbf{2.\ Rectangular\ Supercell\ (Alternative\ Representation):}$",
    r"   $\mathbf{A} = \mathbf{a}_1 = (a, 0, 0) \rightarrow A = a \approx 6.056\ \mathrm{\AA}$",
    r"   $\mathbf{B} = \mathbf{a}_1 + 2\mathbf{a}_2 = (0, a\sqrt{3}, 0) \rightarrow B = a\sqrt{3} \approx 10.489\ \mathrm{\AA}$",
    r"   $\rightarrow\ A \neq B\ (\mathrm{rectangular\ axes\ with\ }\gamma = 90^\circ,\ 4\ \mathrm{Cr},\ 12\ \mathrm{Cl})$",
    "",
    r"$\mathbf{Conclusion:}\ a = b\ \mathrm{in\ our\ cell\ is\ NOT\ an\ error;}$",
    r"$\mathrm{it\ is\ a\ fundamental\ physical\ law\ of\ the\ honeycomb\ lattice!}$"
]
ax6.text(0.02, 0.98, "\n".join(explanation_lines), transform=ax6.transAxes, fontsize=8.8,
         verticalalignment='top', bbox=dict(boxstyle='round,pad=0.7', facecolor='#f8f9fa', edgecolor='#ced4da', linewidth=1.2))

plt.suptitle(r'Monolayer $\mathrm{CrCl}_3$ ($1\times 1$ Primitive Cell): Pre- vs. Post-Relaxation Structural Evolution',
             fontsize=14.5, fontweight='bold', y=0.99)
plt.tight_layout(rect=[0, 0, 1, 0.97])

out_png = os.path.join(BASE_DIR, "crcl3_poscar_vs_contcar_analysis.png")
out_pdf = os.path.join(BASE_DIR, "crcl3_poscar_vs_contcar_analysis.pdf")
fig.savefig(out_png, dpi=300)
fig.savefig(out_pdf)
plt.close(fig)

print(f"Generated comparison figure: {out_png}")
print(f"Generated PDF: {out_pdf}")

# Export comprehensive comparison CSV
csv_out = os.path.join(BASE_DIR, "crcl3_poscar_vs_contcar_metadata.csv")
with open(csv_out, "w") as f:
    f.write("U_eV,N_steps,a_pre_A,b_pre_A,c_pre_A,gamma_pre_deg,a_post_A,b_post_A,c_post_A,gamma_post_deg,delta_a_A,s_xx_pre_kB,s_xx_post_kB,dz_pre_A,dz_post_A,bond_pre_A,bond_post_A\n")
    for u in u_vals:
        p = data_pre[u]
        c = data_post[u]
        da = delta_a[u]
        s_pre = s_xx_pre[u]
        s_post = s_xx_post[u]
        n_st = len(all_trajectories[u])
        f.write(f"{u},{n_st},{p['a']:.6f},{p['b']:.6f},{p['c']:.6f},{p['gamma']:.4f},{c['a']:.6f},{c['b']:.6f},{c['c']:.6f},{c['gamma']:.4f},{da:+.6f},{s_pre:.3f},{s_post:.3f},{p['d_z']:.4f},{c['d_z']:.4f},{p['bond']:.4f},{c['bond']:.4f}\n")

print(f"Exported metadata CSV: {csv_out}")
