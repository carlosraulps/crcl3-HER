# LOBSTER COHP Suite with U_all = 3.29 eV (`cohp_lobster_Uall`)

This directory contains the Crystal Orbital Hamilton Population (COHP) calculations using LOBSTER 4.1.0 with Dudarev Hubbard $U = 3.29\text{ eV}$ applied to all $3d$ transition metal species.

---

## 📌 Uniform Site Definition (Matching Manuscript Section 3.2)

Unlike earlier non-uniform suites, the adsorbed calculations here are **strictly uniform at Site S2 (Threefold Surface Hollow)** for all three transition metals, matching the configurations described in Manuscript Section 3.2 (Figures 3 and 4):

* **`adsorbed/Co`**: **Site S2 (Threefold Surface Hollow)**
  - Co located at $(x,y) = (0.500, 0.500)$ with $\Delta z_{\text{Co-Cr}} = +1.88\text{ \AA}$.
* **`adsorbed/Fe`**: **Site S2 (Threefold Surface Hollow)**
  - Fe located at $(x,y) = (0.500, 0.500)$ with $\Delta z_{\text{Fe-Cr}} = +1.77\text{ \AA}$.
* **`adsorbed/Ni`**: **Site S2 (Threefold Surface Hollow)**
  - Ni located at $(x,y) = (0.500, 0.500)$ with $\Delta z_{\text{Ni-Cr}} = +1.43\text{ \AA}$.

* **`embedded/*`**: **In-Plane Interstitial**
  - Co, Fe, Ni embedded in the monolayer interior, coplanar with the Cr plane ($\Delta z_{\text{TM-Cr}} \approx 0.00\text{ \AA}$).
