# VASP + LOBSTER HER Catalysis Results Summary

This document summarizes the energetics, d-band centers, and Hydrogen Evolution Reaction (HER) catalytic descriptors for transition metal (Co, Fe, Ni) functionalized monolayer $\text{CrCl}_3$ systems in both adsorbed and embedded configurations.

---

## 1. Energetics and Catalytic Descriptors Table

Below are the calculated total energies, $d$-band centers, and hydrogen adsorption free energies ($\Delta G_{\text{H}}$) at 298.15 K:

$$\Delta E_{\text{H}} = E(\text{doped-H}) - E(\text{doped}) - \frac{1}{2} E(\text{H}_2)$$

$$\Delta G_{\text{H}} = \Delta E_{\text{H}} + 0.24\text{ eV}$$

where $E(\text{H}_2) = -6.75965\text{ eV}$ ($\frac{1}{2} E(\text{H}_2) = -3.37983\text{ eV}$).

| Configuration | $E_{\text{doped}}$ (eV) | $E_{\text{doped-H}}$ (eV) | $\Delta E_{\text{H}}$ (eV) | $\Delta G_{\text{H}}$ (eV) | $d$-Band Center, $\varepsilon_d$ (eV) | Max Force (eV/Å) | Cell Magnetization ($\mu_B$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **adsorbed/Co** | -160.03807 | -163.47951 | -0.0616 | **+0.1784** | -1.6643 | 0.0181 | 24.00 |
| **adsorbed/Fe** | -161.19838 | -164.44318 | +0.1350 | **+0.3750** | -2.4319 | 0.0182 | 28.42 |
| **adsorbed/Ni** | -159.47084 | -162.22846 | +0.6222 | **+0.8622** | -1.1599 | 0.0222 | 25.00 |
| **embedded/Co** | -160.76289 | -162.64645 | +1.4963 | **+1.7363** | -1.4597 | 0.0202 | 24.00 |
| **embedded/Fe** | -162.04713 | -164.33853 | +1.0884 | **+1.3284** | -2.4376 | 0.0240 | 27.37 |
| **embedded/Ni** | -159.30521 | -161.03735 | +1.6477 | **+1.8877** | -1.6972 | 0.0224 | 25.00 |

---

## 2. Description of the Descriptor Plot

The descriptor plot correlates the electronic structure of the active site ($d$-band center, $\varepsilon_d$) with the adsorption strength of hydrogen ($\Delta G_{\text{H}}$):

1. **d-Band Center Integration**: The $d$-band center ($\varepsilon_d$) of the transition metal dopants is integrated from the projected density of states (PDOS) in the VASP `vasprun.xml` files, using only the states up to the Fermi level ($E - E_{\text{F}} \le 0$). This captures the occupancy and energy distribution of the bonding states.
2. **Ideal HER Active Window**: The green-shaded area highlights the ideal region for HER activity ($\Delta G_{\text{H}}$ between $-0.1$ and $+0.2$ eV). According to the Sabatier principle, an optimal catalyst must bind intermediate H strongly enough to initiate proton transfer, but weakly enough to facilitate $\text{H}_2$ desorption.
3. **Scaling Relations**:
   - **Adsorbed Configuration**: Fits a linear correlation curve ($R^2 = 0.362$) where the cobalt candidate lies closest to the ideal HER catalytic active window ($\Delta G_{\text{H}} = +0.178$ eV), suggesting high electrocatalytic activity.
   - **Embedded Configuration**: Fits a linear correlation curve ($R^2 = 0.770$). The embedded metals exhibit very positive free energies ($\Delta G_{\text{H}} > 1.3$ eV) and reside outside the active window, showing poor catalytic activity due to steric limits and strong coordination within the $\text{CrCl}_3$ host.
