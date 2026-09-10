# CrCl₃ H-Adsorption Without U — Calculation Status Report
**Generated:** 2026-09-10 05:44 CST | **Cluster:** iskay (2 nodes, 512 cores total)

---

## 1. SLURM Cluster Status

| Node | State | Cores Total | Cores Used | Cores Free | Reason |
|:---:|:---:|:---:|:---:|:---:|:---|
| iskay201 | **MIXED + DRAIN** | 256 | 80 (5 jobs × 16) | 176 | Kill task failed |
| iskay202 | **IDLE + DRAIN** | 256 | 0 | 256 | Kill task failed |

**Both nodes are in DRAIN state:**
- ✅ Existing running jobs on iskay201 will continue until completion
- ❌ No new jobs can be submitted until sysadmins remove the drain
- 432 cores sitting idle but blocked

**Action needed:** Contact sysadmin to undrain nodes. Once undrained, submit all pending jobs immediately.

---

## 2. Computational Conditions (All Calculations)

| Parameter | Value | Notes |
|:---|:---:|:---|
| **Software** | VASP 6.5.1 | aocc-5.0.0, OpenMPI 5.0.8 |
| **Functional** | PBE (no_vdw) / PBE+D3 (yes_vdw) | `IVDW = 11` for D3 |
| **ENCUT** | 400 eV | ~1.33× max ENMAX (Cl ~300 eV) |
| **EDIFF** | 1.0E-06 eV | Electronic SCF convergence |
| **EDIFFG** | −0.025 eV/Å | Force convergence (paper standard) |
| **NSW** | 100 | Max ionic steps |
| **ISPIN** | 2 | Spin-polarized (Cr³⁺ is 3d³) |
| **ISMEAR / SIGMA** | 0 / 0.05 | Gaussian smearing (semiconductor slab) |
| **ISIF** | 2 | Fixed cell, relax ions |
| **IBRION** | 2 | Conjugate gradient |
| **PREC** | Accurate | — |
| **LREAL** | Auto | Real-space projection |
| **LDIPOL / IDIPOL** | TRUE / 3 | Dipole correction along z |
| **NCORE** | 4 | Parallelization |
| **Vacuum** | c = 20.0 Å | Fixed for all supercells |
| **K-points** | **5×5×1 Γ-centered** | **All supercells (per advisor instruction)** |

### K-Points (5×5×1 for ALL sizes — advisor's instruction)

| Scale | Lattice a (Å) | K-grid | Status |
|:---:|:---:|:---:|:---:|
| 1×1 | 6.046 | 5×5×1 | ✅ Correct |
| 2×2 | 12.093 | 5×5×1 | ✅ Correct |
| 3×3 | 18.139 | 5×5×1 | ✅ **Updated** (was 3×3×1, changed to 5×5×1) |

---

## 3. Supercell Structure

| Scale | Clean (no H) | With H adsorbed | Coverage θ | H-H distance |
|:---:|:---:|:---:|:---:|:---:|
| **1×1** | 2 Cr + 6 Cl = 8 atoms | + 1 H = 9 atoms | 1.0 H/cell | 6.05 Å |
| **2×2** | 8 Cr + 24 Cl = 32 atoms | + 1 H = 33 atoms | 0.25 H/cell | 12.09 Å |
| **3×3** | 18 Cr + 54 Cl = 72 atoms | + 1 H = 73 atoms | 0.111 H/cell | 18.14 Å |

All adsorption calculations use a **single H atom** (not H₂) on the surface. This is the correct approach for computing:

```
E_ads = E(slab+H) − E(slab_clean) − ½ × E(H₂)
```

---

## 4. H₂ Gas-Phase Reference

| Variant | Status | Final Energy | Notes |
|:---:|:---:|:---:|:---|
| **H₂ no_vdw** | ✅ **CONVERGED** | **−6.7596 eV** | 3 ionic steps, done |
| **H₂ yes_vdw** | ❌ **NOT RUN** | — | Input files ready, needs submission |

**Does H₂ need a separate calculation per lattice size (1×1, 2×2, 3×3)?**

