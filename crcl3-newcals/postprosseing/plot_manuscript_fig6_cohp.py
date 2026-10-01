import os
import re
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------------------------------
# Matplotlib Premium Design Settings (Times New Roman / STIX)
# ----------------------------------------------------
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.0

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
post_dir = os.path.join(base_dir, "postprosseing")
acs_fig_dir = os.path.abspath(os.path.join(base_dir, "..", "ACS_version", "ACS_resubmission", "figure"))

systems = [
    "adsorbed/co", "adsorbed/fe", "adsorbed/ni",
    "embedded/co", "embedded/fe", "embedded/ni"
]

results = {}

def format_bond_latex(bond_name):
    parts = bond_name.split('-')
    formatted_parts = []
    for p in parts:
        match = re.match(r"([A-Za-z]+)(\d+)", p)
        if match:
            el, idx = match.group(1), match.group(2)
            formatted_parts.append(f"\\mathrm{{{el}}}_{{{idx}}}")
        else:
            formatted_parts.append(f"\\mathrm{{{p}}}")
    return r"$" + "-".join(formatted_parts) + r"$"

# 1. Parse LOBSTER COHPCAR files
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
    
    cohp_curves = {}
    icohps = []
    
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
                    col_cohp_s1 = 4 * bond_num + 1
                    col_icohp_s1 = 4 * bond_num + 2
                    col_cohp_s2 = 4 * bond_num + 3
                    col_icohp_s2 = 4 * bond_num + 4
                    
                    cohp_tot = data[:, col_cohp_s1] + data[:, col_cohp_s2]
                    icohp_tot = data[:, col_icohp_s1] + data[:, col_icohp_s2]
                else:
                    col_cohp = 2 * bond_num + 1
                    col_icohp = 2 * bond_num + 2
                    cohp_tot = data[:, col_cohp]
                    icohp_tot = data[:, col_icohp]
                    
                bond_name = f"{atom1}-{atom2}"
                cohp_curves[bond_name] = {
                    'cohp': cohp_tot,
                    'icohp': icohp_tot,
                    'length': length
                }
                icohps.append(icohp_tot[fermi_idx])
                
    results[name] = {
        'energies': energies,
        'cohp_curves': cohp_curves,
        'avg_icohp': np.mean(icohps),
        'cum_icohp': np.sum(icohps)
    }

# 2. Render High-Resolution 2x3 Figure 6
fig, axes = plt.subplots(2, 3, figsize=(14, 9.8), sharex=True, sharey=True)

panels_info = [
    # Row 1: Adsorbed
    (0, 0, "adsorbed/co", "Co System (adsorbed)", "(a)"),
    (0, 1, "adsorbed/fe", "Fe System (adsorbed)", "(b)"),
    (0, 2, "adsorbed/ni", "Ni System (adsorbed)", "(c)"),
    # Row 2: Embedded
    (1, 0, "embedded/co", "Co System (embedded)", "(d)"),
    (1, 1, "embedded/fe", "Fe System (embedded)", "(e)"),
    (1, 2, "embedded/ni", "Ni System (embedded)", "(f)"),
]

for row, col, sys_key, title_text, label_tag in panels_info:
    ax = axes[row, col]
    sys_data = results[sys_key]
    energies = sys_data['energies']
    curves = sys_data['cohp_curves']
    
    # Preserve natural bond order from COHPCAR (matches original manuscript color mapping)
    sorted_bonds = list(curves.keys())
    
    for bond_name in sorted_bonds:
        curve = curves[bond_name]
        cohp = curve['cohp']
        line, = ax.plot(-cohp, energies, label=format_bond_latex(bond_name), alpha=0.90, linewidth=1.75)
        # Shade bonding region (E <= 0)
        ax.fill_betweenx(energies, 0, -cohp, where=(energies <= 0), alpha=0.14, color=line.get_color())
        
    # Reference lines
    ax.axvline(0, color='#666666', linestyle='--', linewidth=0.9, zorder=1)
    ax.axhline(0, color='black', linestyle='-', linewidth=1.1, zorder=2) # Fermi Level
    
    # Grid and limits
    ax.set_xlim(-1.2, 1.5)
    ax.set_ylim(-7.0, 5.0)
    ax.grid(True, linestyle=':', alpha=0.55, color='#aaaaaa')
    ax.tick_params(axis='both', which='major', labelsize=11.5, direction='in', top=True, right=True)
    
    # Title
    ax.set_title(title_text, fontsize=12.5, fontweight='bold', pad=8)
    
    # Zero-Collision Panel Tag Card
    ax.text(
        0.04, 0.05, label_tag,
        transform=ax.transAxes,
        fontsize=16,
        fontweight='bold',
        va='bottom',
        ha='left',
        bbox=dict(boxstyle='square,pad=0.2', facecolor='white', alpha=0.92, edgecolor='#cccccc', linewidth=0.8)
    )
    
    # Clean Legend with Semi-Transparent Framing
    ax.legend(
        loc='upper right',
        frameon=True,
        facecolor='white',
        edgecolor='#cccccc',
        framealpha=0.92,
        fontsize=10.5,
        borderpad=0.5,
        handlelength=1.4,
        labelspacing=0.3
    )

# Axis labels
for col in range(3):
    axes[1, col].set_xlabel(r'$-\mathrm{COHP}$', fontsize=12.5, fontweight='bold')
    
for row in range(2):
    axes[row, 0].set_ylabel(r'$E - E_{\mathrm{F}}\ (\mathrm{eV})$', fontsize=13, fontweight='bold')

plt.tight_layout()

# Save paths
out_png = os.path.join(post_dir, "Fig6_cohp_publication_multipanel.png")
out_pdf = os.path.join(post_dir, "Fig6_cohp_publication_multipanel.pdf")
plt.savefig(out_png, dpi=300)
plt.savefig(out_pdf)

# Also sync to ACS resubmission figure directory
acs_fig6_png = os.path.join(acs_fig_dir, "Fig6.png")
acs_fig6_pdf = os.path.join(acs_fig_dir, "Fig6.pdf")
plt.savefig(acs_fig6_png, dpi=300)
plt.savefig(acs_fig6_pdf)

acs_orig_dir = os.path.abspath(os.path.join(base_dir, "..", "ACS_version", "figure"))
if os.path.exists(acs_orig_dir):
    plt.savefig(os.path.join(acs_orig_dir, "Fig6.png"), dpi=300)
    plt.savefig(os.path.join(acs_orig_dir, "Fig6.pdf"))

plt.close()

print(f"Generated pristine publication Fig6:")
print(f"  Postprocessing PNG: {out_png}")
print(f"  Postprocessing PDF: {out_pdf}")
print(f"  ACS Resubmission PNG: {acs_fig6_png}")
print(f"  ACS Resubmission PDF: {acs_fig6_pdf}")
