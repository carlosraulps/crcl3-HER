# CrCl3 (2x2) Monolayer: Co, Fe, Ni Adsorbed and Embedded Structures

This package contains fully relaxed DFT geometries (`CONTCAR`, `POSCAR`, `.cif`, `.xyz`) calculated under:
- **Exchange-Correlation:** GGA-PBE
- **Van der Waals:** DFT-D3 with Becke-Johnson damping (`IVDW = 12`)
- **Hubbard U:** Dudarev rotationally invariant DFT+U with $U_{\mathrm{Cr}} = 3.29\text{ eV}$ ($U_{\mathrm{eff}} = 3.29\text{ eV}, J = 0\text{ eV}$)

Prepared for **Zero-Point Energy (ZPE)** and vibrational entropy ($-T\Delta S$) calculation benchmarking for the Hydrogen Evolution Reaction (HER).

---

## Recommended VASP INCAR Settings for Vibrational Calculations (ZPE)

To compute $\Gamma$-point vibrational modes for the adsorbed hydrogen atom and coordinating active site:

```ini
# Frequency Calculation Setup
IBRION = 5              # Finite differences displacement method
NFREE  = 2              # Central differences (+- displacements along x, y, z)
POTIM  = 0.015          # Step size (0.015 A is standard for light H atoms)
NSW    = 1              # Single ionic step for numerical Hessian evaluation

# Electronic Precision (Strict convergence needed for accurate forces)
EDIFF  = 1E-8           # Tight electronic tolerance for force gradients
PREC   = Accurate
ISMEAR = 0; SIGMA = 0.02

# Hubbard U (Matching geometry optimization)
LDAU   = .TRUE.
LDAUTYPE = 2
LDAUL  = 2 -1 -1        # d-orbitals for Cr; -1 for Cl and H
LDAUU  = 3.29 0.00 0.00
LDAUJ  = 0.00 0.00 0.00
LMAXMIX = 4

# Dispersion
IVDW   = 12             # DFT-D3 (BJ)
```

> **Computational Efficiency Tip:**
> In `POSCAR`, enable **Selective Dynamics** and freeze the distant substrate atoms (`F F F`), while allowing only the adsorbed **H atom** (and optionally the active transition-metal adatom/dopant and nearest Cl ligands) to vibrate (`T T T`). This calculates the 3 local vibrational frequencies of the H adsorbate ($\nu_{\mathrm{stretch}}$, $\nu_{\mathrm{bend},1}$, $\nu_{\mathrm{bend},2}$) in ~6 displacements rather than hundreds of displacements for the whole 33-atom slab!

---

## Structure Manifest & Directory Map

| Category | Metal / Substrate | Subtype / Site | Directory Path | Description |
| :--- | :--- | :--- | :--- | :--- |
| **embedded** | Co | clean | `embedded/Co/clean/` | Interstitial pore embedded Co (Clean slab, $E_0 = -152.684\text{ eV}$) |
| **embedded** | Co | H_ads | `embedded/Co/H_ads/` | Interstitial pore embedded Co with adsorbed H ($E_0 = -154.963\text{ eV}$) |
| **embedded** | Fe | clean | `embedded/Fe/clean/` | Interstitial pore embedded Fe (Clean slab, $E_0 = -154.080\text{ eV}$) |
| **embedded** | Fe | H_ads | `embedded/Fe/H_ads/` | Interstitial pore embedded Fe with adsorbed H ($E_0 = -156.629\text{ eV}$) |
| **embedded** | Ni | clean | `embedded/Ni/clean/` | Interstitial pore embedded Ni (Clean slab, $E_0 = -151.218\text{ eV}$) |
| **embedded** | Ni | H_ads | `embedded/Ni/H_ads/` | Interstitial pore embedded Ni with adsorbed H ($E_0 = -153.979\text{ eV}$) |
| **adsorbed** | Co | clean_S1_topCl | `adsorbed/Co/clean_S1_topCl/` | Co adsorbed at Site S1 (Top-Cl, $E_0 = -152.444\text{ eV}$) |
| **adsorbed** | Co | clean_S2_hollow | `adsorbed/Co/clean_S2_hollow/` | Co adsorbed at Site S2 (Hollow, $E_0 = -152.368\text{ eV}$) |
| **adsorbed** | Co | clean_S3_topCr | `adsorbed/Co/clean_S3_topCr/` | Co adsorbed at Site S3 (Top-Cr, $E_0 = -151.773\text{ eV}$) |
| **adsorbed** | Co | H_ads_S3 | `adsorbed/Co/H_ads_S3/` | **Ground-state active site:** Co at S3 with H ($E_0 = -155.463\text{ eV}, \Delta G = -0.069\text{ eV}$) |
| **adsorbed** | Fe | clean_S1_pore_GS | `adsorbed/Fe/clean_S1_pore_penetrated_GS/` | **Ground state:** Fe relaxed into interstitial pore ($E_0 = -154.834\text{ eV}$) |
| **adsorbed** | Fe | clean_S2_hollow | `adsorbed/Fe/clean_S2_hollow/` | Fe adsorbed at Site S2 hollow ($E_0 = -153.430\text{ eV}$) |
| **adsorbed** | Fe | clean_S3_topCr | `adsorbed/Fe/clean_S3_topCr/` | Fe adsorbed at Site S3 top-Cr ($E_0 = -152.932\text{ eV}$) |
| **adsorbed** | Fe | H_ads_pbe_ref | `adsorbed/Fe/H_ads_pbe_reference/` | Fe adsorbed with H (Pure PBE relaxed reference geometry) |
| **adsorbed** | Ni | clean_S1_topCl | `adsorbed/Ni/clean_S1_topCl/` | Ni adsorbed at Site S1 ($E_0 = -151.461\text{ eV}$) |
| **adsorbed** | Ni | clean_S2_hollow_GS | `adsorbed/Ni/clean_S2_hollow_GS/` | **Ground state:** Ni adsorbed at Site S2 hollow ($E_0 = -151.676\text{ eV}$) |
| **adsorbed** | Ni | clean_S3_topCr | `adsorbed/Ni/clean_S3_topCr/` | Ni adsorbed at Site S3 top-Cr ($E_0 = -150.752\text{ eV}$) |
| **adsorbed** | Ni | H_ads_pbe_ref | `adsorbed/Ni/H_ads_pbe_reference/` | Ni adsorbed with H (Pure PBE relaxed reference geometry) |
| **pristine** | substrate | clean_2x2 | `pristine/substrate/clean_2x2/` | Pristine 2x2 monolayer CrCl3 without dopants ($E_0 = -147.304\text{ eV}$) |
| **pristine** | substrate | H_ads_S1_topCl | `pristine/substrate/H_ads_S1_topCl/` | Pristine CrCl3 + H at Site S1 (Top-Cl adduct, $E_0 = -149.769\text{ eV}$) |
| **pristine** | substrate | H_ads_S2_hollow | `pristine/substrate/H_ads_S2_hollow/` | Pristine CrCl3 + H at Site S2 (Hollow, $E_0 = -148.861\text{ eV}$) |
| **pristine** | substrate | H_ads_S3_topCr | `pristine/substrate/H_ads_S3_topCr/` | Pristine CrCl3 + H at Site S3 (Top-Cr, $E_0 = -148.508\text{ eV}$) |
| **gas_ref** | H2 | H2_molecule | `gas_reference/H2/H2_molecule/` | Isolated H2 molecule in 20 A box ($E_0 = -6.762\text{ eV}$) |