**No.** The H₂ molecule is computed in an **isolated 15 Å cubic box** with Γ-only k-points. It is completely **lattice-independent** — the same E(H₂) value is used for ALL supercell sizes:

- ½ × E(H₂ no_vdw) = ½ × (−6.7596) = **−3.3798 eV** → used for all no_vdw calculations
- ½ × E(H₂ yes_vdw) = **needs to be computed** → used for all yes_vdw calculations

The H₂ yes_vdw job is a ~10 minute calculation. **Critical blocker for all PBE+D3 adsorption energies.**

---

## 5. Full Calculation Status Matrix

### 1×1 Supercell (9 atoms, 16 cores/job, ~2-6h each)

| Variant | Site | Status | Ionic Steps | Fmax (eV/Å) | E_final (eV) | Notes |
|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| no_vdw | **clean** | ✅ CONVERGED | 1 | < 0.025 | **−39.0717** | Reference slab |
| no_vdw | **S1** (top-Cl) | ⚠️ INTERRUPTED | 5 | **0.3128** | −40.7737 | Needs more relaxation |
| no_vdw | **S2** (hollow) | ✅ CONVERGED | 2 | < 0.025 | **−39.9659** | Done |
| no_vdw | **S3** (top-Cr) | ⚠️ INTERRUPTED | 13 | **0.0104** | −40.8155 | Forces < EDIFFG! Needs 1 more step |
| yes_vdw | **clean** | ✅ CONVERGED | 3 | < 0.025 | **−39.9841** | Reference slab (D3) |
| yes_vdw | **S1** (top-Cl) | ⚠️ INTERRUPTED | 6 | **0.3282** | −41.8238 | Needs more relaxation |
| yes_vdw | **S2** (hollow) | ⚠️ INTERRUPTED | 12 | **0.0054** | −40.9921 | Forces < EDIFFG! Needs 1 step |
| yes_vdw | **S3** (top-Cr) | ⚠️ INTERRUPTED | 13 | **0.0138** | −41.7093 | Forces < EDIFFG! Needs 1 step |

### 2×2 Supercell (33 atoms, 16 cores/job, ~1-2 days each)

| Variant | Site | Status | Ionic Steps | Fmax (eV/Å) | E_final (eV) | ETA |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| no_vdw | **clean** | ✅ CONVERGED | 1 | < 0.025 | **−156.2868** | — |
| no_vdw | **S1** (top-Cl) | 🔄 RUNNING #242 | 2 | in progress | −157.8530 | **~33h** |
| no_vdw | **S2** (hollow) | ✅ CONVERGED | 2 | < 0.025 | **−157.1957** | — |
| no_vdw | **S3** (top-Cr) | 🔄 RUNNING #244 | 5 | 0.0327 | −157.9748 | **~3.5h** |
| yes_vdw | **clean** | ✅ CONVERGED | 3 | < 0.025 | **−159.9366** | — |
| yes_vdw | **S1** (top-Cl) | 🔄 RUNNING #245 | 1 | in progress | −161.2691 | **~33h** |
| yes_vdw | **S2** (hollow) | 🔄 RUNNING #246 | 3 | 0.0519 | −160.9409 | **~4h** |
| yes_vdw | **S3** (top-Cr) | 🔄 RUNNING #247 | 2 | in progress | −161.5308 | **~10h** |

### 3×3 Supercell (73 atoms, 32 cores/job, estimated ~5-7 days each with 5×5×1)

| Variant | Site | Status | Notes |
|:---:|:---:|:---:|:---|
| no_vdw | **clean** | ⬜ NOT STARTED | KPOINTS updated to 5×5×1 |
| no_vdw | **S1** (top-Cl) | ⬜ NOT STARTED | KPOINTS updated to 5×5×1 |
| no_vdw | **S2** (hollow) | ⬜ NOT STARTED | KPOINTS updated to 5×5×1 |
| no_vdw | **S3** (top-Cr) | ⬜ NOT STARTED | KPOINTS updated to 5×5×1 |
| yes_vdw | **clean** | ⬜ NOT STARTED | KPOINTS updated to 5×5×1 |
| yes_vdw | **S1** (top-Cl) | ⬜ NOT STARTED | KPOINTS updated to 5×5×1 |
| yes_vdw | **S2** (hollow) | ⬜ NOT STARTED | KPOINTS updated to 5×5×1 |
| yes_vdw | **S3** (top-Cr) | ⬜ NOT STARTED | KPOINTS updated to 5×5×1 |

