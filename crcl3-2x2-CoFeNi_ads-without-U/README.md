# CrCl3 2x2 Monolayer Transition Metal Adsorption Suite (Co, Fe, Ni)
**SLURM Optimized Suite: Pure GGA-PBE (no_vdw) vs PBE + DFT-D3 (yes_vdw, IVDW = 12 Zero-Damping), U = 0 eV**

## 1. Directory Structure (Zero Symlinks, Direct Folders)
```text
crcl3-2x2-CoFeNi_ads-without-U/
├── crcl3-2x2-co_ads-without-U/   # Cobalt suite (8 calculations)
│   ├── no_vdw/                   # clean, S1, S2, S3
│   └── yes_vdw/                  # clean, S1, S2, S3 (IVDW = 12)
├── crcl3-2x2-fe_ads-without-U/   # Iron suite (8 calculations)
│   ├── no_vdw/                   # clean, S1, S2, S3
│   └── yes_vdw/                  # clean, S1, S2, S3 (IVDW = 12)
├── crcl3-2x2-ni_ads-without-U/   # Nickel suite (8 calculations)
│   ├── no_vdw/                   # clean, S1, S2, S3
│   └── yes_vdw/                  # clean, S1, S2, S3 (IVDW = 12)
├── submit_slurm_jobs.sh          # Master SLURM cluster submission & monitoring script
├── verify_all.py                 # Standalone verification runner (408 checks)
├── pack_cofeni_suite.py          # Clean pack script (no symlinks)
└── README.md
```

## 2. Cluster Portability
- **Self-detecting paths**: Every `job.sh` detects its own path dynamically via `BASH_SOURCE[0]`. No hardcoded local machine paths (`/home/cr/...`).
- **Dynamic scratch space**: Automatically routes to `$SLURM_TMPDIR` (fast node SSD), `$SCRATCH/$USER`, or `/tmp/$USER/scratch_vasp`.
- **Zero symlinks**: No broken links or duplicate files during `scp`, `rsync`, or `tar -xzf`.

## 3. Cluster Submission Commands
```bash
# Check status of all 24 calculations
./submit_slurm_jobs.sh status

# Submit all 24 calculations to SLURM
./submit_slurm_jobs.sh submit-all

# Submit only a specific metal
./submit_slurm_jobs.sh submit co
./submit_slurm_jobs.sh submit fe
./submit_slurm_jobs.sh submit ni

# Submit only a specific vdW variant
./submit_slurm_jobs.sh submit yes_vdw
./submit_slurm_jobs.sh submit no_vdw
```
