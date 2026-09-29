# Comprehensive Analysis: Cococcioni & de Gironcoli (2005)
## *A Linear Response Approach to the Calculation of the Effective Interaction Parameters in the LDA+U Method*
**Authors:** Matteo Cococcioni and Stefano de Gironcoli (*Phys. Rev. B* **71**, 035105, 2005 / arXiv:cond-mat/0405160)

---

## 1. Executive Summary & Foundational Motivation

Standard semi-local exchange-correlation approximations in Density Functional Theory (DFT)—such as the Local Spin Density Approximation (LSDA) and spin-polarized Generalized Gradient Approximations ($\sigma$-GGA)—systematically fail in transition metal oxides, 2D magnetic materials, and correlated systems. The primary symptom is severe underestimation of electronic bandgaps, often erroneously predicting metallic ground states for Mott and charge-transfer insulators (e.g., FeO, NiO, CrCl$_3$).

Historically, the on-site Coulomb interaction parameter $U$ in DFT+$U$ was treated semi-empirically by fitting $U$ to reproduce experimental bandgaps, photoemission spectra, or lattice parameters. Cococcioni and de Gironcoli established a rigorous, basis-set independent, **first-principles non-empirical framework** to calculate $U$ from the density-functional response of the system itself, eliminating all empirical parameter fitting.

---

## 2. Mathematical Derivation of the Linear Response Formulation

### 2.1 The Origin of Hubbard $U$: Spurious Self-Interaction & Energy Curvature

In an open physical system in contact with an electron reservoir, the exact ground-state energy $E(N)$ as a function of continuous particle number $N = N_0 + \omega$ ($0 \le \omega \le 1$) is strictly **piecewise linear** between integer electron counts (Perdew, Parr, Levy, & Balduz, 1982):

$$E(N) = (1 - \omega) E(N_0) + \omega E(N_0 + 1)$$

Consequently, the physical derivative discontinuity yields:

$$\frac{\partial^2 E^{\mathrm{exact}}}{\partial N^2} = 0 \quad (\text{except at integer boundaries})$$

Semi-local approximations (LDA/GGA) violate this condition due to the uncancelled self-interaction of partially occupied Kohn-Sham orbitals. The Hartree energy contains a spurious self-interaction that creates an unphysical convex curvature:

$$\frac{\partial^2 E^{\mathrm{LDA/GGA}}}{\partial N^2} > 0$$

The Hubbard $+U$ functional adds an energy penalty designed to cancel this spurious curvature:

$$E_U[\{n^{I\sigma}\}] = \frac{U}{2} \sum_{I, \sigma} \mathrm{Tr}\left[ n^{I\sigma} (1 - n^{I\sigma}) \right] = \frac{U}{2} \sum_{I, \sigma, i} \lambda_i^{I\sigma} (1 - \lambda_i^{I\sigma})$$

where $\lambda_i^{I\sigma} \in [0, 1]$ are the eigenvalues of the localized occupation matrix $n^{I\sigma}$. The Hubbard parameter $U$ is **identically defined as the unphysical curvature** of the approximate functional:

$$U \equiv \frac{\partial^2 E^{\mathrm{LDA/GGA}}}{\partial n_I^2}$$

When $U$ is set to this curvature, the $+U$ term exactly subtracts the spurious quadratic term, restoring piecewise linearity.

---

### 2.2 Constrained Density Functional Theory (cDFT) & Legendre Transformation

To compute the curvature of the total energy with respect to localized orbital occupation $q_I$, cDFT enforces constraints via Lagrange multipliers $\alpha_I$:

$$E[\{q_I\}] = \min_{n(\mathbf{r}), \alpha_I} \left\{ E[n(\mathbf{r})] + \sum_I \alpha_I (n_I - q_I) \right\}$$

Because constraining local occupations directly in plane-wave or grid codes is computationally prohibitive, a Legendre transformation passes to the unconstrained potential shift representation:

$$E[\{\alpha_I\}] = \min_{n(\mathbf{r})} \left\{ E[n(\mathbf{r})] + \sum_I \alpha_I n_I \right\}$$

Applying the Hellmann-Feynman theorem to the Legendre-transformed functional:

$$\frac{\partial E[\{\alpha_I\}]}{\partial \alpha_I} = n_I, \quad \frac{\partial E[\{q_I\}]}{\partial q_I} = -\alpha_I$$

$$\frac{\partial^2 E[\{q_I\}]}{\partial q_I^2} = -\frac{\partial \alpha_I}{\partial q_I}$$

---

### 2.3 Bare vs. Screened Linear Response Matrices

When an electron is localized on site $I$, the energy cost includes:
1. The on-site Coulomb penalty (the true Hubbard $U$).
2. The non-interacting Kohn-Sham band rehybridization curvature $\frac{\partial^2 E^{\mathrm{KS}}}{\partial q_I^2}$.

To isolate the electron-electron interaction, the non-interacting rehybridization curvature must be subtracted:

$$U = \frac{\partial^2 E}{\partial q_I^2} - \frac{\partial^2 E^{\mathrm{KS}}}{\partial q_I^2} = \left(-\frac{\partial \alpha_I}{\partial q_I}\right) - \left(-\frac{\partial \alpha_I^{\mathrm{KS}}}{\partial q_I}\right)$$

