import os
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ----------------------------------------------------
# Matplotlib Premium Design Settings (Times New Roman / STIX)
# ----------------------------------------------------
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.0

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
post_dir = os.path.join(base_dir, "postprosseing")
acs_resub_fig_dir = os.path.abspath(os.path.join(base_dir, "..", "ACS_version", "ACS_resubmission", "figure"))
acs_orig_fig_dir = os.path.abspath(os.path.join(base_dir, "..", "ACS_version", "figure"))

systems = [
    "cohp_lobster_Uall/adsorbed/Co", "cohp_lobster_Uall/adsorbed/Fe", "cohp_lobster_Uall/adsorbed/Ni",
    "cohp_lobster_Uall/embedded/Co", "cohp_lobster_Uall/embedded/Fe", "cohp_lobster_Uall/embedded/Ni"
]

results = {}

for name in systems:
    d = os.path.join(base_dir, name)
    cohp_file = os.path.join(d, "COHPCAR.lobster")
    
    if not os.path.exists(cohp_file):
        raise FileNotFoundError(f"Missing {cohp_file}")
        
    with open(cohp_file, 'r') as f:
        cohp_lines = f.readlines()
        
    header_parts = cohp_lines[1].split()
    num_bonds = int(header_parts[0])
    is_spin_polarized = int(header_parts[1]) == 2
    num_points = int(header_parts[2])
    
    bonds = []
    data_start_line = 0
    for idx in range(2, len(cohp_lines)):
        parts = cohp_lines[idx].split()
        if len(parts) > 0:
            try:
                float(parts[0])
                data_start_line = idx
                break
            except ValueError:
                pass
        bonds.append(cohp_lines[idx].strip())
        
    data = []
    for idx in range(data_start_line, data_start_line + num_points):
        parts = [float(x) for x in cohp_lines[idx].split()]
        data.append(parts)
    data = np.array(data)
    
    energies = data[:, 0]
    fermi_idx = np.argmin(np.abs(energies))
    
    icohps = []
    bond_details = []
    
    for i in range(1, len(bonds)):
        bond_desc = bonds[i]
        match = re.search(r"No\.(\d+):(.*)->(.*)\((.*)\)", bond_desc)
        if match:
            bond_num = int(match.group(1))
            atom1 = match.group(2).strip()
            atom2 = match.group(3).strip()
            length = float(match.group(4))
            
            a1_num = re.search(r"\d+", atom1).group()
            a2_num = re.search(r"\d+", atom2).group()
            
            if a1_num == "33" or a2_num == "33":
                if is_spin_polarized:
                    col_icohp_s1 = 4 * bond_num + 2
                    col_icohp_s2 = 4 * bond_num + 4
                    icohp_f = data[fermi_idx, col_icohp_s1] + data[fermi_idx, col_icohp_s2]
                else:
                    col_icohp = 2 * bond_num + 2
                    icohp_f = data[fermi_idx, col_icohp]
                    
                icohps.append(icohp_f)
                bond_name = f"{atom1}-{atom2}"
                bond_details.append({
                    'pair': bond_name,
                    'atom1': atom1,
                    'atom2': atom2,
                    'length': length,
                    'icohp': icohp_f
                })
                
    results[name] = {
        'avg_icohp': np.mean(icohps) if len(icohps) > 0 else 0.0,
        'cumulative_icohp': np.sum(icohps) if len(icohps) > 0 else 0.0,
        'bonds': bond_details
    }

colors = {
    'adsorbed': '#2c3e50',  # Slate / Dark Navy
    'embedded': '#e74c3c'   # Crimson Red
}

def format_bond_label(atom1, atom2, config):
    def fmt(at):
        m = re.match(r"([A-Za-z]+)(\d+)", at)
        if m:
            return f"\\mathrm{{{m.group(1)}}}_{{{m.group(2)}}}"
        return f"\\mathrm{{{at}}}"
    cfg_tag = "Ads" if config == 'adsorbed' else "Emb"
    return f"${fmt(atom1)}\\text{{--}}{fmt(atom2)}\\ (\\text{{{cfg_tag}}})$"

