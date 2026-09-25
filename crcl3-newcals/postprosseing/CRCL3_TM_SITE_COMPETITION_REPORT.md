# Transition Metal Adsorption and Site Competition on Monolayer $\text{CrCl}_3$
## Comparative Study: Cobalt ($\text{Co}$), Iron ($\text{Fe}$), Nickel ($\text{Ni}$) on $2\times2$ Supercells

**Methodology:**
- Substrate: Monolayer $\text{CrCl}_3$ ($2\times2\times1$ supercell, 8 Cr + 24 Cl atoms, $20$ Å vacuum box).
- Functionals: Pure GGA-PBE vs. PBE + Grimme DFT-D3 with Becke-Johnson damping (`IVDW=12`).
- Binding Energy definition: $\Delta E_{\mathrm{bind}} = E_{\mathrm{slab+TM}} - E_{\mathrm{clean}}$ (eV).
- Ground state reference: $\Delta E_{\mathrm{rel}} = \Delta E_{\mathrm{bind}} - \min(\Delta E_{\mathrm{bind}})$.

---

### 1. Energetics Summary Table

| TM Adatom | Functional | Site Key | Site Description | $E_{\mathrm{clean}}$ (eV) | $E_{\mathrm{tot}}$ (eV) | Binding $\Delta E$ (eV) | Relative Penalty (eV) | Total Mag ($\mu_B$) | Ionic Steps |
|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Co** (Cobalt) | Pure PBE | S1 | Site 1 (Top-Cl) | -156.2868 | -161.0147 | **-4.728** | **GROUND STATE** | 23.00 | 83 |
| **Co** (Cobalt) | Pure PBE | S2 | Site 2 (Hollow) | -156.2868 | -161.0131 | **-4.726** | +0.002 eV | 23.00 | 12 |
| **Co** (Cobalt) | Pure PBE | S3 | Site 3 (Top-Cr) | -156.2868 | -160.3660 | **-4.079** | +0.649 eV | 23.00 | 27 |
| **Co** (Cobalt) | PBE+D3 (BJ) | S1 | Site 1 (Top-Cl) | -162.1068 | -166.9422 | **-4.835** | +0.222 eV | 27.00 | 75 |
| **Co** (Cobalt) | PBE+D3 (BJ) | S2 | Site 2 (Hollow) | -162.1068 | -167.1637 | **-5.057** | **GROUND STATE** | 23.00 | 12 |
| **Co** (Cobalt) | PBE+D3 (BJ) | S3 | Site 3 (Top-Cr) | -162.1068 | -166.4536 | **-4.347** | +0.710 eV | 23.00 | 42 |
| **Fe** (Iron) | Pure PBE | S1 | Site 1 (Top-Cl) | -156.2868 | -161.9051 | **-5.618** | +0.715 eV | 28.41 | 81 |
| **Fe** (Iron) | Pure PBE | S2 | Site 2 (Hollow) | -156.2868 | -162.6198 | **-6.333** | **GROUND STATE** | 28.44 | 54 |
| **Fe** (Iron) | Pure PBE | S3 | Site 3 (Top-Cr) | -156.2868 | -161.3136 | **-5.027** | +1.306 eV | 21.65 | 25 |
| **Fe** (Iron) | PBE+D3 (BJ) | S1 | Site 1 (Top-Cl) | -162.1068 | -168.9135 | **-6.807** | **GROUND STATE** | 22.00 | 92 |
| **Fe** (Iron) | PBE+D3 (BJ) | S2 | Site 2 (Hollow) | -162.1068 | -168.1160 | **-6.009** | +0.797 eV | 28.39 | 19 |
| **Fe** (Iron) | PBE+D3 (BJ) | S3 | Site 3 (Top-Cr) | -162.1068 | -165.9127 | **-3.806** | +3.001 eV | 24.18 | 31 |
| **Ni** (Nickel) | Pure PBE | S1 | Site 1 (Top-Cl) | -156.2868 | -159.7885 | **-3.502** | +0.290 eV | 24.00 | 76 |
| **Ni** (Nickel) | Pure PBE | S2 | Site 2 (Hollow) | -156.2868 | -160.0785 | **-3.792** | **GROUND STATE** | 24.00 | 16 |
| **Ni** (Nickel) | Pure PBE | S3 | Site 3 (Top-Cr) | -156.2868 | -159.2846 | **-2.998** | +0.794 eV | 24.00 | 12 |
| **Ni** (Nickel) | PBE+D3 (BJ) | S1 | Site 1 (Top-Cl) | -162.1068 | -165.9142 | **-3.807** | +0.392 eV | 24.00 | 33 |
| **Ni** (Nickel) | PBE+D3 (BJ) | S2 | Site 2 (Hollow) | -162.1068 | -166.3062 | **-4.199** | **GROUND STATE** | 24.00 | 16 |
| **Ni** (Nickel) | PBE+D3 (BJ) | S3 | Site 3 (Top-Cr) | -162.1068 | -165.2844 | **-3.178** | +1.022 eV | 24.00 | 20 |

