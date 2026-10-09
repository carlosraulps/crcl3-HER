# CrCl3 (2x2) Band Structures with U_Cr = 3.29 eV (`bands_U_Cr`)

This directory contains the electronic band structure calculations along the high-symmetry path $\Gamma \to \mathrm{M} \to \mathrm{K} \to \Gamma$ under PBE+D3(BJ) with Dudarev Hubbard $U = 3.29\text{ eV}$ applied to Chromium $3d$ orbitals.

---

## 📌 Site Provenance of the Adsorbed & Embedded Series

* **`adsorbed/Co`**: **Site S3 (Top-Cr)**
  - Co located at $(x,y) = (0.667, 0.333)$, apical above Cr ($\Delta z_{\text{Co-Cr}} = +2.28\text{ \AA}$).
* **`adsorbed/Fe`**: **Pore-Penetrated Ground State**
  - Fe located inside the central hollow pore at $(x,y) = (0.500, 0.499)$, nearly coplanar with Cr ($\Delta z_{\text{Fe-Cr}} = +0.18\text{ \AA}$).
* **`adsorbed/Ni`**: **Site S2 (Threefold Surface Hollow)**
  - Ni located in the threefold hollow site at $(x,y) = (0.500, 0.500)$, above the surface ($\Delta z_{\text{Ni-Cr}} = +1.43\text{ \AA}$).

* **`embedded/*`**: **In-Plane Interstitial**
  - Co, Fe, Ni embedded in the monolayer interior, coplanar with the Cr plane ($\Delta z_{\text{TM-Cr}} \approx 0.00\text{ \AA}$).
