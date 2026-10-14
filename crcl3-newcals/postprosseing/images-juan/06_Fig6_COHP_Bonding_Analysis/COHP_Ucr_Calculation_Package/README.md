# LOBSTER COHP Calculation Suite (+U_Cr = 3.29 eV)
### Self-Contained Slurm Package for Monolayer $\text{CrCl}_3$ Transition-Metal Functionalization

This directory contains the complete, self-contained input files, pseudopotentials, and Slurm execution scripts to compute the **Crystal Orbital Hamilton Population ($-\text{COHP}$)** curves for the single-site $+U_{\text{Cr}} = 3.29\text{ eV}$ tier of **Figure 6** and **Supplementary Figure S4**.

---

## 🔬 Systems Included

All systems are based on fully relaxed $2\times2$ monolayer $\text{CrCl}_3$ host structures (33 atoms total: 8 Cr, 24 Cl, 1 TM):

1. **Surface Adsorbed ($S_2$ Threefold Hollow Cavity):**
   * `adsorbed/Co`: Co adsorbed above the Cr hollow cavity ($h = 1.88\text{ \AA}$)
   * `adsorbed/Fe`: Fe adsorbed above the Cr hollow cavity ($h = 1.77\text{ \AA}$)
   * `adsorbed/Ni`: Ni adsorbed above the Cr hollow cavity ($h = 1.43\text{ \AA}$)

2. **Monolayer Embedded (In-Plane Octahedral Pore):**
   * `embedded/Co`: Co embedded coplanar with the chromium cation layer ($\Delta z \approx 0.00\text{ \AA}$)
   * `embedded/Fe`: Fe embedded coplanar with the chromium cation layer ($\Delta z \approx 0.00\text{ \AA}$)
   * `embedded/Ni`: Ni embedded coplanar with the chromium cation layer ($\Delta z \approx 0.00\text{ \AA}$)

---

## 📁 Directory Structure & File Manifest

Each system subfolder contains complete, standalone VASP and LOBSTER inputs:

```text
COHP_Ucr_Calculation_Package/
├── README.md                      # This documentation guide
├── run_all_slurm.sh               # Master script: Submits all 6 systems as parallel jobs
├── run_cohp_ads.sh                # Single-node script: Runs adsorbed Co -> Fe -> Ni sequentially
├── run_cohp_emb.sh                # Single-node script: Runs embedded Co -> Fe -> Ni sequentially
│
├── adsorbed/
│   ├── Co/  [INCAR, POSCAR, POTCAR, KPOINTS, lobsterin, run_slurm.sh]
│   ├── Fe/  [INCAR, POSCAR, POTCAR, KPOINTS, lobsterin, run_slurm.sh]
│   └── Ni/  [INCAR, POSCAR, POTCAR, KPOINTS, lobsterin, run_slurm.sh]
│
└── embedded/
    ├── Co/  [INCAR, POSCAR, POTCAR, KPOINTS, lobsterin, run_slurm.sh]
    ├── Fe/  [INCAR, POSCAR, POTCAR, KPOINTS, lobsterin, run_slurm.sh]
    └── Ni/  [INCAR, POSCAR, POTCAR, KPOINTS, lobsterin, run_slurm.sh]
```

### Essential DFT Settings for LOBSTER in `INCAR`:
* **Functional:** PBE with Grimme DFT-D3(BJ) dispersion correction (`IVDW = 12`)
* **Hubbard $U$:** Dudarev $+U_{\text{Cr}} = 3.29\text{ eV}$ applied strictly to Cr-$3d$ (`LDAUU = 3.29 0.00 0.00`)
* **Symmetry:** Strictly turned off (`ISYM = -1`) as required by LOBSTER
* **Bands:** Extended to `NBANDS = 216` to provide complete projection space
* **Wavefunction:** Full binary output written (`LWAVE = .TRUE.`, `PREC = Accurate`, `EDIFF = 1E-06`)

---

## 🚀 Execution Instructions on Any Private Slurm Cluster

Transfer the `COHP_Ucr_Calculation_Package` folder to your private cluster and choose one of the execution strategies:

### Strategy A: High-Throughput Parallel (Fastest — ~7 hours total)
If your cluster has multiple idle nodes or sufficient cores (e.g., 6 jobs $\times$ 24–32 cores = 144–192 cores):
```bash
chmod +x run_all_slurm.sh
./run_all_slurm.sh <partition_name>
```
*Submits 6 independent Slurm jobs simultaneously.*

### Strategy B: Two-Node Parallel (~21 hours total)
If you have 2 nodes available (e.g., 24–32 cores each):
```bash
# Node 1: Executes Adsorbed Co -> Fe -> Ni
sbatch -p <partition_name> run_cohp_ads.sh

# Node 2: Executes Embedded Co -> Fe -> Ni
sbatch -p <partition_name> run_cohp_emb.sh
```

### Strategy C: Single-System Submission
To run a specific system individually:
```bash
cd adsorbed/Co
sbatch -p <partition_name> run_slurm.sh
```

---

## 📊 Expected Outputs & Deliverable Generation

Each job will output:
* **`vasp.out` / `OSZICAR` / `OUTCAR`**: Electronic SCF convergence logs
* **`WAVECAR`**: Binary wavefunction file (~300 MB)
* **`COHPCAR.lobster`**: The Crystal Orbital Hamilton Populations (~711–760 KB)
* **`ICOHPLIST.lobster`**: Integrated ICOHP values for all TM–Cl bonds
* **`DOSCAR.lobster`**: Projected density of states

Once the `COHPCAR.lobster` files are generated across all 6 systems, copying them into `crcl3-newcals/cohp_lobster_Ucr/` and running:
```bash
python3 plot_fig6_dual_tier_cohp.py
```
will automatically generate `Fig6_Ucr.png` and `Fig6_Ucr.pdf` in `06_Fig6_COHP_Bonding_Analysis/`.
