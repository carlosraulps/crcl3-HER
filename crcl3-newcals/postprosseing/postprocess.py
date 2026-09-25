# cspell:ignore fontsize
import os
import re
import numpy as np
import matplotlib.pyplot as plt


# Directories
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
post_dir = os.path.join(base_dir, "postprosseing")
os.makedirs(post_dir, exist_ok=True)

systems = [
    "adsorbed/co", "adsorbed/fe", "adsorbed/ni",
    "embedded/co", "embedded/fe", "embedded/ni"
]

results = {}

for name in systems:
    d = os.path.join(base_dir, name)
    outcar = os.path.join(d, "OUTCAR")
    cohp_file = os.path.join(d, "COHPCAR.lobster")
    
    if not os.path.exists(outcar):
        print(f"Warning: {outcar} not found")
        continue
        
    toten = None
    fermi = None
    mag = None
    tm_mag = None
    
    # Parse OUTCAR
    with open(outcar, 'r') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if "free energy    TOTEN" in line:
            toten = float(line.split("=")[1].split()[0].strip())
        elif "E-fermi" in line:
            parts = line.split()
            fermi = float(parts[2])
        elif "number of electron " in line:
            if "magnetization" in line:
                mag = float(line.split("magnetization")[-1].strip())
        elif "magnetization (x)" in line:
            # Find the magnetization on the last atom (ion 33)
            for j in range(i+1, min(i+100, len(lines))):
                if lines[j].strip().startswith("33 "):
                    tm_mag = float(lines[j].split()[-1])
                    break
                    
    # Parse COHP
    icohps = []
    bond_details = []
    energies = None
    cohp_data = {}
    icohp_data = {}
    
    if os.path.exists(cohp_file):
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
                        
                        cohp_s1 = data[:, col_cohp_s1]
                        cohp_s2 = data[:, col_cohp_s2]
                        icohp_s1 = data[:, col_icohp_s1]
                        icohp_s2 = data[:, col_icohp_s2]
                        
                        cohp_f = data[fermi_idx, col_cohp_s1] + data[fermi_idx, col_cohp_s2]
                        icohp_f = data[fermi_idx, col_icohp_s1] + data[fermi_idx, col_icohp_s2]
                        
                        cohp_curve = {'tot': cohp_s1 + cohp_s2}
                        icohp_curve = {'tot': icohp_s1 + icohp_s2}
                    else:
                        col_cohp = 2 * bond_num + 1
                        col_icohp = 2 * bond_num + 2
                        cohp_f = data[fermi_idx, col_cohp]
                        icohp_f = data[fermi_idx, col_icohp]
                        
                        cohp_curve = {'tot': data[:, col_cohp]}
                        icohp_curve = {'tot': data[:, col_icohp]}
                        
                    icohps.append(icohp_f)
                    bond_name = f"{atom1}-{atom2}"
                    cohp_data[bond_name] = cohp_curve
                    icohp_data[bond_name] = icohp_curve
                    bond_details.append({
                        'pair': bond_name,
                        'length': length,
                        'cohp_ef': cohp_f,
                        'icohp': icohp_f
                    })
        
        if len(icohps) > 0:
            avg_icohp = np.mean(icohps)
            cumulative_icohp = np.sum(icohps)
        else:
            avg_icohp = 0.0
            cumulative_icohp = 0.0
    else:
        cumulative_icohp = 0.0
        avg_icohp = 0.0
        
    results[name] = {
        'toten': toten,
        'fermi': fermi,
        'mag': mag,
        'tm_mag': tm_mag,
        'avg_icohp': avg_icohp,
        'cumulative_icohp': cumulative_icohp,
        'bonds': bond_details,
        'energies': energies,
        'cohp_curves': cohp_data,
        'icohp_curves': icohp_data
    }