In terms of density-density response matrices:
- **Screened (Interacting) Response Matrix $\chi$**: Calculated by allowing the Kohn-Sham potential and charge density to relax self-consistently (SCF):
  $$\chi_{IJ} = \frac{\partial n_I}{\partial \alpha_J} = \frac{\partial^2 E}{\partial \alpha_I \partial \alpha_J}$$

- **Bare (Non-Interacting) Response Matrix $\chi_0$**: Calculated with frozen Kohn-Sham potential (non-SCF, single diagonalisation / `ICHARG=11` in VASP):
  $$\chi^0_{IJ} = \frac{\partial n_I}{\partial \alpha_J^0} = \frac{\partial^2 E^{\mathrm{KS}}}{\partial \alpha_I^0 \partial \alpha_J^0}$$

Using the matrix relation $\left(\frac{\partial \mathbf{q}}{\partial \boldsymbol{\alpha}}\right)^{-1} = \frac{\partial \boldsymbol{\alpha}}{\partial \mathbf{q}}$:

$$\mathbf{U}_{IJ} = \left( \boldsymbol{\chi}_0^{-1} - \boldsymbol{\chi}^{-1} \right)_{IJ}$$

For a single site $I$:

$$U = \chi_{0, II}^{-1} - \chi_{II}^{-1}$$

---

## 3. Supercell Scaling & Finite-Size Corrections

In periodic boundary conditions, perturbing a single site in a supercell coherently perturbs an infinite periodic array of image sites. The response $\chi$ therefore includes unwanted inter-image Coulomb interactions.

### 3.1 The $1/L^3$ Scaling Law

The electrostatic interaction between periodic dipolar/quadrupolar replicas decays with the supercell volume $\Omega \propto L^3$. The calculated Hubbard parameter scales asymptotically as:

$$U(L) = U_\infty + \frac{\gamma}{L^3}$$

where:
- $L$: Linear dimension of the supercell (or average inter-site distance).
- $U_\infty$: True isolated-defect Hubbard parameter (the physical limit).
- $\gamma$: System-dependent screening and dielectric constant coefficient.

For monolayer $\mathrm{CrCl}_3$:
- $1 \times 1$ ($L = 6.05\text{ \AA}$): $U = 4.09\text{ eV}$ (heavy replica screening error)
- $2 \times 2$ ($L = 12.10\text{ \AA}$): $U = 3.32\text{ eV}$
- $3 \times 3$ ($L = 18.15\text{ \AA}$): $U = 3.28\text{ eV}$
- $L \to \infty$ extrapolation: $U_\infty = 3.27\text{ eV}$

---

## 4. Implementation Protocol for VASP & SIESTA

### 4.1 VASP PAW Implementation Protocol
1. **Unperturbed Ground State**: Converge ground state at $\alpha = 0$ with `LMAXMIX = 4`, saving `CHGCAR` and `WAVECAR`.
2. **Species Splitting**: Split the target transition metal into a separate species in `POSCAR` and `POTCAR` (e.g., `Cr_pert` and `Cr`).
3. **Alpha Grid Perturbations**: Apply potential shifts $\alpha \in \{-0.08, -0.04, 0.00, +0.04, +0.08\}\text{ eV}$ via `LDAUTYPE = 3` or local potential operator.
4. **Bare Response ($\chi_0$)**: Execute with `ICHARG = 11` (non-SCF, 1 iteration) using ground-state `CHGCAR`. Extract localized occupations from `OUTCAR` (or `LDAUPRINT = 2`).
5. **Screened Response ($\chi$)**: Execute with `ICHARG = 1`, `ISTART = 1` (SCF convergence in ~5–8 steps). Extract relaxed occupations.
6. **Linear Regression & Inversion**:
   $$\chi_0 = \frac{dn_d^{\mathrm{bare}}}{d\alpha}, \quad \chi = \frac{dn_d^{\mathrm{screened}}}{d\alpha} \implies U = \frac{1}{|\chi_0|} - \frac{1}{|\chi|}$$

### 4.2 SIESTA Implementation Protocol
1. Employ Pulay mixing (`DM.MixingWeight 0.04`, `DM.NumberPulay 5`) to prevent charge sloshing.
2. Introduce local orbital shift on selected atom via synthetic pseudopotential or onsite projector operator.
3. Compute $\chi_0$ in single DM iteration and $\chi$ upon SCF convergence (`grep -q "End of run" run.log`).

---

## 5. Key Scientific Takeaways for Our Project

1. **Strictly Non-Empirical**: Cococcioni's method does not rely on experimental lattice constants, optical gaps, or literature fitting. It is an intrinsic electronic property of the chosen exchange-correlation functional and atomic projector basis.
2. **Basis Dependence**: Different projector definitions (e.g., pseudo-atomic orbitals vs. Wannier functions) yield different numerical values of $U$, but identically describe physical observables when applied consistently.
3. **Cross-Validation with Structural Benchmarks**:
   In our monolayer $\mathrm{CrCl}_3$ study:
   - Cococcioni linear response ($L \to \infty$): $U = 3.27\text{ eV}$
   - Independent structural benchmark ($a(U) = a_{\mathrm{exp}} = 6.056\text{ \AA}$): $U = 3.29\text{ eV}$
   The $< 1.5\%$ agreement is a rigorous cross-validation between structural and electronic observables.