**Note:** Using 5×5×1 k-points on a 3×3 supercell (73 atoms) will be significantly more expensive than 3×3×1 (~2.8× more k-points). Estimated ~5-7 days per job with 32 cores.

---

## 6. Overall Progress

```
           CONVERGED    RUNNING    INTERRUPTED    NOT STARTED    TOTAL
  1×1:        4            0           4              0            8
  2×2:        3            5           0              0            8
  3×3:        0            0           0              8            8
  H₂ ref:     1            0           0              1            2
  ─────────────────────────────────────────────────────────────────
  TOTAL:      8            5           4              9           26
```

**Completion: 8/26 (31%) converged | 5/26 (19%) running | 4/26 (15%) near-done | 9/26 (35%) not started**

---

## 7. Cancelled Jobs (2026-09-10)

Jobs 248-252 were cancelled because both nodes are DRAINED:

| Job ID | Name | Reason |
|:---:|:---:|:---|
| 248 | H1x1_S3_novdw | Nodes DOWN/DRAINED |
| 249 | H1x1_S1_novdw | ReqNodeNotAvail |
| 250 | H1x1_S1_yesvdw | ReqNodeNotAvail |
| 251 | H1x1_S2_yesvdw | ReqNodeNotAvail |
| 252 | H1x1_S3_yesvdw | ReqNodeNotAvail |

---

## 8. Resource Planning — Acceleration Strategy

### When Nodes Come Back Online

**Priority 1 — Quick wins (~30 min total, 64 cores):**
- H₂ yes_vdw reference (16 cores, ~10 min) — **critical blocker**
- 1×1 no_vdw S3 restart (16 cores, ~10 min) — forces already below EDIFFG
- 1×1 yes_vdw S2 restart (16 cores, ~10 min) — forces already below EDIFFG
- 1×1 yes_vdw S3 restart (16 cores, ~10 min) — forces already below EDIFFG

**Priority 2 — Medium (~4-6h, 32 cores):**
- 1×1 no_vdw S1 (16 cores) — Fmax 0.31, needs full relaxation
- 1×1 yes_vdw S1 (16 cores) — Fmax 0.33, needs full relaxation

**Priority 3 — Heavy (~5-7 days, 256 cores):**
- All 8 × 3×3 calculations (32 cores each = 256 cores total)
- Can all run simultaneously on iskay202 if undrained

### Maximum Parallel Throughput
- iskay201 (176 free + 80 running): Priority 1+2 jobs alongside running 2×2
- iskay202 (256 free): All 8 × 3×3 jobs simultaneously
- **All 26 calculations could finish within ~7 days**

---

## 9. Adsorption Sites

| Site | Label | Position | Description |
|:---:|:---:|:---|:---|
| **S1** | top-Cl | Above top-layer Cl | H on top of Cl |
| **S2** | hollow | Center of Cr honeycomb | H in hollow site |
| **S3** | top-Cr | Above Cr atom | H on top of Cr |
| **clean** | — | No adsorbate | Reference slab energy |

---

## 10. Action Checklist

- [ ] Contact sysadmin to undrain iskay201/iskay202
- [ ] Submit H₂ yes_vdw reference (~10 min job)
- [ ] Resubmit 1×1 near-converged jobs (S3 no_vdw, S2/S3 yes_vdw)
- [ ] Resubmit 1×1 S1 jobs (no_vdw, yes_vdw)
- [x] Update 3×3 KPOINTS from 3×3×1 → 5×5×1 (done)
- [ ] Submit all 8 × 3×3 jobs
- [ ] Wait for 5 running 2×2 jobs (~4-33h remaining)
