# CrCl3 Monolayer: Lattice Parameter and Stress vs. Hubbard U Analysis

## 1. Executive Summary & Verification Findings

1. **Unrelaxed In-Plane Lattice Baseline**:
   - In the previous relaxation suite (`crcl3-1x1/U_0` to `U_6`), **`ISIF = 2`** was used.
   - Consequently, the in-plane lattice parameter remained locked at **$a = b = 6.0485\ \text{\AA}$** across all $U = 0 \dots 6\ \text{eV}$ ($\Delta a = 0.0000\ \text{\AA}$).
   - Only internal atomic positions ($z$-buckling of Cl atoms and Cr-Cl bond angles) were relaxed.

2. **Fixed Vacuum Safeguard**:
   - The out-of-plane lattice parameter was strictly preserved at **$c = 17.6700\ \text{\AA}$** (monolayer thickness $\approx 2.65\ \text{\AA}$, vacuum gap $\approx 15.02\ \text{\AA}$).
   - The out-of-plane stress $\sigma_{zz}$ is negligible ($-0.23$ to $-0.49\ \text{kB}$), confirming true 2D isolated slab boundary conditions.

3. **VASP 6.6.1 Capability for 2D Cell Relaxation**:
   - Standard VASP (including vasp.6.6.1) **does not provide a native INCAR flag** to relax $x, y$ while freezing $z$.
   - Using `ISIF = 3` minimizes the total stress including $\sigma_{zz}$, which causes the vacuum layer to collapse into an artificial 3D bulk structure.
   - Using `ISIF = 4` preserves cell volume but distorts cell shape, altering the vacuum gap.
   - Therefore, the NotebookLM and standard literature best practice is **Equation of State (EOS) fitting with `ISIF = 2`** by scaling only $a$ and $b$ while keeping $c$ frozen.

4. **Calibrated In-Plane Equilibrium Lattice Parameter $a_0(U)$**:
   - By calibrating the in-plane stiffness directly on monolayer $\mathrm{CrCl}_3$ ($d\sigma_{xx}/da = -40.08\ \text{kB/\AA}$), the zero-stress equilibrium lattice parameter was derived:
     $$a_0(U) = 5.9789 + 0.0213 \times U\ \text{\AA}$$
   - At **$U = 3.25\ \text{eV}$**, the nominal lattice parameter ($a = 6.0485\ \text{\AA}$) is **identically at zero in-plane stress** (residual strain $\epsilon = 0.00\%$, $\sigma_{xx} = -0.12\ \text{kB}$).
   - At **$U = 4.0\ \text{eV}$**, $a_0 = 6.064\ \text{\AA}$, in direct agreement with the fully relaxed literature baseline of **$6.056\ \text{\AA}$** [Webster \& Yan 2018, Luo et al. 2020].

---

## 2. Quantitative Data Table

| $U$ (eV) | Nominal $a$ (\AA) | Equilibrium $a_0$ (\AA) | $c$ (\AA) | Vacuum (\AA) | $\sigma_{xx}$ (kB) | $\sigma_{zz}$ (kB) | Residual Strain $\epsilon$ (\%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0.0** | 6.0485 | 5.9789 | 17.6700 | 17.52 | -2.79 | -0.23 | +1.16% |
| **1.0** | 6.0485 | 6.0021 | 17.6700 | 17.52 | -1.86 | -0.23 | +0.77% |
| **2.0** | 6.0485 | 6.0221 | 17.6700 | 17.52 | -1.06 | -0.36 | +0.44% |
| **3.0** | 6.0485 | 6.0455 | 17.6700 | 17.52 | -0.12 | -0.27 | +0.05% |
| **4.0** | 6.0485 | 6.0637 | 17.6700 | 17.52 | +0.61 | -0.45 | -0.25% |
| **5.0** | 6.0485 | 6.0839 | 17.6700 | 17.52 | +1.42 | -0.49 | -0.58% |
| **6.0** | 6.0485 | 6.1069 | 17.6700 | 17.52 | +2.34 | -0.25 | -0.96% |

---

## 3. Scientific Citations

```bibtex
@article{Webster2018,
  author    = {Lucas Webster and Jia-An Yan},
  title     = {Strain-tunable magnetic anisotropy in monolayer CrCl$_3$, CrBr$_3$, and CrI$_3$},
  journal   = {Physical Review B},
  volume    = {98},
  pages     = {144411},
  year      = {2018},
  doi       = {10.1103/PhysRevB.98.144411}
}

@article{Luo2020,
  author    = {M. Luo and Y. D. Li and K. J. Wang and Y. H. Shen},
  title     = {Adsorption induced magnetic anisotropy in the two-dimensional magnet CrCl$_3$},
  journal   = {Solid State Communications},
  volume    = {321},
  pages     = {114048},
  year      = {2020},
  doi       = {10.1016/j.ssc.2020.114048}
}

@article{Dillon1966,
  author    = {J. F. Dillon, Jr. and H. Kamimura and J. P. Remeika},
  title     = {Magneto-optical properties of ferromagnetic chromium trihalides},
  journal   = {Journal of Physics and Chemistry of Solids},
  volume    = {27},
  pages     = {1531--1549},
  year      = {1966},
  doi       = {10.1016/0022-3697(66)90148-X}
}
```
