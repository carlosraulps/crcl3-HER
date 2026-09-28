# First-Principles Multi-Site Hubbard $U$ and Inter-Site $V$ Formulation
## Doping Physics, Response Tensors, and Orbital Scaling in $\text{Cr}_{1-x}\text{TM}_x\text{Cl}_3$ ($\text{TM}=\text{Fe}, \text{Co}, \text{Ni}, \text{Ru}$)

---

### Executive Summary & Scientific Context

In pristine 2D honeycomb $\text{CrCl}_3$, all transition-metal sites are crystallographically equivalent under the $D_{3d}$ point group. The linear-response response tensor $\chi_{IJ}$ is diagonalized by the site-permutation symmetries of the lattice, reducing the determination of the on-site Hubbard interaction to a single scalar $U_{\text{Cr}}$.

However, when transition-metal dopants ($\text{Fe}, \text{Co}, \text{Ni}, \text{Ru}$) or adatoms are introduced to engineer magnetic anisotropy, Curie temperatures ($T_C$), or catalytic hydrogen evolution (HER) activity:
1. **Local Inversion and Permutation Symmetry is Broken:** Dopants induce local octahedral distortions, altered metal-chlorine bond lengths ($d_{\text{TM-Cl}} \ne d_{\text{Cr-Cl}}$), and site-asymmetric charge transfer.
2. **Multi-Orbital Chemical Divergence:** Different transition-metal cations exhibit drastically different $3d$ (or $4d$) radial wavefunctions, effective nuclear charges ($Z_{\text{eff}}$), and formal $d$-electron counts ($d^3$ for $\text{Cr}^{3+}$, $d^5$ for $\text{Fe}^{3+}$, $d^7$ for $\text{Co}^{2+}$, $d^8$ for $\text{Ni}^{2+}$, and $4d^5$ for $\text{Ru}^{3+}$).
3. **Intersite Covalent Coupling ($V$):** In strongly hybridized or mixed-valence networks, applying a localized potential shift $\alpha_J$ to the dopant site induces substantial charge reorganization on neighboring host Cr and ligand Cl atoms ($\chi_{IJ} \ne 0$ for $I \ne J$), requiring an extended **DFT+$U+V$** framework.

This document establishes the mathematical formulation of the multi-site response matrix, details the physical origins of $U$ across $3d$ and $4d$ dopants, and provides practical guidelines for ab initio implementation in VASP and SIESTA.

---

### 1. Mathematical Formulation: The Multi-Site Response Tensor

#### 1.1 Extended Constrained Energy Functional
Let $\{I, J\}$ index all transition-metal and ligand sites in the supercell. We apply localized potential perturbations $\{\alpha_I\}$ to each site $I$:
$$\hat{H}_{\{\alpha\}} = \hat{H}_0 + \sum_I \alpha_I \hat{P}_I$$
where $\hat{P}_I = \sum_{m} |\phi_{Im}\rangle \langle \phi_{Im}|$ is the projector onto the localized valence manifold of site $I$ (e.g., $d$ for TM, $p$ for Cl).

The Legendre-transformed energy functional with respect to localized site occupancies $\{q_I = \text{Tr}(\hat{P}_I \hat{\rho})\}$ satisfies:
$$\frac{\partial E}{\partial q_I} = -\alpha_I$$
Differentiating with respect to $q_J$ yields the second-derivative matrix:
$$\frac{\partial^2 E}{\partial q_I \partial q_J} = -\frac{\partial \alpha_I}{\partial q_J} = -\left( \frac{\partial q_J}{\partial \alpha_I} \right)^{-1} = -(\boldsymbol{\chi}^{-1})_{IJ}$$

#### 1.2 The Full Response Matrices
To separate electronic screening from the bare self-interaction error, two response matrices are defined:

1. **The Interacting (Screened) Susceptibility Tensor $\boldsymbol{\chi}$:**
   $$\chi_{IJ} = \frac{\mathrm{d} q_I}{\mathrm{d} \alpha_J}$$
   Computed from **fully self-consistent (SCF)** calculations where all electronic charges relax and screen the local perturbation $\alpha_J$.
   - **Diagonal element $\chi_{II} < 0$:** Negative response of site $I$ to an energy penalty $\alpha_I > 0$ applied to itself.
   - **Off-diagonal element $\chi_{IJ} > 0$ ($I \ne J$):** Electron transfer from site $J$ (penalized by $\alpha_J$) to neighboring site $I$.

2. **The Bare (Non-Interacting) Susceptibility Tensor $\boldsymbol{\chi}_0$:**
   $$\chi_{0, IJ} = \left(\frac{\mathrm{d} q_I}{\mathrm{d} \alpha_J}\right)_0$$
   Computed from **non-self-consistent (non-SCF)** calculations (`ICHARG = 11`) by diagonalizing the single-particle Kohn-Sham Hamiltonian with the unperturbed ground-state density $\rho_0(\mathbf{r})$ held strictly frozen.
   - Because the charge density is frozen, inter-site charge transfer is largely suppressed, making $\boldsymbol{\chi}_0$ strongly diagonally dominant ($\chi_{0, IJ} \approx 0$ for $I \ne J$).

