# Cococcioni Self-Consistent Linear Response Test Cases: Pristine Monolayer $\text{CrCl}_3$

This directory contains benchmark test cases for determining the self-consistent Hubbard $U$ parameter for pristine monolayer $\text{CrCl}_3$ using the linear response approach of Cococcioni & de Gironcoli (*Phys. Rev. B* **71**, 035105, 2005) and the self-consistent feedback scheme of Kulik et al. (*Phys. Rev. Lett.* **97**, 103001, 2006).

---

## Directory Structure

```text
u-a-scf/test_case_crcl3/
├── 1x1_primitive/
│   ├── POSCAR           # Primitive cell (2 Cr, 6 Cl atoms, a = 6.046 Å)
│   ├── KPOINTS          # Gamma-centered 4x4x1 mesh
│   ├── INCAR.template   # VASP template with accurate settings & lorbit
│   └── run_1x1_test.sh  # Automated dry-run and launcher script
├── 2x2_supercell/
│   ├── POSCAR           # 2x2 supercell (8 Cr, 24 Cl atoms, a = 12.093 Å)
│   ├── KPOINTS          # Gamma-centered 3x3x1 mesh
│   ├── INCAR.template   # VASP template
│   └── run_2x2_test.sh  # Automated dry-run and launcher script
└── README.md            # This documentation
```

---

## Physical Background & Methodology

### 1. Inversion of the Response Matrices
The effective Hubbard interaction parameter $U$ is extracted from the difference between the bare (unscreened, non-SCF) susceptibility $\chi_0$ and the interacting (screened, SCF) susceptibility $\chi$:

$$U = \chi_0^{-1} - \chi^{-1} = \left(\frac{\partial n_I}{\partial \alpha_I}\right)_{0}^{-1} - \left(\frac{\partial n_I}{\partial \alpha_I}\right)^{-1}$$

where $\alpha_I$ is a local potential perturbation applied to the localized manifold (Cr $3d$, $l=2$) of target atom $I$, and $n_I$ is the trace of the on-site $d$-electron occupation matrix ($n_I = \sum_{m} n_{mm}^{I}$).

### 2. Finite-Size Scaling & Supercell Extrapolation
In periodic boundary calculations, a localized perturbation on site $I$ in a supercell of parameter $L$ interacts with its periodic images through the long-range dipolar and electrostatic response of the medium. The calculated $U(L)$ follows the universal scaling law:

$$U(L) = U_{\infty} - \frac{c}{L^3}$$

- **Primitive $1\times1$ ($L \approx 6.05\text{ Å}$)**: Highly computationally affordable ($\approx 8$ atoms), ideal for rapid verification of the linear response slopes and preliminary $U$ estimation ($U_{1\times1} \sim 3.0\text{–}3.1\text{ eV}$).
- **Supercell $2\times2$ ($L \approx 12.09\text{ Å}$)**: Minimizes spurious image interaction down to $< 0.1\text{ eV}$, yielding a converged bulk-limit value ($U_{2\times2} \approx 3.25\text{–}3.29\text{ eV}$).

### 3. VASP Technical Implementation
- **Species Splitting**: VASP requires the perturbed Cr atom to be distinguished in the `POSCAR` and `POTCAR` as a separate chemical species (e.g. `Cr1  Cr  Cl`), enabling `LDAUU` and `LDAUJ` to be tuned selectively on atom 1.
- **Bare Response ($\chi_0$)**: Executed with `ICHARG = 11`, `NELM = 1` reading the self-consistent `CHGCAR` of the unperturbed ground state.
- **Interacting Response ($\chi$)**: Executed with full self-consistency (`ICHARG = 2`, `NELM = 100`).
- **Occupation Tracking**: Extracted from the `LDAUPRINT = 2` block in `OUTCAR`.

---

## Quick Execution

### Dry Run (Input Verification)
To generate the perturbation grid and verify POSCAR splitting without submitting Slurm jobs:

```bash
cd u-a-scf/test_case_crcl3/1x1_primitive
./run_1x1_test.sh
```

### HPC Cluster Dispatch
To run on the Huk cluster:

```bash
# In 1x1 primitive cell
bash ../../scripts/run_u_scf_vasp.sh \
    --poscar POSCAR \
    --target-site 1 \
    --cluster huk \
    --partition "alto,medio,normal" \
    --tol 0.005

# In 2x2 supercell
bash ../../scripts/run_u_scf_vasp.sh \
    --poscar ../2x2_supercell/POSCAR \
    --target-site 1 \
    --cluster huk \
    --partition alto \
    --tol 0.005
```
