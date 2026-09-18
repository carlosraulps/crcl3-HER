import os
import re
import zipfile
import numpy as np
import matplotlib.pyplot as plt

# Directories
base_dir = "/Users/apple/Research/abc/paper-adaptation/crcl3-newcals"
post_dir = os.path.join(base_dir, "postprosseing")
indiv_dir = os.path.join(post_dir, "individual_plots")
os.makedirs(indiv_dir, exist_ok=True)

# Set Times New Roman font globally
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['mathtext.fontset'] = 'stix'

systems = [
    "adsorbed/co", "adsorbed/fe", "adsorbed/ni",
    "embedded/co", "embedded/fe", "embedded/ni"
]

results = {}

for name in systems:
    d = os.path.join(base_dir, name)
    outcar = os.path.join(d, "OUTCAR")
    cohp_file = os.path.join(d, "COHPCAR.lobster")
    
    toten = None
    if os.path.exists(outcar):
        with open(outcar, 'r') as f:
            for line in f:
                if "free energy    TOTEN" in line:
                    toten = float(line.split("=")[1].split()[0].strip())
                    
    results[name] = {'toten': toten}

e_diffs = {
    'Co': results["embedded/co"]['toten'] - results["adsorbed/co"]['toten'],
    'Fe': results["embedded/fe"]['toten'] - results["adsorbed/fe"]['toten'],
    'Ni': results["embedded/ni"]['toten'] - results["adsorbed/ni"]['toten']
}

# 1. Combined Stability Plot (2 sig figs)
tms = ['Co', 'Fe', 'Ni']
diff_vals = [e_diffs['Co'], e_diffs['Fe'], e_diffs['Ni']]
colors = ['#1f77b4' if x < 0 else '#d62728' for x in diff_vals]

plt.figure(figsize=(6, 4.5))
plt.bar(tms, diff_vals, color=colors, edgecolor='black', width=0.5, zorder=3)
plt.axhline(0, color='black', linewidth=1.2, zorder=2)
plt.ylabel(r'$\Delta E = E_{\mathrm{embedded}} - E_{\mathrm{adsorbed}}\ (\mathrm{eV})$', fontsize=11)
plt.xlabel('Transition Metal', fontsize=11)
plt.title('Relative Stability of Embedded vs Adsorbed Configurations', fontsize=12, fontweight='bold', pad=15)
plt.ylim(-1.1, 0.3)
plt.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)

for i, val in enumerate(diff_vals):
    va_dir = 'bottom' if val > 0 else 'top'
    offset = 0.02 if val > 0 else -0.02
    plt.text(i, val + offset, f"{val:+.2f} eV", ha='center', va=va_dir, fontweight='bold', fontsize=10)

plt.tight_layout()
p_combined = os.path.join(indiv_dir, "stability_comparison.png")
plt.savefig(p_combined, dpi=300)
plt.close()

# Copy to post_dir as well
plt.figure(figsize=(6, 4.5))
plt.bar(tms, diff_vals, color=colors, edgecolor='black', width=0.5, zorder=3)
plt.axhline(0, color='black', linewidth=1.2, zorder=2)
plt.ylabel(r'$\Delta E = E_{\mathrm{embedded}} - E_{\mathrm{adsorbed}}\ (\mathrm{eV})$', fontsize=11)
plt.xlabel('Transition Metal', fontsize=11)
plt.title('Relative Stability of Embedded vs Adsorbed Configurations', fontsize=12, fontweight='bold', pad=15)
plt.ylim(-1.1, 0.3)
plt.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
for i, val in enumerate(diff_vals):
    va_dir = 'bottom' if val > 0 else 'top'
    offset = 0.02 if val > 0 else -0.02
    plt.text(i, val + offset, f"{val:+.2f} eV", ha='center', va=va_dir, fontweight='bold', fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(post_dir, "stability_comparison.png"), dpi=300)
plt.close()

# 2. Individual Stability Plots for each metal
for tm, val in e_diffs.items():
    color = '#1f77b4' if val < 0 else '#d62728'
    plt.figure(figsize=(4, 4.5))
    plt.bar([tm], [val], color=color, edgecolor='black', width=0.4, zorder=3)
    plt.axhline(0, color='black', linewidth=1.2, zorder=2)
    plt.ylabel(r'$\Delta E = E_{\mathrm{embedded}} - E_{\mathrm{adsorbed}}\ (\mathrm{eV})$', fontsize=11)
    plt.xlabel('Transition Metal', fontsize=11)
    plt.title(f'Relative Stability: {tm}', fontsize=12, fontweight='bold', pad=15)
    
    if val < 0:
        plt.ylim(val - 0.25, 0.15)
    else:
        plt.ylim(-0.15, val + 0.25)
        
    plt.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    
    va_dir = 'bottom' if val > 0 else 'top'
    offset = 0.015 if val > 0 else -0.015
    plt.text(0, val + offset, f"{val:+.2f} eV", ha='center', va=va_dir, fontweight='bold', fontsize=11)
    
    plt.tight_layout()
    p_metal = os.path.join(indiv_dir, f"stability_{tm}.png")
    plt.savefig(p_metal, dpi=300)
    plt.close()
    print(f"Saved individual stability plot: {p_metal}")

# 3. Collect all PNG plots into individual_plots.zip
zip_path = os.path.join(post_dir, "individual_plots.zip")
root_zip_path = os.path.join(base_dir, "individual_plots.zip")

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    # Add files from indiv_dir
    for f in sorted(os.listdir(indiv_dir)):
        if f.endswith('.png'):
            fp = os.path.join(indiv_dir, f)
            zipf.write(fp, arcname=f)
            
    # Add other PNG files from post_dir
    for f in sorted(os.listdir(post_dir)):
        if f.endswith('.png') and f not in os.listdir(indiv_dir):
            fp = os.path.join(post_dir, f)
            zipf.write(fp, arcname=f)

# Copy to root directory for easy access
import shutil
shutil.copyfile(zip_path, root_zip_path)

print(f"\nZIP archive successfully created at:\n - {zip_path}\n - {root_zip_path}")
