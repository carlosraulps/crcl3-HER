# Systematic 9-System Site Suite: U_all = 3.29 eV (`crcl3-2x2-CoFeNi-sites-vdw12-U_all3.29`)

This directory contains the systematic $3 \times 3 = 9$ site calculations designed to rigorously evaluate site competition across all transition metals (Co, Fe, Ni) and all three adsorption sites ($S_1$, $S_2$, $S_3$) under Dudarev Hubbard $U = 3.29\text{ eV}$ on Cr and TM species under PBE+D3(BJ) (IVDW = 12).

---

## 📌 Canonical Site Directory Matrix

### 1. Cobalt (`Co/`)
* **`Co/S1`**: **Surface Hollow (Relaxed from Top-Cl path)**
  - Initial setup: $(0.500, 0.497, 0.597)$
  - Final converged state: $(0.500, 0.498, 0.594)$, $E_0 = \mathbf{-150.47078\text{ eV}}$, $M = 27.00\,\mu_{\mathrm{B}}$
  - Note: Unconstrained relaxation starting on top of Cl spontaneously slides into this hollow minimum.
* **`Co/S2`**: **Threefold Surface Hollow (Symmetric)**
  - Initial setup: $(0.500, 0.500, 0.593)$
  - Final converged state: $(0.500, 0.500, 0.592)$, $E_0 = \mathbf{-150.41006\text{ eV}}$, $M = 27.00\,\mu_{\mathrm{B}}$
  - Energy difference vs S1: $\Delta E = +0.061\text{ eV}$ ($+5.86\text{ kJ/mol}$)
* **`Co/S3`**: **Apical Top-Cr Site**
  - Initial setup: $(0.667, 0.333, 0.613)$
  - Currently relaxing on Huk node `huk125` (Job 8179), $E_0 \approx -149.785\text{ eV}$.

---

### 2. Iron (`Fe/`)
* **`Fe/S1`**: **Deep Pore-Penetrated Ground State**
  - Initial setup: $(0.500, 0.499, 0.513)$
  - Final converged state: $(0.500, 0.498, 0.513)$, $E_0 = \mathbf{-153.37421\text{ eV}}$, $M = 30.00\,\mu_{\mathrm{B}}$
  - Note: Fe penetrates into the pore plane, nearly coplanar with Cr ($\Delta z_{\text{Fe-Cr}} = +0.18\text{ \AA}$).
* **`Fe/S2`**: **Threefold Surface Hollow**
  - Initial setup: $(0.500, 0.500, 0.587)$ ($\Delta z_{\text{Fe-Cr}} = +1.77\text{ \AA}$)
  - Currently relaxing on Carbono node `n07` (Job 171122).
* **`Fe/S3`**: **Apical Top-Cr Site**
  - Initial setup: $(0.667, 0.333, 0.627)$ ($\Delta z_{\text{Fe-Cr}} = +2.54\text{ \AA}$)
  - Currently relaxing on Huk node `huk124` (Job 8191).

---

### 3. Nickel (`Ni/`)
* **`Ni/S1`**: **Near-Cl Rim Coordinated State**
  - Initial setup: $(0.500, 0.095, 0.564)$ ($\Delta z_{\text{Ni-Cr}} = +1.28\text{ \AA}$)
  - In queue on Carbono (`n08`, Job 171124).
* **`Ni/S2`**: **Threefold Surface Hollow Ground State**
  - Initial setup: $(0.500, 0.500, 0.571)$ ($\Delta z_{\text{Ni-Cr}} = +1.43\text{ \AA}$)
  - In queue on Carbono (Job 171125).
* **`Ni/S3`**: **Apical Top-Cr Site**
  - Initial setup: $(0.667, 0.333, 0.621)$ ($\Delta z_{\text{Ni-Cr}} = +2.42\text{ \AA}$)
  - In queue on Carbono (Job 171126).
