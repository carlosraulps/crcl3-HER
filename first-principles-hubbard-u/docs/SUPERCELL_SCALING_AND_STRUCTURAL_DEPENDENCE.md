# Physical & Mathematical Foundations: Supercell Scaling, Structural Dependence, and Multi-Site Hubbard Parameters

**Authors**: Antigravity Materials Modeling & Theory Team  
**Focus**: Monolayer $\text{CrCl}_3$, Doped Derivatives ($\text{Cr}_{1-x}\text{TM}_x\text{Cl}_3$), and General 2D Correlated Systems  
**Date**: September 27, 2026  
**Repository Branch**: `master`

---

## 1. Physical Origin of the Hubbard Parameter: Why Does $U$ Depend on Structure?

A common misconception in condensed matter physics is that the Hubbard $U$ is an intrinsic, invariant property of an isolated chemical element (analogous to nuclear charge $Z$ or atomic mass). In reality:

$$U = U_{\text{bare}} - \Delta U_{\text{screening}}$$

where:
- **$U_{\text{bare}} \approx 15\text{–}25\text{ eV}$** is the bare Coulomb repulsion between two electrons in the isolated atomic $3d$ shell (the Slater integral $F^0$).
- **$\Delta U_{\text{screening}} \approx 12\text{–}21\text{ eV}$** is the dynamic polarization and dielectric screening provided by the surrounding valence electrons, ligand ions ($\text{Cl}^-$), and substrate.

Because $\Delta U_{\text{screening}}$ arises entirely from the dielectric and covalent environment, **$U$ is fundamentally a local material property that varies with structural geometry**:

### 1.1 The Role of Interatomic Distance & Covalent Hybridization
According to Harrison's and Slater-Koster hopping models, the covalent hybridization matrix element $t_{pd}$ between transition-metal $3d$ orbitals and ligand $p$ orbitals scales strongly with bond length $d$:
$$t_{pd} \propto \frac{1}{d^{3.5} \text{ to } d^4}$$

- **Under Compressive Strain / Shortened Cr–Cl Bonds**:
  - Cr($3d$)–Cl($3p$) orbital overlap increases dramatically.
  - Electrons delocalize more easily into the ligand cage.
  - Dielectric screening $\varepsilon_{\infty}$ increases.
  - **Result**: $\Delta U_{\text{screening}}$ increases, and the effective **$U$ decreases** ($U \sim 3.0\text{–}3.2\text{ eV}$).
- **Under Tensile Strain / Elongated Cr–Cl Bonds**:
  - Orbital overlap is quenched, narrowing the bandwidth $W$.
  - Covalent screening is suppressed.
  - **Result**: Electrons become more strongly localized, and the effective **$U$ increases** ($U \sim 3.8\text{–}4.2\text{ eV}$).

### 1.2 Dimensionality & Quantum Confinement (Bulk vs Monolayer)
In bulk 3D $\text{CrCl}_3$, an atom is screened isotropically by neighboring atomic planes in all three dimensions with an effective high-frequency dielectric constant $\varepsilon_{\text{bulk}} \approx 5.5$.

In a 2D monolayer $\text{CrCl}_3$, electric field lines between localized $d$-electrons escape into the vacuum above and below the slab ($\varepsilon_{\text{vacuum}} = 1$):
$$\varepsilon_{\text{2D}}(q) = 1 + 2\pi \alpha_{\text{2D}} q$$

Because dielectric screening is severely reduced at long wavelengths in 2D geometries:
$$U_{\text{monolayer}} > U_{\text{bilayer}} > U_{\text{bulk}}$$
For $\text{CrCl}_3$, this causes a systematic upward shift of $\Delta U \approx +0.3\text{ to } +0.5\text{ eV}$ when exfoliating bulk crystals down to the isolated monolayer limit.

### 1.3 Octahedral Crystal Field Distortion ($O_h \to D_{3d}$)
In monolayer $\text{CrCl}_3$, each $\text{Cr}^{3+}$ ion sits at the center of an edge-sharing $\text{CrCl}_6$ octahedron. Trigonal distortion splits the $O_h$ manifold:
- $t_{2g} \to a_{1g} + e_g^{\pi}$
- $e_g \to e_g^{\sigma}$

