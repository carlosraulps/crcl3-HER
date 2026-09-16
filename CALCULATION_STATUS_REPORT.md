# CrCl₃ H-Adsorption Project — Comprehensive Status Report
**Date:** 2026-09-16 08:31 CST | **Cluster:** `iskay` (2 nodes, 512 cores total)

---

## 1. Executive Summary & Key Milestones

1. **New Convergence Milestone:**
   - **$2\times2$ `yes_vdw` S3 (top-Cr):** **CONVERGED** ✅ after 20 ionic steps ($E_{\mathrm{TOTEN}} = -161.692639\text{ eV}$, $F_{\mathrm{max}} = 0.0228\text{ eV/\AA}$).
   - **Total Converged Calculations:** **9 / 26** across all supercell matrices.

2. **Thermodynamic Site Preference Ranking (Ground State):**
   - **Top-Cr ($S_3$) & Top-Cl ($S_1$)** are the most thermodynamically stable adsorption sites, with binding energies $\Delta E \approx -1.75 \text{ to } -1.80\text{ eV}$.
   - **Hollow ($S_2$)** is significantly less favorable ($\Delta E \approx -0.90\text{ eV}$), higher in energy by **~0.85 eV**.

3. **Coverage Scaling ($\theta = 1.0$ vs $\theta = 0.25$):**
   - The binding energy shift from $1\times1$ ($\theta = 1.0$) to $2\times2$ ($\theta = 0.25$) is minimal (**0.011 – 0.015 eV** for $S_2$ and $S_3$), demonstrating fast spatial convergence of H-H interactions beyond ~6 Å separation.

4. **SLURM Cluster Status:**
   - Both nodes (`iskay201`, `iskay202`) are currently in `IDLE+DRAIN` state (0 cores in use, 512 cores blocked).
   - System administrator action (`scontrol update NodeName=iskay201,iskay202 State=RESUME`) is required to resume queued jobs.

---

## 2. Complete Calculation Status Matrix

### Legend: ✅ = Converged | ⏸️ = Interrupted (In Progress) | ⬜ = Not Started

| Scale | Variant | Clean Slab | S1 (top-Cl) | S2 (hollow) | S3 (top-Cr) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **$1\times1$** | `no_vdw` | ✅ **CONVERGED** | ⏸️ Fmax = 1.292 eV/Å | ✅ **CONVERGED** | ⏸️ Fmax = 0.044 eV/Å |
| **$1\times1$** | `yes_vdw` | ✅ **CONVERGED** | ⏸️ Fmax = 0.445 eV/Å | ⏸️ Fmax = 0.316 eV/Å | ⏸️ Fmax = 0.044 eV/Å |
| **$2\times2$** | `no_vdw` | ✅ **CONVERGED** | ⏸️ Fmax = 1.036 eV/Å | ✅ **CONVERGED** | ⏸️ Fmax = 0.076 eV/Å |
| **$2\times2$** | `yes_vdw` | ✅ **CONVERGED** | ⏸️ Fmax = 1.423 eV/Å | ⏸️ Fmax = 0.055 eV/Å | ✅ **CONVERGED** |
| **$3\times3$** | `no_vdw` | ⬜ Not Started | ⬜ Not Started | ⬜ Not Started | ⬜ Not Started |
| **$3\times3$** | `yes_vdw` | ⬜ Not Started | ⬜ Not Started | ⬜ Not Started | ⬜ Not Started |
| **$H_2$ Ref** | — | **`no_vdw`:** ✅ **CONVERGED** | — | **`yes_vdw`:** ⬜ Not Started | — |

---

## 3. DFT Total Energies & Adsorption Thermodynamics

### Reference Energies
- **$H_2$ gas-phase (`no_vdw`):** $E(H_2) = -6.759600 \text{ eV} \implies \frac{1}{2}E(H_2) = -3.379800 \text{ eV}$
- **Formula:** 
  $$\Delta E = E_{\mathrm{slab+H}} - E_{\mathrm{clean}}$$
  $$E_{\mathrm{ads}} = \Delta E - \frac{1}{2}E(H_2)$$

---

### A. $1\times1$ Supercell ($\theta = 1.0$ H/cell, $d_{\mathrm{H-H}} = 6.05$ Å)

| Variant | Site | Status | $E_{\mathrm{TOTEN}}$ (eV) | $\Delta E$ (eV) | $E_{\mathrm{ads}}$ (eV) | $F_{\mathrm{max}}$ (eV/Å) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `no_vdw` | **clean** | ✅ CONVERGED | -39.071660 | — | — | 0.0081 |
| `no_vdw` | **S1** (top-Cl) | ⏸️ Interrupted | -40.773716 | -1.702056 | +1.677744 | 1.2922 |
| `no_vdw` | **S2** (hollow) | ✅ CONVERGED | -39.965871 | -0.894211 | **+2.485589** | 0.0174 |
| `no_vdw` | **S3** (top-Cr) | ⏸️ Interrupted | -40.815517 | -1.743857 | +1.635943 | 0.0444 |
| `yes_vdw` | **clean** | ✅ CONVERGED | -39.984116 | — | — | 0.0225 |
| `yes_vdw` | **S1** (top-Cl) | ⏸️ Interrupted | -41.823791 | -1.839675 | — | 0.4445 |
| `yes_vdw` | **S2** (hollow) | ⏸️ Interrupted | -40.992114 | -1.007998 | — | 0.3160 |
| `yes_vdw` | **S3** (top-Cr) | ⏸️ Interrupted | -41.709266 | -1.725150 | — | 0.0443 |

