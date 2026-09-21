# Primary Literature & Reference Analysis for Monolayer $\mathrm{CrCl}_3$

This document compiles the exhaustive bibliographic data, primary source text citations, and physical interpretations evaluated during the **Decision Council** deliberation to resolve Reviewer 4's band gap query and establish verified benchmarks for monolayer $\mathrm{CrCl}_3$ under DFT-D3 + Hubbard $U$.

---

## 1. Primary Sources Summary & Verified Findings

### [1] Pollini & Spinolo (1970) — Fundamental Bulk Optical Gap & Crystal-Field Excitations
- **Citation**: I. Pollini and G. Spinolo, *"Intrinsic Optical Properties of $\mathrm{CrCl}_3$"*, *Physica Status Solidi (b)* **41**, 691–701 (1970).
- **DOI**: [10.1002/pssb.19700410224](https://doi.org/10.1002/pssb.19700410224)
- **Experimental System**: Bulk single crystals and sublimed thin films; optical transmission, absorption coefficient $\alpha(\hbar\omega)$, photoconductivity yield, and vacuum-UV polarized reflectivity from 80 K to 300 K.
- **Key Experimental Findings**:
  1. **Regime I (Crystal-Field Region, $0.6 - 3.0\ \mathrm{eV}$)**:
     - Weak optical absorption ($\alpha \approx 10^1 - 10^2\ \mathrm{cm}^{-1}$) with an initial visible absorption edge at $\approx 1.5\ \mathrm{eV}$ (80 K) following Urbach's rule.
     - Sharp absorption peaks at $1.68\ \mathrm{eV}$ (300 K) / $1.70\ \mathrm{eV}$ (80 K) corresponding to intra-ionic $3d \to 3d$ transitions within $\mathrm{Cr}^{3+}$ ($^4A_{2g} \to\ ^4T_{2g}$).
     - Photoconductivity yield in this region is negligible; transport occurs only via localized, thermally activated polaron hopping between Cr sites.
  2. **Regime II (Fundamental Charge-Transfer Edge, $3.2 \pm 0.2\ \mathrm{eV}$)**:
     - Steep absorption onset ($\alpha \approx 10^4 - 10^5\ \mathrm{cm}^{-1}$) at $(3.2 \pm 0.2)\ \mathrm{eV}$.
     - Photoconductivity yield increases by **two orders of magnitude ($100\times$)** relative to the $1.68\ \mathrm{eV}$ peak.
     - Confirms true delocalized free carrier generation, attributed to interband charge-transfer transitions ($\mathrm{Cl}\ 3p \to \mathrm{Cr}\ 3d$ or $\mathrm{Cl}\ 3p \to \mathrm{Cr}\ 4s$).
- **Historical Precedent**: Pollini & Spinolo confirm the earlier optical work of J. F. Dillon Jr., H. Kamimura, and J. P. Remeika, *J. Phys. Chem. Solids* **27**, 1531 (1966) [DOI: 10.1016/0022-3697(66)90148-X].

---

### [2] Webster & Yan (2018) — Monolayer PBE Baseline & Strain Effects
- **Citation**: L. Webster and J.-A. Yan, *"Strain-tunable magnetic anisotropy in monolayer $\mathrm{CrCl}_3$, $\mathrm{CrBr}_3$, and $\mathrm{CrI}_3$"*, *Physical Review B* **98**, 144411 (2018).
- **DOI**: [10.1103/PhysRevB.98.144411](https://doi.org/10.1103/PhysRevB.98.144411)
- **Method**: VASP, PAW, GGA-PBE, $E_{\text{cut}} = 500\ \mathrm{eV}$, $8\times 8\times 1$ $k$-mesh, fully relaxed ($a_0 = 6.056\ \text{\AA}$, $\mathrm{Cr-Cl} = 2.357\ \text{\AA}$).
- **Key Findings**:
  - Unstrained pristine monolayer $\mathrm{CrCl}_3$ exhibits a direct band gap of **$1.58\ \mathrm{eV}$** (PBE).
  - Ground state is ferromagnetic with $M = 6.00\ \mu_{\mathrm{B}}$ per cell ($3\ \mu_{\mathrm{B}}/\mathrm{Cr}$).
  - In contrast to $\mathrm{CrI}_3$, the electronic band structure of $\mathrm{CrCl}_3$ is virtually unaffected by spin-orbit coupling (SOC).

---

### [3] Luo et al. (2020) — Monolayer Direct Gap Verification
- **Citation**: M. Luo, Y. D. Li, K. J. Wang, and Y. H. Shen, *"Adsorption induced magnetic anisotropy in the two-dimensional magnet $\mathrm{CrCl}_3$"*, *Solid State Communications* **321**, 114048 (2020).
- **DOI**: [10.1016/j.ssc.2020.114048](https://doi.org/10.1016/j.ssc.2020.114048)
- **Method**: VASP, PAW, GGA-PBE, $E_{\text{cut}} = 500\ \mathrm{eV}$, $10\times 10\times 1$ $k$-mesh, vacuum $20\ \text{\AA}$, fully relaxed ($a = 6.056\ \text{\AA}$, $\mathrm{Cr-Cl} = 2.352\ \text{\AA}$).
- **Key Findings**:
  - Pristine monolayer $\mathrm{CrCl}_3$ has a direct band gap of **$1.59\ \mathrm{eV}$** under standard PBE.

---

### [4] Gao et al. (2018) — Mechanism of Hubbard $+U$ Gap Opening
- **Citation**: Y. Gao, J. Wang, Y. Li, M. Xia, Z. Li, and F. Gao, *"Point-Defect-Induced Half Metal in $\mathrm{CrCl}_3$ Monolayer"*, *Physica Status Solidi (RRL)* **12**, 1800105 (2018).
- **DOI**: [10.1002/pssr.201800105](https://doi.org/10.1002/pssr.201800105)
- **Method**: VASP, PAW, GGA-PBE, DFT-D2, Dudarev GGA+$U$ ($U = 3.0 - 6.0\ \mathrm{eV}$).
- **Key Findings**:
  - Pristine PBE band gap is $\approx 1.6\ \mathrm{eV}$ between $\mathrm{Cr}\ t_{2g}$ spin-up and $\mathrm{Cr}\ e_g$ spin-up.
  - Applying Hubbard $+U$ ($U = 5.0\ \mathrm{eV}$) widens the band gap to **$2.2\ \mathrm{eV}$**.
  - **Physical mechanism**: On-site Coulomb repulsion pushes occupied $\mathrm{Cr}\ t_{2g}$ states downwards below the $\mathrm{Cl}\ 3p$ manifold, shifting the valence band maximum to $\mathrm{Cl}\ 3p$ and converting the system from a Mott/crystal-field insulator into a **charge-transfer insulator** ($\mathrm{Cl}\ 3p \to \mathrm{Cr}\ 3d$).

---

## 2. Reconciling Reviewer 4's Query

**Reviewer 4 Query**:
> *"The experimental band gap of $\mathrm{CrCl}_3$ is $\sim 3\ \mathrm{eV}$, whereas conventional PBE yields $\sim 1.5\ \mathrm{eV}$. Please justify your PBE baseline and clarify the effect of Coulomb repulsion."*

**Author Response Formula**:
1. **PBE Accuracy for the Visible Optical Threshold**:
   Conventional PBE calculates an electronic gap of $1.50\ \mathrm{eV}$ (this work), $1.58\ \mathrm{eV}$ [Webster 2018], $1.59\ \mathrm{eV}$ [Luo 2020], and $1.6\ \mathrm{eV}$ [Gao 2018]. This numerical range coincides directly with the **visible absorption threshold** ($1.5 - 1.7\ \mathrm{eV}$) measured experimentally in bulk $\mathrm{CrCl}_3$ by Dillon et al. (1966) and Pollini & Spinolo (1970).
2. **Crystal-Field vs. Fundamental Charge-Transfer Distinction**:
   As demonstrated by Pollini & Spinolo (1970) through photoconductivity spectroscopy, this visible absorption onset corresponds strictly to **localized intra-ionic $3d \to 3d$ crystal-field excitations** ($^4A_{2g} \to\ ^4T_{2g}$, peak at $1.68\ \mathrm{eV}$), yielding negligible photocurrents.
3. **The True Fundamental Gap at $3.2\ \mathrm{eV}$**:
   The genuine fundamental band gap that produces mobile charge carriers occurs at $(3.2 \pm 0.2)\ \mathrm{eV}$ (with $100\times$ higher photoconductivity yield), representing an interband charge-transfer process ($\mathrm{Cl}\ 3p \to \mathrm{Cr}\ 3d/4s$).
4. **The Role of Hubbard $+U$**:
   Due to known self-interaction error, standard PBE underestimates the energy of the occupied $\mathrm{Cr}\ 3d$ states, placing them artificially above or near the $\mathrm{Cl}\ 3p$ valence band. Incorporating on-site Coulomb repulsion ($U = 1 \dots 6\ \mathrm{eV}$) penalizes double occupancy on $\mathrm{Cr}\ 3d$, pushing the occupied $d$-manifold below the $\mathrm{Cl}\ 3p$ bands. Consequently, the band gap opens from $1.50\ \mathrm{eV}$ to $2.59\ \mathrm{eV}$ (relaxed) / $2.67\ \mathrm{eV}$ (static), bridging the gap toward the experimental fundamental charge-transfer threshold ($3.2\ \mathrm{eV}$) and restoring the proper charge-transfer insulator character.

---

## 3. Ready-to-Use BibTeX Entries

```bibtex
@article{Pollini1970,
  author    = {I. Pollini and G. Spinolo},
  title     = {Intrinsic Optical Properties of {CrCl}$_3$},
  journal   = {Physica Status Solidi (b)},
  volume    = {41},
  number    = {2},
  pages     = {691--701},
  year      = {1970},
  doi       = {10.1002/pssb.19700410224}
}

@article{Dillon1966,
  author    = {J. F. Dillon, Jr. and H. Kamimura and J. P. Remeika},
  title     = {Magneto-optical properties of ferromagnetic chromium trihalides},
  journal   = {Journal of Physics and Chemistry of Solids},
  volume    = {27},
  number    = {9},
  pages     = {1531--1549},
  year      = {1966},
  doi       = {10.1016/0022-3697(66)90148-X}
}

@article{Webster2018,
  author    = {Lucas Webster and Jia-An Yan},
  title     = {Strain-tunable magnetic anisotropy in monolayer {CrCl}$_3$, {CrBr}$_3$, and {CrI}$_3$},
  journal   = {Physical Review B},
  volume    = {98},
  number    = {14},
  pages     = {144411},
  year      = {2018},
  doi       = {10.1103/PhysRevB.98.144411}
}

@article{Luo2020,
  author    = {M. Luo and Y. D. Li and K. J. Wang and Y. H. Shen},
  title     = {Adsorption induced magnetic anisotropy in the two-dimensional magnet {CrCl}$_3$},
  journal   = {Solid State Communications},
  volume    = {321},
  pages     = {114048},
  year      = {2020},
  doi       = {10.1016/j.ssc.2020.114048}
}

@article{Gao2018,
  author    = {Yuan Gao and Jing Wang and Yan Li and Meirong Xia and Zhiping Li and Faming Gao},
  title     = {Point-Defect-Induced Half Metal in {CrCl}$_3$ Monolayer},
  journal   = {Physica Status Solidi (RRL) -- Rapid Research Letters},
  volume    = {12},
  number    = {6},
  pages     = {1800105},
  year      = {2018},
  doi       = {10.1002/pssr.201800105}
}
```

---

### [5] Dillon et al. (1966) — Foundation of Chromium Trihalide Magneto-Optics & Bulk Crystal Data
- **Citation**: J. F. Dillon, Jr., H. Kamimura, and J. P. Remeika, *"Magneto-optical properties of ferromagnetic chromium trihalides"*, *Journal of Physics and Chemistry of Solids* **27**(9), 1531–1549 (1966).
- **DOI**: [10.1016/0022-3697(66)90148-X](https://doi.org/10.1016/0022-3697(66)90148-X)
- **Key Findings**:
  - Established low-temperature $BiI_3$-type crystal structure ($R\bar{3}$) with hexagonal in-plane lattice parameter $a = 6.048\ \text{\AA}$.
  - Optical absorption spectrum exhibits intra-ionic $3d \to 3d$ crystal field transitions ($^4A_{2g} \to\ ^4T_{2g}$ at $1.68\ \mathrm{eV}$ and $^4A_{2g} \to\ ^4T_{1g}$ at $\sim 2.3\ \mathrm{eV}$).
  - Identified steep interband charge-transfer absorption onset ($\mathrm{Cl}\ 3p \to \mathrm{Cr}\ 3d$) above $3.0\ \mathrm{eV}$.
  - Demonstrates in-plane ferromagnetic coupling with weak antiferromagnetic inter-layer coupling ($T_N = 16.8\ \mathrm{K}$, $\theta = +40\ \mathrm{K}$).

---

### [6] Bedoya-Pinto et al. (Science 2021) — Experimental Realization of Monolayer CrCl3 & 2D-XY Physics
- **Citation**: A. Bedoya-Pinto, J.-R. Ji, A. Pandeya, P. Gargiani, M. Valvidares, P. Sessi, F. Radu, K. Chang, and S. S. P. Parkin, *"Intrinsic 2D-XY ferromagnetism in a van der Waals monolayer"*, *Science* **374**(6567), 616–620 (2021) / arXiv:2006.07605.
- **DOI**: [10.1126/science.abd5146](https://doi.org/10.1126/science.abd5146)
- **Key Findings**:
  - First experimental synthesis and proof of pristine monolayer $\mathrm{CrCl}_3$ via molecular beam epitaxy (MBE) on graphene/SiC(0001).
  - Unambiguously establishes that monolayer $\mathrm{CrCl}_3$ is an **intrinsic 2D-XY easy-plane ferromagnet**, undergoing a finite-size Berezinskii-Kosterlitz-Thouless (BKT) phase transition at $T_{\mathrm{BKT}} \approx 13\ \mathrm{K}$.
  - Magnetic easy plane lies strictly in the $xy$-plane (continuous $O(2)$ rotational symmetry) due to weak spin-orbit coupling of chlorine, contrasting with the out-of-plane Ising anisotropy of $\mathrm{CrI}_3$.
  - Atomic-resolution STM confirms honeycomb Cr sublattice with octahedral coordination to Cl atoms and clean van der Waals gap to the substrate.
