import os
import re
import numpy as np
import matplotlib.pyplot as plt

# Setup paths
base_dir = "/Users/apple/Research/abc/paper-adaptation/crcl3-newcals"
post_dir = os.path.join(base_dir, "postprosseing")
os.makedirs(post_dir, exist_ok=True)

# ----------------------------------------------------
# Matplotlib Premium Design Settings (Times New Roman)
# ----------------------------------------------------
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['mathtext.fontset'] = 'stix'

systems = [
    "adsorbed/co", "adsorbed/fe", "adsorbed/ni",
    "embedded/co", "embedded/fe", "embedded/ni"
]

results = {}

# ----------------------------------------------------
# 1. Parse LOBSTER files dynamically
# ----------------------------------------------------
for name in systems:
    d = os.path.join(base_dir, name)
    cohp_file = os.path.join(d, "COHPCAR.lobster")
    
    if not os.path.exists(cohp_file):
        print(f"Warning: {cohp_file} not found")
        continue
        
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
            
            # TM is always index 33 in these structures (python index 32)
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
                    'length': length,
                    'icohp': icohp_f
                })
                
    if len(icohps) > 0:
        avg_icohp = np.mean(icohps)
        cumulative_icohp = np.sum(icohps)
    else:
        avg_icohp = 0.0
        cumulative_icohp = 0.0
        
    results[name] = {
        'avg_icohp': avg_icohp,
        'cumulative_icohp': cumulative_icohp,
        'bonds': bond_details
    }

# ----------------------------------------------------
# 2. Plot Overview (Average vs Cumulative)
# ----------------------------------------------------
tms = ['Co', 'Fe', 'Ni']
avg_ads = [results['adsorbed/co']['avg_icohp'], results['adsorbed/fe']['avg_icohp'], results['adsorbed/ni']['avg_icohp']]
avg_emb = [results['embedded/co']['avg_icohp'], results['embedded/fe']['avg_icohp'], results['embedded/ni']['avg_icohp']]

cum_ads = [results['adsorbed/co']['cumulative_icohp'], results['adsorbed/fe']['cumulative_icohp'], results['adsorbed/ni']['cumulative_icohp']]
cum_emb = [results['embedded/co']['cumulative_icohp'], results['embedded/fe']['cumulative_icohp'], results['embedded/ni']['cumulative_icohp']]

x = np.arange(len(tms))
width = 0.35

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5.5))

colors = {
    'adsorbed': '#2c3e50',  # Slate / Dark Blue-Grey
    'embedded': '#e74c3c'   # Crimson Red
}

# Plot 1: Average ICOHP
rects1_ads = ax1.bar(x - width/2, avg_ads, width, label='Adsorbed', color=colors['adsorbed'], edgecolor='black', zorder=3)
rects1_emb = ax1.bar(x + width/2, avg_emb, width, label='Embedded', color=colors['embedded'], edgecolor='black', zorder=3)

ax1.axhline(0, color='black', linewidth=1.0, zorder=2)
ax1.set_ylabel(r'Average $\mathrm{TM-Cl}$ ICOHP [eV/bond]', fontsize=12)
ax1.set_title('Average Bond Strength (per TM-Cl Bond)', fontsize=13, fontweight='bold', pad=10)
ax1.set_xticks(x)
ax1.set_xticklabels(tms, fontsize=11)
ax1.set_ylim(-2.7, 0.2)
ax1.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
ax1.legend(loc='lower right', frameon=True, edgecolor='black', fancybox=False)

def autolabel(rects, ax):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, -15),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9.5, fontweight='bold')

autolabel(rects1_ads, ax1)
autolabel(rects1_emb, ax1)

# Plot 2: Cumulative ICOHP
rects2_ads = ax2.bar(x - width/2, cum_ads, width, label='Adsorbed', color=colors['adsorbed'], edgecolor='black', zorder=3)
rects2_emb = ax2.bar(x + width/2, cum_emb, width, label='Embedded', color=colors['embedded'], edgecolor='black', zorder=3)

ax2.axhline(0, color='black', linewidth=1.0, zorder=2)
ax2.set_ylabel(r'Cumulative $\mathrm{TM-Cl}$ ICOHP [eV]', fontsize=12)
ax2.set_title('Total Bonding Interaction Energy', fontsize=13, fontweight='bold', pad=10)
ax2.set_xticks(x)
ax2.set_xticklabels(tms, fontsize=11)
ax2.set_ylim(-13.0, 0.5)
ax2.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
ax2.legend(loc='lower right', frameon=True, edgecolor='black', fancybox=False)

autolabel(rects2_ads, ax2)
autolabel(rects2_emb, ax2)

plt.suptitle(r'Comparison of LOBSTER ICOHP Bonding Energies at $E_{\mathrm{F}}$', fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()

overview_path = os.path.join(post_dir, "icohp_bar_chart.png")
plt.savefig(overview_path, dpi=300)
plt.close()
print(f"ICOHP overview bar chart saved to {overview_path}")


# ----------------------------------------------------
# 3. Plot Individual Bonds (3-Panel Horizontal Bar Chart)
# ----------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(15, 6.5), sharex=True)
tms_names = ['Co', 'Fe', 'Ni']

for idx, tm in enumerate(tms_names):
    ax = axes[idx]
    
    # Collect bonds for this metal
    ads_bonds = results[f'adsorbed/{tm.lower()}']['bonds']
    emb_bonds = results[f'embedded/{tm.lower()}']['bonds']
    
    all_bonds = []
    for b in ads_bonds:
        all_bonds.append({
            'label': f"{b['pair']} (Ads)",
            'icohp': b['icohp'],
            'length': b['length'],
            'config': 'adsorbed'
        })
    for b in emb_bonds:
        all_bonds.append({
            'label': f"{b['pair']} (Emb)",
            'icohp': b['icohp'],
            'length': b['length'],
            'config': 'embedded'
        })
        
    # Sort bonds by bond length (shortest first)
    all_bonds = sorted(all_bonds, key=lambda val: val['length'])
    
    labels = [b['label'] for b in all_bonds]
    icohps = [b['icohp'] for b in all_bonds]
    colors_list = [colors[b['config']] for b in all_bonds]
    
    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, icohps, align='center', color=colors_list, edgecolor='black', zorder=3)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10.5)
    ax.invert_yaxis()  # Keep shortest bonds at the top
    ax.set_xlabel('ICOHP [eV]', fontsize=12)
    ax.set_title(f'{tm} System Bonds', fontsize=13, fontweight='bold')
    ax.grid(axis='x', linestyle='--', alpha=0.5, zorder=0)
    ax.axvline(0, color='black', linewidth=1.0, zorder=2)
    
    # X-axis limits to accommodate labels inside/around
    ax.set_xlim(-2.9, 0.05)
    
    # Add value labels next to the bars
    for bar in bars:
        width = bar.get_width()
        ax.annotate(f'{width:.3f} eV',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(-5, 0),
                    textcoords="offset points",
                    ha='right', va='center', fontsize=9, fontweight='bold')

plt.suptitle(r'Individual $\mathrm{TM-Cl}$ Bond ICOHP values at $E_{\mathrm{F}}$ (Sorted by Bond Length)', fontsize=15, fontweight='bold', y=0.98)
plt.tight_layout()

bonds_path = os.path.join(post_dir, "icohp_individual_bonds.png")
plt.savefig(bonds_path, dpi=300)
plt.close()
print(f"Individual bonds ICOHP bar chart saved to {bonds_path}")