# ----------------------------------------------------
# 1. Generate Markdown Summary Table
# ----------------------------------------------------
summary_path = os.path.join(post_dir, "results_summary.md")
with open(summary_path, 'w') as f:
    f.write("# VASP + LOBSTER Postprocessing Summary\n\n")
    f.write("This document summarizes the energetics, magnetic properties, and LOBSTER COHP bonding analysis for the CrCl3 monolayer functionalized with transition metals (Co, Fe, Ni) in both adsorbed and embedded configurations.\n\n")
    
    f.write("## 1. Energetics and Magnetic Moments\n\n")
    f.write("| System | TOTEN (eV) | Fermi Level (eV) | Total Magnetization ($\\mu_B$) | TM Local Mag. Moment ($\\mu_B$) | Avg. TM-Cl ICOHP (eV) | Cumulative TM-Cl ICOHP (eV) |\n")
    f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
    for name in systems:
        data = results[name]
        f.write(f"| **{name}** | {data['toten']:.4f} | {data['fermi']:.4f} | {data['mag']:.4f} | {data['tm_mag']:.4f} | {data['avg_icohp']:.4f} | {data['cumulative_icohp']:.4f} |\n")
    
    f.write("\n## 2. Relative Stability (Embedding Energy Difference)\n\n")
    f.write("The energy difference between embedded and adsorbed configurations ($E_{\\text{diff}} = E_{\\text{embedded}} - E_{\\text{adsorbed}}$) determines the thermodynamic preference for metal incorporation:\n\n")
    
    e_diff_co = results["embedded/co"]['toten'] - results["adsorbed/co"]['toten']
    e_diff_fe = results["embedded/fe"]['toten'] - results["adsorbed/fe"]['toten']
    e_diff_ni = results["embedded/ni"]['toten'] - results["adsorbed/ni"]['toten']
    
    f.write(f"*   **Cobalt (Co):** $E_\\text{{diff}} = {e_diff_co:.4f}\\text{{ eV}}$ (Embedded is more stable by **{-e_diff_co:.4f} eV**)\n")
    f.write(f"*   **Iron (Fe):** $E_\\text{{diff}} = {e_diff_fe:.4f}\\text{{ eV}}$ (Embedded is more stable by **{-e_diff_fe:.4f} eV**)\n")
    f.write(f"*   **Nickel (Ni):** $E_\\text{{diff}} = {e_diff_ni:.4f}\\text{{ eV}}$ (Adsorbed is more stable by **{e_diff_ni:.4f} eV**)\n\n")
    
    f.write("## 3. Detailed Bond Parameters\n\n")
    for name in systems:
        f.write(f"### {name}\n")
        f.write("| Bond | Length (Å) | COHP at $E_F$ | LOBSTER ICOHP (eV) |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for b in results[name]['bonds']:
            f.write(f"| {b['pair']} | {b['length']:.3f} | {b['cohp_ef']:.4f} | {b['icohp']:.4f} |\n")
        f.write("\n")

print(f"Summary table written to {summary_path}")

# Set Times New Roman and MathText font settings globally
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['mathtext.fontset'] = 'stix'

# ----------------------------------------------------
# 2. Generate Stability Plots (Original and Grouped)
# ----------------------------------------------------
tms = ['Co', 'Fe', 'Ni']

# 2.1 Original Difference Plot (kept for backward compatibility)
e_diffs = [e_diff_co, e_diff_fe, e_diff_ni]
colors = ['#1f77b4' if x < 0 else '#d62728' for x in e_diffs]

plt.figure(figsize=(6, 4.5))
plt.bar(tms, e_diffs, color=colors, edgecolor='black', width=0.5, zorder=3)
plt.axhline(0, color='black', linewidth=1.2, zorder=2)
plt.ylabel(r'$\Delta E = E_{\mathrm{embedded}} - E_{\mathrm{adsorbed}}\ (\mathrm{eV})$', fontsize=11)
plt.xlabel('Transition Metal', fontsize=11)
plt.title('Relative Stability of Embedded vs Adsorbed Configurations', fontsize=12, fontweight='bold', pad=15)
plt.ylim(-1.1, 0.3)  # Increased limits to solve overlapping
plt.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)

