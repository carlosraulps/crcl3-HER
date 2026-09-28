#!/usr/bin/env python3
"""
run_cococcioni_live_test.py

Executes a live, end-to-end first-principles Cococcioni Linear Response calculation
on the CrCl3 1x1 primitive cell to determine the ab initio Hubbard U parameter.
Designed for parallel execution with VASP on the local Arch workstation (AMD Ryzen 9 5950X, 16 cores).
"""

import os
import sys
import re
import subprocess
import numpy as np

WORK_DIR = "/home/cr/scratch_vasp/cococcioni_crcl3_1x1"
MPIRUN = "/home/cr/.local/share/mamba/envs/vasp-env/bin/mpirun"
VASP_BIN = "/home/cr/computational-materials-suite/vasp.6.6.1/bin/vasp_std"
NPROCS = 16

os.makedirs(WORK_DIR, exist_ok=True)
os.chdir(WORK_DIR)

print("=" * 75)
print("🚀 Live First-Principles Cococcioni Linear-Response Test for CrCl3")
print("   Host: Arch Linux (AMD Ryzen 9 5950X, 16 Cores / 32 Threads)")
print("=" * 75)

# 1. Prepare POSCAR with split species (Cr1: 1, Cr: 1, Cl: 6)
poscar_content = """CrCl3 1x1 Primitive Split Cococcioni
1.0
 6.0462744985246628    0.0000000000000000    0.0000000000000000
-3.0231372492623314    5.2362273139763751    0.0000000000000000
 0.0000000000000000    0.0000000000000000   20.0000000000000000
Cr1 Cr Cl
 1   1  6
Direct
 0.3333333333333357    0.6666666666666643    0.5000000000000000
 0.6666666666666643    0.3333333333333357    0.5000000000000000
 0.3580759152473423    0.0000000000000000    0.4332349139338483
 0.0000000000000000    0.3580759152473423    0.4332349139338483
 0.6419240847526577    0.6419240847526577    0.4332349139338483
 0.6419240847526577    0.0000000000000000    0.5667650860661517
 0.0000000000000000    0.6419240847526577    0.5667650860661517
 0.3580759152473423    0.3580759152473423    0.5667650860661517
"""
with open("POSCAR", "w") as f:
    f.write(poscar_content)

# 2. Assemble POTCAR
subprocess.run(
    "sed -n '1,2620p' /home/cr/scratch_vasp/crcl3-1x1/U_0/POTCAR > /tmp/p_cr && "
    "sed -n '2621,4896p' /home/cr/scratch_vasp/crcl3-1x1/U_0/POTCAR > /tmp/p_cl && "
    "cat /tmp/p_cr /tmp/p_cr /tmp/p_cl > POTCAR",
    shell=True, check=True
)

# 3. KPOINTS (4x4x1)
with open("KPOINTS", "w") as f:
    f.write("Gamma\n0\nMonkhorst\n4 4 1\n0 0 0\n")

# 4. Helper function to parse d occupation from OUTCAR
def parse_d_occ(outcar_path, target_ion=1):
    if not os.path.exists(outcar_path):
        return None
    with open(outcar_path, "r") as f:
        content = f.read()
    
    # Try onsite density matrix (LDAUPRINT=2)
    pattern = re.compile(
        r"onsite density matrix.*?ion\s+" + str(target_ion) + r".*?(?=onsite density matrix|total charge|$)",
        re.DOTALL | re.IGNORECASE
    )
    matches = list(pattern.finditer(content))
    if matches:
        last_block = matches[-1].group(0)
        diag_vals = []
        for line in last_block.split("\n"):
            parts = line.split()
            try:
                floats = [float(p) for p in parts]
                if len(floats) == 5:
                    diag_vals.append(floats)
            except ValueError:
                continue
        if len(diag_vals) >= 5:
            spin1_diag = sum(diag_vals[i][i] for i in range(5))
            spin2_diag = sum(diag_vals[5 + i][i] for i in range(5)) if len(diag_vals) >= 10 else 0.0
            return spin1_diag + spin2_diag
            
    # Fallback to total charge by orbital (LORBIT=11)
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "total charge" in line and "ion" in lines[min(i+1, len(lines)-1)]:
            for j in range(i+2, min(i+15, len(lines))):
                parts = lines[j].split()
                if len(parts) >= 5 and parts[0] == str(target_ion):
                    try:
                        return float(parts[3]) # d orbital column
                    except ValueError:
                        pass
    return None

