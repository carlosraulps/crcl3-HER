# $\mathrm{CrCl}_3$ Monolayer: Band Gap vs. Hubbard $U$ Parameter

### Simulation Parameters
- **Structure**: $1\times 1$ Primitive Cell ($P\bar{3}1m$, $a = 6.0485\text{ \AA}$, $c = 17.67\text{ \AA}$, $\mathrm{Cr}_2\mathrm{Cl}_6$)
- **Functional**: PBE + Grimme DFT-D3 (`IVDW = 11`) + Dudarev DFT+$U$ (`LDAUTYPE = 2` on $\mathrm{Cr}\ 3d$)
- **PAW Flags**: `LASPH = .TRUE.`, `LMAXMIX = 4`, `ENCUT = 400.0\text{ eV}`
- **Smearing**: Gaussian smearing ($\sigma = 0.05\text{ eV}$), $11\times 11\times 1$ $\Gamma$-centered mesh

### Results Summary

| $U$ (eV) | Status | $E_{\text{tot}}$ (eV) | $E_{\text{F}}$ (eV) | $M_{\text{cell}}$ ($\mu_{\text{B}}$) | $\mu_{\mathrm{Cr}}$ ($\mu_{\text{B}}$) | $E_g$ (eV) | $E_{g,\uparrow}$ (eV) | $E_{g,\downarrow}$ (eV) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | `Completed` | -39.9928 | -3.804 | 6.00 | 2.91 | **1.817** | 1.817 | 3.269 |
| **1** | `Completed` | -38.8067 | -4.185 | 6.00 | 2.98 | **2.113** | 2.113 | 3.539 |
| **2** | `Completed` | -37.6763 | -4.515 | 6.00 | 3.04 | **2.359** | 2.359 | 3.811 |
| **3** | `Completed` | -36.5986 | -4.768 | 6.00 | 3.10 | **2.536** | 2.536 | 4.079 |
| **4** | `Completed` | -35.5724 | -4.856 | 6.00 | 3.17 | **2.587** | 2.587 | 4.339 |
| **5** | `Completed` | -34.5928 | -4.952 | 6.00 | 3.23 | **2.557** | 2.557 | 4.610 |
| **6** | `Completed` | -33.6618 | -4.989 | 6.00 | 3.29 | **2.516** | 2.516 | 4.879 |