# ----------------------------------------------------
# Create 5-panel Composite Figure (Fig S4)
# ----------------------------------------------------
fig = plt.figure(figsize=(18.0, 11.0))
gs = gridspec.GridSpec(2, 6, figure=fig, height_ratios=[1.2, 1.0], hspace=0.38, wspace=1.40)

# Row 1: 3 Panels for Individual Bonds (a, b, c)
ax_a = fig.add_subplot(gs[0, 0:2])
ax_b = fig.add_subplot(gs[0, 2:4])
ax_c = fig.add_subplot(gs[0, 4:6])

tms = ['Co', 'Fe', 'Ni']
row1_axes = [(ax_a, 'Co', '(a)'), (ax_b, 'Fe', '(b)'), (ax_c, 'Ni', '(c)')]

for ax, tm, tag in row1_axes:
    ads_bonds = results[f'cohp_lobster_Uall/adsorbed/{tm}']['bonds']
    emb_bonds = results[f'cohp_lobster_Uall/embedded/{tm}']['bonds']
    
    all_bonds = []
    for b in ads_bonds:
        all_bonds.append({
            'label': format_bond_label(b['atom1'], b['atom2'], 'adsorbed'),
            'icohp': b['icohp'],
            'length': b['length'],
            'config': 'adsorbed'
        })
    for b in emb_bonds:
        all_bonds.append({
            'label': format_bond_label(b['atom1'], b['atom2'], 'embedded'),
            'icohp': b['icohp'],
            'length': b['length'],
            'config': 'embedded'
        })
        
    all_bonds = sorted(all_bonds, key=lambda val: val['length'])
    
    labels = [b['label'] for b in all_bonds]
    icohps = [b['icohp'] for b in all_bonds]
    colors_list = [colors[b['config']] for b in all_bonds]
    
    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, icohps, align='center', color=colors_list, edgecolor='black', linewidth=0.8, zorder=3)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10.5)
    ax.tick_params(axis='both', labelsize=10.5)
    ax.invert_yaxis()
    ax.set_xlabel(r'$\mathrm{ICOHP}\ (\mathrm{eV})$', fontsize=12, fontweight='bold')
    ax.set_title(f'{tm} System Bonds', fontsize=13, fontweight='bold', pad=9)
    ax.grid(axis='x', linestyle='--', alpha=0.5, zorder=0)
    ax.axvline(0, color='black', linewidth=1.0, zorder=2)
    ax.set_xlim(-2.95, 0.05)
    
    for bar in bars:
        width = bar.get_width()
        val_str = f'{width:.2f} eV'
        if width <= -1.75:
            ax.annotate(val_str,
                        xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(5, 0),
                        textcoords="offset points",
                        ha='left', va='center', fontsize=9.5, fontweight='bold', color='white')
        else:
            ax.annotate(val_str,
                        xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(-5, 0),
                        textcoords="offset points",
                        ha='right', va='center', fontsize=9.5, fontweight='bold', color='black')
                        
    # Panel tag card below the panel
    ax.text(0.5, -0.19, tag, transform=ax.transAxes, fontsize=16, fontweight='bold', ha='center', va='top')

# Row 2: 2 Panels for Summary (d, e), centered in 6-grid (columns 1..3 and 3..5)
ax_d = fig.add_subplot(gs[1, 1:3])
ax_e = fig.add_subplot(gs[1, 3:5])

avg_ads = [results[f'cohp_lobster_Uall/adsorbed/{tm}']['avg_icohp'] for tm in tms]
avg_emb = [results[f'cohp_lobster_Uall/embedded/{tm}']['avg_icohp'] for tm in tms]
cum_ads = [results[f'cohp_lobster_Uall/adsorbed/{tm}']['cumulative_icohp'] for tm in tms]
cum_emb = [results[f'cohp_lobster_Uall/embedded/{tm}']['cumulative_icohp'] for tm in tms]

x = np.arange(len(tms))
width = 0.35