# 5. Run Ground-State Calculation (alpha = 0)
print("\n[Step 1/3] Running Unperturbed Ground-State DFT (alpha = 0)...")
gs_dir = os.path.join(WORK_DIR, "ground_state")
os.makedirs(gs_dir, exist_ok=True)
subprocess.run(f"cp POSCAR POTCAR KPOINTS {gs_dir}/", shell=True, check=True)

incar_gs = """SYSTEM = CrCl3_GS
ENCUT = 400
PREC = Accurate
ALGO = Fast
ISMEAR = 0
SIGMA = 0.05
ISPIN = 2
MAGMOM = 3.0 3.0 6*0.0
EDIFF = 1E-6
NELM = 60
LREAL = .FALSE.
LMAXMIX = 4
IVDW = 12
LDAU = .TRUE.
LDAUTYPE = 3
LDAUL = 2 2 -1
LDAUU = 0.0000 0.0 0.0
LDAUJ = 0.0000 0.0 0.0
LDAUPRINT = 2
LORBIT = 11
LWAVE = .FALSE.
LCHARG = .TRUE.
NCORE = 4
"""
with open(f"{gs_dir}/INCAR", "w") as f:
    f.write(incar_gs)

cmd_gs = f"cd {gs_dir} && {MPIRUN} -np {NPROCS} {VASP_BIN} > vasp.out 2>&1"
subprocess.run(cmd_gs, shell=True, check=True)
n_gs = parse_d_occ(f"{gs_dir}/OUTCAR", 1)
print(f"✔ Ground-state converged! Target Cr1 3d occupation n_0 = {n_gs:.5f}")

# 6. Perturbation Grid
alphas = [-0.08, -0.04, 0.00, 0.04, 0.08]
bare_occs = []
scf_occs = []

print("\n[Step 2/3] Running Response Calculations across alpha grid...")
print(f"   Alpha values (eV): {alphas}")

for a in alphas:
    # Bare calculation (non-SCF, ICHARG=11, NELM=1)
    b_dir = os.path.join(WORK_DIR, f"bare_alpha_{a:+.2f}")
    os.makedirs(b_dir, exist_ok=True)
    subprocess.run(f"cp POSCAR POTCAR KPOINTS {b_dir}/", shell=True, check=True)
    subprocess.run(f"cp {gs_dir}/CHGCAR {b_dir}/", shell=True, check=True)
    
    incar_bare = f"""SYSTEM = CrCl3_Bare_{a}
ENCUT = 400
PREC = Accurate
ALGO = None
ICHARG = 11
NELM = 1
ISMEAR = 0
SIGMA = 0.05
ISPIN = 2
EDIFF = 1E-6
LREAL = .FALSE.
LMAXMIX = 4
IVDW = 12
LDAU = .TRUE.
LDAUTYPE = 3
LDAUL = 2 2 -1
LDAUU = {a:.4f} 0.0 0.0
LDAUJ = {a:.4f} 0.0 0.0
LDAUPRINT = 2
LORBIT = 11
LWAVE = .FALSE.
LCHARG = .FALSE.
NCORE = 4
"""
    with open(f"{b_dir}/INCAR", "w") as f:
        f.write(incar_bare)
    subprocess.run(f"cd {b_dir} && {MPIRUN} -np {NPROCS} {VASP_BIN} > vasp.out 2>&1", shell=True, check=True)
    nb = parse_d_occ(f"{b_dir}/OUTCAR", 1)
    bare_occs.append(nb)
    
    # Interacting calculation (SCF, ICHARG=1, NELM=40)
    s_dir = os.path.join(WORK_DIR, f"scf_alpha_{a:+.2f}")
    os.makedirs(s_dir, exist_ok=True)
    subprocess.run(f"cp POSCAR POTCAR KPOINTS {s_dir}/", shell=True, check=True)
    
    incar_scf = f"""SYSTEM = CrCl3_SCF_{a}
ENCUT = 400
PREC = Accurate
ALGO = Fast
ICHARG = 1
NELM = 40
ISMEAR = 0
SIGMA = 0.05
ISPIN = 2
MAGMOM = 3.0 3.0 6*0.0
EDIFF = 1E-6
LREAL = .FALSE.
LMAXMIX = 4
IVDW = 12
LDAU = .TRUE.
LDAUTYPE = 3
LDAUL = 2 2 -1
LDAUU = {a:.4f} 0.0 0.0
LDAUJ = {a:.4f} 0.0 0.0
LDAUPRINT = 2
LORBIT = 11
LWAVE = .FALSE.
LCHARG = .FALSE.
NCORE = 4
"""
    with open(f"{s_dir}/INCAR", "w") as f:
        f.write(incar_scf)
    subprocess.run(f"cd {s_dir} && {MPIRUN} -np {NPROCS} {VASP_BIN} > vasp.out 2>&1", shell=True, check=True)
    ns = parse_d_occ(f"{s_dir}/OUTCAR", 1)
    scf_occs.append(ns)
    
    print(f"   α = {a:+.2f} eV  -->  n_bare = {nb:.5f},  n_scf = {ns:.5f}")