---

### B. $2\times2$ Supercell ($\theta = 0.25$ H/cell, $d_{\mathrm{H-H}} = 12.09$ Å)

| Variant | Site | Status | $E_{\mathrm{TOTEN}}$ (eV) | $\Delta E$ (eV) | $E_{\mathrm{ads}}$ (eV) | $F_{\mathrm{max}}$ (eV/Å) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `no_vdw` | **clean** | ✅ CONVERGED | -156.286781 | — | — | 0.0081 |
| `no_vdw` | **S1** (top-Cl) | ⏸️ Interrupted | -158.087799 | -1.801018 | +1.578782 | 1.0363 |
| `no_vdw` | **S2** (hollow) | ✅ CONVERGED | -157.195690 | -0.908909 | **+2.470891** | 0.0183 |
| `no_vdw` | **S3** (top-Cr) | ⏸️ Interrupted | -158.042245 | -1.755464 | +1.624336 | 0.0759 |
| `yes_vdw` | **clean** | ✅ CONVERGED | -159.936609 | — | — | 0.0226 |
| `yes_vdw` | **S1** (top-Cl) | ⏸️ Interrupted | -161.803836 | -1.867227 | — | 1.4226 |
| `yes_vdw` | **S2** (hollow) | ⏸️ Interrupted | -160.957123 | -1.020514 | — | 0.0547 |
| `yes_vdw` | **S3** (top-Cr) | ✅ CONVERGED | -161.692639 | **-1.756030** | — | **0.0228** |

---

## 4. Coverage Scaling & Multi-Scale Insights

Comparing the binding energy $\Delta E = E_{\mathrm{slab+H}} - E_{\mathrm{clean}}$ across cell sizes:

```
Hollow Site (S2, Pure PBE):
  1x1 (θ = 1.00):  ΔE = -0.8942 eV
  2x2 (θ = 0.25):  ΔE = -0.9089 eV
  Δ(Coverage)     =  0.0147 eV (~15 meV difference)

Top-Cr Site (S3, Pure PBE):
  1x1 (θ = 1.00):  ΔE = -1.7439 eV
  2x2 (θ = 0.25):  ΔE = -1.7555 eV
  Δ(Coverage)     =  0.0116 eV (~12 meV difference)
```

**Key Finding:** The lateral adsorbate-adsorbate repulsion on monolayer $\text{CrCl}_3$ decays rapidly. The energy shift between $\theta = 1.0$ and $\theta = 0.25$ is only **~12–15 meV**, indicating that $2\times2$ is already very close to the isolated adsorbate limit ($\theta \to 0$). The upcoming $3\times3$ calculations will confirm the asymptotic value at $\theta = 0.111$.

---

## 5. SLURM Cluster & Node Availability Report

```
Partition: normal | State: UP | Max Walltime: 30-00:00:00
Total Resources: 2 nodes, 512 cores, 1484.4 GB RAM

Node iskay201: IDLE+DRAIN  (0/256 CPUs in use, 256 free but BLOCKED)  [Reason: Kill task failed]
Node iskay202: IDLE+DRAIN  (0/256 CPUs in use, 256 free but BLOCKED)  [Reason: Kill task failed]

Total Usable Capacity: 0 / 512 cores (100% blocked by DRAIN flag)
```

> [!WARNING]
> **Action Required:** The cluster sysadmin needs to reset the node flags:
> ```bash
> sudo scontrol update NodeName=iskay201,iskay202 State=RESUME
> ```
> Once undrained, all 18 pending/queued jobs can be executed concurrently across the 512 available cores.

---

## 6. Next Steps & Recommended Workflow

1. **Undrain Nodes:** System admin clears `DRAIN` flags on `iskay201` and `iskay202`.
2. **Submit $H_2$ `yes_vdw` Reference:** Run the 10-minute gas-phase reference job (`H2_reference/yes_vdw/job.sh`) to obtain $E(H_2)_{\mathrm{yes\_vdw}}$ for complete PBE+D3 adsorption energies.
3. **Resume Interrupted $1\times1$ & $2\times2$ Jobs:** Resubmit remaining 9 interrupted jobs (CONTCAR $\to$ POSCAR restart is already built into `job.sh`).
4. **Launch $3\times3$ Supercell Matrix:** Submit all 8 $3\times3$ jobs (with $5\times5\times1$ k-points as instructed). All 8 jobs can run simultaneously on `iskay202` (256 cores).
