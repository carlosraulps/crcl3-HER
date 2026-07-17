# VASP + LOBSTER Postprocessing Summary

This document summarizes the energetics, magnetic properties, and LOBSTER COHP bonding analysis for the CrCl3 monolayer functionalized with transition metals (Co, Fe, Ni) in both adsorbed and embedded configurations.

## 1. Energetics and Magnetic Moments

| System | TOTEN (eV) | Fermi Level (eV) | Total Magnetization ($\mu_B$) | TM Local Mag. Moment ($\mu_B$) | Avg. TM-Cl ICOHP (eV) | Cumulative TM-Cl ICOHP (eV) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **adsorbed/co** | -160.0665 | -2.4137 | 26.9997 | 1.7820 | -2.2332 | -6.6996 |
| **adsorbed/fe** | -161.2266 | -2.3810 | 29.1210 | 2.7220 | -2.2799 | -6.8396 |
| **adsorbed/ni** | -159.4708 | -2.6569 | 24.0000 | -0.7550 | -2.0604 | -6.1812 |
| **embedded/co** | -160.8042 | -2.3978 | 27.1167 | 2.0840 | -1.8705 | -11.2230 |
| **embedded/fe** | -162.1081 | -2.4717 | 28.9597 | 3.2960 | -1.9007 | -11.4043 |
| **embedded/ni** | -159.3190 | -2.4916 | 23.9998 | -1.0220 | -1.6687 | -10.0122 |

## 2. Relative Stability (Embedding Energy Difference)

The energy difference between embedded and adsorbed configurations ($E_{\text{diff}} = E_{\text{embedded}} - E_{\text{adsorbed}}$) determines the thermodynamic preference for metal incorporation:

*   **Cobalt (Co):** $E_\text{diff} = -0.7377\text{ eV}$ (Embedded is more stable by **0.7377 eV**)
*   **Iron (Fe):** $E_\text{diff} = -0.8816\text{ eV}$ (Embedded is more stable by **0.8816 eV**)
*   **Nickel (Ni):** $E_\text{diff} = 0.1518\text{ eV}$ (Adsorbed is more stable by **0.1518 eV**)

## 3. Detailed Bond Parameters

### adsorbed/co
| Bond | Length (Å) | COHP at $E_F$ | LOBSTER ICOHP (eV) |
| :--- | :---: | :---: | :---: |
| Cl24-Co33 | 2.220 | -0.0029 | -2.1803 |
| Cl26-Co33 | 2.219 | 0.0335 | -2.3468 |
| Cl31-Co33 | 2.219 | 0.0655 | -2.1724 |

### adsorbed/fe
| Bond | Length (Å) | COHP at $E_F$ | LOBSTER ICOHP (eV) |
| :--- | :---: | :---: | :---: |
| Cl24-Fe33 | 2.262 | -0.0055 | -2.1044 |
| Cl26-Fe33 | 2.262 | 0.1007 | -2.4048 |
| Cl31-Fe33 | 2.262 | 0.2838 | -2.3303 |

### adsorbed/ni
| Bond | Length (Å) | COHP at $E_F$ | LOBSTER ICOHP (eV) |
| :--- | :---: | :---: | :---: |
| Cl24-Ni33 | 2.159 | -0.0000 | -2.2661 |
| Cl26-Ni33 | 2.158 | 0.0000 | -2.1480 |
| Cl31-Ni33 | 2.158 | 0.0000 | -1.7671 |

### embedded/co
| Bond | Length (Å) | COHP at $E_F$ | LOBSTER ICOHP (eV) |
| :--- | :---: | :---: | :---: |
| Cl11-Co33 | 2.470 | 0.0167 | -2.5532 |
| Cl13-Co33 | 2.472 | 0.0032 | -2.3476 |
| Cl20-Co33 | 2.478 | 0.0074 | -2.3179 |
| Cl23-Co33 | 2.471 | 0.2266 | -1.3420 |
| Cl25-Co33 | 2.479 | 0.2224 | -1.3327 |
| Cl32-Co33 | 2.473 | 0.2220 | -1.3296 |

### embedded/fe
| Bond | Length (Å) | COHP at $E_F$ | LOBSTER ICOHP (eV) |
| :--- | :---: | :---: | :---: |
| Cl11-Fe33 | 2.507 | 0.0185 | -2.5535 |
| Cl13-Fe33 | 2.501 | -0.0036 | -2.3035 |
| Cl20-Fe33 | 2.505 | 0.0082 | -2.2968 |
| Cl23-Fe33 | 2.506 | 0.2575 | -1.4175 |
| Cl25-Fe33 | 2.503 | 0.2627 | -1.4086 |
| Cl32-Fe33 | 2.500 | 0.2597 | -1.4244 |

### embedded/ni
| Bond | Length (Å) | COHP at $E_F$ | LOBSTER ICOHP (eV) |
| :--- | :---: | :---: | :---: |
| Cl11-Ni33 | 2.344 | 0.0000 | -2.5600 |
| Cl13-Ni33 | 2.400 | 0.0000 | -2.4467 |
| Cl20-Ni33 | 2.953 | 0.0000 | -2.4106 |
| Cl23-Ni33 | 2.350 | 0.0000 | -1.0551 |
| Cl25-Ni33 | 2.622 | 0.0000 | -0.6524 |
| Cl32-Ni33 | 2.378 | 0.0000 | -0.8873 |