# Panel d: Average ICOHP
rects_d_ads = ax_d.bar(x - width/2, avg_ads, width, label='Adsorbed', color=colors['adsorbed'], edgecolor='black', linewidth=0.8, zorder=3)
rects_d_emb = ax_d.bar(x + width/2, avg_emb, width, label='Embedded', color=colors['embedded'], edgecolor='black', linewidth=0.8, zorder=3)
ax_d.axhline(0, color='black', linewidth=1.0, zorder=2)
ax_d.set_ylabel(r'Average $\mathrm{TM}\text{--}\mathrm{Cl}$ ICOHP $(\mathrm{eV/bond})$', fontsize=12, fontweight='bold')
ax_d.set_title('Average Bond Strength (per TM--Cl Bond)', fontsize=13, fontweight='bold', pad=9)
ax_d.set_xticks(x)
ax_d.set_xticklabels(tms, fontsize=12)
ax_d.set_ylim(-2.7, 0.2)
ax_d.tick_params(axis='both', labelsize=11)
ax_d.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
ax_d.legend(loc='lower right', frameon=True, edgecolor='#cccccc', facecolor='white', framealpha=0.92, fontsize=10.5)

def autolabel_bar(rects, ax, offset=-14):
    for rect in rects:
        h = rect.get_height()
        ax.annotate(f'{h:.2f}',
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, offset),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

autolabel_bar(rects_d_ads, ax_d)
autolabel_bar(rects_d_emb, ax_d)
ax_d.text(0.5, -0.20, '(d)', transform=ax_d.transAxes, fontsize=16, fontweight='bold', ha='center', va='top')

# Panel e: Cumulative ICOHP
rects_e_ads = ax_e.bar(x - width/2, cum_ads, width, label='Adsorbed', color=colors['adsorbed'], edgecolor='black', linewidth=0.8, zorder=3)
rects_e_emb = ax_e.bar(x + width/2, cum_emb, width, label='Embedded', color=colors['embedded'], edgecolor='black', linewidth=0.8, zorder=3)
ax_e.axhline(0, color='black', linewidth=1.0, zorder=2)
ax_e.set_ylabel(r'Cumulative $\mathrm{TM}\text{--}\mathrm{Cl}$ ICOHP $(\mathrm{eV})$', fontsize=12, fontweight='bold')
ax_e.set_title('Total Bonding Interaction Energy', fontsize=13, fontweight='bold', pad=9)
ax_e.set_xticks(x)
ax_e.set_xticklabels(tms, fontsize=12)
ax_e.set_ylim(-14.0, 0.5)
ax_e.tick_params(axis='both', labelsize=11)
ax_e.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
ax_e.legend(loc='lower right', frameon=True, edgecolor='#cccccc', facecolor='white', framealpha=0.92, fontsize=10.5)

autolabel_bar(rects_e_ads, ax_e)
autolabel_bar(rects_e_emb, ax_e)
ax_e.text(0.5, -0.20, '(e)', transform=ax_e.transAxes, fontsize=16, fontweight='bold', ha='center', va='top')

# Save figures
out_png = os.path.join(post_dir, "new_sup_fig_4.png")
out_pdf = os.path.join(post_dir, "new_sup_fig_4.pdf")
plt.savefig(out_png, dpi=300, bbox_inches='tight')
plt.savefig(out_pdf, bbox_inches='tight')

# Sync to ACS resubmission
acs_resub_png = os.path.join(acs_resub_fig_dir, "new_sup_fig_4.png")
acs_resub_pdf = os.path.join(acs_resub_fig_dir, "new_sup_fig_4.pdf")
plt.savefig(acs_resub_png, dpi=300, bbox_inches='tight')
plt.savefig(acs_resub_pdf, bbox_inches='tight')

if os.path.exists(acs_orig_fig_dir):
    plt.savefig(os.path.join(acs_orig_fig_dir, "new_sup_fig_4.png"), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(acs_orig_fig_dir, "new_sup_fig_4.pdf"), bbox_inches='tight')

plt.close()

print("Successfully regenerated pristine unified Figure S4 (+U_all ICOHP):")
print(f"  Postprocessing: {out_png}")
print(f"  ACS Resubmission: {acs_resub_png}")