---

### 2. Physical & Mechanistic Discussion

1. **Nickel ($\text{Ni}$): Definite Hollow-Site Stabilization**
   - For Ni, the **Hollow site ($S_2$)** is the unambiguous thermodynamic ground state in both Pure PBE ($\Delta E = -3.792\text{ eV}$) and PBE+D3 ($\Delta E = -4.199\text{ eV}$).
   - The Hollow site provides symmetric threefold coordination to the basal chlorine atoms with moderate penetration into the hollow cavity, stabilizing Ni by $0.29\text{ eV}$ (PBE) and $0.40\text{ eV}$ (PBE+D3) over the Top-Cl site ($S_1$).
   - The total magnetic moment remains constant at $24.00\,\mu_B$ across all sites, indicating low-spin or paired $d^8$ configuration with negligible net spin perturbation to the ferromagnetic CrCl$_3$ background ($8\times 3\,\mu_B$).

2. **Cobalt ($\text{Co}$): Dispersion-Induced Site Inversion**
   - In Pure PBE, Top-Cl ($S_1$, $-4.728\text{ eV}$) and Hollow ($S_2$, $-4.726\text{ eV}$) are essentially isoenergetic (energy difference $< 2\text{ meV}$).
   - Inclusion of Grimme DFT-D3 (BJ) dispersion stabilizes the hollow coordination by an additional $-0.33\text{ eV}$, establishing **Hollow ($S_2$, $\Delta E = -5.057\text{ eV}$)** as the true ground state over Top-Cl ($-4.835\text{ eV}$).
   - The magnetic moment for Co on Hollow and Top-Cr is $23.00\,\mu_B$ (antiferromagnetic alignment of Co $3d$ electron with the Cr substrate), whereas at Top-Cl in PBE+D3 it polarizes ferromagnetically to $27.00\,\mu_B$.

3. **Iron ($\text{Fe}$): Strongest Adsorption & Spin Transition**
   - Fe exhibits the highest binding energy among all three $3d$ transition metals, exceeding $-6.8\text{ eV}$ at Top-Cl under PBE+D3 (BJ).
   - In Pure PBE, the Hollow site ($S_2$) is the ground state with $\Delta E = -6.333\text{ eV}$ and $M = 28.44\,\mu_B$ ($+4\,\mu_B$ high-spin Fe contribution).
   - Under PBE+D3 (BJ), Top-Cl ($S_1$) undergoes a collective relaxation yielding a deep thermodynamic minimum of **$\Delta E = -6.807\text{ eV}$** with $M = 22.00\,\mu_B$, reflecting strong spin-reorganization and hybridization with the ligand chlorine.

4. **Universal Avoidance of Top-Cr ($S_3$):**
   - For all three transition metals, Site 3 (Top-Cr) is consistently the least favorable position, with an energetic penalty of $+0.65\text{ to } +3.00\text{ eV}$ relative to the ground state.
   - This is physically driven by strong electrostatic repulsion and core Pauli exclusion between the approaching $3d$ transition metal cation and the underlying high-spin $\text{Cr}^{3+}$ ($t_{2g}^3$) center.