for i, val in enumerate(e_diffs):
    va_dir = 'bottom' if val > 0 else 'top'
    offset = 0.02 if val > 0 else -0.02
    plt.text(i, val + offset, f"{val:+.2f} eV", ha='center', va=va_dir, fontweight='bold', fontsize=10)

plt.tight_layout()
plot_stability_path = os.path.join(post_dir, "stability_comparison.png")
plt.savefig(plot_stability_path, dpi=300)
plt.close()

# 2.2 Corrected Grouped Bar Plot using True Formation Energies
# Read the HER_energies.dat file
her_dat = os.path.join(base_dir, "f_crcl3-doped-for-HER", "HER_energies.dat")
if not os.path.exists(her_dat):
    print(f"Warning: {her_dat} not found")
else:
    e_ads = []
    e_emb = []
    with open(her_dat, 'r') as f:
        lines = f.readlines()[1:] # skip header
        for line in lines:
            parts = line.split()
            e_ads.append(float(parts[5]))
            e_emb.append(float(parts[6]))

    x = np.arange(len(tms))
    width = 0.35
    
    plt.figure(figsize=(7, 5))
    
    plt.bar(x - width/2, e_ads, width, label='Adsorbed', color='#1f77b4', edgecolor='black', zorder=3)
    plt.bar(x + width/2, e_emb, width, label='Embedded', color='#ff7f0e', edgecolor='black', zorder=3)
    
    plt.axhline(0, color='black', linewidth=1.2, zorder=2)
    plt.ylabel(r'Formation Energy $E_{\mathrm{form}}\ (\mathrm{eV})$', fontsize=11)
    plt.xlabel('Transition Metal', fontsize=11)
    plt.title('Formation Energies: Adsorbed vs Embedded States', fontsize=13, fontweight='bold', pad=15)
    plt.xticks(x, tms, fontsize=11)
    
    # Adjust ylim dynamically
    min_val = min(min(e_ads), min(e_emb))
    plt.ylim(min_val - 0.5, 0.5)
    plt.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    
    for i in range(len(tms)):
        plt.text(x[i] - width/2, e_ads[i] - 0.05, f"{e_ads[i]:.2f}", ha='center', va='top', fontweight='bold', fontsize=9)
        plt.text(x[i] + width/2, e_emb[i] - 0.05, f"{e_emb[i]:.2f}", ha='center', va='top', fontweight='bold', fontsize=9)
    
    plt.legend(loc='lower right', frameon=True, edgecolor='black', fancybox=False, fontsize=10)
    plt.tight_layout()
    plot_stability_grouped_path = os.path.join(post_dir, "stability_grouped.png")
    plt.savefig(plot_stability_grouped_path, dpi=300)
    plt.close()
    print(f"Corrected grouped stability plot saved to {plot_stability_grouped_path}")

# ----------------------------------------------------
# 3. Generate COHP and ICOHP Plots
# ----------------------------------------------------
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

def plot_cohp_panel(systems_list, title, filename):
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.5), sharey=True)
    tms_names = ['Co', 'Fe', 'Ni']
    
    for idx, sys_name in enumerate(systems_list):
        ax = axes[idx]
        data = results[sys_name]
        energies = data['energies']
        
        if energies is None:
            ax.text(0.5, 0.5, "No LOBSTER COHP Data", ha='center', va='center', fontsize=12)
            ax.set_title(f"{tms_names[idx]} (Not Run)", fontsize=13)
            continue
            
        curves = data['cohp_curves']
        
        for bond_name, curve_data in curves.items():
            # Plot -COHP curve
            line, = ax.plot(-curve_data['tot'], energies, label=format_bond_latex(bond_name), alpha=0.85, linewidth=1.8)
            # Shade the area under the curve up to EF (energy <= 0) to represent the integral
            ax.fill_betweenx(energies, 0, -curve_data['tot'], where=(energies <= 0), alpha=0.15, color=line.get_color())
            
        ax.axvline(0, color='gray', linestyle='--', linewidth=1.0)
        ax.axhline(0, color='black', linestyle='-', linewidth=1.2) # Fermi Level
        
        ax.set_xlim(-1.2, 1.5)
        ax.set_ylim(-7, 5)
        
        ax.set_title(f"{tms_names[idx]} System ({sys_name.split('/')[0]})", fontsize=13, fontweight='bold')
        ax.set_xlabel(r'$-\mathrm{COHP}$', fontsize=12, fontweight='bold')
        ax.legend(loc='upper right', frameon=True, edgecolor='black', fancybox=False, fontsize=11, borderpad=0.6, handlelength=1.5)
        ax.tick_params(axis='both', labelsize=12)
        ax.grid(linestyle=':', alpha=0.6)
        
    axes[0].set_ylabel(r'$E - E_{\mathrm{F}}\ (\mathrm{eV})$', fontsize=13, fontweight='bold')
    fig.suptitle(title, fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    save_path = os.path.join(post_dir, filename)
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"COHP plot saved to {save_path}")

