# CrCl3 (2x2) Multi-Tier Suite: U_all = 3.29 eV (`crcl3-2x2-CoFeNi-vdw12-U_all3.29`)

This directory contains the completed 12 calculations representing Tier 3 ($+U_{\text{all}} = 3.29\text{ eV}$ on Cr and TM species) under PBE+D3(BJ) (IVDW = 12).

---

## 📌 Important Site Provenance Note

The "adsorbed" systems in this directory were seeded from the lowest-energy states available during the multi-tier progression:

* **`adsorbed/Co/clean`**: **Site S3 (Top-Cr)**
  - Adatom Co sits directly atop Chromium #2 at $(x,y) = (0.667, 0.333)$.
  - Vertical height: $\Delta z_{\text{Co-Cr}} = +2.28\text{ \AA}$.
* **`adsorbed/Fe/clean`**: **Pore-Penetrated Ground State**
  - Adatom Fe sits inside the central hollow pore, nearly coplanar with Chromium ($z = 0.513$, $\Delta z_{\text{Fe-Cr}} = +0.18\text{ \AA}$).
  - Derived from unconstrained relaxation of the $S_1$ pathway.
* **`adsorbed/Ni/clean`**: **Site S2 (Threefold Surface Hollow)**
  - Adatom Ni sits exposed above the monolayer in the threefold hollow site at $(x,y) = (0.500, 0.500)$.
  - Vertical height: $\Delta z_{\text{Ni-Cr}} = +1.40\text{ \AA}$.

* **`embedded/*`**: **In-Plane Interstitial**
  - All embedded systems (Co, Fe, Ni) are coplanar interstitials centered inside the hexagonal pore ($\Delta z_{\text{TM-Cr}} \approx 0.00\text{ \AA}$).

For the systematic 9-calculation site suite where Co, Fe, and Ni are evaluated uniformly across all three individual sites ($S_1$, $S_2$, $S_3$), see:
`../crcl3-2x2-CoFeNi-sites-vdw12-U_all3.29/`
