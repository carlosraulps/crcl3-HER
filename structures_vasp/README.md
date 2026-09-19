# CrCl₃ Hydrogen Adsorption Structures (Initial & Optimized)

This directory contains standardized `.vasp` POSCAR/CONTCAR structure files for hydrogen adsorption on monolayer $\text{CrCl}_3$ across $2\times2$ and $1\times1$ supercell scales, comparing both Pure PBE (`no_vdw`) and PBE+D3 (`yes_vdw`).

All files are directly compatible with visualization and modeling packages (**VESTA**, **OVITO**, **ASE**, **pymatgen**, **XCrySDen**).

---

## 1. Directory Layout & File Naming Convention

```
structures_vasp/
├── 2x2/
│   ├── no_vdw/
│   │   ├── crcl3_2x2_no_vdw_clean_pristine_initial.vasp
│   │   ├── crcl3_2x2_no_vdw_clean_pristine_optimized.vasp
│   │   ├── crcl3_2x2_no_vdw_S1_top_Cl_initial.vasp
│   │   ├── crcl3_2x2_no_vdw_S1_top_Cl_optimized.vasp
│   │   ├── crcl3_2x2_no_vdw_S2_hollow_initial.vasp
│   │   ├── crcl3_2x2_no_vdw_S2_hollow_optimized.vasp
│   │   ├── crcl3_2x2_no_vdw_S3_top_Cr_initial.vasp
│   │   └── crcl3_2x2_no_vdw_S3_top_Cr_optimized.vasp
│   └── yes_vdw/
│       ├── crcl3_2x2_yes_vdw_clean_pristine_initial.vasp
│       ├── crcl3_2x2_yes_vdw_clean_pristine_optimized.vasp
│       ├── crcl3_2x2_yes_vdw_S1_top_Cl_initial.vasp
│       ├── crcl3_2x2_yes_vdw_S1_top_Cl_optimized.vasp
│       ├── crcl3_2x2_yes_vdw_S2_hollow_initial.vasp
│       ├── crcl3_2x2_yes_vdw_S2_hollow_optimized.vasp
│       ├── crcl3_2x2_yes_vdw_S3_top_Cr_initial.vasp
│       └── crcl3_2x2_yes_vdw_S3_top_Cr_optimized.vasp
└── 1x1/
    ├── no_vdw/ ...
    └── yes_vdw/ ...
```

**Naming Template:**  
`crcl3_{SCALE}_{VARIANT}_{SITE}_{DESCRIPTION}_{STATE}.vasp`
- `{SCALE}`: `2x2` ($a = 12.09$ Å, $\theta = 0.25$) or `1x1` ($a = 6.05$ Å, $\theta = 1.00$)
- `{VARIANT}`: `no_vdw` (Pure PBE) or `yes_vdw` (PBE + Grimme DFT-D3 zero-damping)
- `{SITE}`: `S1` (Top-Cl), `S2` (Hollow), `S3` (Top-Cr), or `clean` (Pristine slab)
- `{STATE}`: `initial` (unrelaxed input POSCAR) or `optimized` (DFT-relaxed CONTCAR)

---

## 2. Adsorption Site Key Coordinates & Geometries ($2\times2$ Supercell)

| Site | Target Atom | Initial $d(\text{H-Target})$ | Relaxed $d(\text{H-Target})$ | In-Plane Shift $\Delta r_{xy}$ | Out-of-Plane Shift $\Delta z$ |
|:---|:---|:---:|:---:|:---:|:---:|
| **$S_1$ (Top-Cl)** | $\text{Cl}_{19}$ (top layer) | $1.300$ Å | **$1.255 - 1.268$ Å** | $\approx 0.0008$ Å | $+0.077 - +0.079$ Å |
| **$S_2$ (Hollow)** | Center of Cr ring | $1.600$ Å above Cr | $1.520 - 1.580$ Å | $< 0.002$ Å | $-0.020 - -0.080$ Å |
| **$S_3$ (Top-Cr)** | $\text{Cr}_3$ (metal cation) | $1.550$ Å | **$1.544 - 1.546$ Å** | **$0.0000$ Å ($C_3$)** | $+0.140 - +0.195$ Å |
| **Clean** | — | — | Fully relaxed | — | — |

---

## 3. Substrate Restructuring Highlights

- **Site $S_1$:** The coordinated $\text{Cl}_{19}$ ligand pulls upward toward vacuum by $+0.134$ Å. The underlying $\text{Cr}_3\text{--Cl}_{19}$ bond elongates from $2.357$ Å to $2.687$ Å (+14% bond stretching).
- **Site $S_3$:** The $\text{Cr}_3$ cation puckers upward by $+0.199$ Å toward the adsorbate, while the 3 coordinating top-layer chlorine ligands expand symmetrically by $+0.030$ Å.