def plot_icohp_panel(systems_list, title, filename):
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.5), sharey=True)
    tms_names = ['Co', 'Fe', 'Ni']
    
    for idx, sys_name in enumerate(systems_list):
        ax = axes[idx]
        data = results[sys_name]
        energies = data['energies']
        
        if energies is None:
            ax.text(0.5, 0.5, "No LOBSTER ICOHP Data", ha='center', va='center', fontsize=12)
            ax.set_title(f"{tms_names[idx]} (Not Run)", fontsize=13)
            continue
            
        curves = data['icohp_curves']
        
        for bond_name, curve_data in curves.items():
            # Plot -ICOHP curve (so positive values represent bonding integral)
            ax.plot(-curve_data['tot'], energies, label=format_bond_latex(bond_name), alpha=0.85, linewidth=1.8)
            
        ax.axvline(0, color='gray', linestyle='--', linewidth=1.0)
        ax.axhline(0, color='black', linestyle='-', linewidth=1.2) # Fermi Level
        
        ax.set_xlim(-0.2, 3.5)  # ICOHP values go up to ~ -2.5 eV, so -ICOHP goes up to +2.5
        ax.set_ylim(-7, 5)
        
        ax.set_title(f"{tms_names[idx]} System ({sys_name.split('/')[0]})", fontsize=13, fontweight='bold')
        ax.set_xlabel(r'$-\mathrm{ICOHP}\ (\mathrm{eV})$', fontsize=12, fontweight='bold')
        ax.legend(loc='lower right', frameon=True, edgecolor='black', fancybox=False, fontsize=11, borderpad=0.6, handlelength=1.5)
        ax.tick_params(axis='both', labelsize=12)
        ax.grid(linestyle=':', alpha=0.6)
        
    axes[0].set_ylabel(r'$E - E_{\mathrm{F}}\ (\mathrm{eV})$', fontsize=13, fontweight='bold')
    fig.suptitle(title, fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    save_path = os.path.join(post_dir, filename)
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"ICOHP plot saved to {save_path}")

# Generate all COHP plots
plot_cohp_panel(["adsorbed/co", "adsorbed/fe", "adsorbed/ni"], 
                "COHP Curves for Adsorbed TM-Cl Bonds in Monolayer CrCl3", 
                "cohp_adsorbed.png")

plot_cohp_panel(["embedded/co", "embedded/fe", "embedded/ni"], 
                "COHP Curves for Embedded TM-Cl Bonds in Monolayer CrCl3", 
                "cohp_embedded.png")

# Generate all ICOHP plots
plot_icohp_panel(["adsorbed/co", "adsorbed/fe", "adsorbed/ni"], 
                 "Integrated COHP (ICOHP) for Adsorbed TM-Cl Bonds", 
                 "icohp_adsorbed.png")

plot_icohp_panel(["embedded/co", "embedded/fe", "embedded/ni"], 
                 "Integrated COHP (ICOHP) for Embedded TM-Cl Bonds", 
                 "icohp_embedded.png")