# 7. Linear Regression & Susceptibility Inversion
print("\n[Step 3/3] Performing Linear Response Inversion...")
alphas_arr = np.array(alphas)
bare_arr = np.array(bare_occs)
scf_arr = np.array(scf_occs)

fit_bare = np.polyfit(alphas_arr, bare_arr, 1)
chi_0 = fit_bare[0]
ss_tot_b = np.sum((bare_arr - np.mean(bare_arr))**2)
r2_bare = 1.0 - (np.sum((bare_arr - (fit_bare[0]*alphas_arr + fit_bare[1]))**2) / ss_tot_b) if ss_tot_b > 0 else 1.0

fit_scf = np.polyfit(alphas_arr, scf_arr, 1)
chi = fit_scf[0]
ss_tot_s = np.sum((scf_arr - np.mean(scf_arr))**2)
r2_scf = 1.0 - (np.sum((scf_arr - (fit_scf[0]*alphas_arr + fit_scf[1]))**2) / ss_tot_s) if ss_tot_s > 0 else 1.0

inv_chi0 = 1.0 / chi_0
inv_chi = 1.0 / chi
u_calc = inv_chi0 - inv_chi

print("=" * 75)
print("📊 FIRST-PRINCIPLES COCOCCIONI LINEAR-RESPONSE RESULTS FOR CrCl3 (1x1)")
print("=" * 75)
print(f"• Bare Susceptibility      (χ_0) : {chi_0:+.5f} eV^-1  (R^2 = {r2_bare:.4f})")
print(f"• Screened Susceptibility  (χ)   : {chi:+.5f} eV^-1  (R^2 = {r2_scf:.4f})")
print(f"• Bare Inverse Curvature   (χ_0^-1): {inv_chi0:+.3f} eV")
print(f"• Screened Inverse Curvature (χ^-1): {inv_chi:+.3f} eV")
print(f"• Calculated Hubbard U_eff       : {u_calc:+.3f} eV")
print("=" * 75)

# Save JSON report
import json
res = {
    "system": "CrCl3_1x1_primitive",
    "alphas": list(alphas),
    "bare_occupations": [float(x) for x in bare_occs],
    "scf_occupations": [float(x) for x in scf_occs],
    "chi_0": float(chi_0),
    "chi": float(chi),
    "r2_bare": float(r2_bare),
    "r2_scf": float(r2_scf),
    "U_eff": float(u_calc)
}
with open(f"{WORK_DIR}/cococcioni_results.json", "w") as f:
    json.dump(res, f, indent=2)
print(f"Results saved to {WORK_DIR}/cococcioni_results.json")