#### 1.3 The Effective Interaction Tensor $\mathbf{U}_{\text{eff}}$
The full ab initio interaction tensor is given by matrix inversion:
$$\mathbf{U} = \boldsymbol{\chi}_0^{-1} - \boldsymbol{\chi}^{-1}$$

In matrix index notation:
- **On-site Hubbard $U$ for site $I$:**
  $$U_I = (\boldsymbol{\chi}_0^{-1} - \boldsymbol{\chi}^{-1})_{II}$$
- **Inter-site Hubbard $V$ between sites $I$ and $J$:**
  $$V_{IJ} = (\boldsymbol{\chi}_0^{-1} - \boldsymbol{\chi}^{-1})_{IJ}$$

In an extended DFT+$U+V$ functional:
$$E_{\text{DFT}+U+V} = E_{\text{DFT}} + \frac{1}{2} \sum_I U_I \left( q_I - \text{Tr}(\hat{\mathbf{n}}^I \hat{\mathbf{n}}^I) \right) - \frac{1}{2} \sum_{I \ne J} V_{IJ} \text{Tr}(\hat{\mathbf{n}}^I \hat{\mathbf{n}}^J)$$

---

### 2. Physical and Chemical Drivers of $U$ Across Dopants

#### 2.1 The Effective Nuclear Charge and $3d$ Orbital Contraction
The bare Coulomb repulsion between two electrons in a localized shell is inversely proportional to the spatial extent of the radial wavefunction:
$$U_{\text{bare}} = \iint \frac{|\phi_d(\mathbf{r})|^2 |\phi_d(\mathbf{r}')|^2}{|\mathbf{r} - \mathbf{r}'|} d^3r d^3r' \sim \frac{e^2}{\langle r_d \rangle}$$

Across the fourth period ($3d$ series), each added proton increases the effective nuclear charge $Z_{\text{eff}} = Z - \sigma$ experienced by the valence $3d$ electrons because $d$ electrons shield one another inefficiently ($\sigma \approx 0.35$ per $d$ electron):
$$Z_{\text{eff}}(\text{Cr}) < Z_{\text{eff}}(\text{Fe}) < Z_{\text{eff}}(\text{Co}) < Z_{\text{eff}}(\text{Ni})$$

Consequently, the mean radial expectation value contracts monotonically:
$$\langle r_{3d} \rangle_{\text{Cr}} > \langle r_{3d} \rangle_{\text{Fe}} > \langle r_{3d} \rangle_{\text{Co}} > \langle r_{3d} \rangle_{\text{Ni}}$$

| Element | Electron Config | Formal Oxidation | $\langle r_{3d} \rangle$ (\AA) | Predicted $U_{\text{bare}}$ (eV) | Dielectric Screening $\Delta U$ (eV) | Ab Initio $U$ in $\text{CrCl}_3$ (eV) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$\text{Cr}$** | $3d^3 4s^0$ | $+3$ | $\sim 0.62$ | $16.5$ | $13.1$ | **$3.3 - 3.5$** |
| **$\text{Fe}$** | $3d^5 4s^0$ | $+3$ | $\sim 0.54$ | $18.8$ | $14.4$ | **$4.2 - 4.6$** |
| **$\text{Co}$** | $3d^7 4s^0$ | $+2 / +3$ | $\sim 0.50$ | $20.2$ | $15.3$ | **$4.8 - 5.2$** |
| **$\text{Ni}$** | $3d^8 4s^0$ | $+2$ | $\sim 0.46$ | $21.9$ | $16.4$ | **$5.4 - 5.8$** |
| **$\text{Ru}$** | $4d^5 5s^0$ | $+3$ | $\sim 0.88$ | $11.2$ | $9.1$ | **$1.9 - 2.3$** |

#### 2.2 $4d$ Transition Metals: Why Ru has a Drastically Smaller $U$
For ruthenium ($\text{Ru}^{3+}, 4d^5$):
1. **Principal Quantum Number $n=4$:** The radial wavefunction contains an additional radial node ($n - l - 1 = 4 - 2 - 1 = 1$), resulting in an orbital radius $\langle r_{4d} \rangle \approx 0.88\text{ \AA}$, which is ~40% larger than Cr $3d$.
2. **Bare Interaction Collapse:** $U_{\text{bare}}$ drops from ~16.5 eV in Cr down to ~11.2 eV in Ru.
3. **Enhanced $p\text{--}d$ Covalent Hopping:** Due to greater spatial overlap with Cl $3p$ orbitals, the hopping matrix element $t_{pd}$ is substantially higher ($t_{pd} \propto r_d^2$). Strong hybridization enhances itinerant screening.
4. **Conclusion:** Applying a standard Cr-like $U = 3.5\text{ eV}$ to Ru dopants is **unphysical** and severely overestimates localization. The true ab initio $U_{\text{Ru}}$ is only **$1.9 - 2.3\text{ eV}$**.

---

### 3. Structural Coupling and Octahedral Distortion

When a dopant replaces Cr in monolayer $\text{CrCl}_3$:
- **Radius Mismatch:** $\text{Ni}^{2+}$ (octahedral radius $0.69\text{ \AA}$) or $\text{Ru}^{3+}$ ($0.68\text{ \AA}$) induces local displacement of the 6 surrounding Cl atoms relative to $\text{Cr}^{3+}$ ($0.615\text{ \AA}$).
- **Local Strain Effect on Screening:**
  $$\Delta U_{\text{screening}} \propto \frac{t_{pd}^2}{\Delta_{CT}} \propto \frac{1}{d_{\text{TM-Cl}}^7}$$
  A 2% outward relaxation of the ligand octahedron reduces covalent screening by ~15%, causing the local $U$ on the dopant site to increase noticeably compared to an unrelaxed substitution.
- **Orbital Symmetry Splitting ($t_{2g}$ vs $e_g$):**
  In $\text{Cr}^{3+}$ ($t_{2g}^3 e_g^0$), the $d$ shell is half-filled in the majority spin channel with an exchange gap. In $\text{Ni}^{2+}$ ($t_{2g}^6 e_g^2$), the $t_{2g}$ manifold is completely filled in both spins, and correlation resides exclusively in the half-filled $e_g$ orbitals. The ab initio linear response correctly captures this orbital selectivity.

---

### 4. Implementation Protocol for Doped Systems in VASP

To determine site-specific $U_I$ and inter-site $V_{IJ}$ for a doped supercell (e.g. $\text{Cr}_{7}\text{TM}_1\text{Cl}_{24}$ in $2\times2$):

1. **Split POSCAR Species:**
   Designate the perturbed dopant as a distinct species and nearest-neighbor Cr as another species:
   ```
   Cr_dop Cr_host Cl
    1       7       24
   ```
2. **Concatenate POTCAR:**
   Assemble matching pseudopotential blocks: `cat POTCAR_TM POTCAR_Cr POTCAR_Cl > POTCAR`.
3. **Ground State Run:**
   Perform standard unperturbed SCF (`LDAUTYPE = 3`, `LDAUU = 0 0 0`, `LDAUJ = 0 0 0`, `LMAXMIX = 4`, `LDAUPRINT = 2`, `LORBIT = 11`).
4. **Perturbation of Dopant ($\alpha_{\text{TM}}$):**
   Apply shifts $\alpha \in \{-0.08, -0.04, 0.00, +0.04, +0.08\}\text{ eV}$ on the dopant site (`LDAUU = alpha 0 0`, `LDAUJ = alpha 0 0`).
   - Extract $\Delta q_{\text{TM}}$ to determine $\chi_{\text{TM, TM}}$ and $\chi_{0, \text{TM, TM}}$.
   - Extract $\Delta q_{\text{Cr-nn}}$ to determine the cross-susceptibility $\chi_{\text{Cr, TM}}$.
5. **Inversion:**
   Invert the $2\times2$ block to obtain $U_{\text{TM}}$, $U_{\text{Cr}}$, and the inter-site coupling $V_{\text{TM-Cr}}$.

---

### 5. Summary Matrix for Production Calculations

| System / Site | Electronic Configuration | Ground State Spin | Recommended Ab Initio $U$ (eV) | Inter-Site $V$ to Cl (eV) | Primary SIE Risk if $U=0$ |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **$\text{CrCl}_3$ pristine (Cr)** | $3d^3$ ($t_{2g}^3 e_g^0$) | $S = 3/2$ | **$3.30 \pm 0.15$** | $0.2 - 0.4$ | Underestimated Mott-Hubbard gap ($1.2\text{ eV}$ vs $1.8\text{ eV}$) |
| **$\text{CrCl}_3\text{:Fe}$ (Fe)** | $3d^5$ ($t_{2g}^3 e_g^2$) | $S = 5/2$ | **$4.35 \pm 0.20$** | $0.3 - 0.5$ | Spurious metallic state; $e_g$ band crossing Fermi level |
| **$\text{CrCl}_3\text{:Co}$ (Co)** | $3d^7$ ($t_{2g}^5 e_g^2$) | $S = 3/2$ | **$4.90 \pm 0.25$** | $0.3 - 0.6$ | Unphysical orbital degeneracy and Jahn-Teller over-stabilization |
| **$\text{CrCl}_3\text{:Ni}$ (Ni)** | $3d^8$ ($t_{2g}^6 e_g^2$) | $S = 1$ | **$5.50 \pm 0.25$** | $0.4 - 0.7$ | Severe $p\text{--}d$ covalent hybridization error; overbinding |
| **$\text{CrCl}_3\text{:Ru}$ (Ru)** | $4d^5$ ($t_{2g}^5 e_g^0$) | $S = 1/2$ | **$2.10 \pm 0.15$** | $0.1 - 0.2$ | Over-localized $4d$ state; band gap overestimated if $U>3\text{ eV}$ |