Because $t_{2g}$ orbitals point between the chlorine ligands (minimal $\pi$-antibonding) while $e_g$ orbitals point directly toward the $\text{Cl}^-$ ions ($\sigma$-antibonding), the local screening tensor is inherently anisotropic:
$$U_{mm'} = \chi_{0, mm'}^{-1} - \chi_{mm'}^{-1}$$
The standard Dudarev scalar $U_{\text{eff}} = U - J$ represents the spherically averaged trace across the five $d$-orbitals.

---

## 2. Mathematical Foundation of Supercell Scaling ($1\times1 \to 2\times2 \to 3\times3$)

Why does the calculated Cococcioni linear-response $U$ depend on supercell size, and why can it not be evaluated purely in a $1\times1$ primitive cell?

### 2.1 The Periodic Replica Perturbation Problem
In periodic DFT (plane-wave pseudopotentials), when a potential shift $\alpha_I$ is applied to an atom at position $\boldsymbol{\tau}_I$ in the unit cell, translational invariance enforces that **the perturbation is applied simultaneously to all periodic replicas** of atom $I$ across the Bravais lattice:
$$\hat{H}' = \hat{H}_0 + \alpha \sum_{\mathbf{R}} |\phi_{I, \mathbf{R}}\rangle \langle \phi_{I, \mathbf{R}}|$$

In reciprocal space, this corresponds strictly to a perturbation at the zone center ($\mathbf{q} = 0$):
$$\alpha(\mathbf{q}) = \alpha \delta(\mathbf{q})$$

The measured susceptibility $\chi_{\text{cell}}$ in a periodic cell of lattice vectors $\mathbf{R}$ is the sum over all inter-site response functions:
$$\chi_{\text{cell}} = \sum_{\mathbf{R}} \chi_{0\mathbf{R}} = \chi_{00} + \sum_{\mathbf{R} \ne 0} \chi_{0\mathbf{R}}$$

- **$\chi_{00}$ (On-Site Response)**: The true physical response of atom $0$ when only atom $0$ is perturbed and surrounding atoms screen the charge. This is the quantity required to define the atomic Hubbard parameter $U$.
- **$\sum_{\mathbf{R} \ne 0} \chi_{0\mathbf{R}}$ (Inter-Site Image Artifact)**: The spurious charge transfer and electrostatic interaction between atom $0$ and its periodic image replicas at distance $|\mathbf{R}|$.

### 2.2 Supercell Convergence Hierarchy
| Supercell | Lattice Vectors | Nearest-Image Distance $d_{\text{image}}$ | Inter-Image Coupling | Physical Reliability |
| :--- | :---: | :---: | :---: | :--- |
| **$1\times1$ Primitive** | $a = 6.05\text{ \AA}$ | $6.05\text{ \AA}$ | **Very Strong** ($\sim 30\text{–}40\%$ error) | **Qualitative only**. Perturbs entire sublattice uniformly; artificial Fermi-level shifts dominate. |
| **$2\times2$ Supercell** | $2a = 12.09\text{ \AA}$ | $12.09\text{ \AA}$ | **Weak** ($< 8\%$ error) | **Semi-quantitative / Standard Benchmark**. Inter-image interaction drops by $(1/2)^3 = 12.5\%$. |
| **$3\times3$ Supercell** | $3a = 18.14\text{ \AA}$ | $18.14\text{ \AA}$ | **Negligible** ($< 2\%$ error) | **Fully Asymptotic**. Isolated atomic limit reached within electronic convergence error. |

### 2.3 Finite-Size Scaling & Analytical Extrapolation
Because electrostatic interactions between neutral cells decay with dipolar/quadrupolar power laws:
$$\chi(L) = \chi_{\infty} + \frac{B}{L^3}$$
$$U(L) = U_{\infty} + \frac{C}{L^3}$$

By calculating $U(1\times1)$ and $U(2\times2)$, one can perform a two-point linear extrapolation versus $1/L^3$ to obtain the exact macroscopic limit $U_{\infty}$:
$$U_{\infty} = \frac{8 U(2\times2) - U(1\times1)}{7}$$

---

## 3. Transition Metal Doping & Multi-Manifold Linear Response ($\text{Cr}_{1-x}\text{TM}_x\text{Cl}_3$)

When single-atom transition metal dopants or adatoms ($\text{TM} = \text{Fe}, \text{Co}, \text{Ni}, \text{Ru}$) are introduced into the $\text{CrCl}_3$ lattice, the single-parameter approximation breaks down.

### 3.1 The Coupled Multi-Site Response Tensor
Each distinct chemical species $I$ possesses a unique orbital manifold with its own independent susceptibility:
$$\begin{pmatrix} \Delta q_{\text{Cr}} \\ \Delta q_{\text{TM}} \end{pmatrix} = \begin{pmatrix} \chi_{\text{Cr-Cr}} & \chi_{\text{Cr-TM}} \\ \chi_{\text{TM-Cr}} & \chi_{\text{TM-TM}} \end{pmatrix} \begin{pmatrix} \alpha_{\text{Cr}} \\ \alpha_{\text{TM}} \end{pmatrix}$$

Inverting both the bare ($\boldsymbol{\chi}_0$) and screened ($\boldsymbol{\chi}$) response matrices yields the full **DFT+$U+V$ Coulomb interaction matrix**:
$$\mathbf{U}_{\text{eff}} = \boldsymbol{\chi}_0^{-1} - \boldsymbol{\chi}^{-1} = \begin{pmatrix} U_{\text{Cr}} & V_{\text{Cr-TM}} \\ V_{\text{TM-Cr}} & U_{\text{TM}} \end{pmatrix}$$

- **Diagonal Terms ($U_{\text{Cr}}, U_{\text{TM}}$)**: On-site Hubbard corrections for Cr $3d$ and TM $3d$.
- **Off-Diagonal Terms ($V_{\text{Cr-TM}}$)**: Inter-site Coulomb interactions accounting for non-local $p\text{–}d$ or $d\text{–}d$ charge transfer.

### 3.2 Expected $U$ Values Across the $3d$ Transition Metal Series
From atomic physics, the effective nuclear charge $Z_{\text{eff}}$ experienced by the $3d$ valence shell increases monotonically across the $3d$ series: $\text{Cr} (3d^3) \to \text{Fe} (3d^6) \to \text{Co} (3d^7) \to \text{Ni} (3d^8)$. This contracts the $3d$ radial wavefunctions $R_{3d}(r)$, sharply increasing on-site Coulomb localization:

$$U(\text{Cr}) < U(\text{Fe}) \approx U(\text{Co}) < U(\text{Ni})$$

- **$\text{Cr}^{3+}$ ($3d^3$, Octahedral High-Spin)**: $U_{\text{eff}} \approx \mathbf{3.3\text{–}3.8\text{ eV}}$
- **$\text{Fe}^{2+/3+}$ ($3d^5/3d^6$)**: $U_{\text{eff}} \approx \mathbf{3.8\text{–}4.3\text{ eV}}$
- **$\text{Co}^{2+}$ ($3d^7$)**: $U_{\text{eff}} \approx \mathbf{3.5\text{–}4.0\text{ eV}}$
- **$\text{Ni}^{2+}$ ($3d^8$)**: $U_{\text{eff}} \approx \mathbf{5.0\text{–}5.5\text{ eV}}$
- **$4d$ / $5d$ Elements ($\text{Ru}, \text{Ir}$)**: Significantly more diffuse $4d/5d$ orbitals yield much lower Hubbard corrections: $U_{\text{Ru}} \approx \mathbf{1.2\text{–}1.8\text{ eV}}$.

---

## 4. Self-Consistent Outer Loop Protocol (Kulik–Marzari Method)

1. **Step $k=0$**: Start with standard semi-local PBE ($U_{\text{in}}^{(0)} = 0.0\text{ eV}$).
2. **Perturbation Scan**: Compute bare ($\chi_0^{(k)}$) and screened ($\chi^{(k)}$) linear response.
3. **Inversion**: Calculate output parameter $U_{\text{out}}^{(k)} = (\chi_0^{(k)})^{-1} - (\chi^{(k)})^{-1}$.
4. **Convergence Check**: If $|U_{\text{out}}^{(k)} - U_{\text{in}}^{(k)}| < 10^{-3}\text{ eV}$, terminate with converged $U_{\text{scf}}$.
5. **Damping & Update**:
   $$U_{\text{in}}^{(k+1)} = (1 - \beta) U_{\text{in}}^{(k)} + \beta U_{\text{out}}^{(k)} \quad (\beta \approx 0.60)$$
6. **Repeat**: Perform DFT+$U_{\text{in}}^{(k+1)}$ ground-state calculation and re-evaluate linear response until convergence.
